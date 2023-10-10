# -*- coding: utf-8 -*-
# Part of Konos. See LICENSE file for full copyright and licensing details.


import logging
import requests
import json
from dateutil import parser
from datetime import datetime
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, exceptions, _
from calendar import monthrange

_logger = logging.getLogger(__name__)


class AccountBankStatementFintocWizard(models.TransientModel):
    _name = "account.bank.statement.fintoc.wizard"
    _description = "Modulo para integracion con Fintoc"

    bank_id = fields.Many2one('res.bank', default=lambda self:
    self.env['account.bank.statement'].browse(self.env.context.get('active_id', None)).journal_id.bank_id.id)
    bank_account_id = fields.Many2one('res.partner.bank', default=lambda self:
    self.env['account.bank.statement'].browse(self.env.context.get('active_id', None)).journal_id.bank_account_id)
    date_start = fields.Date('Date start')
    date_end = fields.Date('Date end')

    def import_online_mov(self):
        res = False
        now = datetime.now()
        years = now.year
        years_format = str(years)
        values = {}
        bank_statement = self.env['account.bank.statement'].browse(self.env.context.get('active_id', None))
        if bank_statement.line_ids:
            bank_statement.line_ids.unlink()
        bank_account_id = bank_statement.journal_id.bank_account_id.acc_number
        link_token = bank_statement.journal_id.link_token
        secret_key = self.env.user.company_id.secret_key
        if not secret_key:
            raise ValidationError(_("Debe configurar un Secret Key FINTOC para la empresa"))
        if not bank_account_id:
            raise ValidationError(_("Debe configurar una cuenta bancaria en el diario de banco"))
        if not link_token:
            raise ValidationError(_("Debe configurar un FINTOC Link Token en el diario de banco"))
        date_start = '&since=' + self.date_start.strftime("%Y-%m-%dT00:00:00Z") if self.date_start else ''
        date_end = '&until=' + self.date_end.strftime("%Y-%m-%dT00:00:00Z") if self.date_end else ''

        headers = {
            "accept": "application/json",
            "Authorization": secret_key
        }

        url = "https://api.fintoc.com/v1/accounts?link_token=" + link_token
        response = requests.get(url, headers=headers)
        data = json.loads(response.text.encode('utf8'))
        if 'error' in data:
            raise ValidationError(_(data['error']['message']))
        for l in data:
            if l['number'] == bank_account_id:
                id_account = l['id']
                break
        url = "https://api.fintoc.com/v1/accounts/" + id_account + "/movements?link_token=" + \
              link_token + date_start + date_end + "&per_page=300"
        data = self.get_all_mov(headers, url)
        if 'error' in data:
            raise ValidationError(_(data['error']['message']))
        for l in data:
            values['date'] = parser.parse(l['post_date'])
            values['amount'] = l['amount']
            values['payment_ref'] = l['description']
            values['statement_id'] = bank_statement.id
            bank_statement.write({'line_ids': [(0, 0, values)]})

    def get_all_mov(self, headers, base_url):
        all_transactions = []
        next_url = base_url

        while next_url:
            response = requests.get(next_url, headers=headers)
            data = json.loads(response.text.encode('utf8'))

            # Obtener los movimientos bancarios de la respuesta actual y agregarlos a la lista
            transactions = data
            all_transactions.extend(transactions)

            # Verificar si hay una página siguiente
            next_url = None
            link_header = response.headers.get("Link")
            if link_header:
                links = link_header.split(", ")
                for link in links:
                    if "rel=\"next\"" in link:
                        next_url = link[link.index("<") + 1:link.index(">")]

        return all_transactions


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def import_online_mov(self):
        res = False
        values = {}
        now = datetime.now()
        y = now.year
        m = now.month
        d = monthrange(y, m-1)[1]
        date_start = fields.Datetime.to_datetime('%s-%s-%s' % (y, m-1, '01'))
        date_end = fields.Datetime.to_datetime('%s-%s-%s' % (y, m-1, d))
        bank_statement = self.env['account.bank.statement'].search([
            ('journal_id.type', '=', 'bank'),
            ('state', '=', 'open'),
            # ('date', '>=', date_start),
            # ('date', '<=', date_end)
        ])
        for bs in bank_statement:
            bank_account_id = bs.journal_id.bank_account_id.acc_number #"acc_jy4zKBZT1j4K5OMb"
            link_token = bs.journal_id.link_token #"link_Q62Rk5ViJlogLNn5_token_oxhRVdnQhUJm6XLx6D7A5cNJ"
            secret_key = self.env.user.company_id.secret_key #"sk_test_FLEAKwmFfou3Xe-Tjk7NjBLCqswQoa_o"
            if not secret_key:
                _logger.warning(_("Debe configurar un Secret Key FINTOC para la empresa"))
                continue
            if not bank_account_id:
                _logger.warning(_("Debe configurar una cuenta bancaria en el diario de banco"))
                continue
            if not link_token:
                _logger.warning(_("Debe configurar un FINTOC Link Token en el diario de banco"))
                continue
            date_start = "&since=%s-%s-%sT00:00:00Z" % (bs.date.year, str(bs.date.month).zfill(2), '01')
            date_end = "&until=%s-%s-%sT00:00:00Z" % (bs.date.year, str(bs.date.month).zfill(2), str(bs.date.day).zfill(2))

            headers = {
                "accept": "application/json",
                "Authorization": secret_key
            }

            # Consultamos las cuentas relacionadas al Banco
            url = "https://api.fintoc.com/v1/accounts?link_token=" + link_token
            response = requests.get(url, headers=headers)
            data = json.loads(response.text.encode('utf8'))
            # print(data)
            if 'error' in data:
                raise ValidationError(_(data['error']['message']))
            for l in data:
                if l['number'] == bank_account_id:
                    id_account = l['id']
                    break

            # Consultamos los movimientos por la cuenta bancaria
            url = "https://api.fintoc.com/v1/accounts/" + id_account + "/movements?link_token=" + \
                  link_token + date_start + date_end #+ "&per_page=300"
            response = requests.get(url, headers=headers)

            data = json.loads(response.text.encode('utf8'))
            print('URL: ', url)
            print(data)
            if 'error' in data:
                raise ValidationError(_(data['error']['message']))
            if len(data) > 0:
                if bs.line_ids:
                    bs.line_ids.unlink()
                for l in data:
                    values['date'] = parser.parse(l['post_date'])
                    values['amount'] = l['amount']
                    values['payment_ref'] = l['description']
                    values['statement_id'] = bs.id
                    bs.write({'line_ids': [(0, 0, values)]})
        # return True

    #     'https://api.fintoc.com/v1/accounts/acc_qNDRKQeTYAePKvpn/movements?link_token=link_Y75EXAKiEYzwkwR8_token_bjtwNRrnQ7Jv53QQzxArS4G7&since=2022-9-01T00:00:00Z&since=2022-9-30T00:00:00Z'
    #      https://api.fintoc.com/v1/accounts/acc_qNDRKQeTYAePKvpn/movements?link_token=link_Y75EXAKiEYzwkwR8_token_bjtwNRrnQ7Jv53QQzxArS4G7&since=2022-10-01T00%3A00%3A00Z&until=2022-10-30T00%3A00%3A00Z
    def cron_import_online_mov(self):
        self.with_context(cron_skip_connection_errs=True).import_online_mov()
        self.env.cr.commit()