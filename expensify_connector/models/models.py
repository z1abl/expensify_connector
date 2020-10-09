# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.http import request

import logging
import json
import requests
import csv


_logger = logging.getLogger(__name__)

# api-docs: https://integrations.expensify.com/Integration-Server/doc/
# expensify-specific settings should be set manually in
# Settings -> General settings -> Expensify
endpoint = 'https://integrations.expensify.com/Integration-Server/ExpensifyIntegrations'

# gets expenses from Expensify
def get_data(user_id,secret):
    request_job_description = {
        "type": "download",
        "credentials": {
            "partnerUserID": user_id,
            "partnerUserSecret": secret
        },
        "fileName": generate_report(user_id,secret).decode('utf-8'),
        "fileSystem": "integrationServer"
    }

    data = {'requestJobDescription': json.dumps(request_job_description).encode('utf-8')}
    response = requests.request('POST',endpoint, data=data).content.decode('utf-8')
    # data are returned in csv format
    splitted_response = response.strip().split('\n')
    return splitted_response

def generate_report(user_id,secret):
    start_date = request.env['ir.config_parameter'].sudo().get_param('expensify_start_date')
    request_job_description = {
        "type": "file",
        "credentials": {
            "partnerUserID": user_id,
            "partnerUserSecret": secret
        },
        "onReceive": {
            "immediateResponse": [
                "returnRandomFileName"
            ]
        },
        "inputSettings": {
            "type": "combinedReportData",
            "filters": {
                "startDate": f'{start_date}'
            }
        },
        "outputSettings": {
            "fileExtension": "csv"
        }
    }

    template = '''<#if addHeader>Id,Timestamp,Merchant,Amount,Category,MCC,Tag,Description,Reimbursable,Currency,Receipt,ReceiptURL,ReceiptID,Status,Comment,ReportId,ReportName,ReportStatus,ReportUrl,Submitted to,Submitted from\n<#t>
    </#if>
    <#list reports as report>
    <#list report.transactionList as expense>
    <#if expense.modifiedMerchant?has_content>
    <#assign merchant = expense.modifiedMerchant>
    <#else>
    <#assign merchant = expense.merchant>
    </#if>
    <#if expense.convertedAmount?has_content>
    <#assign amount = expense.convertedAmount/100>
    <#elseif expense.modifiedAmount?has_content>
    <#assign amount = expense.modifiedAmount/100>
    <#else>
    <#assign amount = expense.amount/100>
    </#if>
    <#if expense.modifiedCreated?has_content>
    <#assign created = expense.modifiedCreated>
    <#else>
    <#assign id = expense.transactionID>
    <#assign created = expense.created>
    <#assign category = expense.category>
    <#assign mcc = expense.mcc>
    <#assign tag = expense.tag>
    <#assign description = expense.description>
    <#assign reimbursable = expense.reimbursable>
    <#assign currency = expense.currency>
    <#assign receipt = expense.receipt>
    <#assign receiptURL = expense.receiptObject.url>
    <#assign receiptID = expense.receiptID>
    <#assign status = expense.status>
    <#assign comment = expense.comment>
    </#if>
    ${id},<#t>
    ${created},<#t>
    ${merchant},<#t>
    ${amount},<#t>
    ${category},<#t>
    ${currency},<#t>
    ${receiptURL},<#t>
    ${receiptID},<#t>
    ${status},<#t>
    ${comment},<#t>
    ${report.reportID},<#t>
    ${report.reportName},<#t>
    ${report.status},<#t>
    ${report.url},<#t>
    ${report.accountEmail}<#t>\n
    </#list>
    </#list>'''

    data = {'requestJobDescription': json.dumps(request_job_description).encode('utf-8'),'template': template}
    response = requests.request('POST',endpoint, data=data)
    return response.content


class ExpensifyExpense(models.Model):
    _inherit = ['hr.expense']

    expensify_entity = fields.Many2one('expensify.entity', string='Expensify entity',ondelete='cascade')
    expensify = fields.Boolean(string='Expensify')
    rel_expense_id = fields.Char(related='expensify_entity.expense_id', string='Expense Id')
    rel_expense_date = fields.Datetime(related='expensify_entity.expense_date',string='Date')
    rel_expense_amount = fields.Float(related='expensify_entity.expense_amount',string='Amount')
    rel_receipt_id = fields.Char(related='expensify_entity.receipt_id',string='Receipt ID')
    rel_receipt_url = fields.Char(related='expensify_entity.receipt_url',string='Receipt url')
    rel_currency = fields.Char(related='expensify_entity.currency', string='Currency')
    rel_comment = fields.Text(related='expensify_entity.comment',string='Comment')
    rel_report = fields.Many2one(related='expensify_entity.report', string='Report')
    rel_report_id = fields.Char(related='expensify_entity.report.report_id', string='Report Id')
    rel_account_email = fields.Char(related='expensify_entity.report.account_email', string='Account email')
    rel_merchant = fields.Many2one(related='expensify_entity.merchant', string='Merchant')
    rel_category = fields.Many2one(related='expensify_entity.category', string='Category')




class ExpensifyEntity(models.Model):
    _name = 'expensify.entity'
    _rec_name = 'expense_id'
    _description = 'Expensify entity'

    expense_id = fields.Char(string='Expense Id')

    expense_date = fields.Datetime(string='Date')
    expense_amount = fields.Float(string='Amount')
    currency = fields.Char(string='Currency')
    receipt_id = fields.Char(string='Receipt ID')
    receipt_url = fields.Char(string='Receipt url')
    comment = fields.Text(string='Comment')
    report = fields.Many2one('expensify.report', string='Report')
    merchant = fields.Many2one('expensify.merchant', string='Merchant')
    category = fields.Many2one('expensify.category', string='Category')

    def import_from_expensify(self):
        user_id = request.env['ir.config_parameter'].sudo().get_param('expensify_user_id')
        secret = request.env['ir.config_parameter'].sudo().get_param('expensify_secret')
        expensify_create_hr_expenses = request.env['ir.config_parameter'].sudo().get_param('expensify_create_hr_expenses')

        data = get_data(user_id,secret)
        csv_values = list(csv.reader(data))
        employees = {}
        for i, row in enumerate(csv_values[1:]):
            csv_expense_id = row[0]

            if not csv_expense_id:
                _logger.info(f'Expensify expense has no id')
                continue

            if self.env['expensify.entity'].search([('expense_id','=',csv_expense_id)]):
                _logger.info(f'Expensify record with id: {csv_expense_id} already exists')
                continue

            csv_expense_date = row[1]
            csv_merchant = row[2]
            csv_amount = row[3]
            csv_category = row[4]
            csv_currency = row[5]
            csv_receipt_url = row[6]
            csv_receipt_id = row[7]
            csv_status = row[8]
            csv_comment = row[9]
            csv_report_id = row[10]
            csv_report_name = row[11]
            csv_report_status = row[12]
            csv_report_url = row[13]
            csv_report_account_email = row[14]

            matched_report = self.env['expensify.report'].search([('name','=',csv_report_name)],limit=1)
            matched_merchant = self.env['expensify.merchant'].search([('name','=',csv_merchant)],limit=1)
            matched_category = self.env['expensify.category'].search([('name','=',csv_category)],limit=1)

            if matched_report:
                report = matched_report
            else:
                report = self.env['expensify.report'].create({
                    'name':csv_report_name,
                    'report_id':csv_report_id,
                    'url':csv_report_url,
                    'account_email':csv_report_account_email
                })

            if matched_merchant:
                merchant = matched_merchant
            else:
                merchant = self.env['expensify.merchant'].create({
                    'name':csv_merchant
                })

            if matched_category:
                category = matched_category
            else:
                category = self.env['expensify.category'].create({
                    'name':csv_category
                })


            expensify_entity = self.env['expensify.entity'].create({
                'expense_id':csv_expense_id,
                'expense_date':csv_expense_date,
                'expense_amount':csv_amount,
                'receipt_id':csv_receipt_id,
                'receipt_url':csv_receipt_url,
                'currency': csv_currency,
                'comment':csv_comment,
                'report':report.id,
                'merchant':merchant.id,
                'category':category.id,
            })

            if expensify_create_hr_expenses:
                matched_employee_id = self.env['hr.employee'].search([('work_email', '=', csv_report_account_email)], limit=1).id
                if csv_report_account_email in employees:
                    employee_id = employees[csv_report_account_email]
                elif matched_employee_id:
                    employee_id = matched_employee_id
                    employees[csv_report_account_email] = matched_employee_id
                else:
                    employee_id = self.env.ref('expensify_connector.expensify_employee').id


                self.env['hr.expense'].create({
                    'name':csv_expense_id,
                    'expensify_entity':expensify_entity.id,
                    'employee_id':employee_id,
                    'quantity':1,
                    'unit_amount':csv_amount,
                    'product_id':self.env.ref('expensify_connector.expensify_product').id,
                    'expensify':True
                })


class ExpensifyReport(models.Model):
    _name = 'expensify.report'
    _description = 'Expensify report'

    report_id = fields.Char(string='Report ID')
    name = fields.Char(string='Report Name')
    url = fields.Char(string='Report url')
    account_email = fields.Char(string='Account email')


class ExpensifyMerchant(models.Model):
    _name = 'expensify.merchant'
    _description = 'Expensify merchant'

    name = fields.Char(string='Merchant')


class ExpensifyCategory(models.Model):
    _name = 'expensify.category'
    _description = 'Expensify category'

    name = fields.Char(string='Category')



