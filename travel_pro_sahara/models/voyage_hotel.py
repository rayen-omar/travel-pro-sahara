# -*- coding: utf-8 -*-

from odoo import models, fields


class TravelProSaharaVoyageHotel(models.Model):
    _name = "travel_pro_sahara.voyage_hotel"
    _description = "Hôtel du voyage"

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
    nom_hotel = fields.Char(string="Nom de l'hôtel", required=True)
    telephone = fields.Char(string="Téléphone")
    adresse = fields.Char(string="Adresse")
    prix_nuit = fields.Float(string="Prix / nuit", digits="Product Price")
    check_in = fields.Date(string="Check-in")
    check_out = fields.Date(string="Check-out")
