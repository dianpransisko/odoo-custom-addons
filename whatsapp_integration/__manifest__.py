{
    'name': 'WhatsApp Integration',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Kirim pesan WhatsApp dari Sales Order',
    'author': 'Dian Pransisko Harahap',
    'depends': ['sale', 'account'], 
    'data': [
        # Kita nonaktifkan config_views dulu agar tidak ada error "File Not Found"
        # 'views/whatsapp_config_views.xml', 
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': True,
}