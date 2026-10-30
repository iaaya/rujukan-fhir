import html
import streamlit as st

# (diagnosis, ICD-10, SNOMED CT), sama persis dengan pemetaan di HTML
PEMETAAN = [
    ("Diabetes melitus tipe 2", "E11.9", "44054006"),
    ("Hipertensi esensial", "I10", "59621000"),
    ("Pneumonia", "J18.9", "233604007"),
    ("Gagal jantung kongestif", "I50.0", "42343007"),
    ("Diabetes melitus tipe 2 (sudah ada sebelumnya)", "O24.3", "199230006"),
    ("Luka bakar sinar matahari tingkat ketiga", "L55.2", "200835003"),
    ("Infeksi saluran pernapasan atas akut", "J06.9", "54398005"),
    ("Bronkitis akut", "J20", "10509002"),
    ("Penyakit ginjal kronis stadium 5", "N18.5", "433146000"),
    ("Melena (BAB hitam)", "K92.1", "2901004"),
    ("Cedera otak difus", "S06.2", "262693007"),
    ("Fraktur tulang kaki", "S92", "15574005"),
]

CSS = """<style>
.stApp{background:#F5F4F0}
[data-testid="stMainBlockContainer"]{
  max-width:100%!important;padding:0 24px 24px 24px!important}

.fw{font-size:15px;line-height:1.5;color:#112250}
.fw .m-title{font-size:24px;font-weight:700;color:#112250;margin:0 0 4px;padding-top:16px}
.fw .m-sub{color:#3B507D;margin:0 0 18px}

.fw .fbox{background:#FFFFFF;border:1px solid #E7E2CE;border-radius:12px;
  padding:14px;margin-bottom:16px}
.fw .fbox h3{font-size:16px;font-weight:700;color:#112250;margin:0 0 10px;padding:0;line-height:1.5}
.fw .fbox p{margin:0;color:#112250}
.fw .ftwo{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px}
.fw .ftwo .fbox{margin-bottom:0;min-width:0}
.fw .tw{overflow-x:auto}

.fw table{width:100%;border-collapse:collapse;font-size:14px}
.fw th,.fw td{text-align:left;padding:8px 10px;
  border-bottom:1px solid #E7E2CE;white-space:nowrap;color:#112250}
.fw th{color:#3B507D;font-weight:600;font-size:12px}
.fw .chip{background:#E7E2CE;color:#3B507D;border-radius:6px;padding:3px 9px;
  font-size:13px;font-family:ui-monospace,Consolas,monospace}
.fw .sumber{color:#3B507D;font-size:13px;margin:13px 0 0!important}

.fw .foot{margin-top:28px;padding-top:12px;border-top:1px solid #E7E2CE;
  color:#3B507D;font-size:12px;text-align:center}
@media(max-width:760px){.fw .ftwo{grid-template-columns:1fr}}
</style>"""


def e(x):
    return html.escape(str(x)) if x is not None else ""


def _tampil_html(isi):
    if hasattr(st, "html"):
        st.html(isi)
    else:
        st.markdown(isi, unsafe_allow_html=True)


def tampil():
    st.markdown(CSS, unsafe_allow_html=True)

    baris = "".join(
        f'<tr><td>{e(n)}</td><td><span class="chip">{e(i)}</span></td>'
        f'<td><span class="chip">{e(s)}</span></td></tr>'
        for n, i, s in PEMETAAN)

    _tampil_html(
        '<div class="fw">'
        '<div class="m-title">Info Standar</div>'
        '<div class="m-sub">Perbedaan ICD-10 dan SNOMED CT.</div>'
        '<div class="ftwo">'
        '<div class="fbox"><h3>ICD-10</h3><p>Sistem klasifikasi penyakit dari WHO. '
        'Satu penyakit dikelompokkan ke satu kode, dipakai untuk pelaporan, '
        'statistik, dan penagihan. Granularitas terbatas.</p></div>'
        '<div class="fbox"><h3>SNOMED CT</h3><p>Terminologi klinis yang sangat rinci, '
        'berisi konsep beserta hubungan antar konsep. Cocok untuk pencatatan klinis '
        'dan pertukaran data yang bisa diproses komputer.</p></div></div>'
        '<div class="fbox tw"><h3>Pemetaan diagnosis</h3><table><thead><tr>'
        '<th>Diagnosis</th><th>ICD-10</th><th>SNOMED CT</th></tr></thead>'
        f'<tbody>{baris}</tbody></table>'
        '<p class="sumber">Kode bersumber dari kodemedis.com, '
        'Diakses 26 Oktober 2026.</p></div>'
        '<p class="foot">Prototipe akademik · gunakan data fiktif saja. '
        'Server HAPI FHIR publik dapat dibaca siapa pun.</p>'
        '</div>'
    )