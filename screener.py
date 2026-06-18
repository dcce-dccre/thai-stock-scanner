import yfinance as yf
import pandas as pd
import pandas_ta as ta
import datetime

# รายชื่อหุ้น SET50 สภาพคล่องสูงสำหรับระบบสไนเปอร์
tickers = [
    "ADVANC.BK", "AOT.BK", "AWC.BK", "BBL.BK", "BDMS.BK", "BEM.BK", "BGRIM.BK", 
    "BH.BK", "BJC.BK", "BLA.BK", "BTS.BK", "CBG.BK", "CENTEL.BK", "COM7.BK", 
    "CPALL.BK", "CPF.BK", "CPN.BK", "CRC.BK", "DELTA.BK", "EA.BK", "EGCO.BK", 
    "GLOBAL.BK", "GPSC.BK", "GULF.BK", "HMPRO.BK", "INTUCH.BK", "IRPC.BK", 
    "IVL.BK", "KBANK.BK", "KCE.BK", "KTB.BK", "KTC.BK", "LH.BK", "MINT.BK", 
    "MTC.BK", "OR.BK", "OSP.BK", "PTT.BK", "PTTEP.BK", "PTTGC.BK", "RATCH.BK", 
    "SAWAD.BK", "SCB.BK", "SCC.BK", "SCGP.BK", "TISCO.BK", "TOP.BK", "TRUE.BK", 
    "TTB.BK", "TU.BK"
]

results = []
print("🚀 Starting Advanced Investing Engine (V17)...")

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y")
        
        if df.empty or len(df) < 200:
            continue
            
        # 1. คำนวณลำดับขั้นอินดิเคเตอร์ทั้งหมดด้วย pandas-ta
        df['SMA50'] = ta.sma(df['Close'], length=50)
        df['SMA200'] = ta.sma(df['Close'], length=200)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
        
        # เพิ่มมิติที่ 3 และ 4 (MACD & Bollinger Bands)
        macd_df = ta.macd(df['Close'], fast=12, slow=26, signal=9)
        bb_df = ta.bbands(df['Close'], length=20, std=2)
        
        latest = df.iloc[-1]
        latest_macd = macd_df.iloc[-1]
        latest_bb = bb_df.iloc[-1]
        
        price = latest['Close']
        symbol = ticker.replace(".BK", "")
        
        # 2. ถอดรหัสสัญญาณซื้อขาย
        over_sma50 = price > latest['SMA50']
        over_sma200 = price > latest['SMA200']
        rsi_val = round(latest['RSI'], 2)
        atr_val = round(latest['ATR'], 2)
        
        # เจาะลึก MACD (Line > Signal = Bullish เทรนด์พุ่งขึ้น)
        macd_line = latest_macd.iloc[0]
        macd_signal = latest_macd.iloc[2]
        macd_bullish = macd_line > macd_signal
        
        # เจาะลึก Bollinger Bands (ดึงค่าเส้นล่าง และ เส้นบน)
        bb_low = round(latest_bb.iloc[0], 2)
        bb_high = round(latest_bb.iloc[2], 2)
        
        # ดึง EPS พื้นฐาน
        info = stock.info
        eps = info.get('trailingEps', 0)
        if eps is None: eps = 0
        
        # 3. แพ็กลงโครงสร้างข้อมูลใหม่
        results.append({
            "Symbol": symbol,
            "Price": round(price, 2),
            "EPS": eps,
            "SMA50": over_sma50,
            "SMA200": over_sma200,
            "RSI": rsi_val,
            "ATR": atr_val,
            "MACD_Bull": macd_bullish,
            "BB_Low": bb_low,
            "BB_High": bb_high
        })
        print(f"✅ Processed {symbol}")
        
    except Exception as e:
        print(f"❌ Error with {ticker}: {e}")

# 4. บันทึกออกเป็นฐานข้อมูลชุดใหม่
final_df = pd.DataFrame(results)
final_df.to_csv("data.csv", index=False)
print("🎯 Advanced Scanning Complete! Saved to data.csv")
