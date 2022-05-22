# -*- encoding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError, ValidationError

import logging

class BolsonBolson(models.Model):
    _name = 'bolson.bolson'
    _description = 'Bolson de facturas y cheques'
    _order = 'fecha desc'

    fecha = fields.Date(string="Fecha", required=True)
    name = fields.Char(string="Descripcion", required=True)
    facturas = fields.One2many("account.move", "bolson_id", string="Facturas")
    cheques = fields.One2many("account.payment", "bolson_id", string="Cheques")
    company_id = fields.Many2one("res.company", string="Company", required=True, default=lambda self: self.env.user.company_id.id)
    diario = fields.Many2one("account.journal", string="Diario", required=True)
    asiento = fields.Many2one("account.move", string="Asiento")
    usuario_id = fields.Many2one("res.users", string="Usuario")
    cuenta_desajuste = fields.Many2one("account.account", string="Cuenta de desajuste")

    def conciliar(self):
        for rec in self:
            lineas = []

            total = 0
            for f in rec.facturas:
                logging.warn(f.name)
                logging.warn(f.amount_total)
                for l in f.line_ids:
                    if l.account_id.reconcile:
                        if not l.reconciled:
                            total += l.credit - l.debit
                            lineas.append(l)
                            logging.warn(l.credit - l.debit)
                        else:
                            raise UserError('La factura %s ya esta conciliada' % (f.number))

            for c in rec.cheques:
                logging.warn(c.name)
                logging.warn(c.amount)
                for l in c.line_ids:
                    if l.account_id.reconcile:
                        if not l.reconciled :
                            total -= l.debit - l.credit
                            lineas.append(l)
                            logging.warn(l.debit - l.credit)
                        else:
                            raise UserError('El cheque %s ya esta conciliado' % (c.name))

            if round(total) != 0 and not rec.cuenta_desajuste:
                raise UserError('El total de las facturas no es igual al total de los cheques y los extractos')

            pares = []
            nuevas_lineas = []
            for linea in lineas:
                nuevas_lineas.append((0, 0, {
                    'name': linea.name,
                    'debit': linea.credit,
                    'credit': linea.debit,
                    'account_id': linea.account_id.id,
                    'partner_id': linea.partner_id.id,
                    'journal_id': rec.diario.id,
                    'date_maturity': rec.fecha,
                }))

            if total != 0:
                nuevas_lineas.append((0, 0, {
                    'name': 'Diferencial en ' + rec.name,
                    'debit': -1 * total if total < 0 else 0,
                    'credit': total if total > 0 else 0,
                    'account_id': rec.cuenta_desajuste.id,
                    'date_maturity': rec.fecha,
                }))

            move = self.env['account.move'].create({
                'line_ids': nuevas_lineas,
                'ref': rec.name,
                'date': rec.fecha,
                'journal_id': rec.diario.id,
            });

            move.post()
            
            indice = 0
            invertidas = move.line_ids[::-1]
            for linea in lineas:
                par = linea | invertidas[indice]
                par.reconcile()
                indice += 1

            
            self.write({'asiento': move.id})

        return True

    def cancelar(self):
        for rec in self:
            for l in rec.asiento.line_ids:
                if l.reconciled:
                    l.remove_move_reconcile()
            rec.asiento.button_cancel()
            rec.asiento.unlink()

        return True
