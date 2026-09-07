import json
import re
import sys
import pykakasi
import pyperclip

# Inisialisasi converter
kks = pykakasi.kakasi()

def unescape_and_romajify(input_text):
    # 1. Unescape JSON jika input berupa JSON string/object
    try:
        data = json.loads(input_text)
        if isinstance(data, dict):
            input_text = data.get("syncedLyrics") or data.get("plainLyrics") or input_text
    except Exception:
        # Unescape manual jika bukan JSON utuh
        input_text = input_text.replace(r"\n", "\n").replace(r'\"', '"').replace(r"\\", "\\")

    # 2. Proses baris per baris
    result_lines = []
    for line in input_text.splitlines():
        # Cek apakah ada timestamp [mm:ss.xx]
        match = re.match(r"^(\[\d{2}:\d{2}\.\d{2,3}\])(.*)", line)
        if match:
            timestamp, text = match.group(1), match.group(2)
            converted = kks.convert(text)
            romaji = " ".join([item['hepburn'] for item in converted])
            result_lines.append(f"{timestamp} {romaji}")
        elif line.strip():
            converted = kks.convert(line)
            romaji = " ".join([item['hepburn'] for item in converted])
            result_lines.append(romaji)
        else:
            result_lines.append("")

    return "\n".join(result_lines)

if __name__ == "__main__":
    print("==============================================")
    print("    LRC & JSON TO ROMAJI CONVERTER (OFFLINE)  ")
    print("==============================================")
    print("1. Paste teks lirik / JSON kamu di bawah ini.")
    print("2. Jika sudah selesai, tekan Ctrl + Z lalu tekan Enter:\n")

    raw_input = sys.stdin.read()

    if not raw_input.strip():
        print("\n[!] Input kosong. Program dibatalkan.")
        sys.exit()

    output = unescape_and_romajify(raw_input)

    # Otomatis Copy ke Clipboard
    pyperclip.copy(output)

    # Simpan juga ke file output.lrc
    with open("output.lrc", "w", encoding="utf-8") as f:
        f.write(output)

    print("\n----------------------------------------------")
    print("[SUCCESS] Hasil Romaji sudah OTOMATIS TER-COPY!")
    print("Silakan langsung tekan Ctrl + V di mana saja.")
    print("----------------------------------------------")
