from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request


class Hospital(http.Controller):

    @http.route(['/hospital/doctor', '/hospital/doctor/<model("hospital.patient"):id>'], auth='public', website=True)
    def hospital_doctors(self, id=None, **kwargs):
        # return "Hello Word"
        one = False
        if id:
            patients = id
            # patients = request.env['hospital.patient'].sudo().browse(id)
            one = True
        else:
            patients = request.env['hospital.patient'].sudo().search([])
        context = {
            'one': one,
            'patients': patients,
        }
        print(context)
        return request.render('hospital.web_patients_page', context)

    @http.route('/hospital/form', auth='public', website=True)
    def patient_webform(self, **kwrags):
        doctors = request.env['hospital.doctor'].sudo().search([])
        print(doctors)
        return request.render('hospital.web_patient_form', {'doctor_rec': doctors, })

    @http.route('/hospital/create-patient', auth='public', website=True)
    def create_patient(self, **kwargs):
        print(kwargs, request, sep='\n')
        request.env['hospital.patient'].create(kwargs)
        return request.redirect('/hospital/doctor')
        # return request.render('hospital.web_patient_form', {})

    @http.route('/get_patients', auth='public', type='json', methods=['GET'], website=True)
    def get_patients(self):
        patient_rec = request.env['hospital.patient'].sudo().search([]).read(['id', 'name_seq', 'patient_name'])
        # return request.redirect('/hospital/doctor')
        return {
            'status': 200,
            'message': 'success',
            'response': patient_rec,
        }


class Digitalconfirmation(WebsiteSale):

    @http.route('/shop', type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        print("Here")
        print(request.env.uid, request.env.user)
        res = super().shop(page=0, category=None, search='', ppg=False, **post)
        return res

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        print("Here in def address....")
        if request.httprequest.method == 'GET':
            res = super(Digitalconfirmation, self).address(**kw)
            data = res.qcontext
            country = request.env['res.country'].browse(156)
            state = request.env['res.country.state'].browse(508)
            data.update({'country': country})
            data.update({'country_states': country.state_ids})
            data['checkout'].update({'state_id': state})
            return res
