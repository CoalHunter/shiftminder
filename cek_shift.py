import datetime
import json
import calendar

def hitung_shift(target_date):
    anchor_monday = datetime.date(2026, 10, 19)  # SENIN Shift Pagi pertama
    delta_weeks = (target_date - anchor_monday).days // 7
    
    if target_date.weekday() == 6:  # Minggu
        return {"status": "LIBUR", "time": "-", "emoji": "🏖️"}
    elif delta_weeks % 2 == 0:
        return {"status": "SHIFT PAGI", "time": "07:00 - 14:00", "emoji": "🌅"}
    else:
        return {"status": "SHIFT SIANG", "time": "14:00 - 21:00", "emoji": "🌇"}

def generate_data():
    now_wib_tz = datetime.timezone(datetime.timedelta(hours=7))
    now_wib = datetime.datetime.now(now_wib_tz)
    today = now_wib.date()
    
    hari_indo = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    bulan_indo = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                  'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    
    # --- Data Hari Ini ---
    shift_today = hitung_shift(today)
    today_data = {
        "day_name": hari_indo[today.weekday()],
        "full_date": f"{hari_indo[today.weekday()]}, {today.day} {bulan_indo[today.month-1]} {today.year}",
        **shift_today
    }
    
    # --- 7 Hari ke Depan ---
    next_7_days = []
    for i in range(1, 8):
        d = today + datetime.timedelta(days=i)
        shift = hitung_shift(d)
        next_7_days.append({
            "day_name": hari_indo[d.weekday()],
            "short_date": f"{d.day} {bulan_indo[d.month-1][:3]}",
            **shift
        })
    
    # --- 4 Minggu ke Depan ---
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

    # --- Statistik Bulan Ini (Untuk Kalkulator HK) ---
    year, month = today.year, today.month
    total_days_in_month = calendar.monthrange(year, month)[1]
    
    # Hitung berapa banyak hari Minggu (hari libur potensial untuk HK) di bulan ini
    libur_days = 0
    for d in range(1, total_days_in_month + 1):
        date_obj = datetime.date(year, month, d)
        if date_obj.weekday() == 6: # Minggu
            libur_days += 1

    monthly_stats = {
        "month_name": f"{bulan_indo[month-1]} {year}",
        "total_minggu": libur_days, # Jumlah hari Minggu di bulan ini
        "rate_hk": 170000 # Nilai Harian Kontan
    }
    
    return {
        "last_updated": now_wib.strftime("%d-%m-%Y %H:%M:%S"),
        "today": today_data,
        "next_7_days": next_7_days,
        "next_4_weeks": next_4_weeks,
        "monthly_stats": monthly_stats
    }

if __name__ == "__main__":
    data = generate_data()
    
    with open("template.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    json_str = json.dumps(data, ensure_ascii=False)
    html = html.replace("__SHIFT_DATA_PLACEHOLDER__", json_str)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ Done! Hari ini: {data['today']['day_name']}, {data['today']['status']}")
