"""SQLite: status keputusan rujukan dan status pengiriman FHIR disimpan di kolom terpisah."""
import sqlite3
from datetime import date, datetime

from config import DB_FILE, DIAGNOSIS, FMT


def db(sql, args=(), ambil=False):
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    try:
        cur = con.execute(sql, args)
        con.commit()
        return [dict(r) for r in cur.fetchall()] if ambil else None
    finally:
        con.close()


def simpan(r: dict):
    kolom = ", ".join(r)
    tanda = ", ".join("?" for _ in r)
    db(f"INSERT INTO rujukan ({kolom}) VALUES ({tanda})", tuple(r.values()))


def perbarui(id_rujukan, **kolom):
    set_sql = ", ".join(f"{k}=?" for k in kolom)
    db(f"UPDATE rujukan SET {set_sql} WHERE id_rujukan=?", (*kolom.values(), id_rujukan))


def catat_log(skenario, masukan, diharapkan, aktual, hasil):
    db(
        "INSERT INTO log_uji (waktu, skenario, input, diharapkan, aktual, hasil) VALUES (?,?,?,?,?,?)",
        (datetime.now().strftime(FMT), skenario, masukan, diharapkan, aktual, hasil),
    )


def siapkan_db():
    db("""CREATE TABLE IF NOT EXISTS rujukan(
        id_rujukan TEXT PRIMARY KEY, id_pasien TEXT, nama TEXT, tgl_lahir TEXT, jk TEXT,
        pengirim TEXT, tujuan TEXT, diagnosis TEXT, icd10 TEXT, snomed TEXT, alasan TEXT,
        waktu_kirim TEXT, status_fhir TEXT, id_patient TEXT, id_condition TEXT, pesan_fhir TEXT,
        json_patient TEXT, json_condition TEXT, respons TEXT, readback TEXT,
        status_rujukan TEXT, waktu_keputusan TEXT, alasan_tolak TEXT)""")
    db("""CREATE TABLE IF NOT EXISTS log_uji(
        id INTEGER PRIMARY KEY AUTOINCREMENT, waktu TEXT, skenario TEXT, input TEXT,
        diharapkan TEXT, aktual TEXT, hasil TEXT)""")
    if db("SELECT COUNT(*) AS n FROM rujukan", ambil=True)[0]["n"] == 0:
        isi_seed()


def isi_seed():
    """Data fiktif untuk demo."""
    h = date.today().isoformat()
    seed = [
        ("RJ001", "P001", "Andi Pratama", "Diabetes melitus tipe 2", "RS Sehat Makassar", "RS Bhakti Persada", "Menunggu", "08:10", None, None),
        ("RJ002", "P002", "Budi Santoso", "Hipertensi esensial", "RS Harapan", "RS Bhakti Persada", "Diterima", "07:30", "07:52", None),
        ("RJ003", "P003", "Siti Aminah", "Pneumonia", "RS Sejahtera", "RS Bhakti Persada", "Ditolak", "07:00", "07:40", "Ruang ICU penuh"),
        ("RJ004", "P004", "Rahmat Hidayat", "Diabetes melitus tipe 2", "Puskesmas Tamalanrea", "RS Bhakti Persada", "Menunggu", "08:25", None, None),
        ("RJ005", "P005", "Dewi Lestari", "Diabetes melitus tipe 2", "RS Mitra Medika", "RS Sehat Makassar", "Diterima", "06:50", "07:20", None),
        ("RJ006", "P006", "Yusuf Karim", "Hipertensi esensial", "RS Bhakti Persada", "RS Harapan", "Menunggu", "08:40", None, None),
        ("RJ007", "P007", "Maya Sari", "Pneumonia", "Puskesmas Mamajang", "RS Sejahtera", "Menunggu", "08:55", None, None),
        ("RJ008", "P008", "Hendra Wijaya", "Hipertensi esensial", "RS Harapan", "Puskesmas Mamajang", "Menunggu", "09:05", None, None),
    ]
    for (idr, pid, nama, dx, pengirim, tujuan, status, tk, tp, tolak) in seed:
        simpan({
            "id_rujukan": idr, "id_pasien": pid, "nama": nama, "tgl_lahir": "1980-05-12", "jk": "male",
            "pengirim": pengirim, "tujuan": tujuan, "diagnosis": dx,
            "icd10": DIAGNOSIS[dx][0], "snomed": DIAGNOSIS[dx][1], "alasan": "Data contoh",
            "waktu_kirim": f"{h} {tk}", "status_fhir": "Contoh", "status_rujukan": status,
            "waktu_keputusan": f"{h} {tp}" if tp else None, "alasan_tolak": tolak,
        })


def reset_data():
    db("DELETE FROM rujukan")
    db("DELETE FROM log_uji")
    isi_seed()