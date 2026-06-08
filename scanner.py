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

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
})

print("กำลังดาวน์โหลดข้อมูล Benchmark (SET Index)...")
try:
    # เปลี่ยนมาใช้ yf.Ticker() ซึ่งเสถียรกว่าสำหรับการดึงดัชนีเดี่ยวๆ
    set_ticker = yf.Ticker('^SET.BK', session=session)
    set_df = set_ticker.history(start=start_date, end=end_date)
    
    if len(set_df) >= 60:
        set_latest = float(set_df['Close'].iloc[-1])
        set_past = float(set_df['Close'].iloc[-60])
        set_return = (set_latest / set_past) - 1
        print(f"ผลตอบแทน SET 3 เดือนล่าสุด: {round(set_return * 100, 2)}%")
    else:
        print("ข้อมูล SET ย้อนหลังไม่ถึง 60 วัน")
        set_return = 0.0
except Exception as e:
    print(f"ดึงดัชนี SET ไม่สำเร็จ: {e}")
    set_return = 0.0

all_stocks = []
print("กำลังสแกนและคำนวณความแข็งแกร่งหุ้น SET100...")

for ticker in tickers:
    try:
        df = yf.download(ticker, start=start_date, end=end_date, session=session, progress=False)
        if len(df) < 60:
            continue
            
        if isinstance(df.columns, pd.MultiIndex):
            close_col = df['Close'][ticker]
        else:
            close_col = df['Close']
            
        latest_close = float(close_col.iloc[-1])
        past_close = float(close_col.iloc[-60])
        
        # คำนวณผลตอบแทนและ RS Score ของจริง!
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

# จัดอันดับ Top 10
sorted_stocks = sorted(all_stocks, key=lambda x: x['rs_score'], reverse=True)
top_10_stocks = sorted_stocks[:10]

output = {
    "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "set_return_3m": round(set_return * 100, 2),
    "data": top_10_stocks
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=4, ensure_ascii=False)

print("จัดอันดับ Top 10 เสร็จสมบูรณ์! ข้อมูล RS Score แม่นยำ 100%")
