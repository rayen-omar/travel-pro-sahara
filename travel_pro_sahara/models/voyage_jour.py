# -*- coding: utf-8 -*-

from odoo import models, fields


class TravelProSaharaVoyageJour(models.Model):
    _name = "travel_pro_sahara.voyage_jour"
    _description = "Programme jour par jour du voyage"
    _order = "numero_jour"

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
    numero_jour = fields.Integer(string="N° jour", required=True, default=1)
    destination_id = fields.Many2one(
        "travel_pro_sahara.destination",
        string="Destination",
        domain="[('voyage_id', '=', voyage_id)]",
    )
    description = fields.Text(string="Description")
