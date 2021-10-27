from odoo import models, fields
import requests
from datetime import timedelta

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    client_id = fields.Char('Client ID')
    client_secret = fields.Char('Client Secret')
    syscom_token = fields.Char('Syscom Token')
    syscom_token_expires_in = fields.Datetime('Syscom Token Expire Time')
     
    def get_syscom_token(self):
        dt_now = fields.Datetime.now()
        if not self.syscom_token_expires_in or not self.syscom_token or self.syscom_token_expires_in < dt_now:
            url = 'https://developers.syscom.mx/oauth/token'
            header = {'Content-Type': 'application/x-www-form-urlencoded'}
            client_id = self.client_id
            secret_id = self.client_secret
            data = {'client_id': client_id, 'client_secret': secret_id, 'grant_type':'client_credentials'}
            response = requests.request("POST", url, headers=header, data=data)
            result = response.json()
            access_token = result.get('access_token')
            ttl = result.get('expires_in')
            self.write({'syscom_token' : access_token,'syscom_token_expires_in': dt_now + timedelta(seconds=ttl)}) 
            return access_token
        else:
            return self.syscom_token
        
    
    def syscom_category(self):
        access_token = self.get_syscom_token()
        header_cat = {'Authorization': 'Bearer %s'%(access_token)}
        category_url = 'https://developers.syscom.mx/api/v1/categorias'
        
        response_categories = requests.request("GET", category_url, headers=header_cat)
        get_result_cat = response_categories.json()
        
        cat_obj = self.env['syscom.category']
        for brand in get_result_cat:
            cat_exist = cat_obj.search([('syscom_id','=',brand.get('id'))])
            if cat_exist:
                continue
            cat_obj.create({'syscom_id' :brand.get('id'), 'name' : brand.get('nombre'), 'syscom_level': brand.get('nivel')}) 
        
        return True
        
    def syscom_brand(self):
        access_token = self.get_syscom_token()
        header_Brand = {'Authorization': 'Bearer %s'%(access_token)}
        
        brand_url = 'https://developers.syscom.mx/api/v1/marcas'
        response_brand = requests.request("GET", brand_url, headers=header_Brand)
        
        get_result_brand = response_brand.json()
        
        brand_obj = self.env['syscom.brand']
        for brand in get_result_brand:
            syscom_id = brand.get('id')
            if brand_obj.search([('syscom_id','=',syscom_id)]):
                continue
            brand_obj.create({'syscom_id' :syscom_id, 'name' : brand.get('nombre')}) 
        
        return True
    