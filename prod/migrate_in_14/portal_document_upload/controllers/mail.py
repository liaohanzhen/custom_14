# -*- coding: utf-8 -*-

from werkzeug.exceptions import NotFound, Forbidden

from odoo import http
from odoo.http import request

from odoo.tools import plaintext2html
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError, MissingError

from odoo.addons.portal.controllers.mail import _message_post_helper, _check_special_access, PortalChatter
from .portal import CustomerPortalAttachment

def _message_post_helper(res_model, res_id, message, token='', _hash=False, pid=False, nosubscribe=True, **kw):
    """ Generic chatter function, allowing to write on *any* object that inherits mail.thread.
        If a token is specified, all logged in users will be able to write a message regardless
        of access rights; if the user is the public user, the message will be posted under the name
        of the partner_id of the object (or the public user if there is no partner_id on the object).

        :param string res_model: model name of the object
        :param int res_id: id of the object
        :param string message: content of the message

        optional keywords arguments:
        :param string token: access token if the object's model uses some kind of public access
                             using tokens (usually a uuid4) to bypass access rules
        :param bool nosubscribe: set False if you want the partner to be set as follower of the object when posting (default to True)

        The rest of the kwargs are passed on to message_post()
    """
    record = request.env[res_model].browse(res_id)
    pid = int(pid) if pid else False
    author_id = request.env.user.partner_id.id if request.env.user.partner_id else False
    if token:
#         access_as_sudo = _has_token_access(res_model, res_id, token=token)
        access_as_sudo = _check_special_access(res_model, res_id, token=token, _hash=_hash, pid=pid)
        if access_as_sudo:
            record = record.sudo()
            if request.env.user._is_public():
                if kw.get('pid') and consteq(kw.get('hash'), record._sign_token(int(kw.get('pid')))):
                    author_id = kw.get('pid')
                else:
                    # TODO : After adding the pid and sign_token in access_url when send invoice by email, remove this line
                    # TODO : Author must be Public User (to rename to 'Anonymous')
                    author_id = record.partner_id.id if hasattr(record, 'partner_id') and record.partner_id.id else author_id
            else:
                if not author_id:
                    raise NotFound()
        else:
            raise Forbidden()
    kw.pop('csrf_token', None)
    kw.pop('redirect', None)
    kw.pop('attachment_ids', None)
    kw.pop('attachment_tokens', None)
    return record.with_context(mail_create_nosubscribe=nosubscribe).message_post(body=message,
                                                                                   message_type=kw.pop('message_type', "comment"),
                                                                                   subtype=kw.pop('subtype', "mt_comment"),
                                                                                   author_id=author_id,
                                                                                   **kw)

_message_post_helper = _message_post_helper

class PortalChatterAttachment(PortalChatter):
    
    def _post_process_portal_attachments(self, message, res_model, res_id, attachment_ids, attachment_tokens):
        """Associate "pending" attachments to a message and its main record.
        The user must have the rights to all attachments or he must provide a
        valid access_token for each of them. The attachments have to be on a
        "pending" state as well: res_id=0 and res_model='mail.compose.message'.
        :param message: the related message on which to link the attachments
        :type message: recordset of one `mail.message`
        :param res_model: the related model that will be saved on the attachment
        :type res_model: string
        :param res_id: the id of the record that will be saved on the attachment
        :type res_id: int
        :param attachment_ids: id of the attachments to associate
        :type attachment_ids: iterable of int
        :param attachment_tokens: access_token of the attachments to associate.
            Must always be the same length as `attachment_ids`, but only has to
            contain a valid access_token if the user does not have the rights to
            access the attachment without token.
        :type attachment_tokens: iterable of string
        """
        message.ensure_one()
        attachments = request.env['ir.attachment'].sudo()
        for (attachment_id, access_token) in zip(attachment_ids, attachment_tokens):
            try:
                attachment = CustomerPortalAttachment._document_check_access(self, 'ir.attachment', attachment_id, access_token)
                if attachment.res_model == 'mail.compose.message' and attachment.res_id == 0:
                    attachments += attachment
            except (AccessError, MissingError):
                pass
        attachments.write({'res_model': res_model, 'res_id': res_id})
        message.attachment_ids |= attachments
    
    @http.route(['/mail/chatter_post'], type='http', methods=['POST'], auth='public', website=True)
    def portal_chatter_post(self, res_model, res_id, message, redirect=None, attachment_ids=None, attachment_tokens=None, **kw):
        """Create a new `mail.message` with the given `message` and/or
        `attachment_ids` and redirect the user to the newly created message.
        The message will be associated to the record `res_id` of the model
        `res_model`. The user must have access rights on this target document or
        must provide valid identifiers through `kw`. See `_message_post_helper`.
        """
        url = redirect or (request.httprequest.referrer and request.httprequest.referrer + "#discussion") or '/my'
        if message or (attachment_ids and attachment_tokens):
            res_id = int(res_id)
            # message is received in plaintext and saved in html
            if message:
                message = plaintext2html(message)
            message = _message_post_helper(res_model=res_model, res_id=int(res_id), message=message, **kw)

            if attachment_ids and attachment_tokens and message:
                attachment_ids = [int(res_id) for res_id in attachment_ids.split(',')]
                attachment_tokens = attachment_tokens.split(',')
                self._post_process_portal_attachments(message=message, res_model=res_model, res_id=res_id,
                    attachment_ids=attachment_ids, attachment_tokens=attachment_tokens)

        return request.redirect(url)
