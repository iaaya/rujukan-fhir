"""Fungsi bantu tampilan: tabel, pencarian, dan gaya warna."""
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from config import FMT


def lama(kirim, putus):
    if not putus:
        return "—"
    menit = int((datetime.strptime(putus, FMT) - datetime.strptime(kirim, FMT)).total_seconds() // 60)
    return f"{menit} menit"


def tabel(rows, kolom, nama_kolom):
    df = pd.DataFrame(rows)
    if df.empty:
        st.info("Tidak ada rujukan.")
        return
    df = df[kolom].fillna("—")
    df.columns = nama_kolom
    st.dataframe(df, hide_index=True)


def saring(rows, kunci):
    c1, c2 = st.columns([2, 1])
    q = c1.text_input("Cari nama atau ID pasien", key=f"q_{kunci}").strip().lower()
    s = c2.selectbox("Status", ["Semua", "Menunggu", "Diterima", "Ditolak"], key=f"s_{kunci}")
    return [r for r in rows
            if (s == "Semua" or r["status_rujukan"] == s)
            and (not q or q in r["nama"].lower() or q in r["id_pasien"].lower())]


def pasang_gaya():
    st.markdown("""<style>
    /* tombol di konten utama (bukan sidebar) */
    [data-testid="stMain"] div.stButton>button,
    div[data-testid="stFormSubmitButton"]>button{
        background:#3B507D;color:#fff;border:0}
    </style>""", unsafe_allow_html=True)


CSS_DROPDOWN = """
/* kotak dropdown (tertutup) */
[data-baseweb="select"] > div,
[data-baseweb="select"] > div:hover,
[data-baseweb="select"] > div:focus,
[data-baseweb="select"] > div:focus-within,
[data-baseweb="select"] > div:active{
  background:#F5F4F0 !important;
  border:1px solid #E7E2CE !important;
  border-color:#E7E2CE !important;
  border-radius:8px !important;
  outline:none !important;
  box-shadow:none !important}
[data-baseweb="select"] svg{fill:#3B507D !important}

/* popup daftar pilihan */
div[data-baseweb="popover"] > div,
div[data-baseweb="popover"] ul{
  background:#FFFFFF !important;border-radius:12px !important;
  padding:0 !important;overflow:hidden !important}

/* item biasa: hanya lapisan luar yang berwarna */
[role="listbox"] [role="option"],
ul[role="listbox"] > li{
  background:#FFFFFF !important;color:#112250 !important;
  padding:14px 18px !important;margin:0 !important;
  border-radius:0 !important;min-height:0 !important;
  box-shadow:none !important;outline:0 !important}

/* semua lapisan di dalam item: polos, tanpa warna, tanpa sudut membulat */
[role="listbox"] [role="option"] *{
  background:transparent !important;background-color:transparent !important;
  border-radius:0 !important;box-shadow:none !important;
  color:#112250 !important;-webkit-text-fill-color:#112250 !important}

/* kursor lewat: krem (satu lapis saja) */
[role="listbox"] [role="option"]:hover,
[role="listbox"] [role="option"][data-highlighted="true"],
[role="listbox"] [role="option"]:focus{
  background:#E7E2CE !important}

/* terpilih: biru, teks putih tebal */
[role="listbox"] [role="option"][aria-selected="true"],
[role="listbox"] [role="option"][aria-selected="true"]:hover{
  background:#3B507D !important}
[role="listbox"] [role="option"][aria-selected="true"] *{
  color:#FFFFFF !important;-webkit-text-fill-color:#FFFFFF !important;
  font-weight:700 !important}
  /* kolom teks: tanpa garis hitam, border tipis saat fokus */
[data-baseweb="input"],
[data-baseweb="base-input"],
[data-baseweb="input"]:focus-within,
[data-baseweb="base-input"]:focus-within,
[data-baseweb="input"]:focus,
[data-baseweb="base-input"]:focus{
  border:1px solid #E7E2CE !important;
  border-color:#E7E2CE !important;
  outline:none !important;
  box-shadow:none !important;
  border-radius:8px !important}
[data-baseweb="input"]:focus-within,
[data-baseweb="base-input"]:focus-within{
  border-color:#3B507D !important}
[data-testid="stTextInput"] input,
[data-testid="stTextInput"] input:focus,
[data-testid="stTextInput"] input:focus-visible{
  outline:none !important;
  box-shadow:none !important;
  border:0 !important;
  background:transparent !important}
"""


def gaya_dropdown():
    css = f"<style>{CSS_DROPDOWN}</style>"
    if hasattr(st, "html"):
        st.html(css)
    else:
        st.markdown(css, unsafe_allow_html=True)
def pencarian_langsung(kunci_input):
    """Kirim isi kolom pencarian ke Streamlit pada setiap ketukan tombol (debounce 250 ms)."""
    components.html(f"""<script>
    const doc = window.parent.document;
    const pasang = () => {{
      const inp = doc.querySelector('.st-key-{kunci_input} input');
      if (!inp || inp.dataset.live) return;
      inp.dataset.live = "1";
      let t;
      inp.addEventListener('input', () => {{
        clearTimeout(t);
        t = setTimeout(() => {{
          inp.dispatchEvent(new KeyboardEvent('keydown',
            {{key:'Enter', code:'Enter', keyCode:13, which:13, bubbles:true}}));
        }}, 250);
      }});
    }};
    pasang();
    new MutationObserver(pasang).observe(doc.body, {{childList:true, subtree:true}});
    </script>""", height=0)
def catat_uji(skenario, input_, diharapkan, aktual, hasil):
    """Simpan satu baris ke log pengujian FHIR. hasil: 'Berhasil' atau 'Gagal'."""
    from datetime import datetime
    st.session_state.setdefault("log_uji", []).insert(0, {
        "t": datetime.now().strftime("%H:%M"),
        "sk": skenario, "inp": input_, "ex": diharapkan,
        "ak": aktual, "res": hasil,
    })