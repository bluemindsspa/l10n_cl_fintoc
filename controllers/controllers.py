# -*- coding: utf-8 -*-
# from odoo import http


# class L10nClFintoc(http.Controller):
#     @http.route('/l10n_cl_fintoc/l10n_cl_fintoc/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/l10n_cl_fintoc/l10n_cl_fintoc/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('l10n_cl_fintoc.listing', {
#             'root': '/l10n_cl_fintoc/l10n_cl_fintoc',
#             'objects': http.request.env['l10n_cl_fintoc.l10n_cl_fintoc'].search([]),
#         })

#     @http.route('/l10n_cl_fintoc/l10n_cl_fintoc/objects/<model("l10n_cl_fintoc.l10n_cl_fintoc"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('l10n_cl_fintoc.object', {
#             'object': obj
#         })
