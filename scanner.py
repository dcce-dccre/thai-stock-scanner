import pandas as pd
import yfinance as yf
import datetime
import json
import warnings

warnings.filterwarnings('ignore')

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
# ดึงข้อมูลย้อนหลังไปเผื่อไว้ เพื่อให้ได้วันทำการครบ 60 วัน (ประมาณ 3 เดือน)
start_date = end_date - datetime.timedelta(days=120)

print("ดาวน์โหลดข้อมูล Benchmark (SET Index)...")
try:
    set_df = yf.download('^SET.BK', start=start_date, end=end_date, progress=False)
    # หาผลตอบแทนดัชนี SET ในรอบ 60 วันทำการ
    set_return = (float(set_df['Close'].iloc[-1]) / float(set_df['Close'].iloc[-60])) - 1
except:
    set_return = 0.0

all_stocks = []
print("กำลังคำนวณความแข็งแกร่ง (RS Score) ของหุ้นทั้ง 100 ตัว...")

for ticker in tickers:
    try:
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if len(df) < 60: continue
        
        latest_close = float(df['Close'].iloc[-1])
        past_close = float(df['Close'].iloc[-60])
        
        # 1. คำนวณผลตอบแทนของหุ้นตัวนี้
        stock_return = (latest_close / past_close) - 1
        
        # 2. คำนวณ RS Score (ผลตอบแทนหุ้น ลบด้วย ผลตอบแทนดัชนี)
        # ถ้าคะแนนเป็นบวก แปลว่าแข็งแกร่งกว่าตลาด
        rs_score = stock_return - set_return
        
        all_stocks.append({
            "ticker": ticker.replace('.BK', ''),
            "close": round(latest_close, 2),
            "return_3m": round(stock_return * 100, 2),
            "rs_score": round(rs_score * 100, 2)
        })
            
    except Exception as e:
        pass

# 3. เรียงลำดับหุ้นจากตัวที่ RS Score สูงสุดไปต่ำสุด
sorted_stocks = sorted(all_stocks, key=lambda x: x['rs_score'], reverse=True)

# 4. ตัดเอาเฉพาะ 10 อันดับแรก (Top 10)
top_10_stocks = sorted_stocks[:10]

output = {
    "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "set_return_3m": round(set_return * 100, 2),
    "data": top_10_stocks
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=4, ensure_ascii=False)

print("จัดอันดับ Top 10 หุ้นแกร่งสำเร็จ!")
