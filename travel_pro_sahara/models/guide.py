# -*- coding: utf-8 -*-
from odoo import models, fields

class TravelProGuide(models.Model):
    _name = 'travel_pro_sahara.guide'
    _description = 'دليل المستخدم'

    name = fields.Char(string="العنوان", default="دليل البدء السريع")
