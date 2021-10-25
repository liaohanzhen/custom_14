# coding: utf-8

from odoo import SUPERUSER_ID
from odoo.api import Environment


def post_init_hook(cr, pool):
    env = Environment(cr, SUPERUSER_ID, {})
    adjust_deep_search_post(env)


def adjust_deep_search_post(env):
    product_sat = env['product.unspsc.code'].search([])
    for product in product_sat:
        product_count = len(env['product.template'].search([('l10n_mx_edi_code_sat_id', '=', product.id)]))
        product.write({'deep_search': product_count > 1})
