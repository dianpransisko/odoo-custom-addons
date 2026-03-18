from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Field ini wajib ada agar Odoo bisa menyimpan nomor referensi dari Ecommerce
    external_order_sn = fields.Char(string="Ecommerce Order SN", readonly=True)
    #Agar benar-benar aman dari duplikasi menambahkan Constraint unik di model sale.order
    _sql_constraints = [
    ('external_order_sn_unique', 'unique(external_order_sn)', 'Nomor Order Marketplace harus unik!')
]