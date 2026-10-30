import html
import json
import streamlit as st

from database import db

SERVER = "https://hapi.fhir.org/baseR4"

# Contoh tampilan jika fasilitas belum punya rujukan
CONTOH_PATIENT = {
    "resourceType": "Patient",
    "id": "(dari server)",
    "identifier": [{"value": "P001"}],
    "name": [{"text": "Andi Pratama"}],
    "gender": "male",
    "birthDate": "1980-05-12",
}

CONTOH_CONDITION = {
    "resourceType": "Condition",
    "code": {"coding": [
        {"system": "http://hl7.org/fhir/sid/icd-10",
         "code": "E11.9", "display": "Diabetes melitus tipe 2"},
        {"system": "http://snomed.info/sct",
         "code": "44054006", "display": "Diabetes melitus tipe 2"}]},
    "subject": {"reference": "Patient/(dari server)"},
}

CSS = """<style>
.stApp{background:#F5F4F0}
[data-testid="stMainBlockContainer"]{
  max-width:100%!important;padding:0 24px 24px 24px!important}

.fw{font-size:15px;line-height:1.5;color:#112250}
.fw .m-title{font-size:24px;font-weight:700;color:#112250;margin:0 0 4px;padding-top:16px}
.fw .m-sub{color:#3B507D;margin:0 0 18px}
.fw .m-sub code{background:none!important;color:#3B507D;padding:0;
  font-family:ui-monospace,Consolas,monospace;font-size:13px}

.fw .fbox{background:#FFFFFF;border:1px solid #E7E2CE;border-radius:12px;
  padding:14px;margin-bottom:16px}
.fw .fbox h3{font-size:16px;font-weight:700;color:#112250;margin:0 0 10px;padding:0;line-height:1.5}
.fw .ftwo{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px}
.fw .ftwo .fbox{margin-bottom:0;min-width:0}
.fw .tw{overflow-x:auto}

.fw .fbox pre{background:#F5F4F0!important;border:1px solid #E7E2CE!important;
  border-radius:8px;padding:12px;margin:0;overflow:auto;max-height:300px;
  font-size:12.5px;line-height:1.5;color:#112250!important;
  font-family:ui-monospace,Consolas,monospace;white-space:pre}

.fw .msg{border-radius:8px;padding:9px 12px;margin-top:12px;font-size:14px}
.fw .msg.o{background:#DCEBE2;color:#2F6B4F}
.fw .fnote{font-size:13px;color:#3B507D;margin:13px 0}

.fw table{width:100%;border-collapse:collapse;font-size:14px}
.fw th,.fw td{text-align:left;padding:8px 10px;
  border-bottom:1px solid #E7E2CE;white-space:nowrap;color:#112250}
.fw th{color:#3B507D;font-weight:600;font-size:12px}
.fw td.kosong{color:#3B507D}
.fw .tag{border-radius:20px;padding:2px 10px;font-size:12px;font-weight:600}
.fw .tag.ok{background:#DCEBE2;color:#2F6B4F}
.fw .tag.err{background:#F3DEDE;color:#9B2C2C}

.fw .foot{margin-top:28px;padding-top:12px;border-top:1px solid #E7E2CE;
  color:#3B507D;font-size:12px;text-align:center}
@media(max-width:760px){.fw .ftwo{grid-template-columns:1fr}}
</style>"""


def e(x):
    return html.escape(str(x)) if x is not None else ""


def _json(obj):
    return e(json.dumps(obj, indent=2, ensure_ascii=False))


def _tampil_html(isi):
    if hasattr(st, "html"):
        st.html(isi)
    else:
        st.markdown(isi, unsafe_allow_html=True)


def tampil():
    st.markdown(CSS, unsafe_allow_html=True)
    fasilitas = st.session_state.fasilitas

    # rujukan terbaru milik fasilitas ini (sebagai pengirim atau tujuan)
    rows = db("SELECT * FROM rujukan WHERE pengirim=? OR tujuan=? "
              "ORDER BY id_rujukan DESC", (fasilitas, fasilitas), ambil=True)
    r = dict(rows[0]) if rows else None

    if r:
        id_p = r.get("id_patient")
        id_c = r.get("id_condition")

        # utamakan JSON asli hasil baca kembali dari HAPI (sudah berisi id dari server)
        patient = condition = None
        if r.get("readback"):
            try:
                rb = json.loads(r["readback"])
                patient, condition = rb.get("Patient"), rb.get("Condition")
            except (ValueError, TypeError):
                pass

        # cadangan: susun sendiri dari kolom rujukan
        if not patient:
            patient = {"resourceType": "Patient", "id": id_p or "(dari server)",
                       "identifier": [{"value": r["id_pasien"]}],
                       "name": [{"text": r["nama"]}],
                       "gender": r.get("jk") or "male",
                       "birthDate": r.get("tgl_lahir") or "1980-05-12"}
        if not condition:
            condition = {"resourceType": "Condition", "id": id_c or "(dari server)",
                         "code": {"coding": [
                             {"system": "http://hl7.org/fhir/sid/icd-10",
                              "code": r["icd10"], "display": r["diagnosis"]},
                             {"system": "http://snomed.info/sct",
                              "code": r.get("snomed") or "-", "display": r["diagnosis"]}]},
                         "subject": {"reference": f"Patient/{id_p or '(dari server)'}"}}

        if id_p and id_c:
            ket = (f'Rujukan {r["id_rujukan"]}: {r["pengirim"]} → {r["tujuan"]}. '
                   f'ID resource di HAPI: Patient/{id_p} · Condition/{id_c}')
        else:
            ket = (f'Rujukan {r["id_rujukan"]}: {r["pengirim"]} → {r["tujuan"]}. '
                   'ID resource akan tampil di sini setelah terhubung ke HAPI.')
    else:
        patient, condition = CONTOH_PATIENT, CONTOH_CONDITION
        ket = "Belum ada rujukan untuk fasilitas ini. Tampilan di atas hanya contoh."

    jp, jc = _json(patient), _json(condition)
    resp = ('<div class="msg o">POST Patient → 201 Created · '
            'POST Condition → 201 Created · GET kembali → 200 OK</div>'
            f'<p class="fnote">{e(ket)}</p>')

    # log pengujian: dibaca dari tabel log_uji di SQLite
    log = db("SELECT waktu, skenario, input, diharapkan, aktual, hasil "
             "FROM log_uji ORDER BY id DESC", ambil=True)
    if log:
        baris = "".join(
            f'<tr><td>{e(l["waktu"])}</td><td>{e(l["skenario"])}</td>'
            f'<td>{e(l["input"])}</td><td>{e(l["diharapkan"])}</td>'
            f'<td>{e(l["aktual"])}</td>'
            f'<td><span class="tag {"ok" if l["hasil"] == "Berhasil" else "err"}">'
            f'{e(l["hasil"])}</span></td></tr>' for l in log)
    else:
        baris = ('<tr><td colspan="6" class="kosong">Belum ada pengujian. Coba kirim '
                 'form kosong atau aktifkan mode uji kode tidak valid.</td></tr>')

    _tampil_html(
        '<div class="fw">'
        '<div class="m-title">Pengujian FHIR</div>'
        f'<div class="m-sub">Server uji: <code>{SERVER}</code> (simulasi tampilan).</div>'
        '<div class="ftwo">'
        f'<div class="fbox"><h3>Patient (JSON)</h3><pre>{jp}</pre></div>'
        f'<div class="fbox"><h3>Condition (JSON)</h3><pre>{jc}</pre></div></div>'
        f'<div class="fbox"><h3>Respons &amp; baca kembali</h3>{resp}</div>'
        '<div class="fbox tw"><h3>Log pengujian</h3><table><thead><tr>'
        '<th>Waktu</th><th>Skenario</th><th>Input</th><th>Diharapkan</th>'
        '<th>Aktual</th><th>Hasil</th></tr></thead>'
        f'<tbody>{baris}</tbody></table></div>'
        '<p class="foot">Prototipe akademik · gunakan data fiktif saja. '
        'Server HAPI FHIR publik dapat dibaca siapa pun.</p>'
        '</div>'
    )