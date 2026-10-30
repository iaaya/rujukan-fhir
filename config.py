"""Konfigurasi dan data referensi. Ubah daftar diagnosis dan fasilitas di sini."""

FHIR_BASE = "https://hapi.fhir.org/baseR4"
HEADERS = {"Content-Type": "application/fhir+json", "Accept": "application/fhir+json"}
SISTEM_ICD10 = "http://hl7.org/fhir/sid/icd-10"
SISTEM_SNOMED = "http://snomed.info/sct"
DB_FILE = "rujukan.db"
FMT = "%Y-%m-%d %H:%M"
PILIH = "— pilih —"

FASKES = [
    "RS Bhakti Persada", "RS Sehat Makassar", "RS Sejahtera", "RS Harapan",
    "RS Mitra Medika", "Puskesmas Tamalanrea", "Puskesmas Mamajang",
]

# nama diagnosis -> (kode ICD-10, kode SNOMED CT). Sumber: kodemedis.com
# PENTING: verifikasi ulang tiap kode di browser resmi sebelum dilaporkan.
DIAGNOSIS = {
    "Diabetes melitus tipe 2": ("E11.9", "44054006"),
    "Hipertensi esensial": ("I10", "59621000"),
    "Pneumonia": ("J18.9", "233604007"),
    "Gagal jantung kongestif": ("I50.0", "42343007"),
    "Diabetes melitus tipe 2 (sudah ada sebelumnya)": ("O24.3", "199230006"),
    "Luka bakar sinar matahari tingkat ketiga": ("L55.2", "200835003"),
    "Infeksi saluran pernapasan atas akut": ("J06.9", "54398005"),
    "Bronkitis akut": ("J20", "10509002"),
    "Penyakit ginjal kronis stadium 5": ("N18.5", "433146000"),
    "Melena (BAB hitam)": ("K92.1", "2901004"),
    "Cedera otak difus": ("S06.2", "262693007"),
    "Fraktur tulang kaki": ("S92", "15574005"),
}
NAMA_BY_ICD = {v[0]: k for k, v in DIAGNOSIS.items()}