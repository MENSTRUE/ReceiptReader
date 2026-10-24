# ReceiptReader — Dokumentasi Utama Bahasa Indonesia

**Day 17/100 | OCR struk dan ekstraksi informasi dengan verifikasi manusia**

[Baca README utama](../../README.md) · [English](../en/README.md) · [Aturan agen](../../AGENTS.md) · [Repository](https://github.com/MENSTRUE/ReceiptReader)

## Ringkasan eksekutif

ReceiptReader membantu pengguna menyalin empat field struk: **nama toko, tanggal, alamat, dan total pembayaran**. Sistem membaca gambar melalui OCR, menawarkan kandidat nilai, dan meminta koreksi serta konfirmasi pengguna sebelum mengunduh CSV/JSON. Ini prototipe portofolio, bukan pengganti akuntan atau sistem penagihan otomatis.

**Status terbukti (24 Oktober 2026):** screenshot uji lokal menunjukkan empat field tepat pada **satu contoh struk** setelah perubahan heuristik alamat. Kode GitHub yang diaudit masih berjudul **Tesseract baseline + field heuristics** dan **belum mengintegrasikan inferensi riset v10**. Keberhasilan satu contoh tidak berarti akurasi 100%.

## Before → Now → Next

| Tahap | Kondisi | Bukti / tindakan |
|---|---|---|
| **Before** | Eksperimen riset OCR/KIE pada SROIE dan CORD v2, terakhir v10 | `notebooks/receiptreader.ipynb`, audit dan laporan di `reports/` |
| **Now** | Streamlit: upload, preview, OCR, empat field editable, centang verifikasi, ekspor JSON/CSV | `app/streamlit_app.py`, `src/receiptreader/`, screenshot uji lokal; belum ada tolok ukur aplikasi lintas struk |
| **Next** | Audit artefak model v10, parity test dan dataset evaluasi struk nyata berizin | Rencana; jangan disebut selesai |

## Masalah, pengguna, dan kriteria keberhasilan

Pengguna: pekerja administrasi, UMKM dan pencatat pengeluaran yang memproses gambar struk. OCR mempersingkat penyalinan awal tetapi salah membaca angka atau alamat bisa berdampak nyata. Alur produk mengutamakan koreksi manusia; keberhasilan MVP berarti nilai mudah diedit, jejak OCR tersedia, dan ekspor dicegah sebelum konfirmasi. Produk tidak menjanjikan validasi pajak, verifikasi keaslian struk, atau pembacaan semua format.

## Alur teknis

```text
Foto JPG/PNG/WEBP
  -> pemeriksaan dan PIL image
  -> orientasi EXIF, grayscale, contrast
  -> Tesseract PSM 6 (default bahasa eng)
  -> raw OCR text
  -> ekstraksi aturan merchant/date/address/total
  -> form review + koreksi
  -> checkbox + tombol confirm
  -> JSON / CSV yang sudah diverifikasi manusia
```

`preprocessing.py` memproses gambar, `ocr.py` memanggil executable OCR, `extraction.py` menangani kandidat field, `inference.py` menyatukan semuanya, `schemas.py` mendefinisikan output, dan `app/streamlit_app.py` menangani UI. Output total berupa **teks**, jangan melakukan perhitungan mata uang sebelum pengaturan locale dan currency disepakati. Field kosong berarti belum ada bukti memadai, bukan bukti bahwa field tidak tercetak.

## Menjalankan di Windows

Gunakan PowerShell dari root repository:

```powershell
cd "D:\porto\100 day\day 17\ReceiptReader"
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
winget install --id UB-Mannheim.TesseractOCR -e
& "C:\Program Files\Tesseract-OCR\tesseract.exe" --version
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py
```

Buka `http://localhost:8501`. Paket `pytesseract` bukan executable Tesseract; keduanya dibutuhkan. Bahasa `ind` hanya boleh diminta jika traineddata terpasang (`tesseract --list-langs`). GitHub mungkin belum memuat perubahan lokal untuk auto-detection path Windows; cek `git diff`.

## Kontrak empat field & pemeriksaan

| Field | Contoh data demonstrasi | Yang wajib ditinjau |
|---|---|---|
| `company` | `TOKO MAJU JAYA` | Bisa tertukar dengan logo, header, nomor telepon |
| `date` | `2025-04-12` | Format tanggal, transaksi vs tanggal cetak, validitas kalender |
| `address` | `Jl. Melati No. 123, Kel. Sukamaju, Kec. Cilandak, Jakarta Selatan 12450` | Alamat bertingkat, prefiks OCR `1 Jl.`, teks hilang |
| `total` | `241980` | Bedakan dari subtotal `228000`, jumlah bayar `250000`, dan uang kembali `8020`; validasi mata uang manual |

Contoh merupakan **gambar ilustratif/smoke case**, bukan data pembuktian akurasi produksi. Di UI, operator membaca raw OCR dan membandingkan dengan gambar sebelum mencentang verifikasi.

## Dataset dan asal-usul data

**SROIE / ICDAR 2019**: [sumber kompetisi resmi](https://rrc.cvc.uab.es/?ch=13). Dipakai dalam riset empat field struk Malaysia (company, date, address, total). Menurut `reports/split_audit.json`: 626 training; internal 501 train dan 125 validasi; 361 published test, dengan 8 overlap hash gambar dikeluarkan dari analisis berulang 353 gambar. Published test sudah dilihat/diinspeksi selama pengembangan sehingga **bukan untouched final test**.

**CORD v2 / NAVER**: [dataset HF](https://huggingface.co/datasets/naver-clova-ix/cord-v2). Riset memakai 800 contoh training dan memanfaatkan anotasi **total**; struktur `gt_parse` CORD tidak menyediakan empat field yang dapat disamakan langsung dengan SROIE. Jangan melatih company/date/address CORD memakai label yang tidak ada.

**Contoh foto UI**: hasil gambar ilustratif yang dipakai untuk smoke test. Tidak dihitung sebagai validasi struk pelanggan atau bukti generalisasi.

**Hak akses:** periksa lisensi asli tiap dataset, syarat unduhan, penggunaan komersial, atribusi dan apakah gambar boleh dipublikasikan. Raw receipt bisa mengandung nama, alamat, telepon, atau ID pesanan. Jangan meng-commit dataset mentah ke GitHub. Lisensi MIT repository hanya mencakup kode sumber yang berhak dilisensikan.

## Audit riset dan angka terukur

| Laporan | N / protokol | Hasil | Interpretasi yang diperbolehkan |
|---|---|---|---|
| `reports/v10_repeated_pixel_metrics.json` | 80 gambar SROIE yang telah diinspeksi sebelumnya | company exact 52,50%; date 75,00%; address 36,25%; total 55,00%; macro 54,6875%; keempatnya benar 5,00% | Diagnostik **repeated image/pixel**, bukan evaluasi independen |
| `reports/total_comparison_validation.json` | SROIE validation, fitur total | SROIE-only 80,8%; CORD-augmented 82,4% | Kinerja total pada **validasi** riset, bukan aplikasi |
| `reports/v10_summary.json` | CORD validation untuk total | 95% exact total | Hanya kondisi/protokol CORD; **bukan** akurasi empat field |

v10 dan baseline pada 80 repeated-pixel mempunyai angka yang **sama** dalam laporan. Jangan mengklaim peningkatan di protokol tersebut. Jangan samakan evaluasi teks anotasi dengan OCR dari piksel. Kesenjangan domain Malaysia → struk Indonesia harus diuji tersendiri.

### Audit penelitian yang harus diulang untuk release

1. Bekukan daftar hash gambar dan pembagian train/validation/test sebelum tuning.
2. Simpan mapping ID, sumber, label, hak pakai, serta OCR/preprocessing yang dieksekusi.
3. Lakukan pemilihan model hanya di validasi; identifikasi test yang pernah diperiksa sebagai diagnostic ulang.
4. Laporkan exact match masing-masing field, macro, all-four, dan kegagalan OCR beserta N dan protokol.
5. Sertakan confusion/error cases dan raw text berizin yang disamarkan; jangan unggah PII.
6. Untuk integrasi v10, audit file ZIP/model dan buat parity test pada **gambar identik** dengan notebook sebelum memberi label “v10 integrated”.

## Bukti, aset, dan publikasi

`assets/plots/01_partitions.png` dan `assets/plots/v10_comparison.png` ada di GitHub; beri keterangan bahwa itu grafik **riset**, bukan screenshot akurasi app. `reports/*.csv` dan `reports/*.json` memuat data audit yang sudah dipublikasi; cek lisensi dan apakah setiap baris ekspor mengandung teks pihak ketiga sebelum mengunggahnya lagi. `assets/screenshots/` di remote baru berisi `.gitkeep` saat audit; pindahkan **screenshot asli aplikasi** ke sana setelah menyensor informasi pribadi, misalnya `01_upload.png`, `02_review_four_fields.png`, `03_export_confirmed.png`.

`exports/` untuk CSV/JSON hasil pengguna bersifat lokal dan Gitignored. Jika ingin contoh publik, buat *synthetic fixture* sendiri berisi `filename,company,date,address,total,source_type,review_status`, lalu tulis jelas `demo_fixture` dan bukan benchmark. Jangan membuat grafik performa tanpa pengujian yang dijalankan.

## Struktur repo & aturan kepemilikan

Lihat [root README](../../README.md#repository-map) untuk daftar path repo yang telah diaudit. `models/README.md` menyatakan **belum ada model v10 terverifikasi untuk aplikasi**; `notebooks/receiptreader.ipynb` dan laporan riset sudah tersedia. `pass/README.md` berisi tata cara keamanan akses, **tidak boleh menyimpan password/token**. `AGENTS.md` adalah aturan source-of-truth.

## Keterbatasan dan claim boundaries

- Baseline saat ini **bukan model KIE v10**; menambah penyesuaian regex pada satu receipt tidak menunjukkan peningkatan ilmiah.
- Empat field benar pada satu contoh tidak berarti 100% akurasi.
- OCR mungkin salah mengenali angka, kehilangan alamat, atau salah menghubungkan nilai total dengan label.
- CORD dan SROIE memiliki anotasi berbeda; menggabungkan label secara otomatis adalah salah.
- “verified_by_user” adalah tindakan operator, **bukan** ground truth yang independen.
- Penggunaan produksi butuh pengujian lintas perangkat/toko/pencahayaan, akses pengguna, TLS, kebijakan retensi, perlindungan PII, dan recovery error.

## Testing dan reproduksibilitas

Gunakan Python 3.11, instal requirements, catat `tesseract --version`, versi `tessdata`, OS, seed dan revisi Git. Jalankan `pytest -q`; tes fungsi dengan teks tanpa gambar untuk memastikan ekstraksi dasar, lalu tes gambar via UI. **Perhatian**: `tests/test_extraction.py` yang terlihat di GitHub mengharapkan tanggal format lama `12/10/2026`; versi extractor lokal terbaru mengembalikan format ISO. Sesuaikan uji dengan spesifikasi yang disepakati dan ukur ulang—jangan melaporkan seluruh test lulus tanpa menjalankannya setelah update.

Tambahkan regresi untuk alamat `1 Jl.`, tanggal `12 Apr 2025`, baris `Subtotal/PPN/Jumlah Bayar/Kembalian/Total`, struk kosong, dua upload dengan nama sama, error Tesseract, dan ekspor tanpa verifikasi. Untuk angka akurasi gunakan dataset independen berlabel dan verifikasi anotator.

## Deploy dan privasi

Local Streamlit di `localhost:8501` sudah didemonstrasikan. **Belum ada deployment publik terverifikasi.** Server cloud membutuhkan biner Tesseract, pembatasan ukuran dan jumlah piksel, pembatasan request, penyimpanan sementara dengan penghapusan eksplisit, validasi tipe file, tidak ada log PII, TLS dan otorisasi. Hindari menyimpan gambar atau raw OCR ke sistem eksternal tanpa persetujuan.

## Troubleshooting

| Masalah | Penyebab / penyelesaian |
|---|---|
| `TesseractNotFoundError` | Install engine Tesseract Windows; panggil path `.exe` secara eksplisit atau perbaiki PATH |
| Language pack `ind` unavailable | Periksa `tesseract --list-langs`, pakai `eng` jika itu yang terinstal |
| Field tanggal kosong | Periksa apakah OCR mengenali `12 Apr 2025`, bukan cuma format numerik |
| Alamat kosong | Periksa raw OCR `1 Jl. Melati...`; gunakan normalisasi yang teruji dan tetap sediakan edit |
| Total menjadi jumlah bayar | Abaikan `Jumlah Bayar`/`Kembalian` dan gunakan label `Total`; laporkan ambigu kosong |
| Tes lama gagal | Periksa kontrak ISO tanggal dan update fixture tanpa mengubah evidence |
| File sama diunggah ulang | Session state lama dapat tertukar; gunakan hash konten dan reset verifikasi (pekerjaan berikutnya) |

## Roadmap

**P0:** audit parity GitHub vs lokal, perbarui unit test, amankan session state, screenshot nyata. **P1:** audit seluruh pipeline/model v10, identifikasi tipe artefak, tambahkan fixture per gambar dan parity; buat error CSV anonim. **P2:** dataset pengujian Indonesia berizin, anotasi independen, confidence/review handling yang terkalibrasi. **P3:** deployment terbatas dengan perlindungan data dan monitoring tanpa PII.

## FAQ

**Apakah ReceiptReader AI?** OCR adalah bagian visi komputer; aplikasi aktif memakai Tesseract dan aturan transparan, bukan model v10 yang terintegrasi.

**Apakah foto sampel cukup untuk evaluasi?** Tidak. Satu foto hanya smoke test.

**Mengapa CORD tidak langsung dipakai untuk empat field?** Anotasi target yang tersedia tidak sama dengan company/date/address/total pada SROIE.

**Apakah hasil CSV otomatis valid?** Tidak; hanya dapat diunduh setelah manusia menyetujui, dan pengguna tetap bertanggung jawab memverifikasi data.

**Bagaimana kontribusi kode?** Sertakan file/path, perintah reproduksi, hasil uji, perubahan kontrak, dan perbarui dokumentasi Indonesia–Inggris secara bersamaan.

## Lisensi dan pengakuan

Source code milik repository berada di bawah **MIT** sesuai `LICENSE`. Setiap dataset, pretrained model, engine OCR, dan gambar mengikuti lisensi/ketentuan masing-masing. Cantumkan sumber [SROIE](https://rrc.cvc.uab.es/?ch=13), [CORD v2](https://huggingface.co/datasets/naver-clova-ix/cord-v2), dan [Tesseract](https://github.com/tesseract-ocr/tesseract). Jangan klaim lisensi MIT memberi izin mendistribusikan data pihak ketiga.
