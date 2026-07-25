#!/usr/bin/env python3
# pip install requests python-dotenv --break-system-packages
#
# ============================================================
#  SUPER CONVERTER — powered by FreeConvert API
# ============================================================
#  Cara pakai:
#    1) Isi API key di file .env (satu folder sama script ini)
#         FREECONVERT_API_KEY=api_production_xxxxxxxx
#    2) Jalankan: python3 converter.py
#    3) Pilih menu mode converter (ketik nomor, Enter)
#    4) Masukkan path input_file
#    5) Konfirmasi Y/N
#    6) Selesai — file hasil convert otomatis muncul di folder
#       yang sama dengan input_file, dengan nama:
#         {namafile}.{formatFileHasilConvert}
# ============================================================

import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# ================= KONFIGURASI =================
# .env dicari relatif ke lokasi file script ini, bukan ke folder tempat
# command dijalankan — jadi tetap kebaca walau script dipanggil dari folder lain.
_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

API_KEY = os.getenv("FREECONVERT_API_KEY", "").strip()

AUDIO_BITRATE = "192k"   # dipakai untuk konversi ke format audio
PNG_DPI       = 200      # dipakai untuk konversi dari pdf ke image
# =================================================

BANNER = """
\033[95m
   ▄████▄   ▒█████   ███▄    █ ██▒   █▓▓█████  ██▀███  ▄▄▄█████▓▓█████  ██▀███
  ▒██▀ ▀█  ▒██▒  ██▒ ██ ▀█   █▓██░   █▒▓█   ▀ ▓██ ▒ ██▒▓  ██▒ ▓▒▓█   ▀ ▓██ ▒ ██▒
  ▒▓█    ▄ ▒██░  ██▒▓██  ▀█ ██▓██  █▒░▒███   ▓██ ░▄█ ▒▒ ▓██░ ▒░▒███   ▓██ ░▄█ ▒
  ▒▓▓▄ ▄██▒▒██   ██░▓██▒  ▐▌██▒██ █░░▒▓█  ▄ ▒██▀▀█▄  ░ ▓██▓ ░ ▒▓█  ▄ ▒██▀▀█▄
  ▒ ▓███▀ ░░ ████▓▒░▒██░   ▓██▒▒▀█░  ░▒████▒░██▓ ▒██▒  ▒██▒ ░ ░▒████▒░██▓ ▒██▒
  ░ ░▒ ▒  ░░ ▒░▒░▒░ ░ ▒░   ▒ ▒░ ▐░  ░░ ▒░ ░░ ▒▓ ░▒▓░  ▒ ░░   ░░ ▒░ ░░ ▒▓ ░▒▓░
    ░  ▒     ░ ▒ ▒░ ░ ░░   ░ ▒░░ ░░   ░ ░  ░  ░▒ ░ ▒░    ░     ░ ░  ░  ░▒ ░ ▒░
  ░        ░ ░ ░ ▒     ░   ░ ░   ░░     ░     ░░   ░   ░         ░     ░░   ░
  ░ ░          ░ ░           ░    ░     ░  ░   ░                 ░  ░   ░
  ░\033[0m
"""

BASE = "https://api.freeconvert.com/v1"
HEAD = {"Authorization": f"Bearer {API_KEY}"}

C_OK, C_ERR, C_INFO, C_DIM, C_WARN, C_TITLE, C_R = (
    "\033[92m", "\033[91m", "\033[94m", "\033[90m", "\033[93m", "\033[96m", "\033[0m"
)


def die(msg):
    print(f"{C_ERR}[!] {msg}{C_R}")
    sys.exit(1)


def bar(pct, width=30):
    fill = int(width * pct)
    return C_OK + "█" * fill + C_DIM + "░" * (width - fill) + C_R


def human(n):
    for u in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.1f}{u}"
        n /= 1024
    return f"{n:.1f}TB"


# ============================================================
#  DAFTAR MODE CONVERTER — super lengkap, per kategori
# ============================================================
# Setiap entri: key nomor -> (label_tampilan, in_fmt, out_fmt, options_fn)
# in_fmt "*" artinya format input mengikuti ekstensi file yang di-input user.

def opt_none():
    return {}


def opt_audio_bitrate():
    return {"audio_bitrate": AUDIO_BITRATE}


def opt_png_dpi():
    return {"dpi": PNG_DPI}


MENU = {
    "VIDEO": [
        ("mp4 → mp3",   "mp4", "mp3", opt_audio_bitrate),
        ("mp4 → gif",   "mp4", "gif", opt_none),
        ("mp4 → avi",   "mp4", "avi", opt_none),
        ("mp4 → mov",   "mp4", "mov", opt_none),
        ("mp4 → mkv",   "mp4", "mkv", opt_none),
        ("mp4 → webm",  "mp4", "webm", opt_none),
        ("mov → mp4",   "mov", "mp4", opt_none),
        ("mkv → mp4",   "mkv", "mp4", opt_none),
        ("avi → mp4",   "avi", "mp4", opt_none),
        ("webm → mp4",  "webm", "mp4", opt_none),
    ],
    "AUDIO": [
        ("mp3 → wav",   "mp3", "wav", opt_none),
        ("wav → mp3",   "wav", "mp3", opt_audio_bitrate),
        ("mp3 → aac",   "mp3", "aac", opt_audio_bitrate),
        ("mp3 → flac",  "mp3", "flac", opt_none),
        ("flac → mp3",  "flac", "mp3", opt_audio_bitrate),
        ("m4a → mp3",   "m4a", "mp3", opt_audio_bitrate),
        ("ogg → mp3",   "ogg", "mp3", opt_audio_bitrate),
    ],
    "IMAGE": [
        ("png → jpg",   "png", "jpg", opt_none),
        ("jpg → png",   "jpg", "png", opt_none),
        ("png → pdf",   "png", "pdf", opt_none),
        ("jpg → pdf",   "jpg", "pdf", opt_none),
        ("webp → png",  "webp", "png", opt_none),
        ("png → webp",  "png", "webp", opt_none),
        ("heic → jpg",  "heic", "jpg", opt_none),
        ("svg → png",   "svg", "png", opt_none),
        ("bmp → png",   "bmp", "png", opt_none),
        ("gif → mp4",   "gif", "mp4", opt_none),
    ],
    "DOCUMENT": [
        ("pdf → png",   "pdf", "png", opt_png_dpi),
        ("pdf → jpg",   "pdf", "jpg", opt_png_dpi),
        ("pdf → docx",  "pdf", "docx", opt_none),
        ("docx → pdf",  "docx", "pdf", opt_none),
        ("pdf → txt",   "pdf", "txt", opt_none),
        ("pptx → pdf",  "pptx", "pdf", opt_none),
        ("xlsx → pdf",  "xlsx", "pdf", opt_none),
        ("xlsx → csv",  "xlsx", "csv", opt_none),
        ("csv → xlsx",  "csv", "xlsx", opt_none),
        ("txt → pdf",   "txt", "pdf", opt_none),
        ("html → pdf",  "html", "pdf", opt_none),
        ("epub → pdf",  "epub", "pdf", opt_none),
    ],
    "ARCHIVE": [
        ("zip → rar",   "zip", "rar", opt_none),
        ("rar → zip",   "rar", "zip", opt_none),
        ("7z → zip",    "7z", "zip", opt_none),
    ],
}


def build_flat_menu():
    """Gabungkan semua kategori jadi satu list bernomor urut untuk ditampilkan & dipilih."""
    flat = []
    for category, items in MENU.items():
        for (label, in_fmt, out_fmt, opt_fn) in items:
            flat.append((category, label, in_fmt, out_fmt, opt_fn))
    return flat


def print_menu(flat):
    print(f"{C_TITLE}Pilih mode converter:{C_R}\n")
    current_category = None
    for idx, (category, label, in_fmt, out_fmt, _) in enumerate(flat, start=1):
        if category != current_category:
            print(f"{C_WARN}— {category} —{C_R}")
            current_category = category
        print(f"  [{idx:02d}] {label}")
    print()


def ask_menu_choice(flat):
    print_menu(flat)
    while True:
        raw = input(f"{C_INFO}Ketik nomor menu lalu Enter: {C_R}").strip()
        if not raw.isdigit():
            print(f"{C_ERR}[!] Masukkan angka nomor menu.{C_R}")
            continue
        n = int(raw)
        if 1 <= n <= len(flat):
            return flat[n - 1]
        print(f"{C_ERR}[!] Nomor di luar daftar (1-{len(flat)}).{C_R}")


def ask_input_file(expected_ext):
    while True:
        raw = input(f"{C_INFO}Masukkan path input_file: {C_R}").strip().strip('"').strip("'")
        if not raw:
            print(f"{C_ERR}[!] Path tidak boleh kosong.{C_R}")
            continue
        src = Path(raw).expanduser()
        if not src.exists():
            print(f"{C_ERR}[!] File tidak ditemukan: {src}{C_R}")
            continue
        if not src.is_file():
            print(f"{C_ERR}[!] Path ini bukan file: {src}{C_R}")
            continue
        actual_ext = src.suffix.lower().lstrip(".")
        if actual_ext != expected_ext.lower():
            print(f"{C_WARN}[?] Ekstensi file '.{actual_ext}' tidak sama dengan yang diharapkan "
                  f"'.{expected_ext}' untuk mode ini.{C_R}")
            confirm = input(f"{C_INFO}    Tetap lanjutkan? (Y/N): {C_R}").strip().lower()
            if confirm != "y":
                continue
        return src


def ask_confirm(label, src, out):
    print()
    print(f"{C_TITLE}Ringkasan:{C_R}")
    print(f"  Mode    : {label}")
    print(f"  Input   : {src}")
    print(f"  Output  : {out}")
    while True:
        raw = input(f"{C_INFO}Lanjutkan konversi? (Y/N): {C_R}").strip().lower()
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print(f"{C_ERR}[!] Jawab Y atau N.{C_R}")


def convert(src, out, in_fmt, out_fmt, options_fn):
    print(f"\n{C_INFO}[1/4]{C_R} Membuat job  {C_DIM}({in_fmt} → {out_fmt}){C_R}")

    job = requests.post(f"{BASE}/process/jobs", headers=HEAD, json={
        "tasks": {
            "import-1": {"operation": "import/upload"},
            "convert-1": {
                "operation": "convert",
                "input": "import-1",
                "input_format": in_fmt,
                "output_format": out_fmt,
                "options": options_fn()
            },
            "export-1": {"operation": "export/url", "input": "convert-1"}
        }
    }).json()
    if "id" not in job:
        die(f"Gagal membuat job: {job}")

    upload_task = next(t for t in job["tasks"] if t["operation"] == "import/upload")
    upload_url = upload_task["result"]["form"]["url"]
    upload_params = upload_task["result"]["form"]["parameters"]

    print(f"{C_INFO}[2/4]{C_R} Upload {src.name}  {C_DIM}({human(src.stat().st_size)}){C_R}")
    with open(src, "rb") as f:
        requests.post(upload_url, data=upload_params, files={"file": f})

    print(f"{C_INFO}[3/4]{C_R} Konversi berjalan...")
    job_id = job["id"]
    export_urls = []
    for i in range(60):
        status = requests.get(f"{BASE}/process/jobs/{job_id}", headers=HEAD).json()
        state = status.get("status")
        print("\r" + bar(min((i + 1) / 20, 0.95)) + f"  {state or '...'}   ", end="", flush=True)
        if state == "completed":
            export_task = next(t for t in status["tasks"] if t["name"] == "export-1")
            res = export_task["result"]
            export_urls = res.get("files", [res]) if isinstance(res, dict) and "files" in res else [res]
            break
        if state == "failed":
            die("Konversi gagal di server.")
        time.sleep(2)
    print()

    if not export_urls:
        die("Timeout menunggu hasil.")

    print(f"{C_INFO}[4/4]{C_R} Download hasil...")

    # pdf→png dkk bisa multi-halaman → auto numbering, tetap taat pola {namafile}.{ext}
    if len(export_urls) > 1:
        for idx, item in enumerate(export_urls, start=1):
            url = item["url"] if isinstance(item, dict) else item
            r = requests.get(url)
            page_out = out.with_stem(f"{out.stem}_{idx}")
            page_out.write_bytes(r.content)
            print(f"      {C_OK}✓{C_R} {page_out}  {C_DIM}({human(len(r.content))}){C_R}")
    else:
        item = export_urls[0]
        url = item["url"] if isinstance(item, dict) else item
        r = requests.get(url)
        out.write_bytes(r.content)
        print(bar(1.0))
        print(f"{C_OK}[✓] Selesai{C_R} → {out}  {C_DIM}({human(len(r.content))}){C_R}")


def run():
    if not API_KEY:
        die(
            "FREECONVERT_API_KEY belum diset.\n"
            "    Buat file .env di folder yang sama dengan script ini, isi:\n"
            "      FREECONVERT_API_KEY=api_production_xxxxxxxx"
        )

    flat = build_flat_menu()
    category, label, in_fmt, out_fmt, options_fn = ask_menu_choice(flat)

    src = ask_input_file(in_fmt)
    out = src.with_suffix(f".{out_fmt}")  # {namafile}.{formatFileHasilConvert}, path sama dgn input

    if out.exists():
        print(f"{C_WARN}[?] File output sudah ada dan akan ditimpa: {out}{C_R}")

    if not ask_confirm(label, src, out):
        print(f"{C_DIM}Dibatalkan.{C_R}")
        return

    convert(src, out, in_fmt, out_fmt, options_fn)


if __name__ == "__main__":
    print(BANNER)
    try:
        run()
    except KeyboardInterrupt:
        print(f"\n{C_DIM}Dibatalkan oleh user.{C_R}")
