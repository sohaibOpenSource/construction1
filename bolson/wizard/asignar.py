# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError, ValidationError

class Asignar(models.TransientModel):
    _name = "bolson.asignar"
    _description = "Asignar liquidación"

    bolson_id = fields.Many2one("bolson.bolson", string="Liquidación")

    @api.multi
    def asignar(self):
        for rec in self:
            for invoice in self.env['account.invoice'].browse(self.env.context.get('active_ids', [])):
                if rec.bolson_id:
                    invoice.bolson_id = rec.bolson_id.id
        return {'type': 'ir.actions.act_window_close'}
