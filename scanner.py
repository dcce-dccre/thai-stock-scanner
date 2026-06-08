import pandas as pd
import yfinance as yf
import numpy as np
import datetime
import json
import warnings

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

# โหลดข้อมูลดัชนี SET เป็นตัวตั้งต้น
end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=200)

print("ดาวน์โหลดดัชนี SET เพื่อคำนวณความแข็งแกร่งเปรียบเทียบ...")
try:
    set_df = yf.download('^SET.BK', start=start_date, end=end_date, progress=False)
    # คำนวณผลตอบแทนสะสม 3 เดือน (ประมาณ 60 วันทำการ) ของ SET
    set_return = (set_df['Close'].iloc[-1] / set_df['Close'].iloc[-60]) - 1
except:
    set_return = 0

results = []
print("สแกนหาผู้แข็งแกร่ง (Relative Strength) และกราฟบีบตัว (VCP)...")

for ticker in tickers:
    try:
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if len(df) < 60: continue
        
        latest_close = float(df['Close'].iloc[-1])
        
        # 1. คำนวณ Relative Strength (ผลตอบแทนชนะตลาดในรอบ 3 เดือน)
        stock_return = (latest_close / float(df['Close'].iloc[-60])) - 1
        rs_score = stock_return - float(set_return) # ส่วนต่างที่ชนะตลาด (ยิ่งบวกเยอะยิ่งดี)
        
        # 2. คำนวณ VCP (Volatility Contraction) 
        # หาความแกว่งของราคาย้อนหลัง 20 วัน เทียบกับ 60 วัน (ถ้า 20 วันล่าสุดกราฟแกว่งน้อยลง แปลว่ากำลังบีบตัว)
        std_60 = df['Close'].tail(60).std()
        std_20 = df['Close'].tail(20).std()
        
        # 3. เงื่อนไขขั้นเทพ: 
        # - ต้องชนะตลาด (RS Score > 0.05 คือชนะ SET อย่างน้อย 5%)
        # - กราฟต้องบีบตัวแคบลง (ความผันผวน 20 วันล่าสุด น้อยกว่าครึ่งหนึ่งของ 60 วัน)
        # - ราคาต้องยืนเหนือเส้น EMA 50
        
        df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
        is_above_ema50 = latest_close > df['EMA_50'].iloc[-1]
        
        is_stronger_than_market = rs_score > 0.05
        is_contracting = std_20 < (std_60 * 0.6)
        
        if is_above_ema50 and is_stronger_than_market and is_contracting:
            results.append({
                "ticker": ticker.replace('.BK', ''),
                "close": round(latest_close, 2),
                "rs_outperform": f"+{round(rs_score * 100, 2)}%",
                "vcp_status": "กำลังบีบตัว 💥"
            })
            
    except Exception as e:
        pass

# เรียงลำดับจากตัวที่ชนะตลาดมากที่สุด
results = sorted(results, key=lambda x: float(x['rs_outperform'].replace('+','').replace('%','')), reverse=True)

output = {
    "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "data": results
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=4, ensure_ascii=False)

print("อัปเดตระบบ RS + VCP สำเร็จ!")
