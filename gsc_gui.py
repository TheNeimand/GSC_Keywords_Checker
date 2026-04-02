import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import os
import glob
import sys

class GSCApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.current_lang = "tr"
        self.lang_dict = {
            "tr": {
                "title": "Google Search Console - Anahtar Kelime Analiz Aracı",
                "settings": " Ayarlar ",
                "json_label": "Servis Hesabı JSON:",
                "btn_browse": "Dosya Seç",
                "kw_label": "Anahtar Kelimeler:",
                "site_label": "GSC Site URL'si:",
                "days_label": "Analiz Geçmişi (Gün):",
                "match_filter_label": "Eşleşme Tipi Filtresi:",
                "status_filter_label": "Bulunma Durumu Filtresi:",
                "btn_list": "🔍 Sitelerimi Listele",
                "btn_run": "🚀 Analizi Başlat",
                "console_box": " İşlem Çıktısı (Konsol) ",
                "err_json": "Lütfen bir Servis Hesabı (JSON) dosyası seçin veya klasöre ekleyin.",
                "err_all": "Lütfen JSON dosyası, Kelime dosyası ve Site URL kısımlarını eksiksiz doldurun.",
                "match_vals": ["Tümü", "Sadece Tam Eşleşme", "Sadece Kısmi Eşleşme"],
                "status_vals": ["Tümü", "Sadece Bulunanlar", "Sadece Bulunamayanlar"]
            },
            "en": {
                "title": "Google Search Console - Keyword Analyzer Tool",
                "settings": " Settings ",
                "json_label": "Service Account JSON:",
                "btn_browse": "Browse",
                "kw_label": "Keywords:",
                "site_label": "GSC Site URL:",
                "days_label": "Analysis History (Days):",
                "match_filter_label": "Match Type Filter:",
                "status_filter_label": "Found Status Filter:",
                "btn_list": "🔍 List My Sites",
                "btn_run": "🚀 Start Analysis",
                "console_box": " Console Log ",
                "err_json": "Please pick a Service Account (JSON) file.",
                "err_all": "Please fill in JSON file, Keywords and Site URL.",
                "match_vals": ["All", "Exact Match Only", "Partial Match Only"],
                "status_vals": ["All", "Found Only", "Not Found Only"]
            }
        }

        self.title(self.lang_dict[self.current_lang]["title"])
        self.geometry("900x720")
        
        # Tema ve stil ayarları
        style = ttk.Style(self)
        try:
            style.theme_use('vista')
        except:
            style.theme_use('clam')
            
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Dil Seçimi
        lang_frame = ttk.Frame(main_frame)
        lang_frame.pack(side=tk.TOP, fill=tk.X, anchor='e')
        ttk.Button(lang_frame, text="🇹🇷 TR", command=lambda: self.switch_lang("tr"), width=8).pack(side=tk.RIGHT, padx=2)
        ttk.Button(lang_frame, text="🇬🇧 EN", command=lambda: self.switch_lang("en"), width=8).pack(side=tk.RIGHT, padx=2)
        
        self.input_frame = ttk.LabelFrame(main_frame, text=self.lang_dict[self.current_lang]["settings"], padding=15)
        self.input_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 15))
        
        # JSON Dosyası
        self.json_lbl = ttk.Label(self.input_frame, text=self.lang_dict[self.current_lang]["json_label"])
        self.json_lbl.grid(row=0, column=0, sticky='w', pady=8)
        self.json_combo = ttk.Combobox(self.input_frame, width=50)
        self.json_combo.grid(row=0, column=1, padx=10, pady=8)
        self.btn_browse1 = ttk.Button(self.input_frame, text=self.lang_dict[self.current_lang]["btn_browse"], command=self.browse_json)
        self.btn_browse1.grid(row=0, column=2, padx=5, pady=8)
        
        # Kelime Dosyası
        self.kw_lbl = ttk.Label(self.input_frame, text=self.lang_dict[self.current_lang]["kw_label"])
        self.kw_lbl.grid(row=1, column=0, sticky='w', pady=8)
        self.kw_combo = ttk.Combobox(self.input_frame, width=50)
        self.kw_combo.grid(row=1, column=1, padx=10, pady=8)
        self.btn_browse2 = ttk.Button(self.input_frame, text=self.lang_dict[self.current_lang]["btn_browse"], command=self.browse_kw)
        self.btn_browse2.grid(row=1, column=2, padx=5, pady=8)
        
        # Site URL
        self.site_lbl = ttk.Label(self.input_frame, text=self.lang_dict[self.current_lang]["site_label"])
        self.site_lbl.grid(row=2, column=0, sticky='w', pady=8)
        self.site_entry = ttk.Entry(self.input_frame, width=53)
        self.site_entry.insert(0, "sc-domain:altinoran.com")
        self.site_entry.grid(row=2, column=1, padx=10, pady=8, sticky='w')
        
        # Gün
        self.days_lbl = ttk.Label(self.input_frame, text=self.lang_dict[self.current_lang]["days_label"])
        self.days_lbl.grid(row=3, column=0, sticky='w', pady=8)
        self.days_entry = ttk.Entry(self.input_frame, width=10)
        self.days_entry.insert(0, "90")
        self.days_entry.grid(row=3, column=1, sticky='w', padx=10, pady=8)
        
        # Filtreler
        self.match_filter_lbl = ttk.Label(self.input_frame, text=self.lang_dict[self.current_lang]["match_filter_label"])
        self.match_filter_lbl.grid(row=4, column=0, sticky='w', pady=8)
        self.match_combo = ttk.Combobox(self.input_frame, width=35, state="readonly")
        self.match_combo['values'] = self.lang_dict[self.current_lang]["match_vals"]
        self.match_combo.current(0)
        self.match_combo.grid(row=4, column=1, sticky='w', padx=10, pady=8)
        
        self.status_filter_lbl = ttk.Label(self.input_frame, text=self.lang_dict[self.current_lang]["status_filter_label"])
        self.status_filter_lbl.grid(row=5, column=0, sticky='w', pady=8)
        self.status_combo = ttk.Combobox(self.input_frame, width=35, state="readonly")
        self.status_combo['values'] = self.lang_dict[self.current_lang]["status_vals"]
        self.status_combo.current(0)
        self.status_combo.grid(row=5, column=1, sticky='w', padx=10, pady=8)
        
        # Butonlar
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        self.list_btn = ttk.Button(btn_frame, text=self.lang_dict[self.current_lang]["btn_list"], command=self.list_sites)
        self.list_btn.pack(side=tk.LEFT, padx=5)

        self.run_btn = ttk.Button(btn_frame, text=self.lang_dict[self.current_lang]["btn_run"], command=self.run_analysis)
        self.run_btn.pack(side=tk.RIGHT, padx=5)
        
        # Konsol
        self.console_frame = ttk.LabelFrame(main_frame, text=self.lang_dict[self.current_lang]["console_box"], padding=10)
        self.console_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        self.console = scrolledtext.ScrolledText(self.console_frame, wrap=tk.WORD, bg='#1e1e1e', fg='#00ff00', font=('Consolas', 10))
        self.console.pack(fill=tk.BOTH, expand=True)
        
        self.auto_detect_files()
        
    def switch_lang(self, lang):
        self.current_lang = lang
        d = self.lang_dict[lang]
        
        self.title(d["title"])
        self.input_frame.config(text=d["settings"])
        self.json_lbl.config(text=d["json_label"])
        self.btn_browse1.config(text=d["btn_browse"])
        self.kw_lbl.config(text=d["kw_label"])
        self.btn_browse2.config(text=d["btn_browse"])
        self.site_lbl.config(text=d["site_label"])
        self.days_lbl.config(text=d["days_label"])
        self.match_filter_lbl.config(text=d["match_filter_label"])
        self.status_filter_lbl.config(text=d["status_filter_label"])
        self.list_btn.config(text=d["btn_list"])
        self.run_btn.config(text=d["btn_run"])
        self.console_frame.config(text=d["console_box"])
        
        m_idx = self.match_combo.current()
        s_idx = self.status_combo.current()
        self.match_combo['values'] = d["match_vals"]
        self.status_combo['values'] = d["status_vals"]
        self.match_combo.current(m_idx if m_idx >= 0 else 0)
        self.status_combo.current(s_idx if s_idx >= 0 else 0)

    def auto_detect_files(self):
        jsons = glob.glob("*.json")
        kws = glob.glob("*.txt") + glob.glob("*.csv")
        
        if jsons:
            self.json_combo['values'] = jsons
            for j in jsons:
                if "gen-lang" in j:
                    self.json_combo.set(j)
                    break
            else:
                self.json_combo.set(jsons[0])
                
        if kws:
            self.kw_combo['values'] = kws
            if "Keys-new.txt" in kws:
                self.kw_combo.set("Keys-new.txt")
            else:
                self.kw_combo.set(kws[0])
            
    def browse_json(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON", "*.json"), ("All", "*.*")])
        if filename:
            filename = os.path.basename(filename) if os.path.dirname(filename) == os.getcwd() else filename
            self.json_combo.set(filename)
            vals = list(self.json_combo['values'])
            if filename not in vals:
                self.json_combo['values'] = vals + [filename]
                
    def browse_kw(self):
        filename = filedialog.askopenfilename(filetypes=[("Text", "*.txt"), ("CSV", "*.csv"), ("All", "*.*")])
        if filename:
            filename = os.path.basename(filename) if os.path.dirname(filename) == os.getcwd() else filename
            self.kw_combo.set(filename)
            vals = list(self.kw_combo['values'])
            if filename not in vals:
                self.kw_combo['values'] = vals + [filename]
                
    def log(self, msg):
        self.console.insert(tk.END, msg)
        self.console.see(tk.END)
        
    def run_command_in_thread(self, cmd):
        self.run_btn.config(state=tk.DISABLED)
        self.list_btn.config(state=tk.DISABLED)
        self.console.delete(1.0, tk.END)
        
        def target():
            self.log(f"Çalıştırılıyor: {' '.join(cmd)}\n")
            self.log("-" * 60 + "\n\n")
            try:
                creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                
                env = os.environ.copy()
                env["PYTHONIOENCODING"] = "utf-8"
                env["PYTHONUTF8"] = "1"
                
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT, 
                    text=True, 
                    encoding='utf-8',
                    errors='replace',
                    creationflags=creationflags,
                    env=env
                )
                
                for line in process.stdout:
                    if '\r' in line:
                        line = line.replace('\r', '\n')
                    self.after(0, self.log, line)
                    
                process.wait()
                self.after(0, self.log, f"\n\n[İşlem Tamamlandı. Çıkış Kodu: {process.returncode}]\n")
                
            except Exception as e:
                self.after(0, self.log, f"\n\n[HATA]: {str(e)}\n")
            finally:
                self.after(0, lambda: self.run_btn.config(state=tk.NORMAL))
                self.after(0, lambda: self.list_btn.config(state=tk.NORMAL))
                
        threading.Thread(target=target, daemon=True).start()

    def list_sites(self):
        json_file = self.json_combo.get()
        if not json_file:
            messagebox.showerror("Hata/Error", self.lang_dict[self.current_lang]["err_json"])
            return
            
        cmd = [sys.executable, "-X", "utf8", "gsc_keyword_checker.py", "--list-sites", "--auth", "service", "--key", json_file]
        self.run_command_in_thread(cmd)

    def run_analysis(self):
        json_file = self.json_combo.get()
        kw_file = self.kw_combo.get()
        site = self.site_entry.get()
        days = self.days_entry.get()
        
        if not json_file or not kw_file or not site:
            messagebox.showwarning("Uyarı/Warning", self.lang_dict[self.current_lang]["err_all"])
            return
            
        # Değerlerin İngilizce/Türkçe olmasını evrensel backend argümanlarına(all, exact, partial vs) çevirelim.
        m_idx = self.match_combo.current()
        s_idx = self.status_combo.current()
        
        match_map = {0: "all", 1: "exact", 2: "partial"}
        status_map = {0: "all", 1: "found", 2: "not_found"}
        
        m_val = match_map.get(m_idx, "all")
        s_val = status_map.get(s_idx, "all")
            
        cmd = [
            sys.executable, "-X", "utf8", "gsc_keyword_checker.py", 
            "--keywords", kw_file,
            "--site", site,
            "--auth", "service",
            "--key", json_file,
            "--days", days,
            "--match-filter", m_val,
            "--status-filter", s_val,
            "--json"
        ]
        
        self.run_command_in_thread(cmd)

if __name__ == "__main__":
    app = GSCApp()
    app.mainloop()
