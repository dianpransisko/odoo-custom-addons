import requests
import logging
from odoo import models, api, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class EcommerceConnector(models.AbstractModel):
    _name = 'ecommerce.connector'
    _description = 'Mesin Integrasi Ecommerce Pro'

    def _get_api_config(self):
        params = self.env['ir.config_parameter'].sudo()
        url = params.get_param('ecommerce.api_url')
        token = params.get_param('ecommerce.api_token')
        if not url or not token:
            raise UserError(_("Konfigurasi API URL atau Token belum diatur!"))
        return url, token

    # --- SECTION 1: ORDER PROCESSING (PULL) ---

    @api.model
    def sync_orders(self):
        """Fungsi Periodik: Menarik daftar order baru dari API"""
        url, token = self._get_api_config()
        headers = {"Authorization": token}
        try:
            res = requests.get(f"{url}/api/v2/order/get_order_list", headers=headers, timeout=10)
            if res.status_code == 200:
                order_list = res.json().get('response', {}).get('order_list', [])
                for item in order_list:
                    sn = item['order_sn']
                    # Idempotency: Pastikan 1 SN hanya diproses 1 kali
                    existing = self.env['sale.order'].search([('external_order_sn', '=', sn)], limit=1)
                    if not existing:
                        self._create_order_from_detail(sn, url, headers)
                
                self._create_log('order_pull', 'success', f"Berhasil cek {len(order_list)} order.")
        except Exception as e:
            self._create_log('order_pull', 'failed', str(e))

    def _create_order_from_detail(self, order_sn, url, headers):
        """Memproses Detail Order dengan Reservation Gate & Feedback Loop"""
        res = requests.get(f"{url}/api/v2/order/get_order_detail", params={'order_sn': order_sn}, headers=headers)
        if res.status_code != 200: return

        data = res.json().get('response', {}).get('order_list', [])[0]
        buyer = data.get('buyer', {})
        addr = data.get('shipping_address', {})
        
        partner = self.env['res.partner'].search([('name', '=', buyer.get('username'))], limit=1)
        if not partner:
            partner = self.env['res.partner'].create({
                'name': buyer.get('username'),
                'email': buyer.get('email'),
                'phone': buyer.get('phone'),
                'street': addr.get('address_line1'),
                'city': addr.get('city'),
            })

        try:
            # Atomic transaction menggunakan Savepoint
            with self.env.cr.savepoint():
                order_lines = []
                for item in data.get('items', []):
                    product = self.env['product.product'].search([('default_code', '=', item['sku'])], limit=1)
                    
                    if product:
                        # 1. LOCKING: Amankan baris produk di DB (Postgres Level)
                        self.env.cr.execute(
                            "SELECT id FROM product_product WHERE id=%s FOR UPDATE NOWAIT", 
                            (product.id,)
                        )
                        
                        # 2. RE-CHECK: Ambil data stok virtual (Forecasted) terbaru setelah dikunci
                        product.invalidate_recordset(['virtual_available'])
                        
                        if product.virtual_available >= item['qty']:
                            order_lines.append((0, 0, {
                                'product_id': product.id,
                                'product_uom_qty': item['qty'],
                                'price_unit': item['price'],
                                'name': item['name'],
                            }))
                        else:
                            raise UserError(_("Stok tidak cukup untuk SKU %s") % item['sku'])
                    else:
                        raise UserError(_("SKU %s tidak ditemukan di sistem") % item['sku'])

                if order_lines:
                    # 3. ATOMIC CONFIRM: Langsung reserve stok di gudang
                    order = self.env['sale.order'].create({
                        'partner_id': partner.id,
                        'external_order_sn': order_sn,
                        'origin': f"Marketplace: {order_sn}",
                        'order_line': order_lines,
                    })
                    order.action_confirm() 
                    _logger.info("Order %s Diterima & Stok Aman." % order_sn)

        except Exception as e:
            # FEEDBACK LOOP: Jika Odoo menolak, beri tahu Marketplace agar status sinkron
            error_reason = str(e)
            self._reject_order_at_marketplace(order_sn, url, headers, error_reason)
            self._create_log('order_pull', 'failed', f"REJECTED {order_sn}: {error_reason}")

    def _reject_order_at_marketplace(self, order_sn, url, headers, reason):
        """Trigger: Beri tahu API jika order gagal diproses Odoo"""
        payload = {
            "order_sn": order_sn,
            "new_status": "CANCELLED_STOCK_OUT",
            "message": f"Dibatalkan otomatis oleh Odoo: {reason}"
        }
        try:
            requests.post(f"{url}/api/v2/order/update_status", json=payload, headers=headers, timeout=5)
        except Exception as ex:
            _logger.error("Feedback Gagal: %s" % str(ex))

    # --- SECTION 2: STOCK SYNCHRONIZATION (PUSH) ---

    @api.model
    def trigger_instant_sync(self, product_id):
        """Fungsi BARU: Menembak API secara instan (Real-time) untuk satu produk"""
        url, token = self._get_api_config()
        headers = {"Authorization": token, "Content-Type": "application/json"}
        
        # Selalu gunakan Forecasted (virtual_available) untuk keamanan
        forecasted_qty = product_id.virtual_available
        
        payload = {
            "item_id": str(product_id.default_code), 
            "new_stock": int(forecasted_qty)
        }
        
        try:
            requests.post(f"{url}/api/v2/product/update_stock", json=payload, headers=headers, timeout=5)
            _logger.info(">>> INSTANT SYNC: Produk %s terupdate ke API (Stok: %s)" % (product_id.default_code, forecasted_qty))
        except Exception as e:
            _logger.error("Gagal Instant Sync: %s" % str(e))

    @api.model
    def sync_product_stock(self):
        """Fungsi Periodik (Bulk): Backup sinkronisasi stok masal"""
        url, token = self._get_api_config()
        headers = {"Authorization": token, "Content-Type": "application/json"}
        
        # Ambil produk yang terhubung ke Marketplace
        products = self.env['product.product'].search([('external_item_id', '!=', False)])
        success_count = 0
        
        for product in products:
            # Gunakan virtual_available agar sinkron dengan Reservation Gate
            payload = {"item_id": str(product.external_item_id), "new_stock": int(product.virtual_available)}
            try:
                res = requests.post(f"{url}/api/v2/product/update_stock", json=payload, headers=headers, timeout=5)
                if res.status_code == 200:
                    product.last_sync_stock = fields.Datetime.now()
                    success_count += 1
            except: continue

        self._create_log('stock_push', 'success', f"Update stok masal {success_count} produk berhasil.")

    def _create_log(self, op_type, status, message):
        self.env['ecommerce.sync.log'].create({
            'name': 'Sync Activity',
            'operation_type': op_type,
            'status': status,
            'message': message
        })