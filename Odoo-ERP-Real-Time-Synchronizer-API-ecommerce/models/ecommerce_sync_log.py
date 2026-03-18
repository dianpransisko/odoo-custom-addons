from odoo import models, fields

class EcommerceSyncLog(models.Model):
    _name = 'ecommerce.sync.log'
    _description = 'Log Sinkronisasi Ecommerce'
    _order = 'create_date desc' # Log terbaru muncul di paling atas

    name = fields.Char(string="Operasi", required=True)
    operation_type = fields.Selection([
        ('order_pull', 'Tarik Order'),
        ('stock_push', 'Kirim Stok')
    ], string="Tipe Operasi")
    
    status = fields.Selection([
        ('success', 'Berhasil'),
        ('failed', 'Gagal')
    ], string="Status", default='success')
    
    message = fields.Text(string="Pesan/Error")
    external_ref = fields.Char(string="Referensi Eksternal (SN/ID)")