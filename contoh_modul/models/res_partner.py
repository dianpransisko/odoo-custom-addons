from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    nomor_ktp = fields.Char(string='Nomor KTP')
    nomor_npwp = fields.Char(string='Nomor NPWP')

    @api.constrains('nomor_ktp')
    def _check_ktp_format(self):
        for record in self:
            if record.nomor_ktp:
                # Validasi: Harus angka
                if not record.nomor_ktp.isdigit():
                    raise ValidationError("Gagal Simpan: Nomor KTP harus berupa angka saja!")
                # Validasi: Harus 16 digit (Standar KTP Indonesia)
                if len(record.nomor_ktp) != 16:
                    raise ValidationError("Gagal Simpan: Nomor KTP harus berjumlah tepat 16 digit!")

    @api.constrains('nomor_npwp')
    def _check_npwp_format(self):
        for record in self:
            if record.nomor_npwp:
                # Validasi: Harus angka
                if not record.nomor_npwp.isdigit():
                    raise ValidationError("Gagal Simpan: Nomor NPWP harus berupa angka saja!")
                # Validasi: Harus 15 digit
                if len(record.nomor_npwp) != 15:
                    raise ValidationError("Gagal Simpan: Nomor NPWP harus berjumlah tepat 15 digit!")

    # 1. Merubah Label & Menambah Batas Ukuran (Size)
    phone = fields.Char(string='No. Telp Kantor', size=13)
    mobile = fields.Char(string='No. HP Pribadi', size=13)

    # 2. Menambah Validasi agar hanya angka
    @api.constrains('phone', 'mobile')
    def _check_phone_digit(self):
        for record in self:
            if record.phone and not record.phone.isdigit():
                raise ValidationError("Nomor Telepon harus berupa angka!")
            if record.mobile and not record.mobile.isdigit():
                raise ValidationError("Nomor HP harus berupa angka!")