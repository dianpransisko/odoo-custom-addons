{
    'name': 'Modul Tambahan KTP',
    'version': '1.0',
    'category': 'Extra Tools',
    'summary': 'Menambahkan kolom KTP pada Master Partner',
    'author': 'Dian Pransisko Harahap',
    'depends': ['base'],      # Penting! Modul ini butuh modul 'base' (res_partner ada di sana)
    'data': [
        'security/ir.model.access.csv', #untuk hak akses wajib di atas view
        'views/res_partner_views.xml', #untuk view atau tampilan
    ],
    'installable': True,
    'application': True,
}