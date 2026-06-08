import pandas as pd
import yfinance as yf
import datetime
import json
import warnings

warnings.filterwarnings('ignore')

# ดึงหุ้น SET100 มาตรวจสอบพื้นฐาน
tickers = [
    'ADVANC.BK', 'AOT.BK', 'BBL.BK', 'BDMS.BK', 'BEM.BK', 'BGRIM.BK', 'BH.BK', 
    'CPALL.BK', 'CPF.BK', 'CPN.BK', 'CRC.BK', 'DELTA.BK', 'EA.BK', 'EGCO.BK', 
    'GLOBAL.BK', 'GPSC.BK', 'GULF.BK', 'HMPRO.BK', 'INTUCH.BK', 'KBANK.BK', 
    'KTB.BK', 'MINT.BK', 'OR.BK', 'PTT.BK', 'PTTEP.BK', 'PTTGC.BK', 'SCB.BK', 
    'SCC.BK', 'TISCO.BK', 'TOP.BK', 'TRUE.BK', 'TTB.BK', 'WHA.BK'
]

results = []
print("กำลังสแกนหาหุ้น ถูก ดี มีปันผล และ Upside สูง...")

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # ป้องกัน Error กรณี yfinance ไม่มีข้อมูลบางตัว
        current_price = info.get('currentPrice', info.get('previousClose', 0))
        pe_ratio = info.get('trailingPE', 0)
        div_yield = info.get('dividendYield', 0)
        target_price = info.get('targetMeanPrice', 0)
        
        if not all([current_price, target_price]):
            continue
            
        div_yield_percent = div_yield * 100 if div_yield else 0
        upside = ((target_price - current_price) / current_price) * 100
        
        # --- กฎเหล็กสาย VI ---
        # 1. P/E ต้องมากกว่า 0 (บริษัทมีกำไร) และน้อยกว่า 15 เท่า (ราคาถูก)
        # 2. ปันผลมากกว่า 4% 
        # 3. Upside มากกว่า 10% (ราคาเป้าหมายสูงกว่าราคาปัจจุบันพอสมควร)
        
        if (0 < pe_ratio < 15) and (div_yield_percent >= 4.0) and (upside >= 10.0):
            results.append({
                "ticker": ticker.replace('.BK', ''),
                "price": round(current_price, 2),
                "pe": round(pe_ratio, 2),
                "dividend": round(div_yield_percent, 2),
                "target": round(target_price, 2),
                "upside": round(upside, 2)
            })
            
    except Exception as e:
        pass

# เรียงลำดับจากตัวที่มี Upside (ส่วนต่างกำไร) มากที่สุดไปน้อยที่สุด
results = sorted(results, key=lambda x: x['upside'], reverse=True)

output = {
    "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "data": results
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=4, ensure_ascii=False)

print("อัปเดตฐานข้อมูลหุ้น VI สำเร็จ!")
