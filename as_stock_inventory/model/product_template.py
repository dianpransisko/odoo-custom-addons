from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    shelf_location = fields.Char(string='Lokasi Rak', help='Contoh: Blok A - Rak 01')