# -*- coding: utf-8 -*-

from odoo import models, fields


class TravelProSaharaVoyageGuide(models.Model):
    _name = "travel_pro_sahara.voyage_guide"
    _description = "Guide du voyage"

    reservation_id = fields.Many2one(
        "travel_pro_sahara.reservation",
        string="Réservation",
        required=True,
        ondelete="cascade",
    )
    voyage_id = fields.Many2one(
        "travel_pro_sahara.voyage",
        related="reservation_id.voyage_id",
        string="Voyage",
        store=True,
    )
    client_id = fields.Many2one(
        "res.partner",
        related="reservation_id.client_id",
        string="Client",
        store=True,
    )
    nom_guide = fields.Char(string="Nom du guide", required=True)
    telephone = fields.Char(string="Téléphone")
    prix = fields.Float(string="Prix", digits="Product Price")
