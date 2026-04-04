# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class TravelProSaharaReservation(models.Model):
    _name = "travel_pro_sahara.reservation"
    _description = "الحجز"

    name = fields.Char(string="المرجع", copy=False, default="جديد")

    @api.depends('name', 'client_id')
    def _compute_display_name(self):
        for record in self:
            if record.name and record.name not in ("/", "جديد", "Nouveau"):
                record.display_name = f"{record.name} - {record.client_id.name}"
            else:
                record.display_name = f"حجز جديد - {record.client_id.name or 'جديد'}"
    state = fields.Selection(
        [
            ("brouillon", "مسودة"),
            ("confirmee", "مؤكدة"),
            ("facturee", "مفوترة"),
            ("payee", "مدفوعة"),
            ("annulee", "ملغاة"),
        ],
        string="الحالة",
        default="brouillon",
        required=True,
    )
    date_reservation = fields.Date(
        string="تاريخ الحجز",
        default=fields.Date.context_today,
    )
    client_id = fields.Many2one(
        "res.partner",
        string="الزبون",
        required=True,
    )
    voyage_id = fields.Many2one(
        "travel_pro_sahara.voyage",
        string="الرحلة",
        required=True,
    )
    reservation_passager_ids = fields.One2many(
        "travel_pro_sahara.reservation_passager",
        "reservation_id",
        string="الركاب",
        copy=True,
    )
    nombre_passagers = fields.Integer(
        string="عدد الركاب",
        default=1,
    )
    reservation_jour_ids = fields.One2many(
        "travel_pro_sahara.voyage_jour",
        "reservation_id",
        string="اليومية",
        copy=True,
    )
    reservation_transport_ids = fields.One2many(
        "travel_pro_sahara.voyage_transport",
        "reservation_id",
        string="النقل",
        copy=True,
    )
    reservation_hotel_ids = fields.One2many(
        "travel_pro_sahara.voyage_hotel",
        "reservation_id",
        string="الفنادق",
        copy=True,
    )
    reservation_restauration_ids = fields.One2many(
        "travel_pro_sahara.voyage_restauration",
        "reservation_id",
        string="المطاعم",
        copy=True,
    )
    reservation_guide_ids = fields.One2many(
        "travel_pro_sahara.voyage_guide",
        "reservation_id",
        string="المرشدين",
        copy=True,
    )
    reservation_equipement_ids = fields.One2many(
        "travel_pro_sahara.voyage_equipement",
        "reservation_id",
        string="المعدات",
        copy=True,
    )
    invoice_ids = fields.Many2many(
        "account.move",
        string="الفواتير",
    )
    quotation_ids = fields.Many2many(
        "sale.order",
        string="عروض الأسعار",
    )
    prix_calcule = fields.Float(
        string="إجمالي السعر",
        digits="Product Price",
        compute="_compute_prix_calcule",
        store=True,
    )
    montant_paye = fields.Float(
        string="المبلغ المدفوع",
        digits="Product Price",
        compute="_compute_montant_paye",
        store=True,
    )
    reste_a_payer = fields.Float(
        string="المتبقي للدفع",
        digits="Product Price",
        compute="_compute_reste_a_payer",
        store=True,
    )
    is_paid = fields.Boolean(string="تم الدفع", compute="_compute_is_paid", store=True)
    is_invoiced = fields.Boolean(string="تمت الفوترة", compute="_compute_is_invoiced", store=True)
    
    mode_paiement = fields.Selection(
        [
            ("especes", "نقداً"),
            ("cheque", "شيك"),
            ("carte", "بطاقة"),
            ("virement", "تحويل بنكي"),
        ],
        string="طريقة الدفع",
    )
    notes = fields.Text(string="ملاحظات")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "جديد") in ("/", "جديد", "Nouveau", False, ""):
                vals["name"] = self.env["ir.sequence"].sudo().next_by_code("travel_pro_sahara.reservation") or "جديد"
        return super().create(vals_list)

    def write(self, vals):
        if "name" in vals and vals.get("name") in ("/", "جديد", "Nouveau", False, ""):
            vals["name"] = self.env["ir.sequence"].sudo().next_by_code("travel_pro_sahara.reservation") or "جديد"
        elif not self.name or self.name in ("/", "جديد", "Nouveau"):
            if "name" not in vals:
                vals["name"] = self.env["ir.sequence"].sudo().next_by_code("travel_pro_sahara.reservation") or "جديد"
        return super().write(vals)

    @api.depends(
        "reservation_passager_ids.type_place", "reservation_passager_ids",
        "voyage_id.prix_adulte", "voyage_id.prix_enfant", "nombre_passagers",
        "reservation_transport_ids.prix",
        "reservation_hotel_ids.prix_nuit", "reservation_hotel_ids.check_in", "reservation_hotel_ids.check_out",
        "reservation_restauration_ids.prix",
        "reservation_guide_ids.prix",
        "reservation_equipement_ids.prix", "reservation_equipement_ids.quantite"
    )
    def _compute_prix_calcule(self):
        for record in self:
            total = 0.0
            if record.voyage_id:
                if record.reservation_passager_ids:
                    for line in record.reservation_passager_ids:
                        if line.type_place == "adulte":
                            total += record.voyage_id.prix_adulte or 0
                        else:
                            total += record.voyage_id.prix_enfant or 0
                else:
                    total += (record.voyage_id.prix_adulte or 0) * record.nombre_passagers
            total += sum(record.reservation_transport_ids.mapped('prix'))
            for hotel in record.reservation_hotel_ids:
                nuits = 1
                if hotel.check_in and hotel.check_out:
                    delta = (hotel.check_out - hotel.check_in).days
                    nuits = delta if delta > 0 else 1
                total += (hotel.prix_nuit or 0) * nuits
            total += sum(record.reservation_restauration_ids.mapped('prix'))
            total += sum(record.reservation_guide_ids.mapped('prix'))
            for equip in record.reservation_equipement_ids:
                total += (equip.prix or 0) * (equip.quantite or 1)
            record.prix_calcule = total

    @api.depends("invoice_ids.payment_state", "invoice_ids.amount_total", "invoice_ids.amount_residual")
    def _compute_montant_paye(self):
        for record in self:
            paid = 0.0
            for inv in record.invoice_ids:
                if inv.state == 'posted':
                    paid += (inv.amount_total - inv.amount_residual)
            record.montant_paye = paid

    @api.depends("prix_calcule", "montant_paye")
    def _compute_reste_a_payer(self):
        for record in self:
            record.reste_a_payer = (record.prix_calcule or 0) - (record.montant_paye or 0)

    @api.depends("reste_a_payer", "prix_calcule")
    def _compute_is_paid(self):
        for record in self:
            record.is_paid = record.prix_calcule > 0 and record.reste_a_payer <= 0

    @api.depends("invoice_ids")
    def _compute_is_invoiced(self):
        for record in self:
            record.is_invoiced = bool(record.invoice_ids)

    auto_state_updater = fields.Boolean(compute="_compute_auto_state", store=True)

    @api.depends("is_paid", "is_invoiced")
    def _compute_auto_state(self):
        for record in self:
            if record.state not in ('brouillon', 'annulee'):
                if record.is_paid:
                    record.state = 'payee'
                elif record.is_invoiced and record.state != 'payee':
                    record.state = 'facturee'
            record.auto_state_updater = True

    invoice_count = fields.Integer(string="عدد الفواتير", compute="_compute_counts")
    quotation_count = fields.Integer(string="عدد عروض الأسعار", compute="_compute_counts")

    @api.depends("invoice_ids", "quotation_ids")
    def _compute_counts(self):
        for record in self:
            record.invoice_count = len(record.invoice_ids)
            record.quotation_count = len(record.quotation_ids)

    def action_view_invoices(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'الفواتير',
            'view_mode': 'list,form',
            'res_model': 'account.move',
            'domain': [('id', 'in', self.invoice_ids.ids)],
            'context': {
                'default_move_type': 'out_invoice',
                'default_partner_id': self.client_id.id,
                'default_reservation_id': self.id,
            },
        }

    def action_view_quotations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'عروض الأسعار',
            'view_mode': 'list,form',
            'res_model': 'sale.order',
            'domain': [('id', 'in', self.quotation_ids.ids)],
            'context': {
                'default_partner_id': self.client_id.id,
                'default_reservation_id': self.id,
            },
        }

    def _get_default_sale_product(self):
        product = self.env['product.product'].search([('name', '=', 'خدمة سفر')], limit=1)
        if not product:
            product = self.env['product.product'].create({
                'name': 'خدمة سفر',
                'type': 'service',
                'lst_price': 0.0,
            })
        return product

    def action_create_invoice(self):
        self.ensure_one()
        product = self._get_default_sale_product()
        invoice_lines = []
        if self.voyage_id:
            if self.reservation_passager_ids:
                for passager in self.reservation_passager_ids:
                    prix = self.voyage_id.prix_adulte if passager.type_place == "adulte" else self.voyage_id.prix_enfant
                    invoice_lines.append((0, 0, {
                        'product_id': product.id,
                        'name': f"الرحلة: {self.voyage_id.name} - الراكب ({passager.nom_passager})",
                        'quantity': 1,
                        'price_unit': prix or 0.0,
                    }))
            elif self.nombre_passagers > 0:
                invoice_lines.append((0, 0, {
                    'product_id': product.id,
                    'name': f"الرحلة: {self.voyage_id.name} - {self.nombre_passagers} راكب",
                    'quantity': self.nombre_passagers,
                    'price_unit': self.voyage_id.prix_adulte or 0.0,
                }))
        for transport in self.reservation_transport_ids:
            if transport.prix:
                invoice_lines.append((0, 0, {
                    'product_id': product.id,
                    'name': f"النقل ({transport.type_transport})",
                    'quantity': 1,
                    'price_unit': transport.prix,
                }))
        for hotel in self.reservation_hotel_ids:
            if hotel.prix_nuit:
                qty = 1
                if hotel.check_in and hotel.check_out:
                    delta = (hotel.check_out - hotel.check_in).days
                    qty = delta if delta > 0 else 1
                invoice_lines.append((0, 0, {
                    'product_id': product.id,
                    'name': f"الفندق: {hotel.nom_hotel}",
                    'quantity': qty,
                    'price_unit': hotel.prix_nuit,
                }))
        for resto in self.reservation_restauration_ids:
            if resto.prix:
                invoice_lines.append((0, 0, {
                    'product_id': product.id,
                    'name': f"المطعم: {resto.nom_restaurant}",
                    'quantity': 1,
                    'price_unit': resto.prix,
                }))
        for guide in self.reservation_guide_ids:
            if guide.prix:
                invoice_lines.append((0, 0, {
                    'product_id': product.id,
                    'name': f"المرشد: {guide.nom_guide}",
                    'quantity': 1,
                    'price_unit': guide.prix,
                }))
        for equip in self.reservation_equipement_ids:
            if equip.prix:
                invoice_line_vals = {
                    'product_id': equip.product_id.id if equip.product_id else product.id,
                    'name': f"المعدات: {equip.nom_equipement}",
                    'quantity': equip.quantite or 1,
                    'price_unit': equip.prix,
                }
                invoice_lines.append((0, 0, invoice_line_vals))
        
        if not invoice_lines:
            raise UserError("لا يوجد أي عنصر قابل للفواترة في هذا الحجز.")
            
        journal_inv = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        vals = {
            'move_type': 'out_invoice',
            'partner_id': self.client_id.id,
            'reservation_id': self.id,
            'ref': f"حجز {self.name}",
            'invoice_date': fields.Date.context_today(self),
            'invoice_line_ids': invoice_lines,
        }
        if journal_inv:
            vals['journal_id'] = journal_inv.id
        invoice = self.env['account.move'].create(vals)
        self.write({'invoice_ids': [(4, invoice.id)]})
        return {
            'type': 'ir.actions.act_window',
            'name': f'الفاتورة - {self.name}',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
            'target': 'current',
        }

    def action_create_quotation(self):
        self.ensure_one()
        product = self._get_default_sale_product()
        order_lines = []
        
        if self.voyage_id:
            order_lines.append((0, 0, {
                'product_id': product.id,
                'name': f"الرحلة: {self.voyage_id.name}",
                'product_uom_qty': self.nombre_passagers,
                'price_unit': self.voyage_id.prix_adulte or 0.0,
            }))

        for transport in self.reservation_transport_ids:
            if transport.prix:
                order_lines.append((0, 0, {
                    'product_id': product.id,
                    'name': f"النقل ({transport.type_transport}) - {transport.lieu_depart} ➔ {transport.lieu_arrive}",
                    'product_uom_qty': 1,
                    'price_unit': transport.prix,
                }))

        for hotel in self.reservation_hotel_ids:
            if hotel.prix_nuit:
                nuits = 1
                if hotel.check_in and hotel.check_out:
                    delta = (hotel.check_out - hotel.check_in).days
                    nuits = delta if delta > 0 else 1
                order_lines.append((0, 0, {
                    'product_id': product.id,
                    'name': f"إقامة فندق: {hotel.nom_hotel}",
                    'product_uom_qty': nuits,
                    'price_unit': hotel.prix_nuit,
                }))

        for equip in self.reservation_equipement_ids:
            if equip.prix:
                vals = {
                    'product_id': equip.product_id.id if equip.product_id else product.id,
                    'name': f"المعدات: {equip.nom_equipement}",
                    'product_uom_qty': equip.quantite or 1,
                    'price_unit': equip.prix,
                }
                order_lines.append((0, 0, vals))

        vals = {
            'partner_id': self.client_id.id,
            'reservation_id': self.id,
            'order_line': order_lines,
        }
        order = self.env['sale.order'].create(vals)
        self.write({'quotation_ids': [(4, order.id)]})
        
        # Si la réservation est déjà confirmée, confirmer l'ordre de vente (le transformer en BC)
        if self.state in ('confirmee', 'facturee', 'payee'):
            order.action_confirm()

        return {
            'type': 'ir.actions.act_window',
            'name': f'عرض سعر/أمر بيع - {self.name}',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': order.id,
            'target': 'current',
        }

    def action_confirmer(self):
        self.ensure_one()
        if self.name in ("/", "جديد", "Nouveau", False, ""):
            self.name = self.env["ir.sequence"].sudo().next_by_code("travel_pro_sahara.reservation") or "جديد"
        self.write({"state": "confirmee"})
        
        # Confirmer automatiquement les devis liés pour les transformer en Bons de commande (BC)
        for order in self.quotation_ids:
            if order.state in ('draft', 'sent'):
                order.action_confirm()

    def action_annuler(self):
        self.write({"state": "annulee"})

    def action_remettre_brouillon(self):
        self.write({"state": "brouillon"})
