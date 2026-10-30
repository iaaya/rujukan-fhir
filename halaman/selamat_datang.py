import base64
from pathlib import Path

import streamlit as st

from config import FASKES

PLACEHOLDER = "— pilih fasilitas —"
FOLDER_FOTO = Path(__file__).resolve().parent.parent / "assets" / "tim"

# (nama, peran, nama file foto di assets/tim). Sesuaikan nama file dengan foto Anda.
TIM = [
    ("Nur Sariah", "Developer", "riaa.jpg"),
    ("Andi Rezky Ramadhany Hamzah", "Analis kasus dan data", "kiki.jpg"),
    ("Fhanizah Juhaerul Nanda", "Desain UI/UX", "fani.jpg"),
    ("Citra Aulia", "Koordinator dan Penguji Fungsional", "citra.jpg"),
]

CSS = """<style>
.stApp{background:#112250}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important}

/* kontainer penuh layar, tanpa ruang kosong di atas */
.block-container,[data-testid="stMainBlockContainer"]{
  max-width:100%!important;padding:0!important}
[data-testid="stMainBlockContainer"]>[data-testid="stVerticalBlock"]{gap:0!important}

/* ===== bar atas ===== */
.wnav{display:flex;justify-content:space-between;align-items:center;
  background:#0b1637;border-bottom:1px solid #3B507D;padding:14px 28px;margin:0}
.wnav b{color:#FFFFFF;font-size:16px}
.wnav span{font-size:10px;color:#F5F4F0;border:1px solid #E7E2CE;
  border-radius:20px;padding:2px 10px}

/* ===== hero ===== */
.whero{text-align:center;max-width:720px;margin:0 auto;padding:48px 24px 0}
.weye{font-size:17px;color:#E7E2CE;font-weight:600}
.whero h1{font-size:36px;color:#FFFFFF;margin:8px 0 12px;padding:0;line-height:1.2}
.whero p{color:#E7E2CE;max-width:560px;margin:0 auto;font-size:17px}

/* ===== kartu login ===== */
div.st-key-kartu_login{
  background:#FFFFFF;border-radius:16px;padding:22px!important;
  width:100%;max-width:400px;margin:28px auto 0;
  display:flex;flex-direction:column;gap:14px!important}
div.st-key-kartu_login [data-testid="stElementContainer"]{width:100%!important}
div.st-key-kartu_login h2{color:#112250;font-size:16px;text-align:center;
  margin:0;padding:0;line-height:1.3}
div.st-key-kartu_login [data-baseweb="select"]>div{
  background:#F5F4F0!important;border:1px solid #E7E2CE!important;
  border-radius:10px;min-height:48px}
div.st-key-kartu_login [data-baseweb="select"] div,
div.st-key-kartu_login [data-baseweb="select"] input{
  color:#112250!important;-webkit-text-fill-color:#112250}
div.st-key-kartu_login [data-baseweb="select"]>div>div:first-child{
  text-align:center;justify-content:center}
div.st-key-kartu_login [data-baseweb="select"] svg{fill:#3B507D}
div.st-key-kartu_login .stButton{width:100%}
div.st-key-kartu_login .stButton>button{
  width:100%;min-height:48px;background:#3B507D;color:#FFFFFF;
  border:0;border-radius:10px;font-weight:600}
div.st-key-kartu_login .stButton>button:hover{background:#2c3f66;color:#FFFFFF}
div.st-key-kartu_login .stButton>button p{color:#FFFFFF}

/* ===== Tim Pengembang ===== */
.wband{background:#0b1637;border-top:1px solid #3B507D;border-bottom:1px solid #3B507D;
  margin-top:56px;padding:40px 24px 44px}
.wtim{max-width:900px;margin:0 auto;text-align:center}
.wtim .weye{margin-bottom:4px}
.wtim h2{color:#FFFFFF;font-size:28px;margin:0 0 6px;padding:0}
.wtim .wsub{color:#E7E2CE;font-size:13px;margin:0 0 26px}
.wgrid{display:flex;flex-wrap:wrap;justify-content:center;gap:20px}
.wkartu{background:#FFFFFF;border-radius:14px;padding:20px 14px;width:190px;
  box-shadow:0 6px 18px rgba(0,0,0,.25)}
.wkartu img,.winisial{width:100px;height:100px;border-radius:50%;object-fit:cover;
  border:3px solid #E7E2CE;margin:0 auto 12px;display:block}
.winisial{background:#3B507D;color:#FFFFFF;font-size:30px;font-weight:700;
  display:flex;align-items:center;justify-content:center}
.wkartu b{color:#112250;display:block;font-size:15px;margin-bottom:2px}
.wkartu small{color:#3B507D;font-size:12.5px}

/* ===== footer ===== */
.wfoot{text-align:center;color:#E7E2CE;font-size:12px;padding:40px 24px 28px}
</style>"""


def foto_html(nama, file):
    """Foto base64; kalau file tidak ada, tampilkan inisial."""
    path = FOLDER_FOTO / file
    if path.exists():
        data = base64.b64encode(path.read_bytes()).decode()
        ext = "png" if path.suffix.lower() == ".png" else "jpeg"
        return f'<img src="data:image/{ext};base64,{data}" alt="{nama}">'
    inisial = "".join(k[0] for k in nama.split()[:2]).upper()
    return f'<div class="winisial">{inisial}</div>'


def html_tim():
    kartu = "".join(
        f'<div class="wkartu">{foto_html(n, f)}<b>{n}</b><small>{p}</small></div>'
        for n, p, f in TIM
    )
    return (
        '<div class="wband"><div class="wtim">'
        '<h2>Tim Pengembang Projek Kapita Selekta</h2>'
        '<p class="wsub">Kelompok B2</p>'
        f'<div class="wgrid">{kartu}</div>'
        '</div></div>'
    )


def tampil():
    st.markdown(CSS, unsafe_allow_html=True)

    # --- bagian atas (gambar 1) ---
    st.markdown(
        '<div class="wnav"><b>🏥 RujukanFHIR</b><span>Prototipe akademik</span></div>'
        '<div class="whero">'
        '<div class="weye">Penerapan Standar Interoperabilitas HL7 FHIR</div>'
        '<h1>Sistem Rujukan Antar-Rumah Sakit</h1>'
        '<p>Kirim, terima, dan pantau rujukan pasien antar-rumah sakit dalam satu aplikasi, '
        'dengan data yang terstandar.</p></div>',
        unsafe_allow_html=True,
    )

    with st.container(key="kartu_login"):
        st.markdown("<h2>Masuk sebagai</h2>", unsafe_allow_html=True)
        pilih = st.selectbox("Masuk sebagai", [PLACEHOLDER] + FASKES,
                             label_visibility="collapsed")
        if st.button("Masuk"):
            if pilih == PLACEHOLDER:
                st.error("Pilih fasilitas terlebih dahulu.")
            else:
                st.session_state.fasilitas = pilih
                st.rerun()

    # --- bagian bawah (gambar 2) ---
    st.markdown(html_tim(), unsafe_allow_html=True)

    st.markdown(
        '<div class="wfoot">Prototipe akademik · gunakan data fiktif saja. '
        'Server HAPI FHIR publik dapat dibaca siapa pun.</div>',
        unsafe_allow_html=True,
    )