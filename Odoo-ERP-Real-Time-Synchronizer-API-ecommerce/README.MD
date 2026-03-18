# Odoo ERP Real-Time Synchronizer API
> **Marketplace Integration with Anti-Overselling Engine**

Modul ini merupakan ekstensi fitur pada standar ERP Odoo yang dirancang untuk mengotomatisasi sinkronisasi antara operasional internal (ERP) dan etalase digital (Marketplace API). Seluruh fungsi standar Odoo tetap berjalan normal, dengan tambahan jalur otomatisasi untuk transaksi online yang handal.

---

## 🛠️ Stack Teknologi
* **ERP Framework:** Odoo (v17)
* **Language:** Python 3.x
* **Database:** PostgreSQL (Optimized for Row-Level Locking)
* **Communication:** RESTful API / JSON
* **Architecture:** Event-Driven Synchronization

---

## 🌟 Fitur Utama (Enhancement)

### 📥 Automasi Entri Pesanan
Mengurangi beban administrasi dengan mengotomatisasi pembuatan dokumen penjualan:
* **Auto-Creation**: Mengubah data *Nested JSON* dari API menjadi *Confirmed Sales Order* secara instan.
* **SKU Mapping**: Validasi otomatis antara kode produk Marketplace dan *Internal Reference* Odoo.
* **Partner Sync**: Otomatisasi pembuatan data pelanggan baru berdasarkan identitas dari API.

### 🔄 Sinkronisasi Stok Instan (Event-Driven)
Menghubungkan pergerakan gudang fisik langsung ke etalase online:
* **Real-Time Trigger**: Setiap validasi stok di Odoo (surat jalan/kasir) memicu pembaruan stok ke Marketplace dalam hitungan detik.
* **Forecasted Accuracy**: Mengirimkan nilai `virtual_available` (Stok Fisik - Reservasi) untuk mencegah *overselling* pada barang yang sudah dipesan namun belum dikirim.

### 🛡️ Transaksional & Concurrency Control
Menjaga integritas data saat terjadi transaksi bersamaan di offline dan online:
* **Postgres Row-Level Locking**: Mengunci baris database produk (`FOR UPDATE NOWAIT`) saat proses reservasi pesanan online untuk menghindari *race condition*.
* **Reservation Gate**: Memastikan setiap pesanan online divalidasi berdasarkan ketersediaan stok paling update di database.

### 🔁 Feedback Loop (Reject Handler)
Menjaga sinkronisasi status jika terjadi kegagalan stok:
* Otomatis mengirim instruksi `CANCELLED_STOCK_OUT` ke Marketplace API jika reservasi stok di Odoo gagal akibat stok habis di gudang fisik.

---

## 🏗️ Alur Operasional

1.  **Offline/Manual**: Staf gudang bekerja seperti biasa di dalam ekosistem Odoo.
2.  **Online Bridge**: Modul secara mandiri menarik order, membuat dokumen SO, dan mengupdate stok ke API setiap kali ada perubahan data di Odoo.
3.  **Consistency**: Odoo tetap menjadi **Single Source of Truth** untuk seluruh pergerakan barang.
4.  **Audit Trail**: Tersedia menu **Sync Logs** untuk memantau keberhasilan dan kegagalan setiap aktivitas integrasi secara transparan.

---

## 📖 Dokumentasi Lengkap
Informasi teknis mendalam mengenai skema API dan konfigurasi modul dapat diakses melalui tautan di bawah ini:

👉 [**Baca Dokumentasi Lengkap di Academia.edu**](https://www.academia.edu/165219258/MODUL_INTEGRASI_ODOO_API_e_commerce_)

---
*Developed for Odoo ERP Integration Ecosystem.*