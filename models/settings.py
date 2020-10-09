# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging


_logger = logging.getLogger(__name__)

class ResConfigSettingsExpensify(models.TransientModel):
    _inherit = 'res.config.settings'

    module_expensify_connector = fields.Boolean("Expensify",default=True)
    expensify_user_id = fields.Char("Expensify User Id", config_parameter='expensify_user_id', default='')
    expensify_secret = fields.Char("Expensify Secret", config_parameter='expensify_secret', default='')
    expensify_start_date = fields.Char("Expensify Start Date", config_parameter='expensify_start_date', default='2020-01-01')
    expensify_create_hr_expenses = fields.Boolean("Expensify Create HR Expenses", config_parameter='expensify_create_hr_expenses', default=False)

