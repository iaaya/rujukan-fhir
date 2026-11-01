import streamlit as st
from datetime import date, datetime

from config import FASKES, DIAGNOSIS, PILIH, FMT
from database import db, simpan, catat_log
from validasi import cek_field_wajib, cek_kode_diagnosis
from fhir_client import proses_fhir
from utils import catat_uji

CSS = """<style>
.stApp{background:#F5F4F0}
[data-testid="stHeader"]{height:0!important;min-height:0!important;background:transparent!important}
[data-testid="stAppViewContainer"],[data-testid="stMain"]{padding-top:0!important}
[data-testid="stMainBlockContainer"]{
  max-width:100%!important;
  padding:12px 24px 24px 24px!important}

.b-title{font-size:24px;font-weight:700;color:#112250;margin:0;padding-top:0}
.b-sub{color:#3B507D;font-size:14px;margin:4px 0 16px}

/* kartu putih pembungkus form */
.st-key-form_rujukan{background:#FFFFFF!important;
  border:1px solid #E7E2CE!important;border-radius:14px!important;
  padding:16px 16px 18px!important}

/* label kecil */
.st-key-form_rujukan label p{font-size:12px!important;color:#3B507D!important}

/* kolom isian: latar krem + garis tepi tipis */
.st-key-form_rujukan [data-baseweb="input"],
.st-key-form_rujukan [data-baseweb="base-input"],
.st-key-form_rujukan [data-baseweb="select"]>div,
.st-key-form_rujukan [data-baseweb="textarea"]{
  background:#F5F4F0!important;border:1px solid #E7E2CE!important;
  border-radius:8px!important}
.st-key-form_rujukan input,
.st-key-form_rujukan textarea{background:transparent!important;font-size:15px}

/* tombol kirim */
.st-key-form_rujukan .stButton>button{
  background:#3B507D;color:#fff;border:0;border-radius:10px;
  font-weight:700;padding:10px 18px}
[data-testid="stMainBlockContainer"]{
  max-width:100%!important;
  padding:0 24px 24px 24px!important}


.wfoot{text-align:center;color:#3B507D;font-size:12px;
  border-top:1px solid #E7E2CE;padding-top:14px;margin-top:24px}
</style>"""

def id_baru():
    baris = db("SELECT id_rujukan FROM rujukan", ambil=True)
    angka = [int(r["id_rujukan"][2:]) for r in baris if r["id_rujukan"][2:].isdigit()]
    return f"RJ{max(angka, default=0) + 1:03d}"

def footer():
    st.markdown(
        '<div class="wfoot">Prototipe akademik · gunakan data fiktif saja. '
        'Server HAPI FHIR publik dapat dibaca siapa pun.</div>',
        unsafe_allow_html=True,
    )
def tampil():
    st.markdown(CSS, unsafe_allow_html=True)
    pengirim = st.session_state.fasilitas

    st.markdown('<div class="b-title">Buat Rujukan</div>'
                '<div class="b-sub">Isi data pasien fiktif, pilih diagnosis, '
                'lalu kirim ke server FHIR.</div>', unsafe_allow_html=True)

    with st.container(border=True, key="form_rujukan"):
        c1, c2 = st.columns(2)
        id_pasien = c1.text_input("ID Pasien *", placeholder="RJ001")
        nama = c2.text_input("Nama Pasien *", placeholder="Nama fiktif")
        tgl = c1.date_input("Tanggal Lahir", value=date(1980, 5, 12),
                            min_value=date(1700, 1, 1), max_value=date.today())
        jk_label = c2.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        c1.text_input("Fasilitas Pengirim", value=pengirim, disabled=True)
        tujuan = c2.selectbox("Rumah Sakit Tujuan *",
                              [PILIH] + [f for f in FASKES if f != pengirim])

        dx = st.selectbox("Diagnosis *", [PILIH] + list(DIAGNOSIS))
        if dx != PILIH:
            icd, snomed = DIAGNOSIS[dx]
            st.code(f"ICD-10: {icd}    SNOMED CT: {snomed}", language=None)

        alasan = st.text_area("Alasan rujukan / ringkasan kondisi",
                              placeholder="Contoh: gula darah tidak terkontrol, perlu penanganan spesialis")
        uji = st.checkbox("Mode uji: paksa kode diagnosis tidak valid")
        kirim = st.button("Validasi & Kirim ke FHIR")

    if not kirim:
        footer()
        return

       # 1) validasi lokal
    pesan = cek_field_wajib(id_pasien, nama, tujuan) or cek_kode_diagnosis(dx, uji)
    if pesan:
        st.error(f"✖ {pesan}")
        footer()
        return

    # 2) kirim ke FHIR
    icd, snomed = DIAGNOSIS[dx]
    data = {"id_pasien": id_pasien.strip(), "nama": nama.strip(), "tgl_lahir": tgl.isoformat(),
            "jk": "male" if jk_label == "Laki-laki" else "female",
            "diagnosis": dx, "icd10": icd, "snomed": snomed, "alasan": alasan.strip()}
    with st.spinner("Mengirim ke server FHIR..."):
        hasil = proses_fhir(data)

    if hasil["status_fhir"] != "Berhasil":
        catat_log("Pengiriman FHIR", f"{data['id_pasien']} / {icd}", "201 Created",
                  hasil["pesan_fhir"], "Gagal")
        st.error(f"✖ {hasil['pesan_fhir']}")
        footer()
        return

    # 3) simpan ke database
    idr = id_baru()
    simpan({**data, **hasil, "id_rujukan": idr, "pengirim": pengirim, "tujuan": tujuan,
            "waktu_kirim": datetime.now().strftime(FMT), "status_rujukan": "Menunggu",
            "waktu_keputusan": None, "alasan_tolak": None})
    catat_log("Pengiriman valid", f"{data['id_pasien']} / {icd}", "201 Created",
              "201 Created, Patient & Condition tersimpan", "Berhasil")
    st.session_state.terakhir = idr
    st.success(f"✔ Rujukan {idr} terkirim ke {tujuan}. Status: menunggu keputusan {tujuan}.")
    footer()