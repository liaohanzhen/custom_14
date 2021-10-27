from odoo import models, fields
from odoo.exceptions import Warning
import requests
import base64

request_header = {
                "Accept-Language":"en-US,en;q=0.8",
                "User-Agent":"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36",
                "Connection":"keep-alive",
                }

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    product_buscar = fields.Char('Product a buscar')
    syscom_categories_ids = fields.Many2many('syscom.category')
    syscom_brand_ids = fields.Many2many('syscom.brand')
    syscom_model = fields.Char('Modelo')
    
    def get_syscom_product_info(self):
        if not  self.product_buscar:
            raise  Warning('Please enter value in Product a buscar field.')
        if not self.syscom_categories_ids:
            raise Warning('Please Select Syscom Category.')
        if not self.syscom_brand_ids:
            raise Warning('Please Select Syscom Brand.')
        
        sys_cats = self.syscom_categories_ids
        newCatList = [str(i.syscom_id) for i in sys_cats]
        newCatList = ','.join(newCatList)
        
        sys_brand = self.syscom_brand_ids
        newBrandList = [str(i.syscom_id) for i in sys_brand]
        newBrandList = ','.join(newBrandList)
        
        get_product_info = {"categoria":newCatList,"marca":newBrandList,"busqueda":self.product_buscar}
        company = self.company_id or self.env.user.company_id
        access_token = company.get_syscom_token()
        
        header_Brand = {'Authorization': 'Bearer %s'%(access_token)} 
        product_url = 'https://developers.syscom.mx/api/v1/productos'
        response_final = requests.request("GET", product_url, headers=header_Brand, params=get_product_info)
        
        get_result_final = response_final.json()
        products = get_result_final.get('productos')
        if products:
            modelo = self.syscom_model
            map_product = list(filter(lambda p: p.get('modelo')==modelo,products))
            if map_product:
                map_product = map_product[0]
                categ_id = self.get_create_syscom_category(map_product.get('categorias'))
                
                vals = {'name' : map_product.get('titulo'), 
                        'default_code' : map_product.get('modelo', ''), 
                        #'clave_producto' : map_product.get('sat_key'),
                        'standard_price' : map_product.get('precios',{}).get('precio_lista'),
                        }
                
                img_content = self.get_image_from_url(map_product.get('img_portada'))
                if img_content:
                    vals.update({'image_1920' : img_content})
                if categ_id:
                    vals.update({'categ_id' : categ_id})
                    
                self.write(vals)
            else:
                raise Warning('Product not found')
        
        return True
    
    def get_image_from_url(self, image_url):
        content = base64.b64encode(requests.get(image_url,headers=request_header).content)
        content = content.decode()
        return content
    
    def get_create_syscom_category(self,categories):
        categories = sorted(categories,key= lambda x: x.get('nivel'))
        categ_obj = self.env['product.category']
        parent_categ_id = False
        odoo_categ_id = None 
        for category in categories:
            categ_id = eval(category.get('id'))
            categ_exist = categ_obj.search([('syscom_categ_id','=',categ_id),('parent_id','=',parent_categ_id)],limit=1)
            if not categ_exist:
                categ_exist = categ_obj.create({'syscom_categ_id' : categ_id, 'name' : category.get('nombre'), 'parent_id' : parent_categ_id})
            parent_categ_id =  categ_exist.id   
            odoo_categ_id = categ_exist.id
        return odoo_categ_id
    
        
    