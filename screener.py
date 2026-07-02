import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np

# รายชื่อหุ้นเป้าหมายสำหรับสแกนคุณค่าและจังหวะปลอดภัย
tickers = [
    "ADVANC.BK", "AOT.BK", "BBL.BK", "BDMS.BK", "CPALL.BK", 
    "CPF.BK", "CPN.BK", "DELTA.BK", "KBANK.BK", "KCE.BK", 
    "KTB.BK", "PTT.BK", "PTTEP.BK", "SCB.BK", "SCC.BK", "TRUE.BK"
]

results = []
print("🚀 Starting Techno-Fundamental Engine (V18)...")

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        # ดึงข้อมูลย้อนหลัง 1 ปีเพื่อคำนวณเทคนิคอล
        df = stock.history(period="1y")
        if df.empty or len(df) < 200:
            continue
            
        # คำนวณตัวชี้วัดทางเทคนิคอล
        df['SMA200'] = ta.sma(df['Close'], length=200)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        latest = df.iloc[-1]
        price = latest['Close']
        rsi_val = latest['RSI']
        sma200_val = latest['SMA200']
        
        # ดึงข้อมูลปัจจัยพื้นฐาน (Fundamental Info)
        info = stock.info
        pe_ratio = info.get('trailingPE', None)
        div_yield = info.get('dividendYield', 0)
        if div_yield is not None:
            div_yield = div_yield * 100 # แปลงเป็นเปอร์เซ็นต์
        else:
            div_yield = 0.0
            
        earnings_growth = info.get('earningsGrowth', 0)
        if earnings_growth is None:
            earnings_growth = 0.0
            
        symbol = ticker.replace(".BK", "")
        
        # --- 📈 การประมวลผลเงื่อนไขการลงทุน (V18 Filters) ---
        # 1. คัดกรองหุ้นถูก (P/E ต้องไม่สูงเว่อร์ และมีปันผลชวนอุ่นใจ)
        is_good_valuation = (pe_ratio is not None) and (pe_ratio < 22.0)
        is_good_yield = div_yield >= 3.5
        
        # 2. คัดกรองจังหวะกราฟ (ต้องไม่ใช่ขาลงเต็มตัว และราคาพักตัวไม่ไล่ดอย)
        is_uptrend = price >= (sma200_val * 0.95) # ยอมรับระยะสะสมใกล้เส้น 200 วัน
        is_safe_rsi = rsi_val <= 55.0
        
        # คำนวณคะแนนรวมความแข็งแกร่ง (เต็ม 4 คะแนน)
        score = 0
        if is_good_valuation: score += 1
        if is_good_yield: score += 1
        if is_uptrend: score += 1
        if is_safe_rsi: score += 1
        
        status = "HOLD / WATCH"
        if score == 4:
            status = "🔥 STRONG VALUE BUY"
        elif score == 3:
            status = "📈 INTERESTING VALUE"
            
        results.append({
            "Symbol": symbol,
            "Price": round(price, 2),
            "PE": round(pe_ratio, 2) if pe_ratio else "N/A",
            "Yield": f"{div_yield:.2f}%",
            "Growth": f"{(earnings_growth*100):.1f}%" if earnings_growth else "0.0%",
            "RSI": round(rsi_val, 2) if not np.isnan(rsi_val) else "N/A",
            "Score": score,
            "Status": status
        })
        print(f"✅ Analyzed {symbol} | Score: {score}")
        
    except Exception as e:
        print(f"❌ Cannot process {ticker}: {e}")

# บันทึกฐานข้อมูลออกมาใช้งานบนแดชบอร์ด
final_df = pd.DataFrame(results)
final_df.to_csv("data.csv", index=False)
print("🎯 Scanning complete! Data saved to data.csv")
