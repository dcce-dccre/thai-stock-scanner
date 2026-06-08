import pandas as pd
import yfinance as yf
import datetime
import json
import warnings

warnings.filterwarnings('ignore')

# รายชื่อหุ้นกลุ่มธนาคาร พลังงาน และหุ้นปันผลเด่นใน SET100
tickers = [
    'BBL.BK', 'SCB.BK', 'KTB.BK', 'TTB.BK', 'TISCO.BK', 
    'PTT.BK', 'PTTEP.BK', 'TOP.BK', 'BCP.BK', 'BANPU.BK',
    'EGCO.BK', 'RATCH.BK', 'INTUCH.BK', 'ADVANC.BK', 'CPALL.BK',
    'LH.BK', 'SIRI.BK', 'AP.BK', 'WHA.BK', 'TU.BK'
]

results = []
print("กำลังสแกนหาหุ้นคุณค่า (Value Stock) ตามเกณฑ์ Benjamin Graham...")

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        current_price = info.get('currentPrice', info.get('previousClose', 0))
        pe_ratio = info.get('trailingPE', 0)
        pbv_ratio = info.get('priceToBook', 0)
        div_yield = info.get('dividendYield', 0)
        
        if not current_price:
            continue
            
        div_yield_percent = div_yield * 100 if div_yield else 0
        
        # --- กฎเหล็ก VI คลาสสิก ---
        # 1. P/E ต้องมากกว่า 0 และน้อยกว่า 15 เท่า (คืนทุนไว)
        # 2. P/BV ต้องมากกว่า 0 และน้อยกว่า 1.5 เท่า (ราคาถูกเมื่อเทียบกับสินทรัพย์)
        # 3. ปันผลมากกว่า 4% ต่อปี (มีกระแสเงินสดปลอบใจ)
        
        if (0 < pe_ratio <= 15.0) and (0 < pbv_ratio <= 1.5) and (div_yield_percent >= 4.0):
            results.append({
                "ticker": ticker.replace('.BK', ''),
                "price": round(current_price, 2),
                "pe": round(pe_ratio, 2),
                "pbv": round(pbv_ratio, 2),
                "dividend": round(div_yield_percent, 2)
            })
            
    except Exception as e:
        pass

# เรียงลำดับตามความถูกของสินทรัพย์ (P/BV จากต่ำไปสูง)
results = sorted(results, key=lambda x: x['pbv'])

output = {
    "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "data": results
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=4, ensure_ascii=False)

print("อัปเดตฐานข้อมูลหุ้นคุณค่าสำเร็จ!")
