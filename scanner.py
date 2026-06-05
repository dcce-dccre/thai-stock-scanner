import pandas as pd
import yfinance as yf
import pandas_ta as ta
import datetime
import json
import warnings

warnings.filterwarnings('ignore')

# 1. รายชื่อหุ้น SET50 (ยกตัวอย่างมาบางส่วน)
tickers = ['PTT.BK', 'AOT.BK', 'CPALL.BK', 'BDMS.BK', 'ADVANC.BK', 'GULF.BK', 'DELTA.BK', 'SCC.BK', 'KBANK.BK', 'SCB.BK']

end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=100)

results = []

print("กำลังใช้คณิตศาสตร์ถอดรหัสแท่งเทียน...")

for ticker in tickers:
    try:
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if len(df) < 20: continue
            
        # 2. ให้ pandas_ta สแกนหาแพทเทิร์นแท่งเทียน
        # คืนค่าออกมาเป็นตารางที่มีค่า 100 (ถ้าเจอขาขึ้น), -100 (ถ้าเจอขาลง), หรือ 0 (ถ้าไม่เจอ)
        hammer = df.ta.cdl_pattern(name="hammer")
        engulfing = df.ta.cdl_pattern(name="engulfing")
        
        # ดึงข้อมูลแถวล่าสุด (ราคาปิดของวันนี้) มาเช็ก
        latest_close = df['Close'].iloc[-1]
        
        # ตรวจสอบว่ามีค่า 100 ในคอลัมน์ของวันล่าสุดหรือไม่
        latest_hammer = hammer.iloc[-1, 0] if (hammer is not None and not hammer.empty) else 0
        latest_engulfing = engulfing.iloc[-1, 0] if (engulfing is not None and not engulfing.empty) else 0
        
        is_hammer = (latest_hammer == 100)
        is_engulfing = (latest_engulfing == 100)
        
        # 3. ถ้าเจอแพทเทิร์นใดแพทเทิร์นหนึ่ง ให้บันทึกลงระบบ
        if is_hammer or is_engulfing:
            pattern_name = []
            if is_hammer: pattern_name.append("Hammer 🔨")
            if is_engulfing: pattern_name.append("Bullish Engulfing 📈")
            
            results.append({
                "ticker": ticker.replace('.BK', ''),
                "close": round(float(latest_close), 2),
                "pattern": " + ".join(pattern_name)
            })
            
    except Exception as e:
        pass

# 4. บันทึกผลลัพธ์ลงไฟล์ data.json
output = {
    "last_updated": end_date.strftime("%Y-%m-%d %H:%M:%S"),
    "data": results
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=4, ensure_ascii=False)

print("สแกนและบันทึกไฟล์ data.json สำเร็จ!")
