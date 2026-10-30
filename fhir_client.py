"""Integrasi HL7 FHIR: membuat resource, mengirim ke HAPI (POST), membaca kembali (GET)."""
import json

import requests

from config import FHIR_BASE, HEADERS, SISTEM_ICD10, SISTEM_SNOMED


def bangun_patient(id_pasien, nama, tgl_lahir, jk):
    return {
        "resourceType": "Patient",
        "identifier": [{"system": "urn:demo:rekam-medis", "value": id_pasien}],
        "name": [{"text": nama}],
        "gender": jk,
        "birthDate": tgl_lahir,
    }


def bangun_condition(patient_id, diagnosis, icd10, snomed, alasan):
    cond = {
        "resourceType": "Condition",
        "clinicalStatus": {"coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active"}]},
        "code": {
            "coding": [
                {"system": SISTEM_ICD10, "code": icd10, "display": diagnosis},
                {"system": SISTEM_SNOMED, "code": snomed, "display": diagnosis},
            ],
            "text": diagnosis,
        },
        "subject": {"reference": f"Patient/{patient_id}"},
    }
    if alasan:
        cond["note"] = [{"text": alasan}]
    return cond


def periksa_struktur(res):
    """Validasi struktur dasar JSON FHIR sebelum dikirim. Mengembalikan daftar kesalahan."""
    salah = []
    try:
        res = json.loads(json.dumps(res))  # memastikan dapat diserialisasi sebagai JSON
    except (TypeError, ValueError):
        return ["JSON tidak valid: format data perlu diperiksa."]
    if res.get("resourceType") == "Patient":
        if not res.get("name"):
            salah.append("Patient.name wajib ada.")
    elif res.get("resourceType") == "Condition":
        if not res.get("code", {}).get("coding"):
            salah.append("Condition.code.coding wajib ada.")
        if not res.get("subject", {}).get("reference"):
            salah.append("Condition.subject wajib ada.")
    else:
        salah.append("resourceType tidak dikenal.")
    return salah


def post_fhir(res):
    r = requests.post(f"{FHIR_BASE}/{res['resourceType']}", json=res, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.status_code, r.json()


def get_fhir(tipe, id_):
    r = requests.get(f"{FHIR_BASE}/{tipe}/{id_}", headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.status_code, r.json()


def proses_fhir(r: dict):
    """POST Patient -> POST Condition (merujuk Patient) -> GET keduanya. Mengembalikan kolom hasil."""
    hasil = {"status_fhir": "Gagal", "pesan_fhir": "", "id_patient": "", "id_condition": "",
             "respons": "", "readback": ""}
    patient = bangun_patient(r["id_pasien"], r["nama"], r["tgl_lahir"], r["jk"])
    hasil["json_patient"] = json.dumps(patient, indent=2, ensure_ascii=False)
    condition = bangun_condition("(belum ada)", r["diagnosis"], r["icd10"], r["snomed"], r["alasan"])
    hasil["json_condition"] = json.dumps(condition, indent=2, ensure_ascii=False)

    salah = periksa_struktur(patient) + periksa_struktur(condition)
    if salah:
        hasil["pesan_fhir"] = " ".join(salah)
        return hasil
    try:
        kode_p, resp_p = post_fhir(patient)
        pid = resp_p["id"]
        condition = bangun_condition(pid, r["diagnosis"], r["icd10"], r["snomed"], r["alasan"])
        hasil["json_condition"] = json.dumps(condition, indent=2, ensure_ascii=False)
        kode_c, resp_c = post_fhir(condition)
        cid = resp_c["id"]
        _, bp = get_fhir("Patient", pid)
        _, bc = get_fhir("Condition", cid)
        hasil.update(
            status_fhir="Berhasil", id_patient=pid, id_condition=cid,
            respons=json.dumps({"POST Patient": kode_p, "POST Condition": kode_c,
                                "id Patient": pid, "id Condition": cid}, indent=2),
            readback=json.dumps({"Patient": bp, "Condition": bc}, indent=2, ensure_ascii=False),
        )
    except (requests.RequestException, KeyError, ValueError) as e:
        hasil["pesan_fhir"] = f"Pengiriman gagal: periksa koneksi dan coba kembali. ({e})"
    return hasil