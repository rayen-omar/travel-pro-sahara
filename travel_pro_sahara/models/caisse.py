# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TravelProSaharaCaisse(models.Model):
    _name = "travel_pro_sahara.caisse"
    _description = "لوحة معلومات الصندوق العام"

    name = fields.Char(default="الصندوق العام", readonly=True)
    company_currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)

    # Filtres interactifs
    filter_journal_id = fields.Many2one("account.journal", string="تصفية اليومية", domain=[('type', 'in', ('bank', 'cash'))])
    filter_date_start = fields.Date(string="تاريخ البدء")
    filter_date_end = fields.Date(string="تاريخ الانتهاء")
    filter_partner_id = fields.Many2one("res.partner", string="تصفية الزبون")

    solde_especes = fields.Float(string="رصيد النقدي", compute="_compute_soldes")
    solde_banque = fields.Float(string="رصيد البنك", compute="_compute_soldes")
    solde_total = fields.Float(string="الرصيد الإجمالي", compute="_compute_soldes")

    payment_ids = fields.Many2many("account.payment", compute="_compute_payments")

    @api.depends("filter_journal_id", "filter_date_start", "filter_date_end", "filter_partner_id")
    def _compute_payments(self):
        for record in self:
            domain = [
                ('payment_type', '=', 'inbound'),
                '|',
                ('reconciled_invoice_ids.reservation_id', '!=', False),
                ('reconciled_bill_ids.reservation_id', '!=', False)
            ]
            if record.filter_journal_id:
                domain.append(('journal_id', '=', record.filter_journal_id.id))
            if record.filter_date_start:
                domain.append(('date', '>=', record.filter_date_start))
            if record.filter_date_end:
                domain.append(('date', '<=', record.filter_date_end))
            if record.filter_partner_id:
                domain.append(('partner_id', '=', record.filter_partner_id.id))
            record.payment_ids = self.env['account.payment'].search(domain, order="date desc, id desc", limit=100)

    @api.depends("filter_journal_id", "filter_date_start", "filter_date_end", "filter_partner_id")
    def _compute_soldes(self):
        for record in self:
            domain = [
                ('payment_type', '=', 'inbound'),
                ('state', 'not in', ('draft', 'cancel', 'rejected')),
                '|',
                ('reconciled_invoice_ids.reservation_id', '!=', False),
                ('reconciled_bill_ids.reservation_id', '!=', False)
            ]
            if record.filter_journal_id:
                domain.append(('journal_id', '=', record.filter_journal_id.id))
            if record.filter_date_start:
                domain.append(('date', '>=', record.filter_date_start))
            if record.filter_date_end:
                domain.append(('date', '<=', record.filter_date_end))
            if record.filter_partner_id:
                domain.append(('partner_id', '=', record.filter_partner_id.id))

            all_payments = self.env['account.payment'].search(domain)
            
            especes = sum(p.amount for p in all_payments if p.journal_id.type == 'cash')
            banque = sum(p.amount for p in all_payments if p.journal_id.type == 'bank')
            
            record.solde_especes = especes
            record.solde_banque = banque
            record.solde_total = especes + banque

    def action_nouveau_paiement(self):
        return {
            'name': 'دفع جديد مستلم',
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'form',
            'context': {'default_payment_type': 'inbound'},
            'target': 'current'
        }

    def action_open_full_history(self):
        domain = [
            ('payment_type', '=', 'inbound'),
            ('state', 'not in', ('draft', 'cancel', 'rejected')),
            '|',
            ('reconciled_invoice_ids.reservation_id', '!=', False),
            ('reconciled_bill_ids.reservation_id', '!=', False)
        ]
        return {
            'name': 'سجل المدفوعات الكامل',
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'list,form,pivot,graph',
            'domain': domain,
            'context': {'search_default_inbound_filter': 1},
            'target': 'current'
        }

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    force_paid = fields.Boolean(string="فرض كمدفوع", default=False)

    @api.depends('move_id.name', 'is_reconciled', 'is_matched', 'move_id.state', 'force_paid')
    def _compute_state(self):
        super()._compute_state()
        for pay in self:
            if pay.state == 'in_process' and pay.force_paid:
                pay.state = 'paid'

    def action_force_paid(self):
        for pay in self:
            pay.force_paid = True
