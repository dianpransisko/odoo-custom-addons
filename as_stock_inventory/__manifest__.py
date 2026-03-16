{
    'name': 'AS Stock Inventory - Lokasi Rak',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Menambahkan informasi lokasi rak pada produk',
    'author': 'Dian Pransisko Harahap',
    'depends': ['stock'], # WAJIB karena kita mengedit Inventory
    'data': [
        'views/product_template_views.xml',
    ],
    'installable': True,
    'application': False,
}