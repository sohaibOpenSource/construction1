# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import models, fields, api


class SystemInformation(models.Model):
    _name = 'system.information'

    project_id = fields.Many2one('crm.lead', string='Project ID')
    interested_products_or_service = fields.Char(string='INTERESTED PRODUCTS / SERVICES')
    system_brand = fields.Char(string='SYSTEM BRANDS')
    target_price_or_budget = fields.Char(string='TARGET PRICE / BUDGET (Cost)')
    remarks = fields.Char(string='REMARKS')
