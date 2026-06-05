import pandas as pd
import yfinance as yf
import pandas_ta as ta
import datetime
import json
import warnings

warnings.filterwarnings('ignore')

# 1. รายชื่อหุ้นที่ต้องการสแกน (ใส่หุ้น SET50 เบื้องต้น)
tickers = ['PTT.BK', 'AOT.BK', 'CPALL.BK', 'BDMS.BK', 'ADVANC.BK', 'GULF.BK', 'DELTA.BK', 'SCC.BK', 'KBANK.BK', 'SCB.BK']

end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=150)

results = []

for ticker in tickers:
    try:
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if len(df) < 50: continue
            
        # คำนวณ Indicators
        df['EMA_50'] = ta.ema(df['Close'], length=50)
        df['RSI_14'] = ta.rsi(df['Close'], length=14)
        df['Vol_MA_20'] = ta.sma(df['Volume'], length=20)
        df.dropna(inplace=True)
        
        latest = df.iloc[-1]
        
        # กรองข้อมูลเบื้องต้น (เอาตัวที่ RSI > 50 และราคายืนเหนือ EMA50)
        if latest['Close'] > latest['EMA_50'] and latest['RSI_14'] > 50:
            results.append({
                "ticker": ticker.replace('.BK', ''),
                "close": round(float(latest['Close']), 2),
                "rsi": round(float(latest['RSI_14']), 2),
                "volume": int(latest['Volume']),
                "vol_ratio": round(float(latest['Volume'] / latest['Vol_MA_20']), 2)
            })
    except Exception:
        pass

# เรียงลำดับจากวอลุ่มพุ่งมากไปน้อย
results = sorted(results, key=lambda x: x['vol_ratio'], reverse=True)

# 2. บันทึกผลลัพธ์ลงไฟล์ data.json
output = {
    "last_updated": end_date.strftime("%Y-%m-%d %H:%M:%S"),
    "data": results
}

with open('data.json', 'w') as f:
    json.dump(output, f, indent=4)

print("สแกนและบันทึกไฟล์ data.json สำเร็จ!")
