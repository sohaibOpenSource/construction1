# -*- encoding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError, ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    bolson_id = fields.Many2one("bolson.bolson", string="Liquidacion", readonly=False, ondelete='restrict')
