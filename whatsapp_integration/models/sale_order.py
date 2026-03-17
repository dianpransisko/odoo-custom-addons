import os
import requests
from dotenv import load_dotenv
from odoo import models, fields, api
from odoo.exceptions import UserError

# Memuat file .env (Pastikan path-nya benar jika file .env tidak di root)
load_dotenv()

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_send_wa(self):
        # Ambil konfigurasi dari environment variables
        url = os.getenv('FONNTE_API_URL')
        token = os.getenv('FONNTE_API_TOKEN')

        # Proteksi jika .env belum dikonfigurasi
        if not url or not token:
            raise UserError("Konfigurasi API (URL/Token) tidak ditemukan di file .env!")

        for rec in self:
            phone = rec.partner_id.mobile or rec.partner_id.phone
            if not phone:
                raise UserError(f"Nomor HP customer {rec.partner_id.name} kosong.")

            clean_phone = ''.join(filter(str.isdigit, phone))
            if clean_phone.startswith('0'):
                clean_phone = '62' + clean_phone[1:]

            # Variabel dinamis dari Odoo
            customer_name = rec.partner_id.name
            company_name = rec.company_id.name or "Perusahaan Kami"
            so_number = rec.name
            company_contact = rec.company_id.phone or "-"

            # Template Pesan
            message = (
                f"hallo *{customer_name}*,\n\n"
                f"kami dari *{company_name}*.\n"
                f"Untuk Sales order anda *{so_number}* sudah diverifikasi.\n"
                f"silahkan lakukan pembayaran untuk memproses pesanan Anda.\n\n"
                f"untuk info lebih lanjut, hubungi {company_contact}.\n\n"
                f"--- {company_name} ---"
            )

            headers = {
                "Authorization": token.strip()
            }
            payload = {
                "target": clean_phone,
                "message": message
            }

            try:
                response = requests.post(url, data=payload, headers=headers)
                res_data = response.json()

                if res_data.get('status'):
                    return {
                        'effect': {
                            'fadeout': 'slow',
                            'message': f'WA Terkirim ke {customer_name}',
                            'type': 'rainbow_man',
                        }
                    }
                else:
                    raise UserError(f"Fonnte Reject: {res_data.get('reason')}")
            except Exception as e:
                raise UserError(f"Gagal koneksi ke server API: {str(e)}")