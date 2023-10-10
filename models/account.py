# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


class AccountJournal(models.Model):
    _inherit = "account.journal"

    link_token = fields.Char('Fintoc Link Token')
