# -*- coding: utf-8 -*-

import base64
import io
import os
import zipfile

from odoo.http import content_disposition, request

from odoo.addons.documents.controllers.main import ShareRoute


FORBIDDEN_MIMETYPES = ["application/octet-stream", "special_cloud_folder"]


class ShareRouteClass(ShareRoute):
    """
    Re-write to make possible donwload of cloud files instead of opening an url
    """
    def binary_content(self, id, env=None, field='datas', share_id=None, share_token=None,
                       download=False, unique=False, filename_field='name'):
        """
        Fully re-write since we need to process cloud files donwload as well
        """
        env = env or request.env
        record = env['documents.document'].browse(int(id))
        filehash = None

        if share_id:
            share = env['documents.share'].sudo().browse(int(share_id))
            record = share._get_documents_and_check_access(share_token, [int(id)], operation='read')
        if not record:
            return (404, [], None)

        try:
            last_update = record['__last_update']
        except AccessError:
            return (404, [], None)

        mimetype = False
        if record.type == 'url' and record.url:
            if record.cloud_key and record.attachment_id.mimetype not in FORBIDDEN_MIMETYPES:
                status, content, filename, mimetype, filehash = env['ir.http']._binary_ir_attachment_redirect_content(
                    record.attachment_id, default_mimetype='application/octet-stream'
                )               
            else:
                module_resource_path = record.url
                filename = os.path.basename(module_resource_path)
                status = 301
                content = module_resource_path
        else:
            status, content, filename, mimetype, filehash = env['ir.http']._binary_record_content(
                record, field=field, filename=None, filename_field=filename_field,
                default_mimetype='application/octet-stream')
        
        status, headers, content = env['ir.http']._binary_set_headers(
            status, content, filename, mimetype, unique, filehash=filehash, download=download)

        return status, headers, content

    def _make_zip(self, name, documents):
        """
        Fully re-write since we need to process cloud files to zip as well
        """
        stream = io.BytesIO()
        try:
            with zipfile.ZipFile(stream, 'w') as doc_zip:
                for document in documents:
                    if document.type not in ['binary', 'url']:
                        continue
                    if document.type == "url":
                        if document.attachment_id.cloud_key and \
                                document.attachment_id.mimetype not in FORBIDDEN_MIMETYPES:
                            status, content, filename, mimetype, filehash = request.env['ir.http']._binary_ir_attachment_redirect_content(
                                document.attachment_id, default_mimetype='application/octet-stream'
                            ) 
                            if not content:
                                continue
                        else:
                            continue
                    else:
                        status, content, filename, mimetype, filehash = request.env['ir.http']._binary_record_content(
                            document, field='datas', filename=None, filename_field='name',
                            default_mimetype='application/octet-stream')
                    doc_zip.writestr(filename, base64.b64decode(content),
                                     compress_type=zipfile.ZIP_DEFLATED)
        except zipfile.BadZipfile:
            logger.exception("BadZipfile exception")
        content = stream.getvalue()
        headers = [
            ('Content-Type', 'zip'),
            ('X-Content-Type-Options', 'nosniff'),
            ('Content-Length', len(content)),
            ('Content-Disposition', content_disposition(name))
        ]
        return request.make_response(content, headers)
