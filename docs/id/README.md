# ReceiptReader — dokumentasi Indonesia

**Masalah:** Transkripsi struk manual lambat, namun OCR bisa salah membaca merchant, tanggal, alamat, dan total. Sistem ini membantu mengisi field kandidat dan mewajibkan verifikasi manusia sebelum ekspor.

**Status:** Tahap aplikasi dasar. Backend yang berjalan adalah Tesseract + heuristik transparan, belum integrasi eksperimen v10. Empat field disediakan di form; `address` sengaja dibiarkan kosong karena tingkat kesalahan historis tinggi. Jangan sebut hasil ini sebagai akurasi v10.

**Alur:** upload gambar → normalisasi orientasi/kontras → OCR → ekstraksi kandidat → koreksi field → konfirmasi → CSV/JSON.

**Jalankan:** lihat README root; install Tesseract terpisah dari pip. Modul `src/receiptreader` dipisahkan dari `app` agar dapat diuji independen.

**Sumber data:** SROIE sebagai protokol riset struk Malaysia; CORD v2 sebagai sumber anotasi berbeda (bukan label company/address/date yang dapat dipakai langsung). Tidak mendistribusikan ulang data pihak ketiga.

**Sebelum rilis:** audit ZIP notebook v10, verifikasi semua file model dan konfigurasi, tambah parity test pre-processing dan uji gambar mandiri. Laporkan kesalahan per field; sediakan jalur koreksi. Data struk bisa mengandung informasi pribadi sehingga jangan dicatat ke log server atau diunggah ke repo.
