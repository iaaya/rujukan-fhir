import streamlit as st
from config import DIAGNOSIS
from database import db

# Daftar diagnosis (nama, kode ICD-10), diambil dari config.py
DAFTAR_DIAGNOSIS = [(nama, kode[0]) for nama, kode in DIAGNOSIS.items()]

CSS = """<style>
.stApp{background:#F5F4F0}
[data-testid="stHeader"]{background:transparent}
[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none}
.block-container,[data-testid="stMainBlockContainer"]{
  max-width:1100px!important;padding:0px 32px 24px!important}

.d-title{font-size:24px;font-weight:700;color:#112250;margin:0;padding-top:16px}
.d-sub{color:#3B507D;font-size:14px;margin:4px 0 18px}

.kpis{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin-bottom:16px}
.kpi{background:#FFFFFF;border:1px solid #E7E2CE;border-radius:12px;padding:12px 14px}
.kpi .l{font-size:11px;color:#3B507D}
.kpi .v{font-size:26px;font-weight:700;color:#112250;line-height:1.3}

.panel{background:#FFFFFF;border:1px solid #E7E2CE;border-radius:12px;
  padding:16px 18px;margin-bottom:16px}
.panel h3{font-size:15px;color:#112250;margin:0 0 12px;padding:0}

.drow{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);
  align-items:center;padding:6px 0;font-size:13px;color:#112250}
.kode{background:#E7E2CE;color:#3B507D;border-radius:6px;padding:1px 7px;
  font-family:monospace;font-size:11px;margin-left:4px;white-space:nowrap;
  display:inline-block}
.bar{display:flex;align-items:center;gap:10px;font-weight:700;min-height:14px}
.bar span{min-width:14px}
.bar i{display:block;height:10px;border-radius:6px;background:#3B507D}

.ba{display:grid;grid-template-columns:1fr auto 1fr;gap:14px;align-items:center}
.ba .box{background:#F5F4F0;border-radius:10px;padding:12px 14px;
  font-size:13px;color:#112250}
.ba .box b{display:block;margin-bottom:4px}
.ba .box small{color:#3B507D;font-size:11px}
.ba .arrow{font-weight:700;color:#112250}

.wfoot{text-align:center;color:#3B507D;font-size:12px;
  border-top:1px solid #E7E2CE;padding-top:14px;margin-top:8px}
</style>"""


def tampil():
    st.markdown(CSS, unsafe_allow_html=True)
    fasilitas = st.session_state.fasilitas

    keluar = db("SELECT * FROM rujukan WHERE pengirim=?", (fasilitas,), ambil=True)
    masuk = db("SELECT * FROM rujukan WHERE tujuan=?", (fasilitas,), ambil=True)

    # "Gagal kirim" dibaca dari log pengujian (isi sesuai cara catat_log menyimpan)
    gagal = sum(1 for l in st.session_state.get("log_uji", [])
                if l.get("res") == "Gagal")

    ringkasan = {
        "Rujukan keluar": len(keluar),
        "Rujukan masuk": len(masuk),
        "Perlu keputusan": sum(1 for r in masuk if r["status_rujukan"] == "Menunggu"),
        "Keluar diterima": sum(1 for r in keluar if r["status_rujukan"] == "Diterima"),
        "Keluar ditolak": sum(1 for r in keluar if r["status_rujukan"] == "Ditolak"),
        "Gagal kirim": gagal,
    }

    # hitung per kode ICD-10 dari rujukan keluar + masuk
    hitung = {}
    for r in list(keluar) + list(masuk):
        hitung[r["icd10"]] = hitung.get(r["icd10"], 0) + 1

    diagnosis = [(nama, kode, hitung.get(kode, 0)) for nama, kode in DAFTAR_DIAGNOSIS]

    kpi = "".join(
        f'<div class="kpi"><div class="l">{k}</div><div class="v">{v}</div></div>'
        for k, v in ringkasan.items()
    )

    maks = max([j for _, _, j in diagnosis] + [1])
    baris = ""
    for nama, kode, jml in sorted(diagnosis, key=lambda x: -x[2]):
        bar = f'<i style="width:{int(jml / maks * 120)}px"></i>' if jml else ""
        baris += (f'<div class="drow"><div>{nama}<span class="kode">{kode}</span></div>'
                  f'<div class="bar">{bar}<span>{jml}</span></div></div>')

    st.markdown(
        '<div class="d-title">Dashboard</div>'
        '<div class="d-sub">Ringkasan rujukan keluar dan masuk fasilitas Anda.</div>'
        f'<div class="kpis">{kpi}</div>'
        f'<div class="panel"><h3>Rujukan per diagnosis (terstandar)</h3>{baris}</div>'
        '<div class="panel"><h3>Sebelum vs sesudah</h3><div class="ba">'
        '<div class="box"><b>Sebelum (teks bebas)</b>'
        '“DM” · “kencing manis” · “diabetes melitus”<br>'
        '<small>→ 3 entri berbeda, tidak bisa dihitung</small></div>'
        '<div class="arrow">→</div>'
        '<div class="box"><b>Sesudah (FHIR)</b>'
        '<span class="kode">E11.9</span><span class="kode">44054006</span><br>'
        '<small>→ 1 diagnosis, 3 kasus</small></div></div></div>'
        '<div class="wfoot">Prototipe akademik · gunakan data fiktif saja. '
        'Server HAPI FHIR publik dapat dibaca siapa pun.</div>',
        unsafe_allow_html=True,
    )