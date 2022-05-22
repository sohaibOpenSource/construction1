# -*- coding: utf-8 -*-

from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class JobCosting(models.Model):
    _name = 'job.costing'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']  # odoo11
    #    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Job Costing"
    _rec_name = 'number'

    @api.model
    def create(self, vals):
        number = self.env['ir.sequence'].next_by_code('job.costing')
        vals.update({'number': number,})
        return super(JobCosting, self).create(vals)

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'cancel'):
                raise Warning(_('You can not delete Job Cost Sheet which is not draft or cancelled.'))
        return super(JobCosting, self).unlink()

    @api.depends(
        'job_cost_line_ids',
        'job_cost_line_ids.product_qty',
        'job_cost_line_ids.cost_price',
    )
    def _compute_material_total(self):
        for rec in self:
            rec.material_total = sum([(p.product_qty * p.cost_price) for p in rec.job_cost_line_ids])

    @api.depends(
        'job_labour_line_ids',
        'job_labour_line_ids.hours',
        'job_labour_line_ids.cost_price'
    )
    def _compute_labor_total(self):
        for rec in self:
            rec.labor_total = sum([(p.hours * p.cost_price) for p in rec.job_labour_line_ids])

    @api.depends(
        'job_overhead_line_ids',
        'job_overhead_line_ids.product_qty',
        'job_overhead_line_ids.cost_price'
    )
    def _compute_overhead_total(self):
        for rec in self:
            rec.overhead_total = sum([(p.product_qty * p.cost_price) for p in rec.job_overhead_line_ids])

    @api.depends(
        'material_total',
        'labor_total',
        'overhead_total'
    )
    def _compute_jobcost_total(self):
        for rec in self:
            rec.jobcost_total = rec.material_total + rec.labor_total + rec.overhead_total

    @api.depends(
        'job_cost_line_ids',
        'job_cost_line_ids.product_qty',
        'job_cost_line_ids.unit_net_price',
    )
    def _compute_net_total(self):
        for rec in self:
            rec.net_price_total = sum([(p.product_qty * p.unit_net_price) for p in rec.job_cost_line_ids])

    def _qautation_order_count(self):
        qautation_order_obj = self.env['sale.order']
        for order_line in self:
            order_line.qautation_order_count = qautation_order_obj.search_count(
                [('job_cost_id', '=', order_line.id)])

    # @api.multi
    def _purchase_order_line_count(self):
        purchase_order_lines_obj = self.env['purchase.order.line']
        for order_line in self:
            order_line.purchase_order_line_count = purchase_order_lines_obj.search_count(
                [('job_cost_id', '=', order_line.id)])

    def _job_costsheet_line_count(self):
        job_costsheet_lines_obj = self.env['job.cost.line']
        for jobcost_sheet_line in self:
            jobcost_sheet_line.job_costsheet_line_count = job_costsheet_lines_obj.search_count(
                [('direct_id', '=', jobcost_sheet_line.id)])


    # @api.multi
    # def _timesheet_line_count(self):
    #     hr_timesheet_obj = self.env['account.analytic.line']
    #     for timesheet_line in self:
    #         timesheet_line.timesheet_line_count = hr_timesheet_obj.search_count(
    #             [('job_cost_id', '=', timesheet_line.id)])

    # @api.multi

    def _account_invoice_line_count(self):
        #        account_invoice_lines_obj = self.env['account.invoice.line']
        account_invoice_lines_obj = self.env['account.move.line']
        for invoice_line in self:
            invoice_line.account_invoice_line_count = account_invoice_lines_obj.search_count(
                [('job_cost_id', '=', invoice_line.id)])

    # @api.onchange('project_id')
    # def _onchange_project_id(self):
    #     for rec in self:
    #         rec.analytic_id = rec.project_id.analytic_account_id.id


    number = fields.Char(readonly=True, default='New', copy=False)
    name = fields.Char(required=True, copy=True, default='New', string='Name')
    notes_job = fields.Text(required=False, copy=True, string='Job Cost Details')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user, string='Created By', readonly=True)
    description = fields.Char(string='Description')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, string='Company', readonly=True)
    project_id = fields.Many2one('project.project', string='Project')
    project = fields.Char(string='Project')
    analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    contract_date = fields.Date(string='Contract Date')
    start_date = fields.Date(string='Create Date', readonly=True, default=fields.Date.today())
    complete_date = fields.Date(string='Closed Date', readonly=True)
    material_total = fields.Float(string='Total Material Cost', compute='_compute_material_total', store=True)
    labor_total = fields.Float(string='Total Labour Cost', compute='_compute_labor_total', store=True)
    overhead_total = fields.Float(string='Total Overhead Cost', compute='_compute_overhead_total', store=True)
    jobcost_total = fields.Float(string='Total Cost', compute='_compute_jobcost_total', store=True)
    job_cost_line_ids = fields.One2many('job.cost.line', 'direct_id', string='Direct Materials', domain=[('job_type', '=', 'material')])
    job_labour_line_ids = fields.One2many('job.cost.line', 'direct_id', string='Direct Labours', domain=[('job_type', '=', 'labour')])
    job_overhead_line_ids = fields.One2many('job.cost.line', 'direct_id', string='Direct Overheads', domain=[('job_type', '=', 'overhead')])
    state = fields.Selection(selection=[('draft', 'Draft'),('confirm', 'Confirmed'),('approve', 'Approved')])



    account_invoice_line_count = fields.Integer(compute='_account_invoice_line_count')
    # account_invoice_line_ids = fields.One2many('account.move.line', 'job_cost_id')
    task_id = fields.Many2one('project.task', string='Job Order')
    so_number = fields.Char(string='Sale Reference')
    qautation_order_count = fields.Integer(compute='_qautation_order_count')
    purchase_order_line_count = fields.Integer(compute='_purchase_order_line_count')
    job_costsheet_line_count = fields.Integer(compute='_job_costsheet_line_count')
    purchase_order_line_ids = fields.One2many("purchase.order.line", 'job_cost_id')
    # account_invoice_line_count = fields.Integer(compute='_account_invoice_line_count')
    account_invoice_line_ids = fields.One2many('account.move.line', 'job_cost_id')

    valid_date = fields.Date(string='Date Till')
    crm_lead = fields.Many2one('crm.lead', string='Crm Lead', domain=[("stage_id", "=", 'Won')])
    project_type = fields.Many2one('project.type', string='Project Type')
    partner_id = fields.Many2one(related='crm_lead.partner_id', string='Customer')

    @api.depends('customs_value', 'net_price_total')
    def _compute_custom_cost(self):
        for rec in self:
            rec.customs_cost = rec.net_price_total * rec.customs_value

    @api.depends('net_price_total', 'shipping_value', 'labor_cost')
    def _compute_shipping_cost(self):
        for rec in self:
            rec.shipping_cost = rec.net_price_total + rec.shipping_value + rec.labor_cost + 0.01

    @api.depends('net_price_total', 'labor_cost')
    def _compute_landed_cost(self):
        for rec in self:
            rec.landed_cost = rec.net_price_total + rec.labor_cost

    @api.depends('net_price_total', 'risk_value')
    def _compute_risk_amount(self):
        for rec in self:
            rec.risk_amount = rec.net_price_total * rec.risk_value

    @api.depends('landed_cost', 'oh_value')
    def _compute_oh_landed_cost(self):
        for rec in self:
            rec.oh_landed_cost = rec.landed_cost * rec.oh_value

    @api.depends('material_total')
    def _compute_selling_price(self):
        for rec in self:
            rec.selling_price = rec.material_total

    @api.depends('selling_price', 'oh_landed_cost', 'risk_amount', 'oh_landed_cost')
    def _compute_net_profit(self):
        for rec in self:
            rec.net_profit = rec.selling_price - rec.oh_landed_cost - rec.risk_amount - rec.oh_landed_cost

    @api.depends('landed_cost', 'risk_amount', 'oh_landed_cost')
    def _compute_ttoal_cost(self):
        for rec in self:
            rec.oh_landed_cost = rec.landed_cost + rec.risk_amount + rec.oh_landed_cost

    customs_value = fields.Float('Customs')
    shipping_value = fields.Float('Shipping')
    oh_value = fields.Float('OH')
    margin_value = fields.Float('Margin')
    risk_value = fields.Float('Risk')
    net_price_total = fields.Float('Material Cost', compute='_compute_net_total')
    customs_cost = fields.Float('Customs Cost', compute='_compute_custom_cost', store=True)
    shipping_cost = fields.Float('Shipping Cost', compute='_compute_shipping_cost', store=True)
    labor_cost = fields.Float('Labor Cost')
    landed_cost = fields.Float('Landed Cost', compute='_compute_landed_cost', store=True)
    risk_amount = fields.Float('Risk Amount', compute='_compute_risk_amount', store=True)
    oh_landed_cost = fields.Float('OH Landed Cost', compute='_compute_oh_landed_cost', store=True)
    selling_price = fields.Integer(compute= '_compute_selling_price', string='Selling Price')
    net_profit = fields.Float('Net Profit', compute='_compute_net_profit', store=True)
    ttoal_cost = fields.Float('Total Cost w/ OH', compute='_compute_ttoal_cost', store=True)
    gross_profit_total = fields.Float('Gross Profit', compute='_compute_gross_profit_total', store=True)
    net_profit_total = fields.Float('Total Net Profit', compute='_compute_net_profit_total', store=True)

    @api.depends('job_labour_line_ids', 'job_labour_line_ids.product_qty',
                 'job_labour_line_ids.unit_landed_cost',
                 'selling_price')
    def _compute_gross_profit_total(self):
        for rec in self:
            value = sum([(p.product_qty * p.unit_landed_cost) for p in rec.job_labour_line_ids])
            if rec.selling_price:
                rec.gross_profit_total = 1 - value / rec.selling_price
            else:
                pass

    @api.depends('job_labour_line_ids',
                 'job_labour_line_ids.product_qty',
                 'job_labour_line_ids.unit_cost_oh',
                 'selling_price')
    def _compute_net_profit_total(self):
        for rec in self:
            value = sum([(p.product_qty * p.unit_cost_oh) for p in rec.job_labour_line_ids])
            if rec.selling_price:
                rec.net_profit_total = 1 - value / rec.selling_price
            else:
                pass


    # @api.multi
    def action_draft(self):
        for rec in self:
            rec.write({
                'state': 'draft',
            })

    # @api.multi
    def action_confirm(self):
        for rec in self:
            rec.write({
                'state': 'confirm',
            })

    # @api.multi
    def action_approve(self):
        for rec in self:
            rec.write({
                'state': 'approve',
            })

    # @api.multi
    def action_done(self):
        for rec in self:
            rec.write({
                'state': 'done',
                'complete_date': date.today(),
            })

    # @api.multi
    def action_cancel(self):
        for rec in self:
            rec.write({
                'state': 'cancel',
            })

    def action_view_quatation_order(self):
        self.ensure_one()
        quatation_order_obj = self.env['sale.order']
        cost_ids = quatation_order_obj.search([('job_cost_id', '=', self.id),('state','!=','sale')]).ids
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Quatation Order',
            'res_model': 'sale.order',
            'res_id': self.id,
            'domain': "[('id','in',[" + ','.join(map(str, cost_ids)) + "])]",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': self.id,
        }
        return action

    # @api.multi
    def action_view_purchase_order_line(self):
        self.ensure_one()
        purchase_order_lines_obj = self.env['purchase.order.line']
        cost_ids = purchase_order_lines_obj.search([('job_cost_id', '=', self.id)]).ids
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Order Line',
            'res_model': 'purchase.order.line',
            'res_id': self.id,
            'domain': "[('id','in',[" + ','.join(map(str, cost_ids)) + "])]",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': self.id,
        }
        return action





    def action_view_jobcost_sheet_lines(self):
        jobcost_line = self.env['job.cost.line']
        cost_ids = jobcost_line.search([('direct_id', '=', self.id)]).ids
        action = self.env.ref('job_costing_management.action_job_cost_line_custom').read()[0]
        action['domain'] = [('id', 'in', cost_ids)]
        ctx = 'context' in action and action['context'] and eval(action['context']).copy() or {}
        ctx.update(create=False)
        ctx.update(edit=False)
        ctx.update(delete=False)
        action['context'] = ctx
        return action

    # @api.multi
    def action_view_vendor_bill_line(self):
        #        account_invoice_lines_obj = self.env['account.invoice.line']
        account_invoice_lines_obj = self.env['account.move.line']
        cost_ids = account_invoice_lines_obj.search([('job_cost_id', '=', self.id)]).ids
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Account Invoice Line',
            #            'res_model': 'account.invoice.line',
            'res_model': 'account.move.line',
            'res_id': self.id,
            'domain': "[('id','in',[" + ','.join(map(str, cost_ids)) + "])]",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': self.id,
        }
        action['context'] = {
            'create': False,
            'edit': False,
        }
        return action

    def action_open_job_quotation_form(self):
        order_line_list = []
        if self.job_cost_line_ids:
            for job_cost_line_id in self.job_cost_line_ids:
                order_line_list.append((0, 0, {
                    'product_id': job_cost_line_id.product_id.id,
                    'product_uom_qty': job_cost_line_id.product_qty,
                    'price_unit': job_cost_line_id.unit_selling_price,
                    'price_subtotal': job_cost_line_id.total_selling_price,
                    'job_cost_type': 'Material'
                }))
        if self.job_labour_line_ids:
            for job_labour_line_id in self.job_labour_line_ids:
                order_line_list.append((0, 0, {
                    'product_id': job_labour_line_id.product_id.id,
                    'product_uom_qty': job_labour_line_id.product_qty,
                    'job_cost_type': 'Labours'
                }))
        if self.job_overhead_line_ids:
            for job_overhead_line_id in self.job_overhead_line_ids:
                order_line_list.append((0, 0, {
                    'product_id': job_overhead_line_id.product_id.id,
                    'product_uom_qty': job_overhead_line_id.product_qty,
                    'job_cost_type':'Overhead'
                }))
        oredr_id = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'order_line': order_line_list,
            'job_cost_id': self.id
        })
        return oredr_id

        # order_line_list = []
        # for job_cost_line_id in self.job_cost_line_ids:
        #     order_line_list.append((0, 0, {
        #         'product_id': job_cost_line_id.product_id.id,
        #         'product_uom_qty': job_cost_line_id.product_qty
        #     }))
        # print('-----------------------------------------------------------', order_line_list)
        # context = {
        #     'default_partner_id': self.partner_id.id,
        #     'default_company_id': 1,
        #     'default_order_line': order_line_list,
        # }
        # print('/*/*/*///*//*/*/*//**/***/**/*/*/*/*/*/*/*/',context)
        # return {
        #     'name': 'Job Quotation',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'sale.order',
        #     'view_id': False,
        #     'type': 'ir.actions.act_window',
        #     'target': 'new',
        #     'context': context
        # }




