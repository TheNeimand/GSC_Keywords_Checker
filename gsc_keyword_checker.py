#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Search Console - Keyword Checker Tool
=====================================================
Bu araç, verilen anahtar kelime dosyasındaki kelimelerin
Google Search Console verilerine göre sitenizde sıralanıp
sıralanmadığını kontrol eder.

Kullanım:
---------
  python gsc_keyword_checker.py --keywords keywords.txt --site https://www.example.com/
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError:
    print("❌ Gerekli kütüphaneler bulunamadı. Lütfen şunu çalıştırın:")
    print("   pip install -r requirements.txt")
    sys.exit(1)

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import pickle
    OAUTH_AVAILABLE = True
except ImportError:
    OAUTH_AVAILABLE = False

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
API_SERVICE_NAME = "searchconsole"
API_VERSION = "v1"
SCRIPT_DIR = Path(__file__).parent
DEFAULT_DAYS = 90
BATCH_SIZE = 25000

def authenticate_service_account(json_key_path: str):
    if not os.path.exists(json_key_path):
        print(f"❌ Service Account dosyası bulunamadı: {json_key_path}")
        sys.exit(1)
    creds = service_account.Credentials.from_service_account_file(json_key_path, scopes=SCOPES)
    print(f"✅ Service Account ile bağlantı kuruldu.")
    return build(API_SERVICE_NAME, API_VERSION, credentials=creds)

def authenticate_oauth(credentials_path: str):
    if not OAUTH_AVAILABLE:
        print("❌ OAuth2 için gerekli kütüphaneler bulunamadı.")
        sys.exit(1)
    token_path = SCRIPT_DIR / "token.pickle"
    creds = None
    if token_path.exists():
        with open(token_path, "rb") as token_file:
            creds = pickle.load(token_file)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                print(f"❌ OAuth2 credentials dosyası bulunamadı: {credentials_path}")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "wb") as token_file:
            pickle.dump(creds, token_file)
    print("✅ OAuth2 ile bağlantı kuruldu.")
    return build(API_SERVICE_NAME, API_VERSION, credentials=creds)

def read_keywords(file_path: str) -> list[str]:
    keywords = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            kw = line.strip().strip('"').strip()
            if kw and kw.lower() != "keyword":
                keywords.append(kw.lower())
    seen = set()
    unique = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique.append(kw)
    print(f"📄 {len(unique)} benzersiz anahtar kelime okundu: {file_path}")
    return unique

def fetch_all_queries(service, site_url: str, days: int) -> dict:
    end_date = datetime.now() - timedelta(days=3)
    start_date = end_date - timedelta(days=days)
    print(f"\n🔍 GSC verileri çekiliyor...")
    print(f"   Site: {site_url}")
    print(f"   Tarih aralığı: {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')}")
    
    all_queries = {}
    start_row = 0
    while True:
        request_body = {
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
            "dimensions": ["query"],
            "rowLimit": BATCH_SIZE,
            "startRow": start_row,
        }
        try:
            response = service.searchanalytics().query(siteUrl=site_url, body=request_body).execute()
        except Exception as e:
            print(f"\n❌ GSC API hatası: {e}")
            sys.exit(1)
            
        rows = response.get("rows", [])
        if not rows:
            break
            
        for row in rows:
            query = row["keys"][0].lower()
            all_queries[query] = {
                "clicks": row.get("clicks", 0),
                "impressions": row.get("impressions", 0),
                "ctr": round(row.get("ctr", 0) * 100, 2),
                "position": round(row.get("position", 0), 1),
            }
        start_row += len(rows)
        print(f"   ... {start_row} sorgu çekildi", end="\r")
        if len(rows) < BATCH_SIZE:
            break
            
    print(f"\n✅ Toplam {len(all_queries)} benzersiz sorgu bulundu GSC'de.")
    return all_queries

def match_keywords(keywords: list[str], gsc_queries: dict) -> tuple[list, list]:
    found = []
    not_found = []
    for kw in keywords:
        if kw in gsc_queries:
            data = gsc_queries[kw]
            found.append({
                "keyword": kw,
                "match_type": "Tam Eşleşme",
                "matched_query": kw,
                **data,
            })
        else:
            partial_matches = []
            for query, data in gsc_queries.items():
                if kw in query or query in kw:
                    partial_matches.append({
                        "keyword": kw,
                        "match_type": "Kısmi Eşleşme",
                        "matched_query": query,
                        **data,
                    })
            if partial_matches:
                best = max(partial_matches, key=lambda x: x["clicks"])
                found.append(best)
            else:
                not_found.append(kw)
    return found, not_found

def print_report(found: list, not_found: list, total: int):
    found_count = len(found)
    not_found_count = len(not_found)
    print("\n" + "=" * 80)
    print("  📊 ANAHTAR KELİME KONTROL RAPORU")
    print("=" * 80)
    print(f"\n  Toplam anahtar kelime : {total}")
    print(f"  ✅ Bulunan            : {found_count} ({found_count/total*100:.1f}%)")
    print(f"  ❌ Bulunamayan        : {not_found_count} ({not_found_count/total*100:.1f}%)")

    if found:
        print("\n" + "-" * 80)
        print("  ✅ SİTENİZDE SIRALANAN ANAHTAR KELİMELER")
        print("-" * 80)
        print(f"  {'Anahtar Kelime':<45} {'Tıkl':>5} {'Göst':>7} {'CTR%':>6} {'Sıra':>5} {'Eşleşme'}")
        print(f"  {'─' * 44} {'─' * 5} {'─' * 7} {'─' * 6} {'─' * 5} {'─' * 15}")
        for item in sorted(found, key=lambda x: x["clicks"], reverse=True):
            kw_display = item["keyword"][:44]
            match_indicator = "🎯" if item["match_type"] == "Tam Eşleşme" else "🔗"
            print(f"  {kw_display:<45} {item['clicks']:>5} {item['impressions']:>7} "
                  f"{item['ctr']:>5.1f}% {item['position']:>5.1f} {match_indicator} {item['match_type']}")

    if not_found:
        print("\n" + "-" * 80)
        print("  ❌ SİTENİZDE BULUNMAYAN ANAHTAR KELİMELER (İÇERİK FIRSATI!)")
        print("-" * 80)
        for kw in not_found:
            print(f"  • {kw}")
    print("\n" + "=" * 80)

def save_csv_report(found: list, not_found: list, output_path: str):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = output_path or str(SCRIPT_DIR / f"gsc_rapor_{timestamp}.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Anahtar Kelime", "Durum", "Eşleşme Tipi", "Eşleşen Sorgu", "Tıklama", "Gösterim", "CTR (%)", "Ortalama Sıra"])
        for item in sorted(found, key=lambda x: x["clicks"], reverse=True):
            writer.writerow([item["keyword"], "BULUNDU", item["match_type"], item["matched_query"], item["clicks"], item["impressions"], item["ctr"], item["position"]])
        for kw in not_found:
            writer.writerow([kw, "BULUNAMADI", "", "", "", "", "", ""])
    print(f"\n💾 CSV raporu kaydedildi: {csv_path}")
    return csv_path

def save_json_report(found: list, not_found: list, output_path: str = None):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = output_path or str(SCRIPT_DIR / f"gsc_rapor_{timestamp}.json")
    report = {
        "rapor_tarihi": datetime.now().isoformat(),
        "ozet": {"toplam": len(found) + len(not_found), "bulunan": len(found), "bulunamayan": len(not_found)},
        "bulunan_kelimeler": found,
        "bulunamayan_kelimeler": not_found,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"💾 JSON raporu kaydedildi: {json_path}")
    return json_path

def list_sites(service):
    try:
        site_list = service.sites().list().execute()
        sites = site_list.get("siteEntry", [])
        if not sites:
            print("⚠️  GSC'de hiçbir site bulunamadı. Yetkilendirmeyi kontrol edin.")
            return []
        print("\n📋 GSC'deki Siteleriniz:")
        for i, site in enumerate(sites, 1):
            print(f"   {i}. {site['siteUrl']} (Yetki: {site['permissionLevel']})")
        return sites
    except Exception as e:
        print(f"❌ Site listesi alınamadı: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(
        description="Google Search Console Anahtar Kelime Kontrol Aracı",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--keywords", "-k", help="Anahtar kelime dosyasının yolu")
    parser.add_argument("--site", "-s", help="GSC'deki site URL'si (ör: https://www.example.com/)")
    parser.add_argument("--auth", "-a", choices=["service", "oauth"], default="service")
    parser.add_argument("--key", default="service_account.json")
    parser.add_argument("--credentials", default="credentials.json")
    parser.add_argument("--days", "-d", type=int, default=DEFAULT_DAYS)
    parser.add_argument("--output", "-o", help="CSV çıktı dosyası yolu")
    parser.add_argument("--json", "-j", action="store_true")
    parser.add_argument("--list-sites", action="store_true")
    parser.add_argument("--match-filter", choices=["all", "exact", "partial"], default="all")
    parser.add_argument("--status-filter", choices=["all", "found", "not_found"], default="all")

    args = parser.parse_args()

    print("\n🔐 Kimlik doğrulama yapılıyor...")
    if args.auth == "service":
        service = authenticate_service_account(args.key)
    else:
        service = authenticate_oauth(args.credentials)

    if args.list_sites:
        list_sites(service)
        return

    if not args.keywords:
        print("❌ --keywords parametresi gerekli.")
        sys.exit(1)
    if not args.site:
        print("⚠️  --site parametresi belirtilmedi. Mevcut siteleri listeliyorum...\n")
        list_sites(service)
        sys.exit(1)

    keywords = read_keywords(args.keywords)
    if not keywords:
        print("❌ Anahtar kelime dosyasında kelime bulunamadı.")
        sys.exit(1)

    gsc_queries = fetch_all_queries(service, args.site, args.days)
    found, not_found = match_keywords(keywords, gsc_queries)
    
    if args.match_filter == "exact":
        found = [x for x in found if x["match_type"] == "Tam Eşleşme"]
    elif args.match_filter == "partial":
        found = [x for x in found if x["match_type"] == "Kısmi Eşleşme"]
        
    if args.status_filter == "found":
        not_found = []
    elif args.status_filter == "not_found":
        found = []
    
    print_report(found, not_found, len(keywords))
    save_csv_report(found, not_found, args.output)
    if args.json:
        save_json_report(found, not_found)

    print(f"\n✨ İşlem tamamlandı!")

if __name__ == "__main__":
    main()
