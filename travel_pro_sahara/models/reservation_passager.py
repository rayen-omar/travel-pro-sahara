# -*- coding: utf-8 -*-

from odoo import models, fields


class TravelProSaharaReservationPassager(models.Model):
    _name = "travel_pro_sahara.reservation_passager"
    _description = "Passager (réservation)"

    reservation_id = fields.Many2one(
        "travel_pro_sahara.reservation",
        string="Réservation",
        required=True,
        ondelete="cascade",
    )
    nom_passager = fields.Char(string="Nom du passager", required=True)
    type_place = fields.Selection(
        [
            ("adulte", "Adulte"),
            ("enfant", "Enfant"),
        ],
        string="Type",
        required=True,
        default="adulte",
    )
    age = fields.Integer(string="Âge")
