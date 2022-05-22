# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class JobCostLine(models.Model):
    _name = 'job.cost.line'
    _description = 'Job Cost Line'

    @api.depends('product_qty', 'hours', 'cost_price', 'direct_id')
    def _compute_total_cost(self):
        for rec in self:
            if rec.job_type == 'labour':
                rec.product_qty = 0.0
                rec.total_cost = rec.hours * rec.cost_price
            else:
                rec.hours = 0.0
                rec.total_cost = rec.product_qty * rec.cost_price


    @api.depends('purchase_order_line_ids', 'purchase_order_line_ids.product_qty', 'purchase_order_line_ids.order_id.state')
    def _compute_actual_quantity(self):
        for rec in self:
            rec.actual_quantity = sum([p.order_id.state in ['purchase', 'done'] and p.product_qty for p in rec.purchase_order_line_ids])


    @api.depends('account_invoice_line_ids',
        'account_invoice_line_ids.quantity',
        'account_invoice_line_ids.move_id.state',
        'account_invoice_line_ids.move_id.payment_state')
    def _compute_actual_invoice_quantity(self):
        for rec in self:
            rec.actual_invoice_quantity = sum([p.quantity or 0.0 for p in rec.account_invoice_line_ids if p.move_id.state in ['posted'] or p.move_id.payment_state in ['paid']])

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            rec.name = rec.product_id.name
            rec.product_qty = 1.0
            rec.uom_id = rec.product_id.uom_id.id
            rec.cost_price = rec.product_id.standard_price


    direct_id = fields.Many2one('job.costing', string='Job Costing')
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Char(string='Description')
    reference = fields.Char(string='Reference')
    date = fields.Date(string='Date', readonly=True, default=fields.Date.today())
    product_qty = fields.Float(string='Planned Qty', copy=False)
    uom_id = fields.Many2one('uom.uom', string='Uom')
    cost_price = fields.Float(string='Cost / Unit', copy=False)
    total_cost = fields.Float(string='Cost Price Sub Total', compute='_compute_total_cost', store=True)
    analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id)
    job_type_id = fields.Many2one('job.type', string='Job Type')
    job_type = fields.Selection(selection=[('material','Material'), ('labour','Labour'), ('overhead','Overhead')], string="Type", required=True)
    basis = fields.Char(string='Basis')
    hours = fields.Float(string='Hours')
    purchase_order_line_ids = fields.One2many('purchase.order.line', 'job_cost_line_id')
    account_invoice_line_ids = fields.One2many('account.move.line', 'job_cost_line_id')
    actual_quantity = fields.Float(string='Actual Purchased Quantity', compute='_compute_actual_quantity')
    actual_invoice_quantity = fields.Float(string='Actual Vendor Bill Quantity', compute='_compute_actual_invoice_quantity')
    actual_hour = fields.Float(string='Actual Timesheet Hours', compute='_compute_actual_hour')

    discount = fields.Float(string='Discount')
    remarks = fields.Char(string='Remarks')
    stock_qty = fields.Float(related='product_id.qty_available', string='Stock Qty')
    reserved_qty = fields.Float(string='Reserved Qty')
    unit_list_price = fields.Float(string='Unit List Price')
    unit_net_price = fields.Float(string='Unit Net Price', readonly=True)
    total_net_price = fields.Float(string='Total Net Price', readonly=True)
    unit_landed_cost = fields.Float(string='Unit landed Cost', readonly=True)
    total_landed_cost = fields.Float(string='Total landed Cost', readonly=True)
    unit_cost_oh = fields.Float(string='U.Cost/OH', readonly=True)
    total_cost_oh = fields.Float(string='T.Cost/OH', readonly=True)
    unit_selling_price = fields.Float(string='Unit Selling Price', readonly=True)
    total_selling_price = fields.Float(string='Total Selling Price', readonly=True)
    exchange_rate = fields.Float(string='Exchange Rate', store=True)
    sequence = fields.Integer(string='Sequence', default=10)
    display_type = fields.Selection([('line_section', "Section")], default=False, help="Technical field for UX purpose.")

    # @api.depends('direct_id.customs_value', 'direct_id.margin_value',
    #              'direct_id.shipping_value', 'direct_id.oh_value',
    #              'direct_id.risk_value', 'product_qty',
    #              'discount', 'unit_list_price')
    # def _compute_values(self):
    #     for item in self:
    #
    #         # compuet unit net price
    #         ulp = item.unit_list_price
    #         dis = item.discount / 100.0
    #         item.unit_net_price = ulp * (1.0 - dis)
    #
    #         # compuete total net price
    #         item.total_net_price = item.product_qty * item.unit_net_price
    #
    #         # compute unit landed cost
    #         cv = item.direct_id.customs_value / 100.0
    #         sv = item.direct_id.shipping_value / 100.0
    #         item.unit_landed_cost = item.unit_net_price * (1.0 + cv + sv)
    #
    #         # compute total landed cost
    #         item.total_landed_cost = item.product_qty * item.unit_landed_cost
    #
    #         # compute unit cost overhead
    #         ohv = item.direct_id.oh_value / 100.0
    #         rv = item.direct_id.risk_value / 100.0
    #         item.unit_cost_oh = item.unit_landed_cost * (1.0 + ohv + rv)
    #
    #         # compute total cost overhead
    #         item.total_cost_oh = item.product_qty * item.unit_cost_oh
    #
    #         # compute unit selling price
    #         mv = item.direct_id.margin_value / 100.0
    #         item.unit_selling_price = item.unit_cost_oh / (1.0 - mv)
    #
    #         # compute total selling price
    #         item.total_selling_price = item.product_qty * item.unit_selling_price


    @api.onchange('currency_id')
    def get_exchange_rate(self):
        main_currency = self.env.ref('base.main_company').currency_id
        for item in self:
            ex_rate = item.currency_id.rate
            if ex_rate:
                main_rate = main_currency.rate
                convert = main_rate / ex_rate
                item.exchange_rate = item.cost_price / convert


