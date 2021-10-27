# -*- coding: utf-8 -*-

from odoo import http, SUPERUSER_ID, _
from odoo.http import request
from odoo.tools import groupby as groupbyelem
from collections import OrderedDict
from operator import itemgetter

from odoo.addons.portal.controllers.portal import get_records_pager, CustomerPortal, pager as portal_pager
from odoo.osv.expression import OR
import werkzeug.wrappers
import werkzeug.utils
import base64

class AttachmentCustomerPortal(CustomerPortal):
    
    @http.route(['/portal_documents/content/<int:id>',], type='http', auth="public")
    def content_common(self, xmlid=None, model='ir.attachment', id=None, field='datas',
                       filename=None, filename_field='datas_fname', unique=None, mimetype=None,
                       download=None, data=None, token=None, access_token=None, **kw):
        status, headers, content = request.env['ir.http'].sudo().binary_content(
            xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename,
            filename_field=filename_field, download=download, mimetype=mimetype,
            access_token=access_token,)
        if status == 304:
            response = werkzeug.wrappers.Response(status=status, headers=headers)
        elif status == 301:
            return werkzeug.utils.redirect(content, code=301)
        elif status != 200:
            response = request.not_found()
        else:
            content_base64 = base64.b64decode(content)
            headers.append(('Content-Length', len(content_base64)))
            response = request.make_response(content_base64, headers)
        if token:
            response.set_cookie('fileToken', token)
        return response
    
    def get_portal_documents_domain(self):
        user = request.env.user
        domain = ['&','|',('user_ids','in', [user.id]), ('user_ids','=', False),'|',('group_ids','in',user.groups_id.ids),('group_ids','=',False)]
        return domain
    
    def _prepare_portal_layout_values(self):
        values = super(AttachmentCustomerPortal, self)._prepare_portal_layout_values()
        PortalAttachment = request.env['portal.user.attachment']

        domain = self.get_portal_documents_domain()
        attachments = PortalAttachment.sudo().search(domain, order='res_model, sequence, name')
        res_models = attachments.mapped('res_model')
        if res_models:
            model_records = request.env['ir.model'].sudo().search([('model','in',res_models)])
            for m in model_records:
                has_active_field = False
                for f in m.field_id:
                    if f.name=='active':
                        has_active_field = True
                        break
                if has_active_field:
                    models_attachments = attachments.filtered(lambda x: x.res_model==m.model)
                    records = request.env[m.model].sudo().browse(models_attachments.mapped('res_id'))
                    inactive_records = records.filtered(lambda x:not x.active)
                    attachments -= attachments.filtered(lambda x:x.res_model==m.model and x.res_id in inactive_records.ids)
                    
        values['document_count'] = len(attachments) #PortalAttachment.search_count(domain)
        return values
    
    @http.route(['/download/portal/attachment'], type='json', auth="public", methods=['POST'], website=True)
    def download_portal_attachment(self, attachment_id):
        if attachment_id:
            attachment_id = int(attachment_id)
            irAttachObj = request.env['portal.user.attachment'].sudo().browse(attachment_id)
            irAttachObj.downloads = irAttachObj.downloads + 1
        return True
    
    @http.route(['/my/portal/documents'], type='http', auth="user", website=True)
    def portal_my_documents(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', **kw):
        groupby = kw.get('groupby', 'source_name') #TODO master fix this
        
        PortalAttachment = request.env['portal.user.attachment']
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Title'), 'order': 'name'},
            'res_model': {'label': _('Source'), 'order': 'res_model'},
            'category': {'label': _('Category'), 'order': 'attachment_category'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Search <span class="nolabel"> (in Content)</span>')},
            'source_name': {'input': 'source_name', 'label': _('Search in Source Name')},
            'category': {'input': 'category', 'label': _('Search in Category')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'source': {'input': 'source', 'label': _('Source')},
            'source_name': {'input': 'source_name', 'label': _('Source Name')},
            'category': {'input': 'category', 'label': _('Category')},
        }

        main_domain = self.get_portal_documents_domain()
        attachments = PortalAttachment.sudo().search(main_domain, order='res_model, sequence, name')
        
        res_models = attachments.mapped('res_model')
        if res_models:
            model_records = request.env['ir.model'].sudo().search([('model','in',res_models)])
            for m in model_records:
                has_active_field = False
                for f in m.field_id:
                    if f.name=='active':
                        has_active_field = True
                        break
                if has_active_field:
                    models_attachments = attachments.filtered(lambda x: x.res_model==m.model)
                    records = request.env[m.model].sudo().browse(models_attachments.mapped('res_id'))
                    inactive_records = records.filtered(lambda x:not x.active)
                    attachments -= attachments.filtered(lambda x:x.res_model==m.model and x.res_id in inactive_records.ids)
            models_name_dict = dict([(x.model,x.name) for x in model_records])
        else:
            models_name_dict={}
        added_model = []
        doc_name_dict = {}
        for k, g in groupbyelem(attachments, key=itemgetter(*['res_model', 'res_id'])):
            res_model = k[0]
            res_id = k[1]
            model_name = models_name_dict.get(res_model)
            if model_name not in added_model:
                searchbar_filters.update({
                    str(res_model): {'label': _('<b>All : '+model_name+'</b>'), 'domain': [('res_model', '=', res_model)]}
                })
            rec = request.env[res_model].sudo().browse(res_id)
            if rec:
                doc_name_dict.update({k: rec.display_name})
                searchbar_filters.update({
                        str(res_model+'_'+str(res_id)): {'label': model_name+' : '+rec.display_name, 'domain': [('res_model', '=', res_model),('res_id','=',res_id)]}
                    })
            else:
                doc_name_dict.update(k, '')    
        domain = [('id', 'in', attachments.ids)]
        
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # archive groups - Default Group By 'create_date'
#         archive_groups = self._get_archive_groups('portal.user.attachment', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
            if search_in in ('source_name', 'all'):
                search_models = []
                search_res_ids = []
                matched_models = []
                for k,v in doc_name_dict.items():
                    if search.lower() not in v.lower():
                        #source_filter_ids = attachments.filtered(lambda x:x.res_model==k[0] and x.res_id == k[1]).ids
                        search_models.append(k[0])
                        search_res_ids.append(k[1])
                    else:
                        matched_models.append(k[0])
                        #search_domain = OR([search_domain, [('res_model', '!=', k[0]),('res_id','!=',k[1])]])
                search_models = list(set(search_models) - set(matched_models))
                if search_models and search_res_ids: 
                    search_domain = OR([search_domain, [('res_model', 'not in', search_models),('res_id','not in', search_res_ids)]])
                
            if search_in in ('category', 'all'):
                search_domain = OR([search_domain, [('attachment_category', 'ilike', search)]])
            domain += search_domain

        # task count
        document_count = PortalAttachment.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/portal/documents",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby, 'search_in': search_in, 'search': search},
            total=document_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        if groupby == 'source':
            order = "res_model, %s" % order  # force sort on project first to group by project in view
        elif groupby == 'source_name':
            order = "res_model,res_id, %s" % order
        elif groupby == 'category':
            order = "attachment_category, %s" % order  # force sort on project first to group by project in view
        documents = PortalAttachment.sudo().search(domain, order=order, limit=self._items_per_page, offset=(page - 1) * self._items_per_page)
        request.session['my_documents_history'] = documents.ids[:100]
        if groupby == 'source':
            grouped_documents = [PortalAttachment.concat(*g) for k, g in groupbyelem(documents, itemgetter('res_model'))]
        elif groupby == 'source_name':
            grouped_documents = [PortalAttachment.concat(*g) for k, g in groupbyelem(documents, key=itemgetter(*['res_model', 'res_id']))]
        elif groupby == 'category':
            grouped_documents = [PortalAttachment.concat(*g) for k, g in groupbyelem(documents, itemgetter('attachment_category'))]
        elif documents:
            grouped_documents = [documents]
        else:
            grouped_documents = []

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'attachments': attachments,
            'documents': documents, #TODO master remove this, grouped_documents is enough
            'grouped_documents': grouped_documents,
            'page_name': 'portal_documents',
#             'archive_groups': archive_groups,
            'default_url': '/my/portal/documents',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'models_name_dict' : models_name_dict,
            'doc_name_dict' : doc_name_dict,
        })
        return request.render("portal_documents.portal_my_documents", values)
