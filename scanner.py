import pandas as pd
import yfinance as yf
import pandas_ta as ta
import datetime
import json
import warnings

warnings.filterwarnings('ignore')

# 1. รายชื่อหุ้น SET100
tickers = ['AAV.BK', 'ADVANC.BK', 'AMATA.BK', 'AOT.BK', 'AP.BK', 'AWC.BK', 'BAM.BK', 'BANPU.BK', 
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
    'TRUE.BK', 'TTB.BK', 'TU.BK', 'VGI.BK', 'WHA.BK', 'WHAUP.BK']

end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=100)

results = []

print("กำลังใช้คณิตศาสตร์ถอดรหัสแท่งเทียน...")

for ticker in tickers:
    try:
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if len(df) < 20: continue
            
        # 2. ให้ pandas_ta สแกนหาแพทเทิร์นแท่งเทียน
        # คืนค่าออกมาเป็นตารางที่มีค่า 100 (ถ้าเจอขาขึ้น), -100 (ถ้าเจอขาลง), หรือ 0 (ถ้าไม่เจอ)
        hammer = df.ta.cdl_pattern(name="hammer")
        engulfing = df.ta.cdl_pattern(name="engulfing")
        
        # ดึงข้อมูลแถวล่าสุด (ราคาปิดของวันนี้) มาเช็ก
        latest_close = df['Close'].iloc[-1]
        
        # ตรวจสอบว่ามีค่า 100 ในคอลัมน์ของวันล่าสุดหรือไม่
        latest_hammer = hammer.iloc[-1, 0] if (hammer is not None and not hammer.empty) else 0
        latest_engulfing = engulfing.iloc[-1, 0] if (engulfing is not None and not engulfing.empty) else 0
        
        is_hammer = (latest_hammer == 100)
        is_engulfing = (latest_engulfing == 100)
        
        # 3. ถ้าเจอแพทเทิร์นใดแพทเทิร์นหนึ่ง ให้บันทึกลงระบบ
        if is_hammer or is_engulfing:
            pattern_name = []
            if is_hammer: pattern_name.append("Hammer 🔨")
            if is_engulfing: pattern_name.append("Bullish Engulfing 📈")
            
            results.append({
                "ticker": ticker.replace('.BK', ''),
                "close": round(float(latest_close), 2),
                "pattern": " + ".join(pattern_name)
            })
            
    except Exception as e:
        pass

# 4. บันทึกผลลัพธ์ลงไฟล์ data.json
output = {
    "last_updated": end_date.strftime("%Y-%m-%d %H:%M:%S"),
    "data": results
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=4, ensure_ascii=False)

print("สแกนและบันทึกไฟล์ data.json สำเร็จ!")
