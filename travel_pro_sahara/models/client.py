# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = "res.partner"

    nom = fields.Char(string="اللقب")
    prenom = fields.Char(string="الاسم الأول")
    numero_cin = fields.Char(string="رقم بطاقة التعريف")
    numero_passport = fields.Char(string="رقم جواز السفر")

    @api.onchange('nom', 'prenom')
    def _onchange_name_parts(self):
        if self.nom or self.prenom:
            self.name = " ".join(filter(None, [self.prenom or "", self.nom or ""])).strip()
