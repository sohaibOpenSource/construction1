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
from odoo.exceptions import ValidationError


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    # Project INFORMATION PAGE
    project_information = fields.Char(string='Project Information*')
    project_name = fields.Many2one('project.project', string="Project Name")
    project_type = fields.Many2one(related='project_name.project_type', string="Project Type")
    consultant_name = fields.Many2one('res.partner', 'Consultant')
    mep_contractor_name = fields.Many2one('res.partner', 'MEP Contractor')
    project_received_date = fields.Date(string='Received Date')
    proposal_submittal_deadline = fields.Date(string='Proposal Submittal Deadline*(Approximate)')
    project_start_date = fields.Date(string='Project Start Date')
    contractor_name = fields.Char(string='Contractor')
    expected_awarding_date = fields.Date(string='Expected Awarding Date*')
    project_duration = fields.Char(string='Project Duration')
    is_old_customer = fields.Boolean(string='Old Customer')
    is_budget_price_ave = fields.Boolean(string='Budget Price Ave')
    is_high_rank_end_user = fields.Boolean(string='High Rank End User')
    is_deadline = fields.Boolean(string='Deadline(Gov. or Semi Gov)')
    is_boq = fields.Boolean(string='BOQ')
    is_drawing = fields.Boolean(string='Drawing')
    is_vendor_list = fields.Boolean(string='Vendor List')

    probability_lead = fields.Float('Probability', default=0.0)

    # Lead/INQUIRY INFORMATION PAGE
    inquiry_date = fields.Date(string='Date*')
    rfi_contact_name = fields.Char(string='RFI Contact Name*')
    exp_budget = fields.Float(string='Expected Budget')
    account_manager = fields.Many2one('hr.employee', string='Account Manager*')
    rfi_contact_number = fields.Integer(string='RFI Contact Number*')
    rfi_contact_email = fields.Char(string='RFI Contact Email*')

    # CHECKLIST FOR QUOTATION PAGE
    rfq_or_tender_documents = fields.Binary(string='RFQ / Tender Documents')
    is_rfq_or_tender_documents = fields.Boolean(string='Is RFQ / Tender Documents')
    boq = fields.Binary(string='BOQ')
    is_boq_file = fields.Boolean(string='Is BOQ')
    soft_copy_drawing_scaled_and_autocad_for_evl_and_security_systems = fields.Binary(
        string='Soft Copy Drawing Scaled & Autocad For EVL & Security Systems')
    is_soft_copy_for_autocad_and_security = fields.Boolean(
        string='Is soft copy for autocad and security')
    drawing_list_and_legend_drawings = fields.Binary(string='Drawing List & Legend Drawings')
    is_drawing_list_and_legend_drawings = fields.Boolean(string='Is Drawing List & Legend Drawings')
    single_line_diagrams = fields.Binary(string='Single Line Diagrams(Only EVL & Security)')
    is_single_line_diagrams = fields.Boolean(string='Is Single Line Diagrams(Only EVL & Security)')
    vendor_list = fields.Binary(string='Vendor List')
    is_vendor_list_file = fields.Boolean(string='Is Vendor List')
    specification = fields.Binary(string='Specification')
    is_specification = fields.Boolean(string='Is Specification')
    site_survey_bom = fields.Binary(string='Site Survey BOM')
    is_site_survey_bom = fields.Boolean(string='Is Site Survey BOM')
    civil_work_or_electrical_work = fields.Binary(string='Civil Work / Electrical Work')
    is_civil_work_or_electrical_work = fields.Boolean(string='Is Civil Work / Electrical Work')
    other_docs = fields.Binary(string='Other Docs(Please Specify)')
    is_other_docs = fields.Boolean(string='Is Other Docs(Please Specify)')

    # Presales Deliverables PAGE
    boq_with_costing_as_per_DXB = fields.Boolean(string='BOQ with Costing as per DXB')
    datasheet_required = fields.Boolean(string='Datasheet required')
    others_please_specify = fields.Boolean(string='Others')
    others_specification = fields.Char(string='Please Specify:')
    bid_bond_if_required = fields.Boolean(string='Bid Bond if required')
    bid_bond_specification = fields.Char(string='please Specify:')
    presale_percentage = fields.Float(string='%')
    presale_date = fields.Date(string='Date:')
    presale_validity = fields.Char(string='validity:')

    job_in_hand = fields.Boolean(string='Job in Hand(Accurate Pricing w/ Part no.)')
    project_with_end_user = fields.Boolean(string='Project with End User')
    budgetary_price_without_part_no = fields.Boolean(string='Budgetary Price without Part No')
    tender_or_bidding = fields.Boolean(string='Tender / Bidding(Accurate Pricing W Part No)')
    budgetary_price_with_part_no = fields.Boolean(string='Budgetary Price with Part No')
    presales_other_notes = fields.Char(string='Other Notes:')

    # System Interested PAGE
    interested_system_ids = fields.One2many('system.information', 'project_id', string="System Interested")

    lead_number = fields.Char(string='Lead Number')

    @api.constrains('lead_number')
    def _check_lead_number(self):
        record = self.env['crm.lead'].search([('id', '!=', self.id)])
        for lead in record:
            if lead.lead_number:
                if lead.lead_number == self.lead_number:
                    raise ValidationError(
                        'Lead Number must be unique !!')

    @api.onchange('is_old_customer', 'is_budget_price_ave', 'is_high_rank_end_user', 'is_deadline', 'is_boq',
                  'is_drawing', 'is_vendor_list')
    def _calculate_probability(self):
        self.probability_lead = 0.0
        if self.is_old_customer:
            self.probability_lead += 100 / 7
        if self.is_budget_price_ave:
            self.probability_lead += 100 / 7
        if self.is_high_rank_end_user:
            self.probability_lead += 100 / 7
        if self.is_boq:
            self.probability_lead += 100 / 7
        if self.is_drawing:
            self.probability_lead += 100 / 7
        if self.is_vendor_list:
            self.probability_lead += 100 / 7
        if self.is_deadline:
            self.probability_lead += 100 / 7
        # else:
        #     self.probability_lead -= 100 / 7

    def action_open_job_costing_form(self):
        self.ensure_one()
        # view_id = self.env.ref('odoo_job_costing_management.job_costing_form_view').id
        context = {
            'default_partner_id': self.partner_id.id
        }
        return {
            'name': 'Job Costing',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'job.costing',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }

        # partner_ids = self.env.user.partner_id.ids
        # if self.partner_id:
        #     partner_ids.append(self.partner_id.id)
        # action['context'] = {
        #     'default_opportunity_id': self.id if self.type == 'opportunity' else False,
        #     'default_partner_id': self.partner_id.id,
        #     'default_partner_ids': partner_ids,
        #     'default_team_id': self.team_id.id,
        #     'default_name': self.name,
        # }
        # return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
