# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date, datetime
from xlsxwriter.workbook import Workbook
from io import BytesIO
import calendar
import base64

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

MONTHS_SELECTION = [
    ('1', _('January')),
    ('2', _('February')),
    ('3', _('March')),
    ('4', _('April')),
    ('5', _('May')),
    ('6', _('June')),
    ('7', _('July')),
    ('8', _('August')),
    ('9', _('September')),
    ('10', _('October')),
    ('11', _('November')),
    ('12', _('December'))
]

YEARS_SELECTION = [
    ('2016', '2016'),
    ('2017', '2017'),
    ('2018', '2018'),
    ('2019', '2019'),
    ('2020', '2020'),
    ('2021', '2021'),
    ('2022', '2022'),
    ('2023', '2023'),
]

class FbInventoryReport(models.TransientModel):
    _name = 'fb.inventory.report'
    _description = 'FB Inventory Report'

    report_filename = fields.Char('Filename', compute='_compute_report_filename')

    state = fields.Selection(selection=[('draft','draft'),('done','done')], required=True, default='draft')
    start_month = fields.Selection(selection=MONTHS_SELECTION, string='From', readonly=True, states={'draft': [('readonly', False)]})
    end_month = fields.Selection(selection=MONTHS_SELECTION, string='To', readonly=True, states={'draft': [('readonly', False)]})
    year = fields.Selection(selection=YEARS_SELECTION, string='Year', required=True, readonly=True, states={'draft': [('readonly', False)]})

    result_report = fields.Binary(string='Inventory report', readonly=True)

    product_id = fields.Many2one('product.product', string='Product', required=True, readonly=True, states={'draft': [('readonly', False)]}, domain=[('type','=','product')])
    location_id = fields.Many2one('stock.location', string='Location', readonly=True, states={'draft': [('readonly', False)]}, domain=[('usage','=','internal')])
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', readonly=True, states={'draft': [('readonly', False)]})

    @api.depends('year','start_month','end_month','product_id','location_id','warehouse_id')
    def _compute_report_filename(self):
        for record in self:
            product_id = record.product_id.default_code or record.product_id.barcode or str(record.product_id.id)
            period_part = (record.start_month and str(record.start_month) or '1') + '-' + (record.end_month and str(record.end_month) or '12') + '-' + str(record.year)
            res = 'INV-%s_%s.xlsx' %(product_id, period_part)
            record.report_filename = res   
    
    def generate_inventory_report(self):
        self.ensure_one()

        if self.state != 'draft':
            return False

        if not (self.location_id or self.warehouse_id):
            raise ValidationError(_('You must select warehouse or location!'))


        current_date = date.today()
        year = int(self.year)
        start_month = int(self.start_month) or 1
        end_month = int(self.end_month) or current_date.month

        if end_month > current_date.month:
            end_month = current_date.month

        d1 = date(year, start_month, 1)

        if d1 > current_date or end_month < start_month:
            raise ValidationError(_('Incorrect period settings!'))

        location = self.location_id
        product = self.product_id
        warehouse = self.warehouse_id

        if warehouse:
            location = warehouse.view_location_id
            product = product.with_context(warehouse=warehouse.id)
        else:
            product = product.with_context(location=location.id)

        location_ids = self.env['stock.location'].search([('id','child_of',location.id)]).ids

        company_id = self.env.user.company_id.id
        date_format = '%d.%m.%Y' if self.env.user.lang == 'de_DE' else DEFAULT_SERVER_DATE_FORMAT

        sm_query = "select sum(sm.product_qty) from stock_move sm where id in %s;"

        export_stream = BytesIO()
        excel_wkb = Workbook(export_stream)
        wsh = excel_wkb.add_worksheet('Inventory data')
        wsh.set_column(0, 0, 40)
        wsh.set_column(1, 1, 12)
        wsh.set_column(2, 2, 17)
        wsh.set_column(3, 3, 7)
        wsh.set_column(4, 4, 10)
        wsh.set_column(5, 5, 15)

        period_data_cell_format = excel_wkb.add_format({'bg_color':'#D2C9CB'})
        headers_cell_format = excel_wkb.add_format({'bg_color':'#92D5EC'})

        first_row = [product.display_name]
        second_row = [location.display_name]
        third_row = [_('Cost price'), _('Inventory value')]
        row_in_between = [''] * 5

        wsh.write_row(0, 0, first_row, cell_format=headers_cell_format)
        wsh.write_row(1, 0, second_row, cell_format=headers_cell_format)
        wsh.write_row(2, 4, third_row, cell_format=headers_cell_format)

        row_counter = 2

        for month_no in range(start_month, end_month+1):
            row_counter += 1
            start_date = datetime(year, month_no, 1, 0, 0, 1)
            last_day_no = calendar.monthrange(year, month_no)
            end_date = datetime(year, month_no, last_day_no[1], 23, 59, 59)

            if end_date.date() > current_date:
                end_date = datetime(current_date.year, current_date.month, current_date.day, 23, 59, 59)

            out_qty = '0'
            in_qty = '0'

            product_1 = product.with_context(to_date=str(start_date))
            # start_qty = str(product_1.qty_at_date)
            start_qty = str(product_1.free_qty)
            start_price = str(product_1.standard_price)
            #start_price = str(product_1.get_history_price(company_id, date=str(start_date)))
            #start_value = str(product_1.stock_value)
            start_value = str(product_1.value_svl)

            product_2 = product.with_context(to_date=str(end_date))
            #end_qty = str(product_2.qty_at_date)
            end_qty = str(product_2.free_qty)
            end_price = str(product_2.standard_price)
            # end_price = str(product_2.get_history_price(company_id, date=str(end_date)))
            #end_value = str(product_2.stock_value)
            end_value = str(product_2.value_svl)

            outgoing_move_ids = self.env['stock.move'].search([
                ('state', '=', 'done'),
                ('product_id', '=', product.id),
                ('location_id', 'in', location_ids),
                ('location_dest_id','not in',location_ids),
                ('date','>=',str(start_date)),
                ('date','<=',str(end_date))
            ]).ids

            incoming_move_ids = self.env['stock.move'].search([
                ('state', '=', 'done'),
                ('product_id', '=', product.id),
                ('location_dest_id', 'in', location_ids),
                ('location_id', 'not in', location_ids),
                ('date', '>=', str(start_date)),
                ('date', '<=', str(end_date))
            ]).ids

            if outgoing_move_ids:
                self.env.cr.execute(sm_query %(str(tuple(outgoing_move_ids)).replace(',)',')')))
                out_qty = str(float(self.env.cr.fetchone()[0] or 0))

            if incoming_move_ids:
                self.env.cr.execute(sm_query %(str(tuple(incoming_move_ids)).replace(',)', ')')))
                in_qty = str(float(self.env.cr.fetchone()[0] or 0))

            row_1 = [start_date.date().strftime(date_format), _('Quantity at start'), start_qty, start_price,start_value]
            row_2 = ['', _('Received'), in_qty, '', '']
            row_3 = ['', _('Delivered'), out_qty, '', '']
            row_4 = [end_date.date().strftime(date_format), _('Quantity at end'), end_qty,end_price, end_value]

            wsh.write_row(row_counter, 1, row_1, cell_format=period_data_cell_format)
            wsh.write_row(row_counter+1, 1, row_2, cell_format=period_data_cell_format)
            wsh.write_row(row_counter+2, 1, row_3, cell_format=period_data_cell_format)
            wsh.write_row(row_counter+3, 1, row_4, cell_format=period_data_cell_format)
            wsh.write_row(row_counter+4, 1, row_in_between)
            wsh.write_row(row_counter+5, 1, row_in_between)

            row_counter = row_counter + 5

        excel_wkb.close()
        res_report = base64.b64encode(export_stream.getvalue())
        self.write({'result_report': res_report, 'state':'done'})

        result = self.env['ir.actions.act_window']._for_xml_id('frogblue_extensions.fb_inventory_report_action')
        result['res_id'] = self.id
        return result

    @api.model
    def default_get(self, fields):
        res = super(FbInventoryReport, self).default_get(fields)
        res['year'] = str((date.today().year))
        return res
