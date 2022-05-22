# Copyright 2018 ACSONE SA/NV
# Copyright 2019 Eficent and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from datetime import date, timedelta
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    contracted_order_id = fields.Many2one(
        'sale.contracted.order', string='Origin contracted order',
        related='order_line.contracted_order_line.order_id')
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('contracted', 'Contracted'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    @api.model
    def _check_exchausted_contracted_order_line(self):
        return any(line.contracted_order_line.remaining_qty < 0.0 for
                   line in self.order_line)

    def button_confirm(self):
        res = super().button_confirm()
        for order in self:
            if order._check_exchausted_contracted_order_line():
                raise ValidationError(
                    _('Cannot confirm order %s as one of the lines refers '
                      'to a contracted order that has no remaining quantity.')
                    % order.name)
        return res

    @api.constrains('partner_id')
    def check_partner_id(self):
        for line in self.order_line:
            if line.contracted_order_line:
                if line.contracted_order_line.partner_id != \
                        self.partner_id:
                    raise ValidationError(_(
                        'The customer must be equal to the '
                        'contracted order lines customer'))

    def create_blanket_order(self):
        print("\n\n\n\n\n==========self=========", self)
        line_list = []
        res = []
        for line in self.order_line:
            print("\n\n\n\n\n==========line=========", line)
            print("\n\n\n\n\n==========line=========", line.display_type, line.product_id)
            # if line.display_type:
            #     val = (0, 0, {
            #         'display_type': line.display_type,
            #         'name': line.name,
            #
            #     })
            #     line_list.append(val)
            if line.product_id:
                line_dict = {'product_id': line.product_id.id,
                             'name': line.name,
                             'original_uom_qty': line.product_uom_qty,
                             'product_uom': line.product_uom.id,
                             'price_unit': line.price_unit,
                             'taxes_id': line.tax_id.id,
                             'price_subtotal': line.price_subtotal,
                             'job_cost_type': line.job_cost_type
                             }
                line_list.append((0, 0, line_dict))

        vals = {'partner_id': self.partner_id.id,
                'pricelist_id': self.pricelist_id.id,
                # 'currency_id': self.pricelist_id.currency_id.id,
                'payment_term_id': self.payment_term_id.id,
                'validity_date': self.validity_date,
                'user_id': self.user_id.id,
                'team_id': self.team_id.id,
                'company_id': self.company_id.id,
                'fiscal_position_id': self.fiscal_position_id.id,
                'amount_untaxed': self.amount_untaxed,
                'amount_tax': self.amount_tax,
                'amount_total': self.amount_total,
                'line_ids': line_list
                }
        contracted_order = self.env['sale.contracted.order'].create(vals)
        # line_list = []
        # res = []
        # for line in self.order_line:
        #     print("\n\n\n\n\n==========line=========",line)
        #     print("\n\n\n\n\n==========line=========", line.display_type,line.product_id)
        #     if line.display_type:
        #         val = (0, 0, {
        #             'display_type': line.display_type,
        #             'name': line.name,
        #         })
        #         line_list.append(val)
        #     if line.product_id:
        #         line_dict = {'product_id': line.product_id.id,
        #                      'name': line.name,
        #                      'original_uom_qty': line.product_uom_qty,
        #                      'product_uom': line.product_uom.id,
        #                      'price_unit': line.price_unit,
        #                      'taxes_id': line.tax_id.id,
        #                      'price_subtotal': line.price_subtotal,
        #         }
        #         line_list.append((0, 0, line_dict))
        # contracted_order.write({'line_ids': line_list})
        res.append(contracted_order.id)
        self.state = "contracted"
        return {
            'domain': [('id', 'in', res)],
            'name': _('Contracted Orders'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.contracted.order',
            #'context': {'from_sale_order': True},
            'type': 'ir.actions.act_window'
        }

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    contracted_order_line = fields.Many2one(
        'sale.contracted.order.line',
        string='Contracted Order line',
        copy=False)
    job_cost_type = fields.Selection([('Material', "Material"),('Labours', "Labours"),('Overhead', "Overhead")], default=False)

    def _get_assigned_bo_line(self, bo_lines):
        # We get the contracted order line with enough quantity and closest
        # scheduled date
        assigned_bo_line = False
        date_planned = date.today()
        date_delta = timedelta(days=365)
        for line in bo_lines.filtered(lambda l: l.date_schedule):
            date_schedule = line.date_schedule
            if date_schedule and \
                    abs(date_schedule - date_planned) < date_delta:
                assigned_bo_line = line
                date_delta = abs(date_schedule - date_planned)
        if assigned_bo_line:
            return assigned_bo_line
        non_date_bo_lines = bo_lines.filtered(lambda l: not l.date_schedule)
        if non_date_bo_lines:
            return non_date_bo_lines[0]

    def _get_eligible_bo_lines_domain(self, base_qty):
        filters = [
            ('product_id', '=', self.product_id.id),
            ('remaining_qty', '>=', base_qty),
            ('currency_id', '=', self.order_id.currency_id.id),
            ('order_id.state', '=', 'open')]
        if self.order_id.partner_id:
            filters.append(
                ('partner_id', '=', self.order_id.partner_id.id))
        return filters

    def _get_eligible_bo_lines(self):
        base_qty = self.product_uom._compute_quantity(
            self.product_uom_qty, self.product_id.uom_id)
        filters = self._get_eligible_bo_lines_domain(base_qty)
        return self.env['sale.contracted.order.line'].search(filters)

    def get_assigned_bo_line(self):
        self.ensure_one()
        eligible_bo_lines = self._get_eligible_bo_lines()
        if eligible_bo_lines:
            if not self.contracted_order_line or self.contracted_order_line \
                    not in eligible_bo_lines:
                self.contracted_order_line = \
                    self._get_assigned_bo_line(eligible_bo_lines)
        else:
            self.contracted_order_line = False
        self.onchange_contracted_order_line()
        return {'domain': {'contracted_order_line': [
            ('id', 'in', eligible_bo_lines.ids)]}}

    @api.onchange('product_id', 'order_partner_id')
    def onchange_product_id(self):
        # If product has changed remove the relation with contracted order line
        if self.product_id:
            return self.get_assigned_bo_line()
        return

    @api.onchange('product_uom_qty', 'product_uom')
    def product_uom_change(self):
        res = super().product_uom_change()
        if self.product_id and not self.env.context.get(
                'skip_contracted_find', False):
            return self.get_assigned_bo_line()
        return res

    @api.onchange('contracted_order_line')
    def onchange_contracted_order_line(self):
        bol = self.contracted_order_line
        if bol:
            self.product_id = bol.product_id
            if bol.product_uom != self.product_uom:
                price_unit = bol.product_uom._compute_price(
                    bol.price_unit, self.product_uom)
            else:
                price_unit = bol.price_unit
            self.price_unit = price_unit
            if bol.taxes_id:
                self.tax_id = bol.taxes_id
        else:
            self._compute_tax_id()
            self.with_context(skip_contracted_find=True).product_uom_change()

    @api.constrains('product_id')
    def check_product_id(self):
        for line in self:
            if line.contracted_order_line and \
                    line.product_id != line.contracted_order_line.product_id:
                raise ValidationError(_(
                    'The product in the contracted order and in the '
                    'sales order must match'))

    @api.constrains('currency_id')
    def check_currency(self):
        for line in self:
            if line.contracted_order_line:
                if line.currency_id != \
                        line.contracted_order_line.order_id.currency_id:
                    raise ValidationError(_(
                        'The currency of the contracted order must match with '
                        'that of the sale order.'))
