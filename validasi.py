"""Dua skenario kegagalan wajib: (1) field wajib kosong, (2) kode diagnosis tidak ditemukan.
Setiap fungsi mengembalikan pesan kesalahan (str), atau None jika data valid. Hasil dicatat di log."""
from config import DIAGNOSIS, NAMA_BY_ICD, PILIH
from database import catat_log


def cek_field_wajib(id_pasien, nama, tujuan):
    kosong = [n for n, v in [("ID pasien", id_pasien.strip()), ("Nama pasien", nama.strip()),
                             ("Rumah sakit tujuan", "" if tujuan == PILIH else tujuan)] if not v]
    if not kosong:
        return None
    pesan = f"Data belum lengkap: {kosong[0]} wajib diisi."
    catat_log("Field wajib kosong", f"{kosong[0]} = (kosong)", "Ditolak validasi", pesan, "Gagal")
    return pesan


def cek_kode_diagnosis(dx, uji=False):
    kode = "XXX99" if uji else (DIAGNOSIS[dx][0] if dx != PILIH else "")
    if kode in NAMA_BY_ICD:
        return None
    pesan = "Kode tidak ditemukan: pilih diagnosis dari daftar yang tersedia."
    catat_log("Kode diagnosis tidak ditemukan", f"kode = {kode or '(kosong)'}",
              "Ditolak validasi", pesan, "Gagal")
    return pesan