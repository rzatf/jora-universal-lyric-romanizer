import os
import sys
import json
import re
import urllib.request
import urllib.parse
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
    if re.search(r'[\uac00-\ud7a3]', text):
        converted = Romanizer(text).romanize()
        return re.sub(r'\s+', ' ', converted).strip()

    # Check for Japanese (Kanji/Kana)
    if re.search(r'[\u3040-\u30ff]', text):
        converted = kks.convert(text)
        converted_str = " ".join([item['hepburn'] for item in converted])
        return re.sub(r'\s+', ' ', converted_str).strip()

    # Check for Mandarin (Hanzi)
    if re.search(r'[\u4e00-\u9fff]', text):
        py_list = pinyin(text, style=Style.NORMAL)
        converted_str = " ".join([item[0] for item in py_list])
        return re.sub(r'\s+', ' ', converted_str).strip()

    # Fallback for English/Latin text
    return re.sub(r'\s+', ' ', text).strip()

def unescape_and_romajify(input_text):
    if not input_text.strip():
        return ""

    metadata_lines = []

    # Parse JSON structure if present, otherwise handle raw escaped strings
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
    result_lines = []
    for line in input_text.splitlines():
        match = re.match(r"^(\[\d{2}:\d{2}\.\d{2,3}\])(.*)", line)
        if match:
            timestamp, text = match.group(1), match.group(2)
            converted_text = romanize_text(text)
            result_lines.append(f"{timestamp} {converted_text}".strip())
        elif line.strip():
            result_lines.append(romanize_text(line))
        else:
            result_lines.append("")

    final_output = []
    if metadata_lines:
        final_output.extend(metadata_lines)
        final_output.append("")

    final_output.extend(result_lines)
    return "\r\n".join(final_output)

# Handler for online lyric search via LRCLIB API
# Action listener untuk pencarian lirik online
def search_lyrics():
    track = entry_track.get().strip()
    artist = entry_artist.get().strip()

    if not track:
        messagebox.showwarning("Warning", "Please enter at least a track title!")
        return

    status_label.configure(text="● Searching lyrics online...", text_color="#FF9F0A")
    root.update()

    try:
        query = f"track_name={urllib.parse.quote(track)}"
        if artist:
            query += f"&artist_name={urllib.parse.quote(artist)}"

        url = f"https://lrclib.net/api/get?{query}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                raw_json = response.read().decode('utf-8')
                input_box.delete("1.0", tk.END)
                input_box.insert(tk.END, raw_json)
                status_label.configure(text="● Lyrics found & fetched! Click 'Process & Romanize'", text_color="#30D158")
            else:
                status_label.configure(text="● Song not found.", text_color="#FF453A")
                messagebox.showinfo("Not Found", "Lyrics not found for the specified song.")
    except Exception as e:
        status_label.configure(text="● Search failed.", text_color="#FF453A")
        messagebox.showerror("Error", f"Failed to fetch lyrics: {e}")

# Handler for conversion process
def process_lyrics():
    raw_text = input_box.get("1.0", tk.END)
    if not raw_text.strip():
        messagebox.showwarning("Warning", "Input field is empty!")
        return
    
    result = unescape_and_romajify(raw_text)
    
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, result)
    
    pyperclip.copy(result)
    status_label.configure(text="● Successfully converted & copied to clipboard! (Ctrl+V)", text_color="#30D158")

# Handler for manual copy button
def copy_to_clipboard():
    final_text = output_box.get("1.0", tk.END).strip()
    if final_text:
        formatted_text = "\r\n".join(final_text.splitlines())
        pyperclip.copy(formatted_text)
        status_label.configure(text="● Output copied to clipboard!", text_color="#0A84FF")

# Handler for clear button
def clear_all():
    input_box.delete("1.0", tk.END)
    output_box.delete("1.0", tk.END)
    entry_track.delete(0, tk.END)
    entry_artist.delete(0, tk.END)
    status_label.configure(text="● Ready", text_color="#8E8E93")

# Main application window configuration
root = ctk.CTk()
root.title("JORA - Universal JSON Unescaper & Lyric Romanizer")
root.geometry("1150x820")
root.configure(fg_color="#141414")

# Set app icon for window titlebar and taskbar
icon_ico_path = resource_path("JORA_logo.ico")
if os.path.exists(icon_ico_path):
    root.iconbitmap(icon_ico_path)

# Color scheme definitions
COLOR_HEADER = "#141414"
COLOR_BG = "#1A1A1A"
COLOR_CARD = "#242426"
COLOR_TEXT_MAIN = "#FFFFFF"
COLOR_TEXT_MUTED = "#9A9A9E"

# Typography config using Bahnschrift and Cascadia Code
FONT_TITLE = ctk.CTkFont(family="Bahnschrift SemiLight", size=24, weight="bold")
FONT_SUBTITLE = ctk.CTkFont(family="Bahnschrift SemiLight", size=12)
FONT_LABEL = ctk.CTkFont(family="Bahnschrift SemiLight", size=14, weight="bold")
FONT_BTN = ctk.CTkFont(family="Bahnschrift", size=13)
FONT_CODE = ctk.CTkFont(family="Cascadia Code", size=13)

# Top header panel
header_frame = ctk.CTkFrame(root, fg_color=COLOR_HEADER, corner_radius=0, height=85)
header_frame.pack(fill=tk.X)

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

# Search Bar Panel
search_frame = ctk.CTkFrame(root, fg_color="#141414", corner_radius=10)
search_frame.pack(fill=tk.X, padx=24, pady=(13, 0))

search_top_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
search_top_frame.pack(fill=tk.X, padx=12, pady=(8, 2))

entry_track = ctk.CTkEntry(search_top_frame, placeholder_text="Track Title", font=FONT_BTN, width=280, height=36, fg_color=COLOR_CARD)
entry_track.pack(side=tk.LEFT, padx=(0, 8))

entry_artist = ctk.CTkEntry(search_top_frame, placeholder_text="Artist Name [Optional]", font=FONT_BTN, width=280, height=36, fg_color=COLOR_CARD)
entry_artist.pack(side=tk.LEFT, padx=(0, 8))

btn_search = ctk.CTkButton(search_top_frame, text="Fetch Lyrics", command=search_lyrics, font=FONT_BTN, fg_color="#BF5AF2", hover_color="#A239D4", text_color="white", height=36, width=130, corner_radius=8)
btn_search.pack(side=tk.RIGHT)

search_bottom_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
search_bottom_frame.pack(fill=tk.X, padx=12, pady=(0, 6))

lbl_info = ctk.CTkLabel(search_bottom_frame, text="* Powered by LRCLIB API", font=FONT_SUBTITLE, text_color=COLOR_TEXT_MUTED)
lbl_info.pack(side=tk.LEFT, padx=(2, 0))
# Main layout grid container
main_frame = ctk.CTkFrame(root, fg_color=COLOR_BG, corner_radius=0)
main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

content_container = ctk.CTkFrame(main_frame, fg_color=COLOR_BG, corner_radius=0)
content_container.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)

content_container.columnconfigure(0, weight=1)
content_container.columnconfigure(1, weight=1)
content_container.rowconfigure(1, weight=1)

# Section headers
lbl_in = ctk.CTkLabel(content_container, text="INPUT (RAW JSON / ORIGINAL LRC)", font=FONT_LABEL, text_color=COLOR_TEXT_MAIN)
lbl_in.grid(row=0, column=0, sticky="w", padx=2, pady=(0, 10))

lbl_out = ctk.CTkLabel(content_container, text="FINAL OUTPUT (CLEAN / ROMANIZED)", font=FONT_LABEL, text_color=COLOR_TEXT_MAIN)
lbl_out.grid(row=0, column=1, sticky="w", padx=2, pady=(0, 10))

# Dual text editors
input_box = ctk.CTkTextbox(content_container, font=FONT_CODE, fg_color=COLOR_CARD, text_color="#FFFFFF", corner_radius=12, border_width=1, border_color="#333336", activate_scrollbars=True)
input_box.grid(row=1, column=0, sticky="nsew", padx=(0, 12), pady=0)

output_box = ctk.CTkTextbox(content_container, font=FONT_CODE, fg_color=COLOR_CARD, text_color="#FFFFFF", corner_radius=12, border_width=1, border_color="#333336", activate_scrollbars=True)
output_box.grid(row=1, column=1, sticky="nsew", padx=(12, 0), pady=0)

# Bottom action controls bar
btn_frame = ctk.CTkFrame(main_frame, fg_color=COLOR_BG, corner_radius=0)
btn_frame.pack(fill=tk.X, padx=24, pady=(10, 20))

btn_convert = ctk.CTkButton(btn_frame, text="Process & Romanize", command=process_lyrics, font=FONT_BTN, fg_color="#0A84FF", hover_color="#0066CC", text_color="white", corner_radius=10, height=48, width=190)
btn_convert.pack(side=tk.LEFT, padx=(0, 12))

btn_copy = ctk.CTkButton(btn_frame, text="Copy Final Result", command=copy_to_clipboard, font=FONT_BTN, fg_color="#30D158", hover_color="#24A143", text_color="white", corner_radius=10, height=48, width=190)
btn_copy.pack(side=tk.LEFT)

btn_clear = ctk.CTkButton(btn_frame, text="Clear All", command=clear_all, font=FONT_BTN, fg_color="#FF453A", hover_color="#D70015", text_color="white", corner_radius=10, height=48, width=130)
btn_clear.pack(side=tk.RIGHT)

# Bottom status bar indicator
status_frame = ctk.CTkFrame(root, fg_color=COLOR_HEADER, corner_radius=0, height=38)
status_frame.pack(side=tk.BOTTOM, fill=tk.X)

status_label = ctk.CTkLabel(status_frame, text="● Ready", font=FONT_SUBTITLE, text_color=COLOR_TEXT_MUTED)
status_label.pack(side=tk.LEFT, padx=24, pady=6)

root.mainloop()