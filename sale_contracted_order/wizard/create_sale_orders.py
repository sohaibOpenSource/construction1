# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _
from odoo.tools import float_is_zero
from collections import defaultdict
from odoo.exceptions import UserError


class contractedOrderWizard(models.TransientModel):
    _name = 'sale.contracted.order.wizard'
    _description = 'Contracted order wizard'

    @api.model
    def _default_order(self):
        # in case the cron hasn't run
        self.env['sale.contracted.order'].expire_orders()
        if not self.env.context.get('active_id'):
            return False
        contracted_order = self.env['sale.contracted.order'].search(
            [('id', '=', self.env.context['active_id'])], limit=1)
        if contracted_order.state == 'expired':
            raise UserError(_('You can\'t create a sale order from '
                              'an expired contracted order!'))
        return contracted_order

    @api.model
    def _check_valid_contracted_order_line(self, bo_lines):
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        company_id = False

        if all(float_is_zero(
                line.remaining_uom_qty, precision_digits=precision)
               for line in bo_lines):
            raise UserError(
                _('The sale has already been completed.'))

        for line in bo_lines:
            if line.order_id.state != 'open':
                raise UserError(
                    _('Sale contracted Order %s is not open') %
                    line.order_id.name)
            line_company_id = line.company_id and line.company_id.id or False
            if company_id is not False \
                    and line_company_id != company_id:
                raise UserError(
                    _('You have to select lines '
                      'from the same company.'))
            else:
                company_id = line_company_id

    @api.model
    def _default_lines(self):
        contracted_order_line_obj = self.env['sale.contracted.order.line']
        contracted_order_line_ids = self.env.context.get('active_ids', False)
        active_model = self.env.context.get('active_model', False)

        if active_model == 'sale.contracted.order':
            bo_lines = self._default_order().line_ids
        else:
            bo_lines = contracted_order_line_obj.browse(contracted_order_line_ids)

        self._check_valid_contracted_order_line(bo_lines)
        lines = [(0, 0, {
            'job_cost_type':l.job_cost_type,
            'contracted_line_id': l.id,
            'product_id': l.product_id.id,
            'date_schedule': l.date_schedule,
            'remaining_uom_qty': l.remaining_uom_qty,
            'price_unit': l.price_unit,
            'product_uom': l.product_uom,
            'qty': l.remaining_uom_qty,
            'partner_id': l.partner_id,
        }) for l in bo_lines.filtered(lambda l: l.remaining_uom_qty != 0.0)]
        return lines

    contracted_order_id = fields.Many2one(
        'sale.contracted.order', readonly=True)
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Purchase Order',
        domain=[('state', '=', 'draft')])
    line_ids = fields.One2many(
        'sale.contracted.order.wizard.line', 'wizard_id',
        string='Lines', default=_default_lines)

    def create_sale_order(self):
        order_lines_by_customer = defaultdict(list)
        currency_id = 0
        pricelist_id = 0
        user_id = 0
        payment_term_id = 0
        #for line in self.line_ids.filtered(lambda l: l.qty != 0.0):
        if self._context.get('active_model') == 'sale.contracted.order':
            active_id = self.env['sale.contracted.order'].browse(self._context.get('active_id'))
            # for line in active_id.line_ids.filtered(lambda l: l.original_uom_qty != 0.0):
            for line in self.line_ids.filtered(lambda l: l.qty != 0.0):
                if line.remaining_uom_qty < line.qty:
                    raise UserError(
                        _('You can\'t order more than the remaining quantities'))
                vals = {'product_id': line.product_id.id,
                        'name': line.product_id.name,
                        'product_uom': line.product_uom.id,
                        'sequence': line.contracted_line_id.sequence,
                        'price_unit': line.price_unit,
                        'job_cost_type':line.job_cost_type,
                        'contracted_order_line': line.contracted_line_id.id,
                        'product_uom_qty': line.qty,
                        'tax_id': [(6, 0, line.taxes_id.ids)]}
                order_lines_by_customer[active_id.partner_id.id].append((0, 0, vals))
                #active_id = self.env['sale.contracted.order'].browse(self._context.get('active_id'))
                if currency_id == 0:
                    currency_id = active_id.currency_id.id
                elif currency_id != active_id.currency_id.id:
                    currency_id = False

                if pricelist_id == 0:
                    pricelist_id = active_id.pricelist_id.id
                elif pricelist_id != active_id.pricelist_id.id:
                    pricelist_id = False

                if user_id == 0:
                    user_id = active_id.partner_id.id
                elif user_id != active_id.partner_id.id:
                    user_id = False

                if user_id == 0:
                    user_id = active_id.user_id.id
                elif user_id != active_id.user_id.id:
                    user_id = False

                if payment_term_id == 0:
                    payment_term_id = active_id.payment_term_id.id
                elif payment_term_id != active_id.payment_term_id.id:
                    payment_term_id = False
        elif self._context.get('active_model') == 'sale.contracted.order.line':
            active_id = self.env['sale.contracted.order.line'].browse(self._context.get('active_id'))

            for line in self.line_ids.filtered(lambda l: l.qty != 0.0):
                if line.remaining_uom_qty < line.qty:
                    raise UserError(
                        _('You can\'t order more than the remaining quantities'))
                vals = {'product_id': line.product_id.id,
                        'name': line.product_id.name,
                        'product_uom': line.product_uom.id,
                        'sequence': line.contracted_line_id.sequence,
                        'price_unit': line.price_unit,
                        'job_cost_type': line.job_cost_type,
                        'contracted_order_line': line.contracted_line_id.id,
                        'product_uom_qty': line.qty,
                        'tax_id': [(6, 0, line.taxes_id.ids)]}
                order_lines_by_customer[active_id.partner_id.id].append((0, 0, vals))
                if currency_id == 0:
                    currency_id = active_id.currency_id.id
                elif currency_id != active_id.currency_id.id:
                    currency_id = False

                if pricelist_id == 0:
                    pricelist_id = active_id.pricelist_id.id
                elif pricelist_id != active_id.pricelist_id.id:
                    pricelist_id = False

                if user_id == 0:
                    user_id = active_id.partner_id.id
                elif user_id != active_id.partner_id.id:
                    user_id = False

                if user_id == 0:
                    user_id = active_id.user_id.id
                elif user_id != active_id.user_id.id:
                    user_id = False

                if payment_term_id == 0:
                    payment_term_id = active_id.payment_term_id.id
                elif payment_term_id != active_id.payment_term_id.id:
                    payment_term_id = False

            # for line in active_id.order_id.line_ids.filtered(lambda l: l.original_uom_qty != 0.0):
            #     if line.remaining_uom_qty < line.original_uom_qty:
            #         raise UserError(
            #             _('You can\'t order more than the remaining quantities'))
            #     vals = {'product_id': line.product_id.id,
            #             'name': line.product_id.name,
            #             'product_uom': line.product_uom.id,
            #             'sequence': line.sequence,
            #             'price_unit': line.price_unit,
            #             'contracted_order_line': line.id,
            #             'product_uom_qty': line.original_uom_qty,
            #             'tax_id': [(6, 0, line.taxes_id.ids)]}
            #     order_lines_by_customer[active_id.partner_id.id].append((0, 0, vals))
            #     # active_id = self.env['sale.contracted.order'].browse(self._context.get('active_id'))
            #     if currency_id == 0:
            #         currency_id = active_id.currency_id.id
            #     elif currency_id != line.order_id.currency_id.id:
            #         currency_id = False
            #
            #     if pricelist_id == 0:
            #         pricelist_id = line.pricelist_id.id
            #     elif pricelist_id != line.pricelist_id.id:
            #         pricelist_id = False
            #
            #     if user_id == 0:
            #         user_id = line.user_id.id
            #     elif user_id != line.user_id.id:
            #         user_id = False
            #
            #     if payment_term_id == 0:
            #         payment_term_id = line.payment_term_id.id
            #     elif payment_term_id != line.payment_term_id.id:
            #         payment_term_id = False

        if not order_lines_by_customer:
            raise UserError(_('An order can\'t be empty'))

        if not currency_id:
            raise UserError(_('Can not create Sale Order from Contracted '
                              'Order lines with different currencies'))

        res = []
        for customer in order_lines_by_customer:
            order_vals = {
                'partner_id': customer,
                'origin': self.contracted_order_id.name,
                'user_id': user_id,
                'currency_id': currency_id,
                'pricelist_id': pricelist_id,
                'payment_term_id': payment_term_id,
                'order_line': order_lines_by_customer[customer],
            }
            sale_order = self.env['sale.order'].create(order_vals)
            res.append(sale_order.id)
        return {
            'domain': [('id', 'in', res)],
            'name': _('Sales Orders'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'context': {'from_sale_order': True},
            'type': 'ir.actions.act_window'
        }


class contractedOrderWizardLine(models.TransientModel):
    _name = 'sale.contracted.order.wizard.line'
    _description = 'contracted order wizard line'

    wizard_id = fields.Many2one('sale.contracted.order.wizard')
    contracted_line_id = fields.Many2one(
        'sale.contracted.order.line')
    # product_id = fields.Many2one(
    #     'product.product',
    #     related='contracted_line_id.product_id',
    #     string='Product')
    product_id = fields.Many2one(
        'product.product',
        string='Product')
    # product_uom = fields.Many2one(
    #     'uom.uom',
    #     related='contracted_line_id.product_uom',
    #     string='Unit of Measure')
    product_uom = fields.Many2one(
        'uom.uom',
        string='Unit of Measure')
    # date_schedule = fields.Date(
    #     related='contracted_line_id.date_schedule')
    date_schedule = fields.Date()
    remaining_uom_qty = fields.Float()
    qty = fields.Float(string='Quantity to Order', required=True)
    # price_unit = fields.Float(
    #     related='contracted_line_id.price_unit')
    price_unit = fields.Float()
    job_cost_type = fields.Selection([('Material', "Material"), ('Labours', "Labours"), ('Overhead', "Overhead")],
                                     default=False)
    currency_id = fields.Many2one(
        'res.currency', related='contracted_line_id.currency_id')
    # partner_id = fields.Many2one(
    #     'res.partner',
    #     related='contracted_line_id.partner_id',
    #     string='Vendor')
    partner_id = fields.Many2one(
        'res.partner',
        string='Vendor')
    taxes_id = fields.Many2many(
        'account.tax', related="contracted_line_id.taxes_id")
