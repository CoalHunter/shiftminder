import datetime
import json
import calendar
import os

def hitung_shift(target_date):
    anchor_monday = datetime.date(2026, 10, 19)
    delta_weeks = (target_date - anchor_monday).days // 7
    
    if target_date.weekday() == 6:
        return {"status": "LIBUR", "time": "-", "emoji": "🏖️"}
    elif delta_weeks % 2 == 0:
        return {"status": "SHIFT PAGI", "time": "07:00 - 14:00", "emoji": "🌅"}
    else:
        return {"status": "SHIFT SIANG", "time": "14:00 - 21:00", "emoji": ""}

def generate_data():
    wib_tz = datetime.timezone(datetime.timedelta(hours=7))
    now_wib = datetime.datetime.now(wib_tz)
    today = now_wib.date()
    
    hari_indo = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    bulan_indo = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                  'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    
    shift_today = hitung_shift(today)
    today_data = {
        "day_name": hari_indo[today.weekday()],
        "full_date": f"{hari_indo[today.weekday()]}, {today.day} {bulan_indo[today.month-1]} {today.year}",
        **shift_today
    }
    
    next_7_days = []
    for i in range(1, 8):
        d = today + datetime.timedelta(days=i)
        shift = hitung_shift(d)
        next_7_days.append({
            "day_name": hari_indo[d.weekday()],
            "short_date": f"{d.day} {bulan_indo[d.month-1][:3]}",
            **shift
        })
    
    next_4_weeks = []
    days_until_monday = (7 - today.weekday()) % 7
    if days_until_monday == 0 and today.weekday() != 0:
        days_until_monday = 7
    next_monday = today + datetime.timedelta(days=days_until_monday)
    
    for i in range(4):
        monday = next_monday + datetime.timedelta(weeks=i)
        saturday = monday + datetime.timedelta(days=5)
        shift = hitung_shift(monday)
        next_4_weeks.append({
            "week_label": f"{monday.day} {bulan_indo[monday.month-1][:3]} - {saturday.day} {bulan_indo[saturday.month-1][:3]}",
            **shift
        })

    year, month = today.year, today.month
    total_days_in_month = calendar.monthrange(year, month)[1]
    libur_days = sum(1 for d in range(1, total_days_in_month + 1) 
                     if datetime.date(year, month, d).weekday() == 6)

    hk_normal = 170000
    upah_sejam = hk_normal / 8

    monthly_stats = {
        "month_name": f"{bulan_indo[month-1]} {year}",
        "month_key": f"{year}-{str(month).zfill(2)}",
        "total_minggu": libur_days,
        "rate_hk": hk_normal,
        "rate_kontanan": hk_normal * 2,
        "rate_lembur_jam1": round(upah_sejam * 1.5),
        "rate_lembur_jam2": round(upah_sejam * 2),
        "rate_lembur_perusahaan": 7000
    }
    
    return {
        "last_updated": now_wib.strftime("%d-%m-%Y %H:%M:%S"),
        "today": today_data,
        "next_7_days": next_7_days,
        "next_4_weeks": next_4_weeks,
        "monthly_stats": monthly_stats
    }

def ensure_data_json(month_key):
    """Pastikan data.json ada dengan struktur benar. JANGAN reset jika bulan sama."""
    data_file = "data.json"
    
    if os.path.exists(data_file):
        try:
            with open(data_file, "r", encoding="utf-8") as f:
                old_data = json.load(f)
            
            # Cek struktur, tambahkan field yang hilang
            if "kontanan_days" not in old_data:
                old_data["kontanan_days"] = []
            if "lembur_records" not in old_data:
                old_data["lembur_records"] = []
            if "month_key" not in old_data:
                old_data["month_key"] = month_key
            
            # Jika bulan berganti, reset data
            if old_data.get("month_key") != month_key:
                print(f"📅 Bulan berganti! Reset dari {old_data.get('month_key')} ke {month_key}")
                old_data = {
                    "month_key": month_key,
                    "kontanan_days": [],
                    "lembur_records": []
                }
            else:
                print(f"✅ Bulan sama ({month_key}), pertahankan {len(old_data.get('kontanan_days', []))} kontanan, {len(old_data.get('lembur_records', []))} lembur")
            
            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(old_data, f, ensure_ascii=False, indent=2)
            return old_data
        except Exception as e:
            print(f"⚠️ Error baca data.json: {e}")
    
    # File belum ada, buat baru
    print("📄 data.json belum ada, membuat baru...")
    new_data = {
        "month_key": month_key,
        "kontanan_days": [],
        "lembur_records": []
    }
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
    return new_data

def inject_to_html(data, saved_data):
    data["saved_data"] = saved_data
    
    with open("template.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    json_str = json.dumps(data, ensure_ascii=False)
    html = html.replace("__SHIFT_DATA_PLACEHOLDER__", json_str)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    data = generate_data()
    saved_data = ensure_data_json(data["monthly_stats"]["month_key"])
    inject_to_html(data, saved_data)
    print(f"✅ Berhasil! Hari: {data['today']['day_name']}, Status: {data['today']['status']}")
    print(f"📊 Data: {len(saved_data.get('kontanan_days', []))} kontanan, {len(saved_data.get('lembur_records', []))} lembur")
