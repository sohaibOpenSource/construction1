# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderInherit(models.Model):
    _inherit = "sale.contracted.order"

    def reset_draft(self):
        for rec in self:
            rec.state = 'draft'


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def create(self, vals):
        lead_number = self.env['ir.sequence'].next_by_code('crm.lead')
        vals.update({'lead_number': lead_number})
        return super(CrmLead, self).create(vals)


class ProjectType(models.Model):
    _name = 'project.type'

    name = fields.Char("Project Type")

class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_type = fields.Many2one('project.type', 'Project Type')


