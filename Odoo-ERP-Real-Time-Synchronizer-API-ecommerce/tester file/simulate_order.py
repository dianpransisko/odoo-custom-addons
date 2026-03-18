import requests
import time

API_URL = "#######################"

# DATA PESANAN SESUAI PARAMETER WAJIB
order_payload = {
    "order_sn": "ORD-REAL-2026-005",
    "order_status": "PAID",
    "create_time": int(time.time()),
    "buyer": {
        "name": "Sontoloyo2",
        "username": "Kalau gagal.gua tonjok lu",
        "phone": "081236589",
        "email": "budiman@mail.com"
    },
    "shipping_address": {
        "recipient_name": "Gak Error lagi",
        "phone": "08123456789",
        "address_line1": "Jl. Sudirman No. 10",
        "city": "Jakarta",
        "province": "DKI Jakarta",
        "postal_code": "10220",
        "country": "ID"
    },
    "items": [
        {
            "sku": "KBP-001",  # Pastikan SKU ini sama dengan Internal Reference di Odoo Anda
            "name": "KEMEJA BATIK PRIA",
            "qty": 1,
            "price": 250000
        }
    ],
    "payment": {
        "method": "ShopeePay",
        "paid_amount": 500000,
        "payment_status": "PAID"
    },
    "shipping": {
        "courier": "JNT",
        "service": "REG",
        "shipping_fee": 10000
    }
}

try:
    response = requests.post(API_URL, json=order_payload)
    if response.status_code == 200:
        print(f"✅ BERHASIL: Pesanan {order_payload['order_sn']} telah masuk ke Marketplace Mock!")
    else:
        print(f"❌ GAGAL: {response.text}")
except Exception as e:
    print(f"⚠️ ERROR KONEKSI: {str(e)}")