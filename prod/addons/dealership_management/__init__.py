# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from . import controllers
from . import models
from . import wizard

def pre_init_check(cr):
	from odoo.service import common
	from odoo.exceptions import Warning

	server_serie = common.exp_version().get('server_serie')

	if server_serie != '14.0':
		raise Warning('Module support Odoo series 14.0 found {}.'.format(server_serie))
