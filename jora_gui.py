import os
import sys
import json
import re
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image
import pykakasi
import pyperclip
from pypinyin import pinyin, Style
from korean_romanizer.romanizer import Romanizer

# Resolve asset paths for PyInstaller standalone build
# Fungsi penangan path internal saat dibungkus ke .exe oleh PyInstaller
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# UI theme configuration
# Set tema tampilan GUI ke dark mode
ctk.set_appearance_mode("Dark")

# Initialize language converter engines
# Inisialisasi engine converter
kks = pykakasi.kakasi()

def romanize_text(text):
    if not text.strip():
        return ""

    # Check for Korean (Hangul)
    # Deteksi teks Bahasa Korea
    if re.search(r'[\uac00-\ud7a3]', text):
        return Romanizer(text).romanize()

    # Check for Japanese (Kanji/Kana)
    # Deteksi teks Bahasa Jepang
    if re.search(r'[\u3040-\u30ff]', text):
        converted = kks.convert(text)
        return " ".join([item['hepburn'] for item in converted])

    # Check for Mandarin (Hanzi)
    # Deteksi teks Bahasa Mandarin
    if re.search(r'[\u4e00-\u9fff]', text):
        py_list = pinyin(text, style=Style.NORMAL)
        return " ".join([item[0] for item in py_list])

    # Fallback for English/Latin text
    # Teks latin/Inggris tetap dipertahankan
    return text

def unescape_and_romajify(input_text):
    if not input_text.strip():
        return ""

    metadata_lines = []

    # Parse JSON structure if present, otherwise handle raw escaped strings
    # Cek apakah input berbentuk JSON, kalau bukan langsung unescape string biasa
    try:
        data = json.loads(input_text)
        if isinstance(data, dict):
            track_name = data.get("trackName") or data.get("name")
            artist_name = data.get("artistName")
            album_name = data.get("albumName")

            if track_name:
                metadata_lines.append(f"[ti:{track_name}]")
            if artist_name:
                metadata_lines.append(f"[ar:{artist_name}]")
            if album_name:
                metadata_lines.append(f"[al:{album_name}]")

            input_text = data.get("syncedLyrics") or data.get("plainLyrics") or input_text
    except Exception:
        input_text = input_text.replace(r"\n", "\n").replace(r'\"', '"').replace(r"\\", "\\")

    # Process lyrics line by line while preserving timestamps
    # Proses baris per baris sambil menjaga timestamp .lrc tetap utuh
    result_lines = []
    for line in input_text.splitlines():
        match = re.match(r"^(\[\d{2}:\d{2}\.\d{2,3}\])(.*)", line)
        if match:
            timestamp, text = match.group(1), match.group(2)
            converted_text = romanize_text(text)
            result_lines.append(f"{timestamp} {converted_text}")
        elif line.strip():
            result_lines.append(romanize_text(line))
        else:
            result_lines.append("")

    final_output = []
    if metadata_lines:
        final_output.extend(metadata_lines)
        final_output.append("")

    final_output.extend(result_lines)
    return "\n".join(final_output)

# Handler for conversion process
# Action listener untuk tombol proses
def process_lyrics():
    raw_text = input_box.get("1.0", tk.END)
    if not raw_text.strip():
        messagebox.showwarning("Peringatan", "Kolom input masih kosong!")
        return
    
    result = unescape_and_romajify(raw_text)
    
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, result)
    
    pyperclip.copy(result)
    status_label.configure(text="● Berhasil dikonversi & disalin ke clipboard! (Ctrl+V)", text_color="#30D158")

# Handler for manual copy button
# Action listener untuk tombol copy
def copy_to_clipboard():
    final_text = output_box.get("1.0", tk.END).strip()
    if final_text:
        pyperclip.copy(final_text)
        status_label.configure(text="● Teks dari kolom kanan berhasil disalin!", text_color="#0A84FF")

# Handler for clear button
# Action listener untuk reset kolom
def clear_all():
    input_box.delete("1.0", tk.END)
    output_box.delete("1.0", tk.END)
    status_label.configure(text="● Siap", text_color="#8E8E93")

# Main application window configuration
# Setup jendela utama
root = ctk.CTk()
root.title("JORA - Universal JSON Unescaper & Lyric Romanizer")
root.geometry("1150x760")
root.configure(fg_color="#141414")

# Set app icon for window titlebar and taskbar
# Pasang icon di titlebar dan taskbar
icon_ico_path = resource_path("JORA_logo.ico")
if os.path.exists(icon_ico_path):
    root.iconbitmap(icon_ico_path)

# Color scheme definitions
# Palette warna UI
COLOR_HEADER = "#141414"
COLOR_BG = "#1A1A1A"
COLOR_CARD = "#242426"
COLOR_TEXT_MAIN = "#FFFFFF"
COLOR_TEXT_MUTED = "#9A9A9E"

# Typography config using Bahnschrift and Cascadia Code
# Konfigurasi font UI
FONT_TITLE = ctk.CTkFont(family="Bahnschrift SemiLight", size=24, weight="bold")
FONT_SUBTITLE = ctk.CTkFont(family="Bahnschrift SemiLight", size=12)
FONT_LABEL = ctk.CTkFont(family="Bahnschrift SemiLight", size=14, weight="bold")
FONT_BTN = ctk.CTkFont(family="Bahnschrift", size=14)
FONT_CODE = ctk.CTkFont(family="Cascadia Code", size=13)

# Top header panel
# Area header atas
header_frame = ctk.CTkFrame(root, fg_color=COLOR_HEADER, corner_radius=0, height=85)
header_frame.pack(fill=tk.X)

# Load header icon
# Muat logo di header UI
if os.path.exists(icon_ico_path):
    try:
        logo_pil = Image.open(icon_ico_path)
        logo_ctk = ctk.CTkImage(light_image=logo_pil, dark_image=logo_pil, size=(46, 46))
        logo_label = ctk.CTkLabel(header_frame, image=logo_ctk, text="")
        logo_label.pack(side=tk.LEFT, padx=(24, 14), pady=16)
    except Exception as e:
        print("Failed to render header logo:", e)

title_label = ctk.CTkLabel(header_frame, text="JORA", font=FONT_TITLE, text_color=COLOR_TEXT_MAIN)
title_label.pack(side=tk.LEFT, padx=(0, 12), pady=16)

subtitle_label = ctk.CTkLabel(header_frame, text="Universal JSON Unescaper & Romanizer (JP / KR / CN / EN)", font=FONT_SUBTITLE, text_color=COLOR_TEXT_MUTED)
subtitle_label.pack(side=tk.LEFT, pady=(22, 16))

# Main layout grid container
# Container utama untuk text box input & output
main_frame = ctk.CTkFrame(root, fg_color=COLOR_BG, corner_radius=0)
main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

content_container = ctk.CTkFrame(main_frame, fg_color=COLOR_BG, corner_radius=0)
content_container.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)

content_container.columnconfigure(0, weight=1)
content_container.columnconfigure(1, weight=1)
content_container.rowconfigure(1, weight=1)

# Section headers
lbl_in = ctk.CTkLabel(content_container, text="INPUT (JSON / LRC)", font=FONT_LABEL, text_color=COLOR_TEXT_MAIN)
lbl_in.grid(row=0, column=0, sticky="w", padx=2, pady=(0, 10))

lbl_out = ctk.CTkLabel(content_container, text="OUTPUT FINAL (CLEAN / ROMANIZED)", font=FONT_LABEL, text_color=COLOR_TEXT_MAIN)
lbl_out.grid(row=0, column=1, sticky="w", padx=2, pady=(0, 10))

# Dual text editors
# Area input dan output teks
input_box = ctk.CTkTextbox(
    content_container, font=FONT_CODE, fg_color=COLOR_CARD, text_color="#FFFFFF", 
    corner_radius=12, border_width=1, border_color="#333336", activate_scrollbars=True
)
input_box.grid(row=1, column=0, sticky="nsew", padx=(0, 12), pady=0)

output_box = ctk.CTkTextbox(
    content_container, font=FONT_CODE, fg_color=COLOR_CARD, text_color="#FFFFFF", 
    corner_radius=12, border_width=1, border_color="#333336", activate_scrollbars=True
)
output_box.grid(row=1, column=1, sticky="nsew", padx=(12, 0), pady=0)

# Bottom action controls bar
# Barisan tombol di bagian bawah
btn_frame = ctk.CTkFrame(main_frame, fg_color=COLOR_BG, corner_radius=0)
btn_frame.pack(fill=tk.X, padx=24, pady=(10, 20))

btn_convert = ctk.CTkButton(
    btn_frame, text="Process & Romanize", command=process_lyrics, 
    font=FONT_BTN, fg_color="#0A84FF", hover_color="#0066CC", text_color="white",
    corner_radius=10, height=48, width=190
)
btn_convert.pack(side=tk.LEFT, padx=(0, 12))

btn_copy = ctk.CTkButton(
    btn_frame, text="Copy Final Result", command=copy_to_clipboard, 
    font=FONT_BTN, fg_color="#30D158", hover_color="#24A143", text_color="white",
    corner_radius=10, height=48, width=190
)
btn_copy.pack(side=tk.LEFT)

btn_clear = ctk.CTkButton(
    btn_frame, text="Clean", command=clear_all, 
    font=FONT_BTN, fg_color="#FF453A", hover_color="#D70015", text_color="white",
    corner_radius=10, height=48, width=130
)
btn_clear.pack(side=tk.RIGHT)

# Bottom status bar indicator
# Baris status sistem
status_frame = ctk.CTkFrame(root, fg_color=COLOR_HEADER, corner_radius=0, height=38)
status_frame.pack(side=tk.BOTTOM, fill=tk.X)

status_label = ctk.CTkLabel(status_frame, text="● Ready", font=FONT_SUBTITLE, text_color=COLOR_TEXT_MUTED)
status_label.pack(side=tk.LEFT, padx=24, pady=6)

root.mainloop()