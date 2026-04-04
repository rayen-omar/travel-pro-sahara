# -*- coding: utf-8 -*-

from odoo import models, fields


class TravelProSaharaVoyageTransport(models.Model):
    _name = "travel_pro_sahara.voyage_transport"
    _description = "Transport du voyage"

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
    type_transport = fields.Selection(
        [
            ("avion", "Avion"),
            ("train", "Train"),
            ("bus", "Bus"),
            ("voiture", "Voiture"),
            ("bateau", "Bateau"),
            ("autre", "Autre"),
        ],
        string="Type transport",
        required=True,
        default="bus",
    )
    prix = fields.Float(string="Prix", digits="Product Price")
    description = fields.Text(string="Description")
    jour = fields.Integer(string="Jour", default=1)
    lieu_depart = fields.Char(string="Lieu de départ")
    lieu_arrive = fields.Char(string="Lieu d'arrivée")
    sequence = fields.Integer(string="Ordre", default=10)
