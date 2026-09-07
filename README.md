# 🎵 JORA - Universal JSON Unescaper & Lyric Romanizer

**JORA** is a sleek, modern Windows desktop application built to clean JSON-escaped lyrics and automatically convert Japanese (Romaji), Korean (Romaja), and Mandarin (Pinyin) lyrics into clean, romanized formats while preserving `.lrc` timestamps and extracting metadata.

## ✨ Features
- **JSON Unescaper**: Automatically extracts plain/synced lyrics from raw JSON responses and cleans escaped sequences (`\n`, `\"`, etc.).
- **Automatic Metadata Extraction**: Extracts `[ti: Track]`, `[ar: Artist]`, and `[al: Album]` tags automatically when available in JSON.
- **Multi-Language Romanization**:
  - 🇯🇵 **Japanese**: Kanji/Kana to Romaji (`pykakasi`)
  - 🇰🇷 **Korean**: Hangul to Romanized Korean (`korean_romanizer`)
  - 🇨🇳 **Mandarin**: Hanzi to Pinyin (`pypinyin`)
  - 🇬🇧 **English/Latin**: Retains original text without modification
- **Timestamp Preservation**: Keeps `.lrc` timestamp alignment intact (`[mm:ss.xx]`).
- **Clipboard Integration**: Automatically copies converted lyrics to your clipboard for instant `Ctrl+V` pasting.
- **Modern Dark UI**: Built with `CustomTkinter` using Bahnschrift typography and rounded corners.

## 🛠️ Tech Stack
- **Language**: Python 3.x
- **GUI Framework**: `CustomTkinter`
- **NLP / Transliteration**: `pykakasi`, `pypinyin`, `korean_romanizer`
- **Utilities**: `pyperclip`, `Pillow`

## 🚀 Running Locally

1. **Clone the repository**:
   git clone [https://github.com/rzatf/jora-universal-lyric-romanizer.git](https://github.com/rzatf/jora-universal-lyric-romanizer.git)
   cd jora-universal-lyric-romanizer

2. **Install dependencies**:
   pip install customtkinter pykakasi pypinyin korean_romanizer pyperclip Pillow

3. **Run the application**:
   python jora_gui.py

## 📦 Building Executable (.exe)
Run the provided `build.bat` or execute PyInstaller manually:
pyinstaller --noconsole --onefile --name "JORA" --icon=JORA_logo.ico --add-data "JORA_logo.ico;." --add-data "C:\Users\ASUS\AppData\Roaming\Python\Python314\site-packages\pykakasi;pykakasi" jora_gui.py
