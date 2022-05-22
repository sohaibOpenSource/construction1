# -*- encoding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError, ValidationError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    bolson_id = fields.Many2one("bolson.bolson", string="Liquidacion", readonly=False, ondelete='restrict')
