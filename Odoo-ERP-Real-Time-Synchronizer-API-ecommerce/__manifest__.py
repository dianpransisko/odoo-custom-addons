{
    'name': 'e-commarce_integrated_odoo',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Integrasi stok dan order dengan Ecommerce Mock API',
    'author': 'Dian Pransisko Harahap',
    'depends': ['base', 'sale_management', 'stock', 'product'], # WAJIB ADA INI
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/settings_views.xml',
        'views/product_views.xml',
        'views/sale_order_views.xml',
        'views/ecommerce_menus.xml',
        'views/ecommerce_sync_log_views.xml',
    ],
    'installable': True,
    'application': True,
}