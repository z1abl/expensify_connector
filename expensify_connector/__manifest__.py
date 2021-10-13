# -*- coding: utf-8 -*-
{
    'name': "Expensify connector",

    'summary': """
        Expensify connector""",

    'description': """
       Import expenses from Expensify.
    """,

    'author': "Edward",
    'website': "http://odoo.apps-script.ninja",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    'license': 'OPL-1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_expense','product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/expensify.hr_expense.hr_expense_view_form.xml',
        'views/expensify.res_config_settings_view_form.xml',
        'views/schedulers.xml',
        'data/data.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'images': ['static/description/images/api_tokens_700.png',
               'static/description/images/expense_form_view_700.png',
               'static/description/images/expensify_125.png',
               'static/description/images/expensify_expenses_700.png',
               'static/description/images/expensify_form_view_700.png',
               'static/description/images/expensify_menu_700.png',
               'static/description/images/hr_expenses_700.png',
               'static/description/images/main_screenshot.png',
               'static/description/images/schedule_expensify_700.png',
               'static/description/images/install_module_700.png',
               'static/description/images/settings_700.png']
}
