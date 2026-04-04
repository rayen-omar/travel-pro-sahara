# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    reservation_id = fields.Many2one(
        "travel_pro_sahara.reservation",
        string="الحجز المرتبط",
        readonly=True
    )
    
    # Champs relais pour l'affichage de l'interface personnalisée
    voyage_id_from_reservation = fields.Many2one(
        related="reservation_id.voyage_id",
        string="الرحلة",
        readonly=True
    )
    reservation_passager_ids_related = fields.One2many(
        related="reservation_id.reservation_passager_ids",
        string="الركاب والمشاركين",
        readonly=True
    )
    reservation_hotel_ids_related = fields.One2many(
        related="reservation_id.reservation_hotel_ids",
        string="الفنادق",
        readonly=True
    )
    reservation_transport_ids_related = fields.One2many(
        related="reservation_id.reservation_transport_ids",
        string="النقل والارشاد",
        readonly=True
    )
