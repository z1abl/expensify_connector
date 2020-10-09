# -*- coding: utf-8 -*-
# from odoo import http


# class ExpensifyConnector(http.Controller):
#     @http.route('/expensify_connector/expensify_connector/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/expensify_connector/expensify_connector/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('expensify_connector.listing', {
#             'root': '/expensify_connector/expensify_connector',
#             'objects': http.request.env['expensify_connector.expensify_connector'].search([]),
#         })

#     @http.route('/expensify_connector/expensify_connector/objects/<model("expensify_connector.expensify_connector"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('expensify_connector.object', {
#             'object': obj
#         })
