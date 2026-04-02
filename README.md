# 🔍 Google Search Console - Keyword Analyzer Tool 🚀

This is a Python-based tool with a simple Graphical User Interface (GUI) that connects to the Google Search Console (GSC) API. It helps website owners and SEO specialists figure out if their targeted keywords are currently ranking on Google.

![GSC Analyzer Tool Preview](https://via.placeholder.com/800x400.png?text=GSC+GUI+Screenshot)

## ✨ Features
- **GUI & CLI Support:** You can run it directly from the console or via a very simple Matrix-styled Tkinter GUI.
- **Bulk Keyword Checking:** Upload a `.txt` or `.csv` file with your keywords (one per line) and check all of them at once.
- **Match Types:** 
  - 🎯 **Exact Match:** The user typed your keyword exactly.
  - 🔗 **Partial Match:** Your keyword is part of a longer 'long-tail' query that ranks.
- **Opportunity Detection:** The tool cleanly outputs an `"❌ NOT FOUND / İçerik Fırsatı"` category highlighting keywords that you are NOT ranking for — an excellent list for new blog topics!
- **Data Export:** Automatically generated `.csv` and `.json` reports containing Impressions, Clicks, CTR, and Position metrics.

## 📦 Requirements

- Python 3.7+
- Windows (The `.bat` explicitly targets Windows but the python `.py` scripts work safely on macOS/Linux).

## 🚀 Quick Setup

1. **Clone the Repo:**
   ```bash
   git clone https://github.com/YourUsername/GSC-Keyword-Analyzer.git
   cd GSC-Keyword-Analyzer
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get Google Search Console Credentials:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/) and create a project.
   - Enable **Google Search Console API**.
   - Go to Credentials -> Create **Service Account**.
   - Manage Keys -> Add New Key -> Download `.json` file.
   - Put this downloaded `.json` file inside the program folder.
   
4. **Grant Permissions in GSC:**
   - Open the `.json` file you downloaded and copy the `client_email`.
   - Go to your real [Google Search Console Dashboard](https://search.google.com/search-console).
   - Navigate to **Settings > Users and permissions** -> **Add User**.
   - Paste the service account email and give it "Restricted" or "Full" access.

## 💻 How to Use

### Using the Graphic Interface (GUI)
Simply double click on `start_gui.bat` on Windows. 
1. Select your Google Service Account `.json` file.
2. Select your `keywords.txt` file (List of keywords, one per line).
3. Type your property name exactly as it is in GSC (e.g., `sc-domain:example.com` or `https://www.example.com/`). *(You can click 'List My Sites' to see exact domain formats).*
4. Hit **Analizi Başlat (Start Analysis)**.

### Using the Command Line (CLI)
```bash
python gsc_keyword_checker.py --keywords keywords.txt --site "https://www.example.com/" --auth service --key your_service_account.json --days 90
```

## 📝 Example Output format
The script outputs its findings in a highly readable format and generates a CSV:
```
  📊 ANAHTAR KELİME KONTROL RAPORU / KEYWORD REPORT
======================================================================
  ✅ Bulunan / Found        : 250 (94%)
  ❌ Bulunamayan / Not Found: 15 (6%)
  
  ✅ SİTENİZDE SIRALANAN ANAHTAR KELİMELER / RANKING KEYWORDS
----------------------------------------------------------------------
  Anahtar Kelime            Tıkl    Göst    CTR%    Sıra    Eşleşme
  araba camı temizleme        45     852     5.2%    4.5    🎯 Tam Eşleşme
  en iyi araba cilası         12     340     3.5%   12.1    🔗 Kısmi Eşleşme
```

## ⚠️ Disclaimer
Please make sure not to upload your `.json` service account files or secret `.pickle` token files. The included `.gitignore` handles this natively!

## License
MIT License. Feel free to use, modify or distribute!
