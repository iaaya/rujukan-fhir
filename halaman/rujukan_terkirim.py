import html
import streamlit as st
from datetime import datetime

from config import FMT
from database import db
from utils import pencarian_langsung

CSS = """<style>
.stApp{background:#F5F4F0}
[data-testid="stMainBlockContainer"]{
  max-width:100%!important;padding:0 24px 24px 24px!important}

.m-title{font-size:24px;font-weight:700;color:#112250;margin:0;padding-top:16px}
.m-sub{color:#3B507D;font-size:14px;margin:4px 0 16px}

/* kartu putih */
.st-key-filter_kirim,.st-key-tbl_kirim{
  background:#FFFFFF!important;border:1px solid #E7E2CE!important;
  border-radius:14px!important;padding:14px 16px!important;
  margin-bottom:16px;width:100%;box-sizing:border-box;
  overflow:hidden!important}

/* kolom isian */
.st-key-filter_kirim [data-baseweb="input"],
.st-key-filter_kirim [data-baseweb="base-input"],
.st-key-filter_kirim [data-baseweb="select"]>div{
  background:#F5F4F0!important;border:1px solid #E7E2CE!important;
  border-radius:8px!important;outline:none!important;box-shadow:none!important}
.st-key-filter_kirim [data-baseweb="input"]:focus-within,
.st-key-filter_kirim [data-baseweb="base-input"]:focus-within{
  border-color:#3B507D!important}
.st-key-filter_kirim input,
.st-key-filter_kirim input:focus,
.st-key-filter_kirim input:focus-visible{
  background:transparent!important;outline:none!important;
  box-shadow:none!important;border:0!important}

/* tabel */
.st-key-tbl_kirim [data-testid="stHorizontalBlock"]{
  flex-wrap:nowrap!important;gap:8px!important;width:100%}
.st-key-tbl_kirim [data-testid="stColumn"]{min-width:0!important}
.st-key-tbl_kirim [data-testid="stVerticalBlock"]{gap:0!important}
.st-key-tbl_kirim [data-testid="stElementContainer"]{overflow:visible}

.th{font-size:13px;font-weight:700;color:#112250;padding-bottom:6px}
.td{font-size:14px;color:#112250;line-height:1.35}
.td small{display:block;color:#3B507D;font-size:12px}
.kosong{padding:14px 0;color:#3B507D;
  border-top:1px solid #E7E2CE;border-bottom:1px solid #E7E2CE}
.kode{background:#E7E2CE;color:#3B507D;border-radius:6px;padding:1px 7px;
  font-family:monospace;font-size:12px;display:inline-block;margin-top:3px}

.pill{display:inline-block;border-radius:1000px;padding:4px 14px;
  font-size:13px!important;font-weight:600!important;line-height:1.3;
  white-space:nowrap;text-align:center}
.st-key-tbl_kirim .pill.p-Menunggu{background:#E7E2CE!important;color:#6B5D1F!important}
.st-key-tbl_kirim .pill.p-Diterima{background:#DDEFE3!important;color:#1F6B3A!important}
.st-key-tbl_kirim .pill.p-Ditolak{background:#F6D9D9!important;color:#9B2C2C!important}

.st-key-tbl_kirim [class*="st-key-k_"]{
  border-top:1px solid #E7E2CE;padding:10px 0}

.wfoot{text-align:center;color:#3B507D;font-size:12px;
  border-top:1px solid #E7E2CE;padding-top:14px;margin-top:24px}
</style>"""

LEBAR = [0.8, 1.5, 2.2, 1.9, 0.8, 1.8, 1.2]


def jam(s):
    if not s:
        return "–"
    try:
        return datetime.strptime(s, FMT).strftime("%H:%M")
    except (ValueError, TypeError):
        return str(s)


def e(x):
    return html.escape(str(x)) if x is not None else ""


def footer():
    st.markdown('<div class="wfoot">Prototipe akademik · gunakan data fiktif saja. '
                'Server HAPI FHIR publik dapat dibaca siapa pun.</div>',
                unsafe_allow_html=True)


def tampil():
    st.markdown(CSS, unsafe_allow_html=True)
    fasilitas = st.session_state.fasilitas

    st.markdown(f'<div class="m-title">Rujukan Terkirim</div>'
                f'<div class="m-sub">Rujukan yang dikirim {e(fasilitas)} '
                f'beserta status keputusan rumah sakit tujuan.</div>',
                unsafe_allow_html=True)

    semua = db("SELECT * FROM rujukan WHERE pengirim=? ORDER BY id_rujukan ASC",
               (fasilitas,), ambil=True)

    # --- kartu filter ---
    with st.container(border=True, key="filter_kirim"):
        c1, c2 = st.columns([2, 1])
        q = c1.text_input("Cari", placeholder="Cari nama / ID pasien",
                          label_visibility="collapsed", key="q_kirim").strip().lower()
        s = c2.selectbox("Status", ["Semua status", "Menunggu", "Diterima", "Ditolak"],
                         label_visibility="collapsed", key="s_kirim")
        pencarian_langsung("q_kirim")

    rows = [r for r in semua
            if (s == "Semua status" or r["status_rujukan"] == s)
            and (not q or q in r["nama"].lower() or q in r["id_pasien"].lower())]

    # --- kartu tabel ---
    with st.container(border=True, key="tbl_kirim"):
        head = st.columns(LEBAR)
        for col, t in zip(head, ["ID", "Pasien", "Diagnosis", "Tujuan",
                                 "Kirim", "Keputusan", "Status"]):
            col.markdown(f'<div class="th">{t}</div>', unsafe_allow_html=True)

        if not rows:
            st.markdown('<div class="td kosong">Tidak ada rujukan.</div>',
                        unsafe_allow_html=True)

        for r in rows:
            idr = r["id_rujukan"]
            with st.container(key=f"k_{idr}"):
                c = st.columns(LEBAR, vertical_alignment="center")
                c[0].markdown(f'<div class="td">{e(idr)}</div>', unsafe_allow_html=True)
                c[1].markdown(f'<div class="td">{e(r["nama"])}<small>{e(r["id_pasien"])}</small></div>',
                              unsafe_allow_html=True)
                c[2].markdown(f'<div class="td">{e(r["diagnosis"])}<br>'
                              f'<span class="kode">{e(r["icd10"])}</span></div>',
                              unsafe_allow_html=True)
                c[3].markdown(f'<div class="td">{e(r["tujuan"])}</div>', unsafe_allow_html=True)
                c[4].markdown(f'<div class="td">{jam(r["waktu_kirim"])}</div>', unsafe_allow_html=True)

                ket = jam(r["waktu_keputusan"])
                if r["alasan_tolak"]:
                    ket += f'<small>Alasan: {e(r["alasan_tolak"])}</small>'
                c[5].markdown(f'<div class="td">{ket}</div>', unsafe_allow_html=True)

                st_ = r["status_rujukan"]
                c[6].markdown(f'<div class="td"><span class="pill p-{e(st_)}">{e(st_)}</span></div>',
                              unsafe_allow_html=True)

    footer()