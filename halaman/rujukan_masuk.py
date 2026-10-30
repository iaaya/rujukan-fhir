import html
import streamlit as st
from utils import pencarian_langsung
from datetime import datetime

from config import FMT
from database import db, perbarui

ALASAN_CEPAT = ["Ruang penuh", "Dokter spesialis tidak tersedia",
                "Alat tidak tersedia", "Data kurang lengkap"]

CSS = """<style>
.stApp{background:#F5F4F0}
[data-testid="stMainBlockContainer"]{
  max-width:100%!important;padding:0 24px 24px 24px!important}

.m-title{font-size:24px;font-weight:700;color:#112250;margin:0;padding-top:16px}
.m-sub{color:#3B507D;font-size:14px;margin:4px 0 16px}

/* kartu putih */
.st-key-filter_masuk,.st-key-tbl_masuk,.st-key-panel_tolak{
  background:#FFFFFF!important;border:1px solid #E7E2CE!important;
  border-radius:14px!important;padding:14px 16px!important;
  margin-bottom:16px;width:100%;box-sizing:border-box;
  overflow:hidden!important}

/* kolom isian */
.st-key-filter_masuk [data-baseweb="input"],
.st-key-filter_masuk [data-baseweb="base-input"],
.st-key-filter_masuk [data-baseweb="select"]>div,
.st-key-panel_tolak [data-baseweb="textarea"],
.st-key-panel_tolak [data-baseweb="base-input"]{
  background:#F5F4F0!important;border:1px solid #E7E2CE!important;
  border-radius:8px!important}
.st-key-filter_masuk input,.st-key-panel_tolak textarea{background:transparent!important}

/* tabel: cegah scroll horizontal & kolom melebihi kartu */
.st-key-tbl_masuk [data-testid="stHorizontalBlock"]{
  flex-wrap:nowrap!important;gap:8px!important;width:100%}
.st-key-tbl_masuk [data-testid="stColumn"]{min-width:0!important}
.st-key-tbl_masuk [data-testid="stVerticalBlock"]{gap:0!important}
.st-key-tbl_masuk [data-testid="stElementContainer"]{overflow:visible}

.th{font-size:13px;font-weight:700;color:#112250;padding-bottom:6px}
.th.aksi{padding-left:16px}
.td{font-size:14px;color:#112250;line-height:1.35}
.td small{display:block;color:#3B507D;font-size:12px}
.kosong{
  padding:14px 0;color:#3B507D;
  border-top:1px solid #E7E2CE;
  border-bottom:1px solid #E7E2CE}
.kode{background:#E7E2CE;color:#3B507D;border-radius:6px;padding:1px 7px;
  font-family:monospace;font-size:12px;display:inline-block;margin-top:3px}
/* label status */
.pill{
  display:inline-block;border-radius:1000px;padding:4px 14px;
  font-size:13px!important;font-weight:600!important;line-height:1.3;
  white-space:nowrap;text-align:center}
.st-key-tbl_masuk .pill.p-Menunggu{background:#E7E2CE!important;color:#6B5D1F!important}
.st-key-tbl_masuk .pill.p-Diterima{background:#DDEFE3!important;color:#1F6B3A!important}
.st-key-tbl_masuk .pill.p-Ditolak{background:#F6D9D9!important;color:#9B2C2C!important}

.st-key-tbl_masuk [class*="st-key-r_"]{
  border-top:1px solid #E7E2CE;padding:10px 0}

/* tombol aksi di tabel: kecil, lebar sesuai teks */
.st-key-tbl_masuk .stButton>button{
  width:auto!important;min-height:30px!important;
  padding:0 12px!important;border:0;border-radius:8px;
  background:#3B507D;color:#fff;white-space:nowrap}
.st-key-tbl_masuk .stButton>button p{
  font-size:13px!important;font-weight:600;color:#fff!important;margin:0}
.st-key-tbl_masuk [class*="st-key-tolak_"] .stButton>button{
  background:#9B2C2C!important}

/* dua tombol berdampingan, rapat, rata kiri */
.st-key-tbl_masuk [class*="st-key-aksi_"] [data-testid="stHorizontalBlock"]{
  gap:6px!important;justify-content:flex-start!important}
.st-key-tbl_masuk [class*="st-key-aksi_"] [data-testid="stColumn"]{
  width:auto!important;flex:0 0 auto!important;min-width:0!important}
/* geser kolom Aksi ke kanan, jauh dari Status */
.st-key-tbl_masuk [class*="st-key-aksi_"]{padding-left:16px!important}
.st-key-tbl_masuk .td.aksi-kosong{padding-left:16px}

/* panel tolak */
.t-title{font-size:16px;font-weight:700;color:#112250}
.t-sub{font-size:13px;color:#3B507D;margin:2px 0 10px}
.st-key-panel_tolak [data-testid="stVerticalBlock"]{gap:10px!important}
.st-key-panel_tolak .stButton>button{white-space:nowrap;border-radius:8px;min-height:34px}
.st-key-panel_tolak .stButton>button p{font-size:14px;font-weight:600}
.st-key-panel_tolak [class*="st-key-chip_"] .stButton>button{
  background:#FFFFFF!important;border:1px solid #3B507D!important;
  color:#3B507D!important;padding:0 14px}
.st-key-panel_tolak [class*="st-key-chip_"] .stButton>button p{color:#3B507D!important}
.st-key-konfirmasi_tolak .stButton>button{
  background:#9B2C2C!important;border:0!important;padding:0 20px;min-height:44px}
.st-key-konfirmasi_tolak .stButton>button p{color:#fff!important;font-size:15px}
.st-key-batal_tolak .stButton>button{
  background:#FFFFFF!important;border:1px solid #3B507D!important;
  padding:0 20px;min-height:44px}
.st-key-batal_tolak .stButton>button p{color:#3B507D!important;font-size:15px}
/* baris tombol: lebar mengikuti isi, berjajar rapat di kiri */
.st-key-baris_chip [data-testid="stHorizontalBlock"],
.st-key-baris_aksi_tolak [data-testid="stHorizontalBlock"]{
  gap:10px!important;justify-content:flex-start!important;flex-wrap:wrap!important}
.st-key-baris_chip [data-testid="stColumn"],
.st-key-baris_aksi_tolak [data-testid="stColumn"]{
  width:auto!important;flex:0 0 auto!important;min-width:0!important}
.st-key-baris_chip .stButton>button{
  min-height:34px;padding:0 14px!important;width:auto!important;white-space:nowrap}
.st-key-baris_aksi_tolak .stButton>button{
  width:auto!important;white-space:nowrap}

.wfoot{text-align:center;color:#3B507D;font-size:12px;
  border-top:1px solid #E7E2CE;padding-top:14px;margin-top:24px}
</style>"""
LEBAR = [0.8, 1.5, 2.2, 1.9, 0.8, 1.8, 1.2, 2.3]


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


def buka_tolak(idr):
    st.session_state.tolak_id = idr
    st.session_state.teks_tolak = ""


def isi_alasan(teks):
    st.session_state.teks_tolak = teks


def tutup_tolak():
    st.session_state.pop("tolak_id", None)
    st.session_state.pop("teks_tolak", None)


def panel_tolak(rows):
    idr = st.session_state.get("tolak_id")
    r = next((x for x in rows if x["id_rujukan"] == idr
              and x["status_rujukan"] == "Menunggu"), None)
    if not r:
        tutup_tolak()
        return

    with st.container(border=True, key="panel_tolak"):
        st.markdown(f'<div class="t-title">Tolak rujukan {e(idr)} · {e(r["nama"])}</div>'
                    '<div class="t-sub">Alasan penolakan akan ditampilkan kepada '
                    'rumah sakit pengirim.</div>', unsafe_allow_html=True)

        with st.container(key="baris_chip"):
            kol = st.columns(len(ALASAN_CEPAT))
            for i, teks in enumerate(ALASAN_CEPAT):
                with kol[i].container(key=f"chip_{i}"):
                    st.button(teks, key=f"btn_chip_{i}", on_click=isi_alasan, args=(teks,))

        st.text_area("Alasan", key="teks_tolak", height=100,
                     placeholder="Tulis alasan penolakan...",
                     label_visibility="collapsed")

        with st.container(key="baris_aksi_tolak"):
            b1, b2 = st.columns(2)
            with b1.container(key="konfirmasi_tolak"):
                ok = st.button("Konfirmasi penolakan", key="btn_konfirmasi")
            with b2.container(key="batal_tolak"):
                batal = st.button("Batal", key="btn_batal")

        if batal:
            tutup_tolak()
            st.rerun()
        if ok:
            alasan = st.session_state.get("teks_tolak", "").strip()
            if not alasan:
                st.error("Alasan penolakan wajib diisi.")
            else:
                perbarui(idr, status_rujukan="Ditolak",
                         waktu_keputusan=datetime.now().strftime(FMT),
                         alasan_tolak=alasan)
                tutup_tolak()
                st.session_state.pesan_keputusan = f"Rujukan {idr} ditolak. Alasan: {alasan}"
                st.rerun()


def tampil():
    st.markdown(CSS, unsafe_allow_html=True)
    fasilitas = st.session_state.fasilitas

    st.markdown(f'<div class="m-title">Rujukan Masuk</div>'
                f'<div class="m-sub">Pasien yang dirujuk ke {e(fasilitas)}. '
                f'Terima atau tolak setiap rujukan.</div>', unsafe_allow_html=True)

    if "pesan_keputusan" in st.session_state:
        st.success(st.session_state.pop("pesan_keputusan"))

    rows = db("SELECT * FROM rujukan WHERE tujuan=? ORDER BY id_rujukan ASC",
              (fasilitas,), ambil=True)

    # --- panel tolak (muncul setelah tombol Tolak ditekan) ---
    if "tolak_id" in st.session_state:
        panel_tolak(rows)

    # --- kartu filter ---
    with st.container(border=True, key="filter_masuk"):
        c1, c2 = st.columns([2, 1])
        q = c1.text_input("Cari", placeholder="Cari nama / ID pasien",
                          label_visibility="collapsed", key="q_masuk").strip().lower()
        s = c2.selectbox("Status", ["Semua status", "Menunggu", "Diterima", "Ditolak"],
                         label_visibility="collapsed", key="s_masuk")
        pencarian_langsung("q_masuk")

    rows = [r for r in rows
            if (s == "Semua status" or r["status_rujukan"] == s)
            and (not q or q in r["nama"].lower() or q in r["id_pasien"].lower())]

    # --- kartu tabel ---
    with st.container(border=True, key="tbl_masuk"):
        head = st.columns(LEBAR)
        for col, t in zip(head, ["ID", "Pasien", "Diagnosis", "Pengirim",
                                 "Kirim", "Keputusan", "Status", "Aksi"]):
            kelas = "th aksi" if t == "Aksi" else "th"
            col.markdown(f'<div class="{kelas}">{t}</div>', unsafe_allow_html=True)

        if not rows:
            st.markdown('<div class="td kosong">Tidak ada rujukan.</div>',
                        unsafe_allow_html=True)

        for r in rows:
            idr = r["id_rujukan"]
            with st.container(key=f"r_{idr}"):
                c = st.columns(LEBAR, vertical_alignment="center")
                c[0].markdown(f'<div class="td">{e(idr)}</div>', unsafe_allow_html=True)
                c[1].markdown(f'<div class="td">{e(r["nama"])}<small>{e(r["id_pasien"])}</small></div>',
                              unsafe_allow_html=True)
                c[2].markdown(f'<div class="td">{e(r["diagnosis"])}<br>'
                              f'<span class="kode">{e(r["icd10"])}</span></div>',
                              unsafe_allow_html=True)
                c[3].markdown(f'<div class="td">{e(r["pengirim"])}</div>', unsafe_allow_html=True)
                c[4].markdown(f'<div class="td">{jam(r["waktu_kirim"])}</div>', unsafe_allow_html=True)

                ket = jam(r["waktu_keputusan"])
                if r["alasan_tolak"]:
                    ket += f'<small>Alasan: {e(r["alasan_tolak"])}</small>'
                c[5].markdown(f'<div class="td">{ket}</div>', unsafe_allow_html=True)

                st_ = r["status_rujukan"]
                c[6].markdown(f'<div class="td"><span class="pill p-{e(st_)}">{e(st_)}</span></div>',
                              unsafe_allow_html=True)

                if st_ == "Menunggu":
                    with c[7].container(key=f"aksi_{idr}"):
                        b1, b2 = st.columns(2, gap="small")
                        if b1.button("Terima", key=f"terima_{idr}"):
                            perbarui(idr, status_rujukan="Diterima",
                                     waktu_keputusan=datetime.now().strftime(FMT),
                                     alasan_tolak=None)
                            tutup_tolak()
                            st.session_state.pesan_keputusan = f"Rujukan {idr} diterima."
                            st.rerun()
                        with b2.container(key=f"tolak_{idr}"):
                            st.button("Tolak", key=f"btn_tolak_{idr}",
                                      on_click=buka_tolak, args=(idr,))
                else:
                    c[7].markdown('<div class="td aksi-kosong">–</div>', unsafe_allow_html=True)

    footer()