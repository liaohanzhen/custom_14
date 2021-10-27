# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date #, datetime
#from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
    
class DecisionMaker(models.Model):
    _name = 'opportunity.decision.maker'
    
#     @api.multi
    def _compute_score(self):
        for maker in self:
            if maker.last_time_met:
                last_time_met = maker.last_time_met.date() #datetime.strptime(maker.last_time_met, DEFAULT_SERVER_DATE_FORMAT).date()
                diff = date.today() - last_time_met
                days = diff.days
                if days > (365/2):
                    maker.score='0%'
                elif days > (365/4):
                    maker.score='50%'
                else:
                    maker.score='100%'
            else:
                maker.score='0%'
                    
    role = fields.Selection([('Project manager','Project manager'),('Project engineer','Project engineer'),('Purchasing manager','Purchasing manager'),('Board member','Board member')],"Role")
    name = fields.Many2one("res.users",string="Name")
    last_time_met = fields.Date("Last time met")
    score = fields.Char("Score",compute="_compute_score")
    comments = fields.Text("Comments")
    opportunity_id = fields.Many2one("crm.lead","Opportunity")
    
class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    pipeline_category=fields.Selection([('base_case','Base Case'),('best_case ','Best Case'),('funnel ','Funnel')],"Pipeline Category")
    top5_opportunity=fields.Selection([('yes','Yes'),('no','No')],"Top 5 Opportunity")
    sales_region = fields.Selection([('Australia','Australia'),('Oceania','Oceania'), ('Asia', 'Asia'), ('India','India'), ('LATAM','LATAM'),('North America','North America'),('Africa','Africa'),('Europe','Europe'),('USA','USA')],
                                    string='Sales Region')
    contact_id = fields.Many2one('res.partner', string='Contact')
    x_dropbox_link = fields.Char("Sales folder")
    x_pricing_tool = fields.Char("Pricing tool")
    
    @api.model
    def default_get(self,fields_list):
        result = super(CrmLead, self).default_get(fields_list)
        result['decision_maker_ids'] = [(0, 0, {'role':'Project manager'}), (0, 0, {'role':'Project engineer'}), (0, 0, {'role':'Purchasing manager'}), (0, 0, {'role' :'Board member'})]
        
        return result
    
    @api.model
    def get_js_data_for_total_count(self):
        leads = self.search([])
        return {'total_planned_revenue': sum(leads.mapped('expected_revenue')), 'total_project_power': sum(leads.mapped('project_power')), 'total_leads': len(leads)}
    
#     @api.multi
    @api.depends('question_1_ans')
    def _compute_question_1_score(self):
        for lead in self:
            if lead.question_1_ans=='No':
                lead.question_1_score='25%' 
            else:
                lead.question_1_score='0%'
    
#     @api.multi
    @api.depends('question_2_ans')
    def _compute_question_2_score(self):
        for lead in self:
            if lead.question_2_ans=='Yes':
                lead.question_2_score='25%' 
            else:
                lead.question_2_score='0%'
#     @api.multi
    @api.depends('question_3_ans')
    def _compute_question_3_score(self):
        for lead in self:
            if lead.question_3_ans=='Yes':
                lead.question_3_score='25%' 
            else:
                lead.question_3_score='0%'
                
#     @api.multi
    @api.depends('question_4_ans')
    def _compute_question_4_score(self):
        for lead in self:
            if lead.question_4_ans=='Yes':
                lead.question_4_score='25%' 
            else:
                lead.question_4_score='0%'
                
#     @api.multi
    @api.depends('maverick_ecosystem_supply', 'freight', 'engineering_services', 'deployment_services', 'operation_and_maintenance_ser', 'project_power')
    def _compute_total_price_full_scope(self):
        for lead in self:
            lead.total_price_full_scope = lead.maverick_ecosystem_supply + lead.freight + lead.engineering_services + lead.deployment_services + lead.operation_and_maintenance_ser 
            if lead.project_power:
                lead.total_price_full_scope_per = "%.4f"%(lead.total_price_full_scope/lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)
            else:
                lead.total_price_full_scope_per = "%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)
            
        
#     @api.multi
    @api.depends('total_price_full_scope', 'margin_percent','project_power')
    def _compute_total_margin_full_scope(self):
        for lead in self:
            lead.total_margin_full_scope = lead.total_price_full_scope * lead.margin_percent/100.0
            if lead.project_power:
                lead.total_margin_full_scope_per = "%.4f"%(lead.total_margin_full_scope/lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)
            else:
                lead.total_margin_full_scope_per = "%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)
        
    
#     @api.multi
    @api.depends('mav_supply','module_supply', 'inverter_supply', 'wingman_supply', 'dc_equipment_supply', 'ac_equipment_supply', 'monitoring_solution','project_power')
    def _compute_maverick_ecosystem_supply(self):
        for lead in self:
            lead.maverick_ecosystem_supply= lead.mav_supply + lead.module_supply + lead.inverter_supply + lead.wingman_supply + lead.dc_equipment_supply + lead.ac_equipment_supply + lead.monitoring_solution
            if lead.project_power:
                lead.maverick_ecosystem_supply_per = "%.4f"%(lead.maverick_ecosystem_supply/lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)
            else:
                lead.maverick_ecosystem_supply_per="%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)
        
    
#     @api.multi
    @api.depends('module_power','no_of_units_mod', 'project_power_calc', 'project_power_manual')
    def _compute_project_power(self):
        for lead in self:
            if lead.project_power_calc=='Manual':
                lead.project_power = lead.project_power_manual
            else:
                lead.project_power = lead.module_power * lead.no_of_units_mod
    
#     @api.multi
    @api.depends('mav_supply','project_power')
    def _compute_mav_supply_per(self):
        for lead in self:
            if lead.mav_supply and lead.project_power:
                lead.mav_supply_per = "%.4f"%(lead.mav_supply /lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)
            else:
                lead.mav_supply_per="%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)
#     @api.multi
    @api.depends('module_supply','project_power')
    def _compute_module_supply_per(self):
        for lead in self:
            if lead.module_supply and lead.project_power:
                lead.module_supply_per = "%.4f"%(lead.module_supply /lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)
            else:
                lead.module_supply_per="%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)
                
    
#     @api.multi
    @api.depends('inverter_supply','project_power')
    def _compute_inverter_supply_per(self):
        for lead in self:
            if lead.inverter_supply and lead.project_power:
                lead.inverter_supply_per = "%.4f"%(lead.inverter_supply /lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)
            else:
                lead.inverter_supply_per="%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)
    
#     @api.multi
    @api.depends('wingman_supply','project_power')
    def _compute_wingman_supply_per(self):
        for lead in self:
            if lead.wingman_supply and lead.project_power:
                lead.wingman_supply_per = "%.4f"%(lead.wingman_supply /lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)
            else:
                lead.wingman_supply_per = "%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)
#     @api.multi
    @api.depends('dc_equipment_supply','project_power')
    def _compute_dc_equipment_supply_per(self):
        for lead in self:
            if lead.dc_equipment_supply and lead.project_power:
                lead.dc_equipment_supply_per = "%.4f"%(lead.dc_equipment_supply /lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)
            else:
                lead.dc_equipment_supply_per="%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)         
    
#     @api.multi
    @api.depends('ac_equipment_supply','project_power')
    def _compute_ac_equipment_supply_per(self):
        for lead in self:
            if lead.ac_equipment_supply and lead.project_power:
                lead.ac_equipment_supply_per = "%.4f"%(lead.ac_equipment_supply /lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)
            else:
                lead.ac_equipment_supply_per="%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)
#     @api.multi
    @api.depends('ac_equipment_supply','project_power')
    def _compute_monitoring_solution_per(self):
        for lead in self:
            if lead.monitoring_solution and lead.project_power:
                lead.monitoring_solution_per = "%.4f"%(lead.monitoring_solution /lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)
            else:
                lead.monitoring_solution_per="%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)
#     @api.multi
    @api.depends('freight','project_power')
    def _compute_freight_percent(self):
        for lead in self:
            if lead.freight and lead.project_power:
                lead.freight_per = "%.4f"%(lead.freight /lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)
            else:
                lead.freight_per="%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)
    
#     @api.multi
    @api.depends('indicative_project_layout','yield_report', 'site_survey_with_drone', 'detailed_project_layout', 'technical_doc_package', 'specific_eng_study','project_power')
    def _compute_engineering_services(self):
        for lead in self:
            lead.engineering_services = lead.indicative_project_layout + lead.yield_report + lead.site_survey_with_drone + lead.detailed_project_layout + lead.technical_doc_package + lead.specific_eng_study
            if lead.project_power:
                lead.engineering_services_per = "%.4f"%(lead.engineering_services / lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)   
            else:
                lead.engineering_services_per = "%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)
    
#     @api.multi
    @api.depends('indicative_project_layout','project_power')
    def _compute_indicative_project_layout_per(self):
        for lead in self:
            if lead.indicative_project_layout and lead.project_power:
                lead.indicative_project_layout_per = "%.4f"%(lead.indicative_project_layout /lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)
            else:
                lead.indicative_project_layout_per="%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)
    
#     @api.multi
    @api.depends('yield_report','project_power')
    def _compute_yield_report_per(self):
        for lead in self:
            if lead.yield_report and lead.project_power:
                lead.yield_report_per = "%.4f"%(lead.yield_report /lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)
            else:
                lead.yield_report_per= "%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)
#     @api.multi
    @api.depends('site_survey_with_drone','project_power')
    def _compute_site_survey_with_drone_per(self):
        for lead in self:
            if lead.site_survey_with_drone and lead.project_power:
                lead.site_survey_with_drone_per = "%.4f"%(lead.site_survey_with_drone /lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)
            else:
                lead.site_survey_with_drone_per="%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)
#     @api.multi
    @api.depends('detailed_project_layout','project_power')
    def _compute_detailed_project_layout_per(self):
        for lead in self:
            if lead.detailed_project_layout and lead.project_power:
                lead.detailed_project_layout_per = "%.4f"%(lead.detailed_project_layout /lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)
            else:
                lead.detailed_project_layout_per="%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)
    
#     @api.multi
    @api.depends('technical_doc_package','project_power')
    def _compute_technical_doc_package_per(self):
        for lead in self:
            if lead.technical_doc_package and lead.project_power:
                lead.technical_doc_package_per = "%.4f"%(lead.technical_doc_package /lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)
            else:
                lead.technical_doc_package_per="%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)
    
#     @api.multi
    @api.depends('specific_eng_study','project_power')
    def _compute_specific_eng_study_per(self):
        for lead in self:
            if lead.specific_eng_study and lead.project_power:
                lead.specific_eng_study_per = "%.4f"%(lead.specific_eng_study /lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)
            else:
                lead.specific_eng_study_per="%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)
    
#     @api.multi
    @api.depends('mav_deployment','mav_deployment_support', 'dc_electrical_work', 'ac_electrical_work', 'construction_misc','project_power')
    def _compute_deployment_services(self):
        for lead in self:
            lead.deployment_services = lead.mav_deployment + lead.mav_deployment_support + lead.dc_electrical_work + lead.ac_electrical_work + lead.construction_misc
            if lead.project_power:
                lead.deployment_services_per = "%.4f"%(lead.deployment_services / lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)   
            else:
                lead.deployment_services_per = "%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)
    
#     @api.multi
    @api.depends('mav_deployment','project_power')
    def _compute_mav_deployment_per(self):
        for lead in self:
            if lead.mav_deployment and lead.project_power:
                lead.mav_deployment_per = "%.4f"%(lead.mav_deployment /lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)
            else:
                lead.mav_deployment_per="%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)
    
#     @api.multi
    @api.depends('mav_deployment_support','project_power')
    def _compute_mav_deployment_support_per(self):
        for lead in self:
            if lead.mav_deployment_support and lead.project_power:
                lead.mav_deployment_support_per = "%.4f"%(lead.mav_deployment_support /lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)
            else:
                lead.mav_deployment_support_per="%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)
    
#     @api.multi
    @api.depends('dc_electrical_work','project_power')
    def _compute_dc_electrical_work_per(self):
        for lead in self:
            if lead.dc_electrical_work and lead.project_power:
                lead.dc_electrical_work_per = "%.4f"%(lead.dc_electrical_work /lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)
            else:
                lead.dc_electrical_work_per="%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)
    
#     @api.multi
    @api.depends('ac_electrical_work','project_power')
    def _compute_ac_electrical_work_per(self):
        for lead in self:
            if lead.ac_electrical_work and lead.project_power:
                lead.ac_electrical_work_per = "%.4f"%(lead.ac_electrical_work /lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)
            else:
                lead.ac_electrical_work_per="%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)
    
#     @api.multi
    @api.depends('construction_misc','project_power')
    def _compute_construction_misc_per(self):
        for lead in self:
            if lead.construction_misc and lead.project_power:
                lead.construction_misc_per = "%.4f"%(lead.construction_misc /lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)
            else:
                lead.construction_misc_per = "%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)
#     @api.multi
    @api.depends('monitoring_and_reporting','preventive_maintenance', 'corrective_maintenance','project_power')
    def _compute_maintenance_and_deployment_service(self):
        for lead in self:
            lead.operation_and_maintenance_ser = lead.monitoring_and_reporting + lead.preventive_maintenance + lead.corrective_maintenance
            if lead.project_power:
                lead.operation_and_maintenance_ser_per = "%.4f"%(lead.operation_and_maintenance_ser / lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)   
            else:
                lead.operation_and_maintenance_ser_per = "%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)
    
#     @api.multi
    @api.depends('monitoring_and_reporting','project_power')
    def _compute_monitoring_and_reporting_per(self):
        for lead in self:
            if lead.monitoring_and_reporting and lead.project_power:
                lead.monitoring_and_reporting_per = "%.4f"%(lead.monitoring_and_reporting /lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)
            else:
                lead.monitoring_and_reporting_per = "%.4f"%(0)
#     @api.multi
    @api.depends('preventive_maintenance','project_power')
    def _compute_preventive_maintenance_per(self):
        for lead in self:
            if lead.preventive_maintenance and lead.project_power:
                lead.preventive_maintenance_per = "%.4f"%(lead.preventive_maintenance /lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)
            else:
                lead.preventive_maintenance_per = "%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)
    
#     @api.multi
    @api.depends('corrective_maintenance','project_power')
    def _compute_corrective_maintenance_per(self):
        for lead in self:
            if lead.corrective_maintenance and lead.project_power:
                lead.corrective_maintenance_per = "%.4f"%(lead.corrective_maintenance /lead.project_power)+' %s/Wp'%(lead.company_currency.symbol)
            else:
                lead.corrective_maintenance_per = "%.4f"%(0)+' %s/Wp'%(lead.company_currency.symbol)
    
    
    project_code = fields.Char("Code",copy=False, readonly=True, index=True, default=lambda self: '/')
    sop = fields.Boolean("S&OP ?")
    end_user_id = fields.Many2one("res.partner",'End-user')
    
    project_power_calc = fields.Selection([('Automatic','Automatic'), ('Manual','Manual')], default='Automatic', string='Project Power Calculation')
    project_power = fields.Float("Project Power", compute="_compute_project_power",store=True)
    project_power_manual = fields.Float("Project Power Manual Value")
    
    project_location = fields.Char("Project Location")
    incoterms_id = fields.Many2one("account.incoterms","Incoterms")
    application_type = fields.Selection([('On-grid-Behing the meter','On-grid - Behing the meter'),
                                         ('On-grid - Export','On-grid - Export'),
                                         ('Off-grid - Private','Off-grid - Private'),
                                         ('Off-grid - Utility','Off-grid - Utility')], string="Applcation Type")
    likely_to_be_redeployed = fields.Selection([('Yes','Yes'),('No','No')], string="Likely to be redeployed?")
    project_eng_id = fields.Many2one("res.users","Project Engineer")
    deployment_manager_id = fields.Many2one("res.users","Deployment Manager")
    #Customer = Customer
    #Sales Manager = Salesperson 
    #Project Rating = Priority
    #5B entity = Company
    
    #TECHNICAL SPECS
    #MAV solar array
    product_categ_id_mav = fields.Many2one("product.category","Product Category", help="List from category All / Saleable / MAV Solar array")
    product_id_mav = fields.Many2one("product.product",'Product reference')
    no_of_units_mav = fields.Float("Number of units")
    
    
    #Inverters
    product_id_inv = fields.Many2one("product.product",'Product reference', help="List from category All / Saleable / Inverters")
    inverter_power = fields.Float("Inverter power")
    no_of_units_inv = fields.Float("Number of units")
    
    #Modules
    product_id_mod = fields.Many2one("product.product",'Product reference', help="List from category All / Saleable / Modules")
    module_power = fields.Float("Module power")
    no_of_units_mod = fields.Float("Number of units")
    
    #Wingman
    product_id_wingman = fields.Many2one("product.product",'Product reference', help="List from category All / Saleable / Wingman")
    no_of_units_wingman = fields.Float("Number of units")
    
    #Decision Makers
    decision_maker_ids = fields.One2many("opportunity.decision.maker",'opportunity_id','Decision Makers')
#     decision_maker_role_1 = fields.Selection([('Project manager','Project manager'),('Project engineer','Project engineer'),('Purchasing manager','Purchasing manager'),('Board member','Board member')],string='Role 1')
#     decision_maker_role_2 = fields.Selection([('Project manager','Project manager'),('Project engineer','Project engineer'),('Purchasing manager','Purchasing manager'),('Board member','Board member')],string='Role 2')
#     decision_maker_role_3 = fields.Selection([('Project manager','Project manager'),('Project engineer','Project engineer'),('Purchasing manager','Purchasing manager'),('Board member','Board member')],string='Role 3')
#     decision_maker_role_4 = fields.Selection([('Project manager','Project manager'),('Project engineer','Project engineer'),('Purchasing manager','Purchasing manager'),('Board member','Board member')],string='Role 4')
#     
#     decision_maker_user_id_1 = fields.Many2one("res.users","Decision maker User 1")
#     decision_maker_user_id_2 = fields.Many2one("res.users","Decision maker User 2")
#     decision_maker_user_id_3 = fields.Many2one("res.users","Decision maker User 3")
#     decision_maker_user_id_4 = fields.Many2one("res.users","Decision maker User 4")
    
    
    #Project Viability
    #project_viability_ids = fields.One2many("opportunity.project.viability",'opportunity_id','Project Viability')
    
    
#     question_1 = fields.Char("Is the customer bidding on a tender?")
#     question_2 = fields.Char("Did the electricity network provide a connection approval?")
#     question_3 = fields.Char("Did the local council provide a Development Approval (DA)?")
#     question_4 = fields.Char("Is the project financing secured?")
    
    question_1_ans = fields.Selection([('Yes','Yes'),('No','No')], string="Is the customer bidding on a tender?")
    question_2_ans = fields.Selection([('Yes','Yes'),('No','No')], string="Did the electricity network provide a connection approval?")
    question_3_ans = fields.Selection([('Yes','Yes'),('No','No')], string="Did the local council provide a Development Approval (DA)?")
    question_4_ans = fields.Selection([('Yes','Yes'),('No','No')], string="Is the project financing secured?")
    
    question_1_comment = fields.Char("Question 1 Comment")
    question_2_comment = fields.Char("Question 2 Comment")
    question_3_comment = fields.Char("Question 3 Comment")
    question_4_comment = fields.Char("Question 4 Comment")
    
    question_1_score = fields.Char("Question 1 Score",compute="_compute_question_1_score", store=True)
    question_2_score = fields.Char("Question 2 Score",compute="_compute_question_2_score", store=True)
    question_3_score = fields.Char("Question 3 Score",compute="_compute_question_3_score", store=True)
    question_4_score = fields.Char("Question 4 Score",compute="_compute_question_4_score", store=True)
    
    #Scope of work & Pricing
    total_price_full_scope = fields.Float("TOTAL PRICE - Full Scope",compute="_compute_total_price_full_scope", store=True)
    total_price_full_scope_per = fields.Char("TOTAL PRICE - Full Scope %",compute="_compute_total_price_full_scope")
    
    margin_percent = fields.Float("Margin Percent")
    total_margin_full_scope = fields.Float("TOTAL MARGIN - Full scope",compute="_compute_total_margin_full_scope", store=True)
    total_margin_full_scope_per = fields.Char("TOTAL MARGIN - Full scope %",compute="_compute_total_margin_full_scope", store=True)
    
    ##MAVERICK ECOSYSTEM SUPPLY 
    maverick_ecosystem_supply = fields.Float("MAVERICK ECOSYSTEM SUPPLY",compute="_compute_maverick_ecosystem_supply",store=True)
    maverick_ecosystem_supply_per = fields.Char("MAVERICK ECOSYSTEM SUPPLY %",compute="_compute_maverick_ecosystem_supply", store=True)
    
    mav_supply = fields.Float("MES1 - MAV supply")
    module_supply = fields.Float("MES2 - Modules supply")
    inverter_supply = fields.Float("MES3 - Inverter supply ")
    wingman_supply = fields.Float("MES4 - Wingman supply")
    dc_equipment_supply = fields.Float("MES5 - DC equipment supply")
    ac_equipment_supply = fields.Float("MES6 - AC equipment supply")
    monitoring_solution = fields.Float("MES7 - Monitoring solution")
                            
    mav_supply_per = fields.Char("MES1 - MAV supply %",compute="_compute_mav_supply_per", store=True)
    module_supply_per = fields.Char("MES2 - Modules supply %",compute="_compute_module_supply_per", store=True)
    inverter_supply_per = fields.Char("MES3 - Inverter supply %",compute="_compute_inverter_supply_per", store=True)
    wingman_supply_per = fields.Char("MES4 - Wingman supply %",compute="_compute_wingman_supply_per", store=True)
    dc_equipment_supply_per = fields.Char("MES5 - DC equipment supply %",compute="_compute_dc_equipment_supply_per", store=True)
    ac_equipment_supply_per = fields.Char("MES6 - AC equipment supply %",compute="_compute_ac_equipment_supply_per", store=True)
    monitoring_solution_per = fields.Char("MES7 - Monitoring solution %",compute="_compute_monitoring_solution_per", store=True)
    
    mav_supply_comment = fields.Char("MES1 - MAV supply Comment")
    module_supply_comment = fields.Char("MES1 - MAV supply Comment")
    inverter_supply_comment = fields.Char("MES3 - Inverter supply Comment")
    wingman_supply_comment = fields.Char("MES4 - Wingman supply Comment")
    dc_equipment_supply_comment = fields.Char("MES5 - DC equipment supply Comment")
    ac_equipment_supply_comment = fields.Char("MES6 - AC equipment supply Comment")
    monitoring_solution_comment = fields.Char("MES7 - Monitoring solution Comment")
    
    ##TRANSPORT
    freight = fields.Float("FR1 - Freight")
    freight_per = fields.Char("FR1 - Freight %",compute="_compute_freight_percent",store=True)
    freight_comment = fields.Char("FR1 - Freight Comment")
    
    ##ENGINEERING SERVICES
    engineering_services = fields.Float("Engineering Services",compute="_compute_engineering_services")
    engineering_services_per = fields.Char("Engineering Services %",compute="_compute_engineering_services")
    
    indicative_project_layout = fields.Float("SE1 - Indicative project layout")
    yield_report = fields.Float("SE2 - Yield report")
    site_survey_with_drone = fields.Float("SE3 - Site survey with drone")
    detailed_project_layout = fields.Float("SE4 - Detailed project layout")
    technical_doc_package = fields.Float("SE5 - Technical doc. package")
    specific_eng_study = fields.Float("SE6 - Specific eng. study")
    
    indicative_project_layout_per = fields.Char("SE1 - Indicative project layout %",compute="_compute_indicative_project_layout_per",store=True)
    yield_report_per = fields.Char("SE2 - Yield report %",compute="_compute_yield_report_per",store=True)
    site_survey_with_drone_per = fields.Char("SE3 - Site survey with drone %",compute="_compute_site_survey_with_drone_per",store=True)
    detailed_project_layout_per = fields.Char("SE4 - Detailed project layout %",compute="_compute_detailed_project_layout_per",store=True)
    technical_doc_package_per = fields.Char("SE5 - Technical doc. package %",compute="_compute_technical_doc_package_per",store=True)
    specific_eng_study_per = fields.Char("SE6 - Specific eng. study %",compute="_compute_specific_eng_study_per",store=True)
    
    indicative_project_layout_comment = fields.Char("SE1 - Indicative project layout Comment")
    yield_report_comment = fields.Char("SE2 - Yield report Comment")
    site_survey_with_drone_comment = fields.Char("SE3 - Site survey with drone Comment")
    detailed_project_layout_comment = fields.Char("SE4 - Detailed project layout Comment")
    technical_doc_package_comment = fields.Char("SE5 - Technical doc. package Comment")
    specific_eng_study_comment = fields.Char("SE6 - Specific eng. study Comment")
    
                
    ##DEPLOYMENT SERVICES
    deployment_services = fields.Float("Deployment Services",compute='_compute_deployment_services', store=True)
    deployment_services_per = fields.Char("Deployment Services %",compute='_compute_deployment_services', store=True)
    
    mav_deployment = fields.Float("SD1 - MAV deployment")
    mav_deployment_support = fields.Float("SD2 - MAV deployment support")
    dc_electrical_work = fields.Float("SD3 - DC electrical work")
    ac_electrical_work = fields.Float("SD4 - AC electrical work")
    construction_misc = fields.Float("SD5 - Construction misc.")
    
    
                            
    mav_deployment_per = fields.Char("SD1 - MAV deployment %",compute="_compute_mav_deployment_per",store=True)
    mav_deployment_support_per = fields.Char("SD2 - MAV deployment support %",compute="_compute_mav_deployment_support_per",store=True)
    dc_electrical_work_per = fields.Char("SD3 - DC electrical work %",compute="_compute_dc_electrical_work_per",store=True)
    ac_electrical_work_per = fields.Char("SD4 - AC electrical work %",compute="_compute_ac_electrical_work_per",store=True)
    construction_misc_per = fields.Char("SD5 - Construction misc. %",compute="_compute_construction_misc_per",store=True)

    mav_deployment_comment = fields.Char("SD1 - MAV deployment comment")
    mav_deployment_support_comment = fields.Char("SD2 - MAV deployment support comment")
    dc_electrical_work_comment = fields.Char("SD3 - DC electrical work comment")
    ac_electrical_work_comment = fields.Char("SD4 - AC electrical work comment")
    construction_misc_comment = fields.Char("SD5 - Construction misc. comment")
    
    
    ##OPERATION AND MAINTENANCE SERVICES 
    operation_and_maintenance_ser = fields.Float('Operation and Maintenance Services',compute='_compute_maintenance_and_deployment_service',store=True)
    operation_and_maintenance_ser_per = fields.Char('Operation and Maintenance Services %',compute='_compute_maintenance_and_deployment_service',store=True)
    
    monitoring_and_reporting= fields.Float('SOM1 - Monitoring and reporting')
    preventive_maintenance = fields.Float('SOM2 - Preventive maintenance')
    corrective_maintenance = fields.Float('SOM3 - Corrective maintenance')
    
    monitoring_and_reporting_per = fields.Char('SOM1 - Monitoring and reporting %',compute="_compute_monitoring_and_reporting_per",store=True)
    preventive_maintenance_per = fields.Char('SOM2 - Preventive maintenance %',compute="_compute_preventive_maintenance_per",store=True)
    corrective_maintenance_per = fields.Char('SOM3 - Corrective maintenance %',compute="_compute_corrective_maintenance_per",store=True)
    
    monitoring_and_reporting_comment= fields.Char('SOM1 - Monitoring and reporting Comment')
    preventive_maintenance_comment = fields.Char('SOM2 - Preventive maintenance Comment')
    corrective_maintenance_comment = fields.Char('SOM3 - Corrective maintenance Comment')
    
    #Planning
    #purchase_order_signing = fields.Char("Purchase order / contract signing")
    start_date_contract_signing = fields.Date("Purchase order / contract signing Start date")
    end_date_contract_signing = fields.Date("End Date")
    
    #production = fields.Char("Production")
    start_date_production = fields.Date("Production Start Date")
    end_date_production = fields.Date("End Date")
    
    #deliveries = fields.Char("Deliveries")
    start_date_deliveries = fields.Date("Deliveries Start Date")
    end_date_deliveries = fields.Date("End Date")
    
    #deployment_work = fields.Char("Deployment & work")
    start_date_deployment_work = fields.Date("Deployment & work Start Date")
    end_date_deployment_work = fields.Date("End Date")
    
    #commissioning = fields.Char("Commissioning")
    start_date_commissioning = fields.Date("Commissioning Start Date")
    end_date_commissioning = fields.Date("End Date")
    
    project_ids = fields.One2many("project.project",'lead_id',"Projects")
    project_count = fields.Integer(compute='_compute_project_count', string='# of Project')
    
    def _compute_project_count(self):
        for lead in self:
            lead.project_count = len(lead.project_ids)


    @api.model
    def create(self, vals):
        if vals.get('project_code', '/') == '/':
            if 'company_id' in vals:
                vals['project_code'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('crm.lead.project.code') or '/'
            else:
                vals['project_code'] = self.env['ir.sequence'].next_by_code('crm.lead.project.code') or '/'
        result = super(CrmLead, self).create(vals)
        if result.stage_id and result.stage_id.create_project:
            result.create_project_from_opp()
        return result
    
#     @api.multi
    def write(self, vals):
        stage_id = vals.get('stage_id')
        res = super(CrmLead, self).write(vals)
        if stage_id and self.env['crm.stage'].browse(stage_id).create_project:
            self.create_project_from_opp()
        return res
#     @api.multi
    def create_project_from_opp(self):
        if self.env.user.has_group('project.group_project_user') or self.env.user.has_group('project.group_project_manager'):
            project_obj = self.env['project.project']
            for lead in self:
                vals = {
#                     'project_code' : lead.project_code,
                    'name' : lead.name,
                    'description' : lead.description,
                    'partner_id' : lead.partner_id.id,
                    'lead_id' : lead.id,
                    }
                if lead.project_eng_id:
                    vals.update({'user_id' : lead.project_eng_id.id})
                project_obj.create(vals)
            
        return True
