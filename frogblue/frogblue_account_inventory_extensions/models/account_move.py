# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    stock_move_origin_doc = fields.Char(
        string='Move Origin',
        help='The original document for the stock movement.'
    )

    @api.model
    def execute_journal_query(self):
        self._cr.execute("""
                UPDATE
                    account_move
                SET stock_move_origin_doc=sub.sub_origin
                FROM (
                    SELECT
                        am.id AS am_id,
                        st.origin AS sub_origin
                    FROM  account_move AS am
                    JOIN stock_move AS st ON st.id = am.stock_move_id
                ) AS sub
               WHERE account_move.id = sub.am_id
            """)
