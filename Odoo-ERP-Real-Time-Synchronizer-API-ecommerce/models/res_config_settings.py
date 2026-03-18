from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ecommerce_api_url = fields.Char(string="API URL", config_parameter='ecommerce.api_url')
    ecommerce_api_token = fields.Char(string="API Token", config_parameter='ecommerce.api_token')
    ecommerce_api_key = fields.Char(string="API Key", config_parameter='ecommerce.api_key')

    def action_test_connection(self):
        """Tombol untuk mengetes koneksi ke Mock API"""
        if not self.ecommerce_api_url or not self.ecommerce_api_token:
            raise UserError(_("Mohon isi URL dan Token terlebih dahulu!"))
            
        try:
            headers = {"Authorization": self.ecommerce_api_token}
            # Kita tes dengan memanggil list order (endpoint yang sudah ada di Mock API Anda)
            res = requests.get(f"{self.ecommerce_api_url}/api/v2/order/get_order_list", headers=headers, timeout=5)
            
            if res.status_code == 200:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Koneksi Berhasil!'),
                        'message': _('Odoo berhasil terhubung ke Ecommerce Mock API.'),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            elif res.status_code == 401:
                raise UserError(_("Koneksi Gagal: Token tidak valid (401 Unauthorized)."))
            else:
                raise UserError(_("Koneksi Gagal! Status: %s") % res.status_code)
        except Exception as e:
            raise UserError(_("Tidak dapat menghubungi API. Pastikan Mock API sudah jalan! \nError: %s") % str(e))