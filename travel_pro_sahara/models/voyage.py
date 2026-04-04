# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TravelProSaharaVoyage(models.Model):
    _name = "travel_pro_sahara.voyage"
    _description = "الرحلات"

    reference = fields.Char(
        string="المرجع",
        readonly=True,
        copy=False,
        default="New",
    )
    state = fields.Selection(
        [
            ("brouillon", "مسودة"),
            ("confirme", "مؤكد"),
            ("complet", "مكتمل"),
            ("annule", "ملغى"),
        ],
        string="الحالة",
        default="brouillon",
        required=True,
    )
    name = fields.Char(string="اسم الرحلة", required=True)

    @api.depends('reference', 'name')
    def _compute_display_name(self):
        for record in self:
            if record.reference and record.reference not in ("/", "New"):
                record.display_name = f"[{record.reference}] {record.name}"
            else:
                record.display_name = record.name
    type_voyage = fields.Selection(
        [
            ("touristique", "سياحي"),
            ("culturel", "ثقافي"),
            ("religieux", "ديني"),
        ],
        string="النوع",
        required=True,
        default="touristique",
    )
    lieu_depart = fields.Char(string="مكان الانطلاق")
    destination_ids = fields.One2many(
        "travel_pro_sahara.destination",
        "voyage_id",
        string="الوجهات",
        copy=True,
    )
    photo_voyage = fields.Binary(string="الصورة", attachment=True)
    date_debut = fields.Date(string="تاريخ البدء", required=True)
    date_fin = fields.Date(string="تاريخ الانتهاء", required=True)
    prix_adulte = fields.Float(string="سعر البالغ", digits="Product Price")
    prix_enfant = fields.Float(string="سعر الطفل", digits="Product Price")
    note = fields.Text(string="ملاحظات")

    reservation_count = fields.Integer(string="الحجوزات", compute="_compute_reservation_count")

    def _compute_reservation_count(self):
        for record in self:
            record.reservation_count = self.env['travel_pro_sahara.reservation'].search_count([('voyage_id', '=', record.id)])

    def action_view_reservations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'الحجوزات',
            'view_mode': 'list,form',
            'res_model': 'travel_pro_sahara.reservation',
            'domain': [('voyage_id', '=', self.id)],
            'context': {'default_voyage_id': self.id},
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("reference", "New") in ("/", "New"):
                vals["reference"] = self.env["ir.sequence"].next_by_code("travel_pro_sahara.voyage") or "New"
        return super().create(vals_list)

    @api.constrains("date_debut", "date_fin")
    def _check_dates(self):
        for record in self:
            if record.date_debut and record.date_fin and record.date_fin < record.date_debut:
                raise ValidationError("تاريخ الانتهاء يجب أن يكون بعد تاريخ البدء.")

    def action_confirmer(self):
        if self.reference in ("/", "New"):
            self.reference = self.env["ir.sequence"].next_by_code("travel_pro_sahara.voyage") or "New"
        self.write({"state": "confirme"})

    def action_complet(self):
        self.write({"state": "complet"})

    def action_annuler(self):
        self.write({"state": "annule"})

    def action_brouillon(self):
        self.write({"state": "brouillon"})
