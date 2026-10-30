import streamlit as st
from database import siapkan_db
from utils import pasang_gaya, gaya_dropdown
from halaman import (selamat_datang, dashboard, buat_rujukan,
                     rujukan_masuk, rujukan_terkirim,
                     pengujian_fhir, info_standar)

st.set_page_config(page_title="Sistem Rujukan FHIR", page_icon="🏥", layout="wide")
siapkan_db()
pasang_gaya()
gaya_dropdown()

# --- state awal ---
if "fasilitas" not in st.session_state:
    st.session_state.fasilitas = None
if "halaman" not in st.session_state:
    st.session_state.halaman = "Dashboard"

# --- belum login: tampilkan halaman selamat datang ---
if st.session_state.fasilitas is None:
    selamat_datang.tampil()
    st.stop()

# --- sudah login: sidebar + menu ---
MENU = {
    "Dashboard": dashboard,
    "Buat Rujukan": buat_rujukan,
    "Rujukan Masuk": rujukan_masuk,
    "Rujukan Terkirim": rujukan_terkirim,
    "Pengujian FHIR": pengujian_fhir,
    "Info Standar": info_standar,
}

SIDEBAR_CSS = """<style>
/* lebar & latar sidebar */
[data-testid="stSidebar"]{
  background:#112250;
  width:250px!important;min-width:250px!important;max-width:250px!important}
[data-testid="stSidebarHeader"]{display:none}
[data-testid="stSidebarUserContent"]{padding:20px 0 16px 0!important}

/* rapatkan jarak antar-elemen, tapi beri ruang untuk blok teks */
[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{gap:6px!important}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"]{
  margin:0!important;overflow:visible!important}

.sb-brand{color:#FFFFFF;font-weight:700;font-size:16px}
.sb-sub{color:#E7E2CE;font-size:11px;margin-bottom:12px}
.sb-fas{background:#3B507D;color:#FFFFFF;border-radius:10px;
  padding:10px 12px;font-size:13px;font-weight:600;margin-bottom:14px}
.sb-menu{color:#E7E2CE;font-size:12px;line-height:1.4;
  display:block;padding:4px 0 10px;margin:0}

/* tombol menu: rata kiri di semua lapisan */
[data-testid="stSidebar"] .stButton>button{
  width:100%!important;min-height:38px;padding:0 12px!important;
  background:transparent!important;color:#FFFFFF!important;
  border:0!important;border-radius:10px!important;box-shadow:none!important;
  justify-content:flex-start!important;text-align:left!important}
[data-testid="stSidebar"] .stButton>button>div,
[data-testid="stSidebar"] .stButton>button [data-testid="stMarkdownContainer"]{
  width:100%;justify-content:flex-start!important;text-align:left!important}
[data-testid="stSidebar"] .stButton>button p{
  color:inherit!important;font-size:14px;font-weight:400;text-align:left!important;margin:0}
[data-testid="stSidebar"] .stButton>button:hover{background:#1c3170!important}

/* menu aktif */
[data-testid="stSidebar"] .stButton>button[kind="primary"],
[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"]{
  background:#F5F4F0!important;color:#112250!important}
[data-testid="stSidebar"] .stButton>button[kind="primary"] p,
[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] p{
  color:#112250!important;font-weight:400}

/* tombol keluar: kecil, di kiri bawah */
[data-testid="stSidebar"] .st-key-menu_keluar .stButton>button{
  width:auto!important;min-height:32px;padding:0 14px!important;
  background:#3B507D!important;justify-content:center!important}
[data-testid="stSidebar"] .st-key-menu_keluar .stButton>button p{
  font-size:12px;font-weight:400;text-align:center!important}
  [data-testid="stAppViewContainer"] [data-testid="stMain"] [data-testid="stMainBlockContainer"],
[data-testid="stAppViewContainer"] .main .block-container,
section.main > div.block-container{
  padding-top:0!important;margin-top:0!important}
[data-testid="stMain"]{padding-top:0!important}
[data-testid="stAppViewContainer"]{padding-top:0!important}
</style>"""

st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown(
        '<div class="sb-brand">🏥 RujukanFHIR</div>'
        '<div class="sb-sub">Prototipe akademik · HL7 FHIR R4</div>'
        f'<div class="sb-fas">{st.session_state.fasilitas}</div>'
        '<div class="sb-menu">Menu</div>',
        unsafe_allow_html=True,
    )
    for nama in MENU:
        aktif = nama == st.session_state.halaman
        if st.button(nama, key=f"menu_{nama}", use_container_width=True,
                     type="primary" if aktif else "secondary"):
            st.session_state.halaman = nama
            st.rerun()

    st.markdown("<div style='height:40vh'></div>", unsafe_allow_html=True)
    if st.button("Keluar", key="menu_keluar"):
        st.session_state.fasilitas = None
        st.session_state.halaman = "Dashboard"
        st.rerun()

MENU[st.session_state.halaman].tampil()