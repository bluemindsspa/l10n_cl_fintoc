# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


class ResCompany(models.Model):
    _inherit = "res.company"

    secret_key = fields.Char('Secret key')
