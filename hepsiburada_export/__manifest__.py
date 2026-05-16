{
    'name': 'Hepsiburada Export',
    'version': '19.0.1.0.0',
    'summary': 'Export products from Odoo to Hepsiburada marketplace',
    'description': """
        Export Odoo products to Hepsiburada via the official import API.
        Supports multi-product JSON payload building, multipart/form-data upload
        and tracking-code retrieval.
    """,
    'author': 'Faruk',
    'category': 'Inventory/Inventory',
    'license': 'LGPL-3',
    'depends': ['product', 'stock', 'base_setup'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/hepsiburada_product_views.xml',
        'views/hepsiburada_export_wizard_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
