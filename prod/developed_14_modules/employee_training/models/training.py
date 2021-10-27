# -*- coding: utf-8 -*-
from odoo import models,fields,api, _
from odoo.exceptions import Warning

from datetime import datetime
from dateutil.relativedelta import relativedelta

class TrainingSession(models.Model):
    _name = 'training.session'
    
    name = fields.Char("Name")
    training_content = fields.Html("Training content")
    start_date = fields.Datetime("Start Date")
    employee_id = fields.Many2one("hr.employee","Trainer’s name")
    trainee_ids = fields.One2many("hr.employee.trainee",'session_id',string='Trainees')
    package_id = fields.Many2one("training.package",string='Training Package')
    training_template_ids = fields.Many2many("training.template",'training_training_template_rel','training_id','template_id',"Templates")
    state = fields.Selection([('NEW','NEW'), ('IN PROGRESS','IN PROGRESS'),('SIGNATURE REQUIRED', 'SIGNATURE REQUIRED'),('SIGNED','SIGNED'),('DONE','DONE'),('Cancelled','Cancelled')],string="Status",default="NEW")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    #all_employee_signed = fields.Boolean("Signed All Employee ?", compute="_compute_signed_all_employee")
    training_ids = fields.One2many("training.training",'session_id','Trainings')
    count_training = fields.Integer("Count Training",compute="_compute_training_count")
    trainer_signature = fields.Binary("Trainer Signature")
    
    def _compute_training_count(self):
        for session in self:
            session.count_training = len(session.training_ids)
    
#     @api.multi
    def action_open_session_training(self):
        self.ensure_one()
        action = self.env.ref('employee_training.action_training_training')
        result = action.read()[0]
        ctx = self._context.copy()
        ctx.update({'default_session_id':self.id})
        result['context'] = ctx
        training_ids = self.mapped('training_ids')
        result['domain'] = [('id', 'in', training_ids.ids)]
        return result
    
    @api.onchange('package_id')
    def onchange_package_id(self):
        if self.package_id:
            self.training_template_ids = self.training_template_ids + self.package_id.training_template_ids
    
    @api.model
    def create(self, vals):
        if vals.get('training_template_ids',[]):
            training_template_ids = vals.get('training_template_ids',[])
            training_template_ids_new = []
            for template in training_template_ids:
                if template[0]==6 and template[1]==False:
                    training_template_ids_new = [template]
                    break
                elif template[0]==1 and template[1]:
                    training_template_ids_new.append((4, template[1]))
            #training_template_ids = [(4, template[1]) for template in training_template_ids if template[1]] 
            vals['training_template_ids'] = training_template_ids_new
        res  = super(TrainingSession, self).create(vals)
        return res
    
#     @api.multi
    def write(self, vals):
        if vals.get('training_template_ids',[]):
            training_template_ids = vals.get('training_template_ids',[])
            training_template_ids_new = []
            for template in training_template_ids:
                if template[0]==6 and template[1]==False:
                    training_template_ids_new = [template]
                    break
                elif template[0]==1 and template[1]:
                    training_template_ids_new.append((4, template[1]))
            #training_template_ids = [(4, template[1]) for template in training_template_ids if template[1]] 
            vals['training_template_ids'] = training_template_ids_new
        res  = super(TrainingSession, self).write(vals)
        return res
    

#     @api.multi
    def action_start_training(self):
        if not self.start_date:
            raise Warning("Please set start Date")
        if not self.training_template_ids:
            raise Warning("Please set atleast one Training Template in Trainings tab.")
        if not self.trainee_ids:
            raise Warning("Please set atleast one Trainee.")
        training_obj = self.env['training.training']
        for employee in self.trainee_ids:
            for template in self.training_template_ids:
                vals = {'name':self.name +' : '+template.name, 'training_content':template.training_content, 'start_date':self.start_date,'employee_id':employee.employee_id.id,'company_id':self.company_id.id,
                        'trainer_id':self.employee_id.id, 'template_id':template.id, 'employee_signature':employee.signature, 'session_id' : self.id, 'signed_employee': employee.signed, 
                        }
                training_obj.create(vals)
                
        self.write({'state':'IN PROGRESS'})
        self.training_ids.write({'state':'IN PROGRESS'})
        return True
    
#     @api.multi
    def action_request_signatures(self):
        email_template = self.env.ref("employee_training.email_template_training_employee_signature_request",False)
        if email_template:
            for training in self.training_ids:
                email_template.send_mail(training.id, force_send=True)
        self.write({'state':'SIGNATURE REQUIRED'})
        self.training_ids.write({'state':'SIGNATURE REQUIRED'})
        return True
    
#     @api.multi
    def action_email_trainees(self):
        #ctx = self._context.copy()
        template = self.env.ref('employee_training.email_template_training_trainer',False)
        if not template:
            raise Warning("Default email template deleted by User. Please try to upgrade module employee_training to get back it.")
#         ctx.update({
#             'default_model': 'training.training',
#             'default_use_template': bool(template.id),
#             'default_template_id': template.id,
#             'default_composition_mode': 'comment',
#             'default_email_from' : self.company_id.email
#         })
        for training in self.training_ids:
            template.send_mail(training.id, force_send=True)
#             ctx.update({'default_res_id': training.id})
#             training.with_context(ctx).message_post_with_template(template.id)
        self.write({'state':'DONE'})    
        self.training_ids.filtered(lambda x:x.signed_employee and x.state!='Cancelled').write({'state':'DONE'})
        return True
    
#     @api.multi
    def action_cancel_session(self):
        self.write({'state':'Cancelled'})
        self.training_ids.write({'state':'Cancelled'})
        
#     @api.multi
    def action_do_trainer_signature(self):
        form = self.env.ref("employee_training.view_employee_signature_wizard_form",False)
        ctx = self._context.copy()
        ctx.update({'record_id':self.id,'record_model':self._name,'record_field':'trainer_signature'}) #, 'default_signature':self.trainer_signature
        #res = self.env['employee.signature.wizard'].with_context(ctx).create({})
        return {
                'name': _('Draw Signature'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'employee.signature.wizard',
                'view_id': form.id,
                #'res_id':res.id,
                'type': 'ir.actions.act_window',
                'context': ctx,
                'target': 'new'
            }
        
class HrEmployeeTrainee(models.Model):
    _name = 'hr.employee.trainee'
    
    session_id = fields.Many2one("training.session",'Training Session')
    employee_id = fields.Many2one("hr.employee","Employee")
    signature = fields.Binary("Signature")
    signed = fields.Boolean("Signed ?")
    
#     @api.multi
    def action_do_signature(self):
        form = self.env.ref("employee_training.view_employee_signature_wizard_form",False)
        ctx = self._context.copy()
        ctx.update({'record_id':self.id,'record_model':self._name,'record_field':'signature', 'default_signature':self.signature})
        return {
                'name': _('Draw Signature'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'employee.signature.wizard',
                'view_id': form.id,
                'type': 'ir.actions.act_window',
                'context': ctx,
                'target': 'new'
            }
        
    
class TrainingTraining(models.Model):
    _name = 'training.training'
    _inherit = ['mail.thread', 'mail.activity.mixin'] #portal.mixin
    
    name = fields.Char("Name")
    training_content = fields.Html("Training content")
    start_date = fields.Datetime("Start Date")
    employee_id = fields.Many2one("hr.employee","Employee")
    trainer_id = fields.Many2one("hr.employee","Trainer’s name")
    template_id = fields.Many2one("training.template",'Training Template')
    trainer_signature = fields.Binary("Traine's Signature")
    employee_signature = fields.Binary("Employee Signature")
    session_id = fields.Many2one("training.session","Training Session")
    signed_trainer = fields.Boolean("Signed by Trainer ?")
    signed_employee = fields.Boolean("Signed by Employee ?")
    training_date_deadline = fields.Datetime("Deadline Date",store=True,compute="_compute_training_deadline_date")
    
    #trainee_ids = fields.One2many("hr.employee.trainee",'training_id',string='Trainees')
    #package_id = fields.Many2one("training.package",string='Training Package')
    #training_template_ids = fields.Many2many("training.template",'training_training_template_rel','training_id','template_id',"Templates")
    state = fields.Selection([('NEW','NEW'), ('IN PROGRESS','IN PROGRESS'),('SIGNATURE REQUIRED', 'SIGNATURE REQUIRED'),('SIGNED','SIGNED'),('DONE','DONE'),('Cancelled','Cancelled')],string="Status") #,related="session_id.state", store=True
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id)
    
#     @api.multi
    @api.depends('template_id.deadline_days','start_date')
    def _compute_training_deadline_date(self):
        for training in self:
            if training.start_date and training.template_id.deadline_days:
                #training.training_date_deadline = (datetime.strptime(training.start_date,'%Y-%m-%d %H:%M:%S') + relativedelta(days=training.template_id.deadline_days)).strftime("%Y-%m-%d %H:%M:%S") 
                training.training_date_deadline = (training.start_date + relativedelta(days=training.template_id.deadline_days)).strftime("%Y-%m-%d %H:%M:%S")
#     @api.multi
    def action_do_employee_signature(self):
        form = self.env.ref("employee_training.view_employee_signature_wizard_form",False)
        ctx = self._context.copy()
        ctx.update({'record_id':self.id,'record_model':self._name,'record_field':'employee_signature'}) #, 'default_signature':self.employee_signature
        return {
                'name': _('Draw Signature'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'employee.signature.wizard',
                'view_id': form.id,
                'type': 'ir.actions.act_window',
                'context': ctx,
                'target': 'new'
            }
#     @api.onchange('package_id')
#     def onchange_package_id(self):
#         if self.package_id:
#             self.training_template_ids = self.training_template_ids + self.package_id.training_template_ids
#     @api.model
#     def create(self, vals):
#         if vals.get('training_template_ids',[]):
#             training_template_ids = vals.get('training_template_ids',[])
#             training_template_ids_new = []
#             for template in training_template_ids:
#                 if template[0]==6 and template[1]==False:
#                     training_template_ids_new = [template]
#                     break
#                 elif template[0]==1 and template[1]:
#                     training_template_ids_new.append((4, template[1]))
#             #training_template_ids = [(4, template[1]) for template in training_template_ids if template[1]] 
#             vals['training_template_ids'] = training_template_ids_new
#         res  = super(TrainingTraining, self).create(vals)
#         return res

#     @api.multi
    def action_open_wiki_page(self):
        if not self.template_id or not self.template_id.iframe_url:
            raise Warning("No Wiki Page is set in training template.")
        
        form = self.env.ref("employee_training.view_wiki_web_page_wizard_form",False)
        ctx = self._context.copy()
        ctx.update({'default_iframe_url':self.template_id.iframe_url})
        return {
                'name': _('Wiki/Web Page'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wiki.web.page.wizard',
                'view_id': form.id,
                'type': 'ir.actions.act_window',
                'context': ctx,
                'target': 'new'
            }
    
    @api.model
    def training_datedeadline_reminder(self):
        utc_time = datetime.utcnow()
        date_tomorrow = (utc_time + relativedelta(days=1)).strftime("%Y-%m-%d")
        self._cr.execute("select id from training_training where not signed_employee and state in ('IN PROGRESS','SIGNATURE REQUIRED') and training_date_deadline::date='%s'"%(date_tomorrow))
        res = self._cr.fetchall()
        if res:
            training_ids = [t[0] for t in res]
            email_template = self.env.ref("employee_training.email_template_training_employee_signature_request",False)
            if email_template:
                for training_id in training_ids:
                    email_template.send_mail(training_id, force_send=True)
        utc_now_datetime = utc_time.strftime('%Y-%m-%d %H:%M:%S')
        self._cr.execute("select id from training_training where not signed_employee and state in ('IN PROGRESS','SIGNATURE REQUIRED') and training_date_deadline <='%s'"%(utc_now_datetime))
        res = self._cr.fetchall()             
        if res:
            training_ids = [t[0] for t in res]
            self.browse(training_ids).write({'state':'Cancelled'})
        return True
    
