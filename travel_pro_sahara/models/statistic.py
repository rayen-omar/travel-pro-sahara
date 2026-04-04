# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TravelProSaharaStatistic(models.Model):
    _name = "travel_pro_sahara.statistic"
    _description = "لوحة التحكم والإحصائيات"

    name = fields.Char(string="الاسم", default="Travel Pro", readonly=True)

    # Indicateurs globaux (computés)
    total_clients = fields.Integer(string="عدد الزبائن", compute="_compute_statistics")
    total_voyages_actifs = fields.Integer(string="الرحلات النشطة", compute="_compute_statistics")
    total_reservations = fields.Integer(string="إجمالي الحجوزات", compute="_compute_statistics")
    
    # Indicateurs Financiers
    total_revenu = fields.Float(string="إجمالي الإيرادات", compute="_compute_statistics")
    total_encaisse = fields.Float(string="المبالغ المحصلة", compute="_compute_statistics")
    total_reste_apayer = fields.Float(string="المتبقي للدفع", compute="_compute_statistics")

    # Indicateurs Logistique
    total_hotel = fields.Integer(string="الفنادق", compute="_compute_statistics")
    total_restauration = fields.Integer(string="المطاعم", compute="_compute_statistics")
    total_guide = fields.Integer(string="المرشدين", compute="_compute_statistics")
    total_transport = fields.Integer(string="النقل", compute="_compute_statistics")

    last_refresh = fields.Datetime(string="آخر تحديث", default=fields.Datetime.now, readonly=True)

    @api.depends('last_refresh')
    def _compute_statistics(self):
        for record in self:
            # Clients
            record.total_clients = self.env['res.partner'].search_count([('customer_rank', '>', 0)])

            # Voyages actifs
            record.total_voyages_actifs = self.env['travel_pro_sahara.voyage'].search_count([
                ('state', 'in', ['confirme', 'complet'])
            ])

            # Réservations valides
            reservations = self.env['travel_pro_sahara.reservation'].search([
                ('state', 'not in', ['brouillon', 'annulee'])
            ])
            record.total_reservations = len(reservations)

            # Finances
            total_rev = sum(reservations.mapped('prix_calcule'))
            total_enc = sum(reservations.mapped('montant_paye'))
            record.total_revenu = total_rev
            record.total_encaisse = total_enc
            record.total_reste_apayer = total_rev - total_enc

            # Logistique
            record.total_hotel = self.env['travel_pro_sahara.voyage_hotel'].search_count([])
            record.total_restauration = self.env['travel_pro_sahara.voyage_restauration'].search_count([])
            record.total_guide = self.env['travel_pro_sahara.voyage_guide'].search_count([])
            record.total_transport = self.env['travel_pro_sahara.voyage_transport'].search_count([])

    def action_refresh(self):
        self.write({'last_refresh': fields.Datetime.now()})
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_open_clients(self):
        return {
            'name': 'الزبائن',
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'list,form',
            'domain': [('customer_rank', '>', 0)],
        }

    def action_open_voyages(self):
        return {
            'name': 'الرحلات',
            'type': 'ir.actions.act_window',
            'res_model': 'travel_pro_sahara.voyage',
            'domain': [('state', 'in', ['confirme', 'complet'])],
            'view_mode': 'list,form',
        }

    def action_open_reservations(self):
        return {
            'name': 'الحجوزات',
            'type': 'ir.actions.act_window',
            'res_model': 'travel_pro_sahara.reservation',
            'view_mode': 'list,form',
            'domain': [('state', 'not in', ['brouillon', 'annulee'])],
        }
