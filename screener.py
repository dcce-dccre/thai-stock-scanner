import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np

# รายชื่อหุ้นเป้าหมาย (เลือกเฉพาะตัวท็อปที่มีสภาพคล่อง)
tickers = [
    "ADVANC.BK", "AOT.BK", "BBL.BK", "BDMS.BK", "CPALL.BK", 
    "CPF.BK", "CPN.BK", "DELTA.BK", "KBANK.BK", "KCE.BK", 
    "KTB.BK", "PTT.BK", "PTTEP.BK", "SCB.BK", "SCC.BK", "TRUE.BK"
]

results = []
print("🎯 Starting V18.2: Deep Value & Mean Reversion Engine...")
print("กำลังสแกนหาหุ้นที่ถูกเทขายอย่างหนัก (RSI <= 30) แต่พื้นฐานยังแกร่ง!\n")

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        # ไม่จำเป็นต้องดึงข้อมูลยาว 1 ปีแล้ว เพราะเราไม่ได้ใช้ SMA 200
        df = stock.history(period="6mo")
        if df.empty or len(df) < 50:
            continue
            
        # คำนวณเฉพาะ RSI เพื่อหาจุด Oversold
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        latest = df.iloc[-1]
        price = latest['Close']
        rsi_val = latest['RSI']
        
        # ดึงข้อมูลปัจจัยพื้นฐาน (Fundamental Info)
        info = stock.info
        pe_ratio = info.get('trailingPE', None)
        div_yield = info.get('dividendYield', 0)
        div_yield = div_yield * 100 if div_yield is not None else 0.0
            
        symbol = ticker.replace(".BK", "")
        
        # --- 📉 การประมวลผลเงื่อนไข (V18.2: Deep Value Filters) ---
        # 1. ด่านความปลอดภัย: ธุรกิจต้องไม่พัง (P/E ต่ำกว่า 22, ปันผลมากกว่า 3.5%)
        is_good_valuation = (pe_ratio is not None) and (pe_ratio < 22.0)
        is_good_yield = div_yield >= 3.5
        
        # 2. ด่านความตื่นตระหนก: กราฟต้องโดนทุบจนแหลก (RSI ลงมาต่ำกว่า 30)
        is_panic_sold = rsi_val <= 30.0
        
        # คำนวณคะแนนรวมความแข็งแกร่ง (เต็ม 3 คะแนน)
        score = 0
        if is_good_valuation: score += 1
        if is_good_yield: score += 1
        if is_panic_sold: score += 1
        
        status = "WAITING FOR PANIC"
        if score == 3:
            status = "🩸 BLOOD IN THE STREET (STRONG BUY)"
        elif is_panic_sold and score < 3:
            status = "🚨 PANIC SOLD (But Weak Fundament)"
            
        results.append({
            "Symbol": symbol,
            "Price": round(price, 2),
            "PE": round(pe_ratio, 2) if pe_ratio else "N/A",
            "Yield": f"{div_yield:.2f}%",
            "RSI": round(rsi_val, 2) if not np.isnan(rsi_val) else "N/A",
            "Score": score,
            "Status": status
        })
        # พิมพ์บอกความคืบหน้า เพื่อให้รู้ว่าบอทยังทำงานอยู่
        print(f"✅ {symbol} | RSI: {rsi_val:.1f} | Score: {score}/3")
        
    except Exception as e:
        print(f"❌ Cannot process {ticker}: {e}")

# บันทึกฐานข้อมูล
final_df = pd.DataFrame(results)
final_df.to_csv("data.csv", index=False)
print("\n🎯 Deep Value Scanning complete! Data saved to data.csv")
