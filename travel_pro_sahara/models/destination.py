# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TravelProSaharaDestination(models.Model):
    _name = "travel_pro_sahara.destination"
    _description = "Destination (étape d'un voyage)"

    voyage_id = fields.Many2one(
        "travel_pro_sahara.voyage",
        string="Voyage",
        ondelete="cascade",
    )
    ville = fields.Char(string="Ville", required=True)
    pays = fields.Char(string="Pays", required=True)
    adresse = fields.Char(string="Adresse")
    code_postal = fields.Char(string="Code postal")
    sequence = fields.Integer(string="Ordre", default=10)

    @api.depends('ville')
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.ville or "بدون اسم"
