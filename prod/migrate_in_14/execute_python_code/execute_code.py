from odoo import models, fields,api
from odoo.exceptions import Warning
import functools
import logging
_logger = logging.getLogger('base.company.merge')
from odoo.tools import mute_logger
import psycopg2

class execute_code(models.Model):
    _name = 'execute.code'
    
    name = fields.Char('Name')
    query_text = fields.Text('Query Text')
    result_text = fields.Text('Result')
    
#     @api.multi
    def execute_code(self):
        if self.query_text:
            localdict = {
                        'self':self, 
                        'cr': self._cr,
                        'uid': self._uid,
                        'result': None, #used to store the result of the test
                        'context': self._context or {},
                        'user':self.env.user
                        }
            #try:
            exec(self.query_text, localdict)
            #result = eval(self.query_text, localdict)
            self.write({'result_text':localdict.get('result','')})
#             except Exception, e:
#                 raise Warning(str(e))
        return True           

    def _get_fk_on(self, table):
        """ return a list of many2one relation with the given table.
            :param table : the name of the sql table to return relations
            :returns a list of tuple 'table name', 'column name'.
        """
        query = """
            SELECT cl1.relname as table, att1.attname as column
            FROM pg_constraint as con, pg_class as cl1, pg_class as cl2, pg_attribute as att1, pg_attribute as att2
            WHERE con.conrelid = cl1.oid
                AND con.confrelid = cl2.oid
                AND array_lower(con.conkey, 1) = 1
                AND con.conkey[1] = att1.attnum
                AND att1.attrelid = cl1.oid
                AND cl2.relname = %s
                AND att2.attname = 'id'
                AND array_lower(con.confkey, 1) = 1
                AND con.confkey[1] = att2.attnum
                AND att2.attrelid = cl2.oid
                AND con.contype = 'f'
        """
        self._cr.execute(query, (table,))
        return self._cr.fetchall()

    @api.model
    def _update_foreign_keys(self, src_products, dst_product, table_name):
        """ Update all foreign key from the src_product to dst_product. All many2one fields will be updated.
            :param src_products : merge source product.product recordset (does not include destination one)
            :param dst_product : record of destination product.product
        """
        #_logger.debug('_update_foreign_keys for dst_product: %s for src_products: %s', dst_product.id, str(src_products.ids))

        # find the many2one relation to a marketplace.product.product
        relations = self._get_fk_on(table_name)

        for table, column in relations:
            if 'res_company' in table or 'res_users' in table:  # ignore two tables
                continue

            # get list of columns of current table (exept the current fk column)
            query = "SELECT column_name FROM information_schema.columns WHERE table_name LIKE '%s'" % (table)
            self._cr.execute(query, ())
            columns = []
            for data in self._cr.fetchall():
                if data[0] != column:
                    columns.append(data[0])

            # do the update for the current table/column in SQL
            query_dic = {
                'table': table,
                'column': column,
                'value': columns[0],
            }
            if len(columns) <= 1:
                # unique key treated
                query = """
                    UPDATE "%(table)s" as ___tu
                    SET %(column)s = %%s
                    WHERE
                        %(column)s = %%s AND
                        NOT EXISTS (
                            SELECT 1
                            FROM "%(table)s" as ___tw
                            WHERE
                                %(column)s = %%s AND
                                ___tu.%(value)s = ___tw.%(value)s
                        )""" % query_dic
                for product in src_products:
                    self._cr.execute(query, (dst_product, product, dst_product))
            else:
                try:
                    with mute_logger('odoo.sql_db'), self._cr.savepoint():
                        query = 'UPDATE "%(table)s" SET %(column)s = %%s WHERE %(column)s IN %%s' % query_dic
                        self._cr.execute(query, (dst_product, tuple(src_products),))

                except psycopg2.Error:
                    pass
                    # updating fails, most likely due to a violated unique constraint
                    # keeping record with nonexistent product_id is useless, better delete it
                    #query = 'DELETE FROM %(table)s WHERE %(column)s IN %%s' % query_dic
                    #self._cr.execute(query, (tuple(src_products),))

    @api.model
    def _update_reference_fields(self, src_partners, dst_partner):
        """ Update all reference fields from the src_partner to dst_partner.
            :param src_partners : merge source res.partner recordset (does not include destination one)
            :param dst_partner : record of destination res.partner
        """
        #_logger.debug('_update_reference_fields for dst_partner: %s for src_partners: %r', dst_partner.id, src_partners.ids)

        def update_records(model, src_id, field_model='model', field_id='res_id'):
            Model = self.env[model] if model in self.env else None
            if Model is None:
                return
            records = Model.sudo().search([(field_model, '=', 'res.company'), (field_id, '=', src_id)])
            try:
                with mute_logger('odoo.sql_db'), self._cr.savepoint():
                    return records.sudo().write({field_id: dst_partner})
            except psycopg2.Error:
                # updating fails, most likely due to a violated unique constraint
                # keeping record with nonexistent partner_id is useless, better delete it
                return records.sudo().unlink()

        update_records = functools.partial(update_records)

        for partner in src_partners:
            #update_records('calendar', src=partner, field_model='model_id.model')
            update_records('ir.attachment', src_id=partner, field_model='res_model')
            update_records('mail.followers', src_id=partner, field_model='res_model')
            update_records('mail.message', src_id=partner)
            update_records('ir.model.data', src_id=partner)

        records = self.env['ir.model.fields'].search([('ttype', '=', 'reference')])
        for record in records.sudo():
            try:
                Model = self.env[record.model]
                field = Model._fields[record.name]
            except KeyError:
                # unknown model or field => skip
                continue

            if field.compute is not None:
                continue

            for partner in src_partners:
                records_ref = Model.sudo().search([(record.name, '=', 'res.company,%d' % partner)])
                values = {
                    record.name: 'res.company,%d' % dst_partner,
                }
                records_ref.sudo().write(values)    
