# -*- coding: utf-8 -*-

from odoo import models, fields


class TravelProSaharaVoyageRestauration(models.Model):
    _name = "travel_pro_sahara.voyage_restauration"
    _description = "Restauration du voyage"

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
    nom_restaurant = fields.Char(string="Nom du restaurant", required=True)
    adresse = fields.Char(string="Adresse")
    type_repas = fields.Selection(
        [
            ("petit_dejeuner", "Petit-déjeuner"),
            ("dejeuner", "Déjeuner"),
            ("diner", "Dîner"),
            ("autre", "Autre"),
        ],
        string="Type de repas",
        required=True,
        default="dejeuner",
    )
    prix = fields.Float(string="Prix", digits="Product Price")
