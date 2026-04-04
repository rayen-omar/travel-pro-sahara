# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TravelProSaharaVoyageEquipement(models.Model):
    _name = "travel_pro_sahara.voyage_equipement"
    _description = "المعدات"

    reservation_id = fields.Many2one(
        "travel_pro_sahara.reservation",
        string="الحجز",
        required=True,
        ondelete="cascade",
    )
    voyage_id = fields.Many2one(
        "travel_pro_sahara.voyage",
        related="reservation_id.voyage_id",
        string="الرحلة",
        store=True,
    )
    client_id = fields.Many2one(
        "res.partner",
        related="reservation_id.client_id",
        string="الزبون",
        store=True,
    )

    product_id = fields.Many2one(
        "product.product",
        string="المنتج",
        help="اختر منتجاً من القائمة أو أضف اسماً يدوياً أدناه"
    )

    nom_equipement = fields.Char(string="اسم المعدة / التفاصيل", required=True)
    quantite = fields.Integer(string="الكمية", default=1)
    prix = fields.Float(string="السعر", digits="Product Price")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.nom_equipement = self.product_id.display_name
            self.prix = self.product_id.lst_price
