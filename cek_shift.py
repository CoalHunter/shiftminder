import datetime
import json
import re

def hitung_shift(target_date):
    anchor_monday = datetime.date(2026, 10, 19)  # Senin Shift Pagi pertama
    
    hari_indo = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    bulan_indo = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                  'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    
    delta_days = (target_date - anchor_monday).days
    delta_weeks = delta_days // 7
    
    if target_date.weekday() == 6:  # Minggu
        return {"status": "LIBUR", "time": "-", "emoji": "🏖️"}
    elif delta_weeks % 2 == 0:
        return {"status": "SHIFT PAGI", "time": "07:00 - 14:00", "emoji": "🌅"}
    else:
        return {"status": "SHIFT SIANG", "time": "14:00 - 21:00", "emoji": "🌇"}

def generate_data():
    today = datetime.date.today()
    hari_indo = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    bulan_indo = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                  'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    
    # Data hari ini
    shift_today = hitung_shift(today)
    today_data = {
        "date": today.isoformat(),
        "day_name": hari_indo[today.weekday()],
        "full_date": f"{hari_indo[today.weekday()]}, {today.day} {bulan_indo[today.month-1]} {today.year}",
        **shift_today
    }
    
    # 7 hari ke depan
    next_7_days = []
    for i in range(1, 8):
        d = today + datetime.timedelta(days=i)
        shift = hitung_shift(d)
        next_7_days.append({
            "date": d.isoformat(),
            "day_name": hari_indo[d.weekday()],
            "short_date": f"{d.day} {bulan_indo[d.month-1][:3]}",
            **shift
        })
    
    # 4 minggu ke depan (per minggu, mulai Senin)
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
    
    return {
        "last_updated": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "today": today_data,
        "next_7_days": next_7_days,
        "next_4_weeks": next_4_weeks
    }

def inject_to_html(data):
    # Baca template
    with open("template.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    # Suntikkan JSON ke placeholder
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    pattern = r'(/\*__SHIFT_DATA_START__\*/).*?(/\*__SHIFT_DATA_END__\*/)'
    replacement = f'/*__SHIFT_DATA_START__*/\n{json_str}\n/*__SHIFT_DATA_END__*/'
    html = re.sub(pattern, replacement, html, flags=re.DOTALL)
    
    # Tulis ke index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    data = generate_data()
    inject_to_html(data)
    print(f"✅ index.html berhasil diupdate! Status: {data['today']['status']}")
