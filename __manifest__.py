# -*- coding: utf-8 -*-
{
    'name': "Integracion con Fintoc",

    'summary': """
        Integración con Fintoc""",

    'description': """
        Conecta las cuentas bancarias para importar de manera automática los extractos bancarios y poder realizar la conciliación bancaria
    """,

    'author': "Blueminds",
    'website': "http://www.blueminds.cl",
    'contributors': ["Boris Silva <silvaboris@gmail.com>"],

    'category': 'Account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_company_view.xml',
        'views/account_view.xml',
        'wizard/bank_statement_view.xml',
        'data/cron.xml',
    ],
}
