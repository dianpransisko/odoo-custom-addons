from odoo import models, api, _
import logging

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_done(self, cancel_backorder=False):
        """
        Override _action_done: 
        Pintu keluar terakhir stok Odoo. Begitu status menjadi 'Done', 
        kita langsung tembak API Marketplace.
        """
        # 1. Jalankan fungsi standar Odoo terlebih dahulu
        res = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)
        
        # 2. Ambil daftar produk unik yang terlibat dalam pergerakan stok ini
        # (Menggunakan set agar jika ada 5 baris produk yang sama, API hanya ditembak 1x)
        products_to_sync = self.mapped('product_id')

        for product in products_to_sync:
            # Syarat: Hanya sinkronkan jika produk memiliki SKU (Internal Reference)
            # Dan terhubung ke Marketplace (external_item_id tidak kosong)
            if product.default_code and product.external_item_id:
                try:
                    _logger.info(">>> TRIGGER: Mendeteksi perubahan stok fisik untuk %s. Memulai Instant Sync..." % product.default_code)
                    
                    # Panggil fungsi yang sudah kita buat di ecommerce_connector.py
                    self.env['ecommerce.connector'].trigger_instant_sync(product)
                    
                except Exception as e:
                    _logger.error("Gagal memicu Instant Sync untuk %s: %s" % (product.default_code, str(e)))

        return res