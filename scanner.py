import pandas as pd
import yfinance as yf
import datetime
import json
import warnings
import requests

warnings.filterwarnings('ignore')

# 1. รายชื่อหุ้น SET100
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

# 2. วิชาปลอมตัว: สร้าง Session และหลอกว่าเป็นเบราว์เซอร์ Chrome
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
})

print("กำลังดาวน์โหลดข้อมูล Benchmark (SET Index)...")
try:
    set_df = yf.download('^SET.BK', start=start_date, end=end_date, session=session, progress=False)
    
    # รองรับ yfinance เวอร์ชั่นใหม่ (MultiIndex Bug Fix)
    if isinstance(set_df.columns, pd.MultiIndex):
        set_close = set_df['Close']['^SET.BK']
    else:
        set_close = set_df['Close']
        
    set_return = (float(set_close.iloc[-1]) / float(set_close.iloc[-60])) - 1
except Exception as e:
    print(f"ดึง SET ไม่สำเร็จ: {e}")
    set_return = 0.0

all_stocks = []
print("กำลังสแกนและคำนวณหุ้น SET100 (เปิดโหมดกันบล็อก)...")

# ดึงข้อมูลทีละตัวเพื่อความชัวร์ 100%
for ticker in tickers:
    try:
        df = yf.download(ticker, start=start_date, end=end_date, session=session, progress=False)
        if len(df) < 60:
            continue
            
        # ดักจับตาราง 2 ชั้นของ yfinance
        if isinstance(df.columns, pd.MultiIndex):
            close_col = df['Close'][ticker]
        else:
            close_col = df['Close']
            
        latest_close = float(close_col.iloc[-1])
        past_close = float(close_col.iloc[-60])
        
        # คำนวณผลตอบแทนและเปรียบเทียบกับตลาด
        stock_return = (latest_close / past_close) - 1
        rs_score = stock_return - set_return
        
        all_stocks.append({
            "ticker": ticker.replace('.BK', ''),
            "close": round(latest_close, 2),
            "return_3m": round(stock_return * 100, 2),
            "rs_score": round(rs_score * 100, 2)
        })
        
    except Exception as e:
        pass

# เรียงลำดับและคัดเฉพาะ Top 10
sorted_stocks = sorted(all_stocks, key=lambda x: x['rs_score'], reverse=True)
top_10_stocks = sorted_stocks[:10]

output = {
    "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "set_return_3m": round(set_return * 100, 2),
    "data": top_10_stocks
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=4, ensure_ascii=False)

print(f"สแกนสำเร็จ! ได้ข้อมูลผู้รอดชีวิตทั้งหมด {len(all_stocks)} ตัว จัดอันดับ Top 10 เรียบร้อย!")
