import yfinance as yf
import pandas as pd
import pandas_ta as ta
import datetime

# 1. ใส่รายชื่อหุ้นใน Watchlist ของคุณ (ต้องมี .BK ต่อท้ายสำหรับหุ้นไทย)
# สามารถใส่ 100 ตัวได้เลยตามต้องการ
tickers = ["KCE.BK", "ADVANC.BK", "DELTA.BK", "CPALL.BK", "PTTEP.BK", "BBL.BK"]

results = []

print("🚀 Starting Sniper Screener...")

for ticker in tickers:
    try:
        # ดึงข้อมูลจาก Yahoo Finance ย้อนหลัง 1 ปี
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y")
        
        if df.empty or len(df) < 200:
            continue # ข้ามหุ้นที่เพิ่งเข้าตลาดหรือไม่มีข้อมูล
            
        # 2. คำนวณ Technical Indicators ด้วย pandas-ta
        df['SMA50'] = ta.sma(df['Close'], length=50)
        df['SMA200'] = ta.sma(df['Close'], length=200)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
        
        # ดึงข้อมูลแถวล่าสุด (วันปัจจุบัน)
        latest = df.iloc[-1]
        price = latest['Close']
        
        # 3. จัดระเบียบข้อมูลเตรียมลง CSV
        symbol = ticker.replace(".BK", "")
        over_sma50 = price > latest['SMA50']
        over_sma200 = price > latest['SMA200']
        rsi = round(latest['RSI'], 2)
        atr = round(latest['ATR'], 2)
        
        # (Optional) ดึง EPS พื้นฐาน - ถ้า Yahoo บั๊กจะใส่ 0 ไว้ก่อน
        info = stock.info
        eps = info.get('trailingEps', 0)
        if eps is None: eps = 0
        
        results.append({
            "Symbol": symbol,
            "Price": round(price, 2),
            "EPS": eps,
            "SMA50": over_sma50,
            "SMA200": over_sma200,
            "RSI": rsi,
            "ATR": atr
        })
        print(f"✅ Processed {symbol}")
        
    except Exception as e:
        print(f"❌ Error with {ticker}: {e}")

# 4. แปลงเป็น DataFrame และเซฟทับไฟล์ data.csv
final_df = pd.DataFrame(results)
final_df.to_csv("data.csv", index=False)
print("🎯 Scanning Complete! Saved to data.csv")
