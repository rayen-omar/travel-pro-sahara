# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = "account.move"

    reservation_id = fields.Many2one(
        "travel_pro_sahara.reservation",
        string="Réservation Source",
        readonly=True,
    )
    @api.model_create_multi
    def create(self, vals_list):
        journal_inv = self.env['account.journal'].search([('code', '=', 'INV')], limit=1)
        if journal_inv:
            for vals in vals_list:
                if vals.get('move_type') == 'out_invoice' and not vals.get('journal_id'):
                    vals['journal_id'] = journal_inv.id
        return super().create(vals_list)
