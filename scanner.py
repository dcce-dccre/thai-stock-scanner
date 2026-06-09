import pandas as pd
import yfinance as yf
import datetime
import json
import warnings
import requests
import math

warnings.filterwarnings('ignore')

# 🛡️ ระบบแอนตี้ไวรัส: ป้องกันค่าที่พัง (NaN) ให้กลายเป็น 0 
def clean(value):
    try:
        if pd.isna(value) or math.isnan(value) or math.isinf(value):
            return 0.0
        return float(value)
    except:
        return 0.0

# รายชื่อหุ้น SET100
tickers = [
    'AAV.BK', 'ADVANC.BK', 'AMATA.BK', 'AOT.BK', 'AP.BK', 'AWC.BK', 'BAM.BK', 'BANPU.BK', 
    'BBL.BK', 'BCH.BK', 'BCP.BK', 'BCPG.BK', 'BDMS.BK', 'BEM.BK', 'BGRIM.BK', 'BH.BK', 
    'BJC.BK', 'BLA.BK', 'BPP.BK', 'BTS.BK', 'CBG.BK', 'CENTEL.BK', 'CHG.BK', 'CK.BK', 
    'CKP.BK', 'COM7.BK', 'CPALL.BK', 'CPAXT.BK', 'CPF.BK', 'CPN.BK', 'CRC.BK', 'DELTA.BK', 
    'DOHOME.BK', 'EA.BK', 'EGCO.BK', 'EPG.BK', 'ERW.BK', 'GLOBAL.BK', 'GPSC.BK', 'GULF.BK', 
    'GUNKUL.BK', 'HANA.BK', 'HMPRO.BK', 'ICHI.BK', 'INTUCH.BK', 'IRPC.BK', 'ITC.BK', 
    'IVL.BK', 'JMART.BK', 'JMT.BK', 'KBANK.BK', 'KCE.BK', 'KEX.BK', 'KKP.BK', 'KTB.BK', 
    'KTC.BK', 'LH.BK', 'MEGA.BK', 'MINT.BK', 'MTC.BK', 'OR.BK', 'ORI.BK', 'OSP.BK', 
    'PLANB.BK', 'PRM.BK', 'PSL.BK', 'PTG.BK', 'PTT.BK', 'PTTEP.BK', 'PTTGC.BK', 'QH.BK', 
    'RATCH.BK', 'RBF.BK', 'RCL.BK', 'RS.BK', 'SAWAD.BK', 'SCB.BK', 'SCC.BK', 'SCGP.BK', 
    'SIRI.BK', 'SJWD.BK', 'SPALI.BK', 'SPRC.BK', 'STA.BK', 'STEC.BK', 'STGT.BK', 'TCAP.BK', 
    'THANI.BK', 'THCOM.BK', 'THG.BK', 'TIDLOR.BK', 'TIPH.BK', 'TISCO.BK', 'TOP.BK', 
    'TRUE.BK', 'TTB.BK', 'TU.BK', 'VGI.BK', 'WHA.BK', 'WHAUP.BK'
]

end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=120)

# สร้าง Session แปลงร่างเป็นเบราว์เซอร์กันโดนบล็อก
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
})

print("1. ดาวน์โหลดข้อมูล Benchmark (SET Index)...")
try:
    set_ticker = yf.Ticker('^SET.BK', session=session)
    set_df = set_ticker.history(start=start_date, end=end_date)
    if len(set_df) >= 60:
        set_latest = clean(set_df['Close'].iloc[-1])
        set_past = clean(set_df['Close'].iloc[-60])
        set_return = (set_latest / set_past) - 1 if set_past > 0 else 0.0
    else:
        set_return = 0.0
except:
    set_return = 0.0

all_stocks = []
print("2. สแกนกราฟเทคนิคอลหุ้น 100 ตัวรวดเดียว...")

df = yf.download(tickers, start=start_date, end=end_date, session=session, progress=False)

is_multi = isinstance(df.columns, pd.MultiIndex)

for ticker in tickers:
    try:
        if is_multi:
            close_col = df['Close'][ticker].dropna()
            vol_col = df['Volume'][ticker].dropna()
            low_col = df['Low'][ticker].dropna()
        else:
            if ticker not in df['Close']: continue
            close_col = df['Close'].dropna()
            vol_col = df['Volume'].dropna()
            low_col = df['Low'].dropna()
            
        if len(close_col) < 60: continue
            
        latest_close = clean(close_col.iloc[-1])
        past_close = clean(close_col.iloc[-60])
        
        if past_close == 0: continue
        
        stock_return = (latest_close / past_close) - 1
        rs_score = stock_return - set_return
        
        avg_vol_20 = clean(vol_col.tail(20).mean())
        latest_vol = clean(vol_col.iloc[-1])
        vol_ratio = latest_vol / avg_vol_20 if avg_vol_20 > 0 else 1.0
        
        ema50 = clean(close_col.ewm(span=50, adjust=False).mean().iloc[-1])
        trend = "ขาขึ้น 🟢" if latest_close > ema50 else "ขาลง 🔴"
        
        low_5d = clean(low_col.tail(5).min())
        stop_loss = low_5d - 0.05
        
        if stop_loss >= latest_close or stop_loss == -0.05:
            stop_loss = latest_close * 0.95
            
        risk_per_share = latest_close - stop_loss
        take_profit = latest_close + (risk_per_share * 2.0)
            
        all_stocks.append({
            "ticker": ticker.replace('.BK', ''),
            "yf_ticker": ticker,
            "close": round(latest_close, 2),
            "return_3m": round(stock_return * 100, 2),
            "rs_score": round(rs_score * 100, 2),
            "vol_ratio": round(vol_ratio, 2),
            "trend": trend,
            "stop_loss": round(stop_loss, 2),
            "take_profit": round(take_profit, 2)
        })
    except Exception as e:
        pass

# คัดเลือกเฉพาะ Top 10 ตัวที่แกร่งที่สุด
sorted_stocks = sorted(all_stocks, key=lambda x: x['rs_score'], reverse=True)
top_10_stocks = sorted_stocks[:10]

print("3. เจาะงบการเงินเฉพาะหุ้น Top 10 เพื่อหาราคาที่เหมาะสม (Fair Value)...")
for stock in top_10_stocks:
    try:
        info = yf.Ticker(stock['yf_ticker'], session=session).info
        pe = clean(info.get('trailingPE', 0))
        pbv = clean(info.get('priceToBook', 0))
        
        # คำนวณมูลค่าที่แท้จริงตามสูตรของ Graham 
        if pe > 0 and pbv > 0:
            graham_multiplier = math.sqrt(22.5 / (pe * pbv))
            fair_value = stock['close'] * graham_multiplier
            mos = ((fair_value - stock['close']) / fair_value) * 100 
        else:
            fair_value = 0.0
            mos = 0.0
            
        stock['fair_value'] = round(fair_value, 2)
        stock['mos'] = round(mos, 2) 
        
    except Exception as e:
        stock['fair_value'] = 0.0
        stock['mos'] = 0.0

output = {
    "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "set_return_3m": round(set_return * 100, 2),
    "data": top_10_stocks
}

# สร้างไฟล์ json และสั่งไม่ให้มีคำว่า NaN หลุดไปเด็ดขาด
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=4, ensure_ascii=False, allow_nan=False)

print("จัดอันดับ V9 (Fair Value Edition) สำเร็จเรียบร้อย!")
