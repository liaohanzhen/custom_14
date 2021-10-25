import base64
import logging
from datetime import datetime
from io import BytesIO

from odoo import models, fields, api
from odoo.exceptions import except_orm, Warning, ValidationError, UserError

_logger = logging.getLogger(__name__)

try:
    from odoo.addons.import_order_xls.python_library import openpyxl
    from odoo.addons.import_order_xls.python_library.openpyxl import load_workbook
    from odoo.addons.import_order_xls.python_library.openpyxl import Workbook
except ImportError:
    _logger.error('Odoo module import_order_xls depends on the openpyxl python module')
    openpyxl = None
    load_workbook = None
    Workbook = None

try:
    from odoo.addons.import_order_xls.python_library import xlrd
except ImportError:
    _logger.error('Odoo module import_order_xls depends on the xlrd python module')
    xlrd = None


class process_order_import(models.TransientModel):
    _name = 'process.order.import'
    _description = 'Process to import sale order from excel file'

    choose_file = fields.Binary('Choose File', filters='*.xlsx')
    file_name = fields.Char('Filename', size=512)
    datas = fields.Binary('File')

    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        res = super(process_order_import, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                                submenu=submenu)
        sale_obj = self.env['sale.order']
        orders = []
        for order in sale_obj.browse(self.env.context.get('active_ids')):
            if order.state != "draft":
                raise Warning(('Unable to process..! You can process with only draft sale order!.'))
            orders.append(order)

        if len(orders) > 1:
            raise Warning(('Unable to process..! You can process only one sale order at a time!.'))

        return res


    def get_file_name(self, name=datetime.strftime(datetime.now(), '%Y%m%d%H%M%S%f')):
        return '/tmp/sale_order_%s_%s.xlsx' % (self.env.uid, name)

    def get_header(self, worksheet):
        column_header = {}
        columns = worksheet.max_column
        for row in worksheet.iter_rows():
            if row[0].row > 1 or not next((r for r in row if r.row), None):
                break
            for col in range(1, columns + 1):
                column_header.update({col: str(worksheet.cell(row=1, column=col).value).lower()})
        return column_header

    def read_file_xls(self):
        file_name = self.file_name
        file_path = '/tmp/%s_%s' % (datetime.strftime(datetime.now(), '%Y%m%d%H%M%S%f'), file_name)
        fp = open(file_path, 'wb')
        fp.write(base64.decodebytes(self.choose_file))
        fp.close()
        xl_workbook = xlrd.open_workbook(file_path)
        return xl_workbook

    def fill_dictionary_from_xls_file(self, xl_sheet, keys):
        dict_list = []
        for row_index in range(1, xl_sheet.nrows):
            d = {keys[col_index]: xl_sheet.cell(row_index, col_index).value
                 for col_index in range(xl_sheet.ncols)}
            dict_list.append(d)
        return dict_list

    def read_file(self):
        '''
            Read selected file to import order and return worksheet object to the caller
        '''
        imp_file = BytesIO(base64.decodestring(self.choose_file))
        workbook = load_workbook(filename=imp_file, read_only=True)
        worksheet = workbook.get_active_sheet()  # workbook.get_sheet_by_name(name = 'Sheet1')
        return worksheet

    def validate_process(self):
        '''
            Validate process by checking all the conditions and return back with sale order object
        '''
        if not self.choose_file:
            raise Warning(('Unable to process..! Please select file to process...'))

        sale_order = self.env['sale.order'].browse(self.env.context.get('active_id'))
        if not sale_order:
            raise Warning(('Unable to process..! You must need to select one sale order at a time!.'))

        if not self.choose_file:
            raise Warning(('Unable to process..! Please select file to process...'))

        return sale_order

    def validate_fields(self, file_fields):
        '''
            This import pattern requires few fields default, so check it first whether it's there or not.
        '''
        require_fields = ['code']
        missing = []
        for field in require_fields:
            if field not in file_fields:
                missing.append(field)

        if len(missing) > 0:
            raise except_orm(('Incorrect format found..!'),
                             ('Please provide all the required fields in file, missing fields => %s.' % (missing)))

        return True

    def fill_dictionary_from_file(self, worksheet, column_header):
        data = []
        columns = worksheet.max_column
        # rows = worksheet.get_highest_row() + 1
        for row_num, row in enumerate(worksheet.iter_rows()):
            row_num += 1
            if not next((r for r in row if r is not openpyxl.cell.read_only.EmptyCell or r.row), None):
                continue
            if row[0] is not openpyxl.cell.read_only.EmptyCell:
                if row[0].value and row[0].row == 1:
                    continue
            test_data = {}
            for col in range(1, columns + 1):
                test_data.update({column_header.get(col): worksheet.cell(row=row_num, column=col).value})
            data.append(test_data)
        return data

    def get_product_data(self, order, product_id, qty):
        res = self.env['sale.order'].browse(self.ids[0])
        res.order_line.product_id_change()

    def default_quantity(self):
        key_id = self.env.ref('import_order_xls.default_qty_confi_parameter').id
        value = self.env['ir.config_parameter'].search([('id', '=', key_id)]).value
        if value:
            if isinstance(value, list):
                return value[0]
            return value
        return 0

    def make_sale_order_line(self):
        order = self.validate_process()[0]
        file_name = self.file_name
        index = file_name.rfind('.')
        flag = 0
        if index == -1:
            flag = 1
        extension = file_name[index + 1:]

        if flag or extension not in ['xlsx', 'xls']:
            raise except_orm(('Incorrect file format found..!'),
                             ('Please provide only .xlsx or .xls file to import order data!!!'))

        product_obj = self.env['product.product']
        line_obj = self.env['sale.order.line']
        column_header = {}
        try:
            if extension == 'xlsx':
                worksheet = self.read_file()[0]
                column_header = self.get_header(worksheet)
                file_header = column_header.values()
            else:
                worksheet = self.read_file_xls()
                worksheet = worksheet.sheet_by_index(0)
                file_header = [worksheet.cell(0, col_index).value.lower() for col_index in range(worksheet.ncols)]
        except Exception as e:
            raise Warning("Something is wrong.\n %s" % (str(e)))

        not_matched = []
        invalid_code = []
        order_data = []
        multi_product_done = []
        quantity = 0.0
        if self.validate_fields(file_header):
            if extension == 'xlsx':
                order_data = self.fill_dictionary_from_file(worksheet, column_header)
            else:
                order_data = self.fill_dictionary_from_xls_file(worksheet, file_header)

            default_quantity = 0
            if 'qty' not in file_header:
                default_quantity = float(self.default_quantity()[0])

            for data in order_data:
                line_data = {}
                l_id = data.get('id', 0)
                if default_quantity:
                    data.update({'qty': default_quantity})
                    quantity = default_quantity
                else:
                    if type(data.get('qty')) in [None, str]:
                        quantity = 0
                    else:
                        if data.get('qty'):
                            quantity = float(data.get('qty', 0.0)) or 0.0

                default_code = data.get('code', '') and str(data.get('code', ''))
                default_code = default_code and default_code.strip()
                discount = data.get('discount')
                price = data.get('price')
                if 'discount' in data and type(discount) in [None, str]:
                    discount = 0.0
                if 'price' in data and type(price) in [None, str]:
                    price = None

                name = data.get('name', '')
                if not default_code and l_id:
                    domain = [('id', '=', int(l_id)), ('order_id', '=', order.id)]
                    l_obj = line_obj.search(domain)
                    if not l_obj:
                        continue
                    l_obj.write({'discount': discount, 'price_unit': price, 'name': name, 'product_uom_qty': quantity})
                    continue

                product_id = product_obj.search([('default_code', '=', default_code)])
                if not product_id:
                    invalid_code.append(default_code)
                    continue

                if product_id:
                    product = product_id and product_id[0] or False
                    line_data = {}
                    line_data.update({'product_id': product.id})
                    line_data.update({'name': product.name})
                    line_data.update({'price_unit': product_id.list_price})
                    line_data.update({'product_uom': product.uom_id.id})
                    line_data.update({'invoice_status': 'upselling'})
                    tax_id = line_data.get('tax_id', False)
                    if tax_id:
                        line_data.update({'tax_id': [(6, 0, tax_id)]})

                    if price is not None:
                        line_data.update({'price_unit': price})
                        line_data.update({'discount': discount or 0})
                    else:
                        price = order.pricelist_id.get_product_price(product, quantity, partner=False,
                                                                     uom_id=product.uom_id.id)
                        price and line_data.update({'price_unit': price})
                    if name:
                        line_data.update({'name': name})

                    if discount:
                        line_data.update({'discount': discount})

                    line_data.update({'product_uom_qty': quantity})

                    if l_id:
                        domain = [('id', '=', int(l_id)), ('order_id', '=', order.id)]
                        l_obj = line_obj.search(domain)
                        if not l_obj:
                            continue

                        if l_obj and l_obj.product_id and l_obj.product_id.id == product.id and l_obj.order_id.id == order.id:
                            l_obj.write(line_data)
                        continue

                    line_ids = line_obj.search([('product_id', '=', product.id), ('order_id', '=', order.id)])
                    if line_ids:
                        for line in line_ids:
                            vals = {}
                            vals.update({
                                'product_id': product.id,
                                'product_name': product.name,
                                'product_uom_id': product.uom_id.id,
                                'description': name,
                                'price': price,
                                'order_id': order.id,
                                'quantity': quantity,
                                'discount': discount,
                                'line_id': line.id
                            })
                            not_matched.append(vals)
                    else:
                        line_data.update({
                            'order_id': order.id,
                        })
                        line_data.update({'qty_delivered': 0.0})
                        line_obj.create(line_data)

            if len(not_matched) > 0 or len(invalid_code) > 0:
                import_order_id = self.env['import.order'].create({'order_id': order.id})
                order_lines = []
                invalid_code_lines = ""
                none_in_file = False
                if len(not_matched) > 0:
                    for vals in not_matched:
                        vals.update({'import_order_id': import_order_id.id})
                        import_line_id = self.env['import.order.line'].create(vals)
                        order_lines.append(import_line_id.id)

                if len(invalid_code) > 0:
                    if 'None' in invalid_code:
                        invalid_code = filter(lambda x: x != 'None', invalid_code)
                        none_in_file = True
                    invalid_code_lines = ', '.join(map(str, invalid_code))
                    import_order_id.write({'invalid_code_ids': invalid_code_lines})
                ctx = self.env.context.copy()
                ctx.update({'import_order_id': import_order_id.id, 'item_ids': order_lines, 'order_id': order.id,
                            'invalid_code_ids': invalid_code_lines, 'none_in_file': none_in_file})
                return import_order_id.with_context(ctx).wizard_view()
        order.write({})
        return True


    def export_sale_order_line(self):
        line_obj = self.env['sale.order.line']
        line_ids = line_obj.search([('order_id', 'in', self.env.context.get('active_ids'))])
        filename = self.get_file_name()

        wb = Workbook()
        worksheet = wb.create_sheet(index=0)

        worksheet.cell(coordinate='A1').value = 'ID'
        worksheet.cell(coordinate='B1').value = 'Code'
        worksheet.cell(coordinate='C1').value = 'Name'
        worksheet.cell(coordinate='D1').value = 'Qty'
        worksheet.cell(coordinate='E1').value = 'Price'
        worksheet.cell(coordinate='F1').value = 'Discount'
        row = 2

        for line in line_ids:
            worksheet.cell(coordinate='A%d' % (row)).value = line.id
            worksheet.cell(coordinate='B%d' % (row)).value = line.product_id.default_code
            worksheet.cell(coordinate='C%d' % (row)).value = line.name
            worksheet.cell(coordinate='D%d' % (row)).value = line.product_uom_qty
            worksheet.cell(coordinate='E%d' % (row)).value = line.price_unit
            worksheet.cell(coordinate='F%d' % (row)).value = line.discount
            row = row + 1

        wb.save(filename)

        order_name = line_ids and line_ids[0].order_id.name or ''
        file_read = open(filename, 'rb')
        file_read.seek(0)
        stock_file = base64.encodestring(file_read.read())
        file_read.close()
        self.write({'datas': stock_file})
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?model=process.order.import&field=datas&id=%s&filename=sale_order_line_%s.xls' % (
            self.id, order_name),
            'target': 'new',
        }
