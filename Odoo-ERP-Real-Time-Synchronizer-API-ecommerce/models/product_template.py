from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    external_item_id = fields.Char(string="Ecommerce Item ID", help="ID Produk di sistem Ecommerce")
    last_sync_stock = fields.Datetime(string="Terakhir Sinkron Stok", readonly=True)