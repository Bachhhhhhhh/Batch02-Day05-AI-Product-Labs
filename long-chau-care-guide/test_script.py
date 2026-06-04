import urllib.request
import json

msg = """vẫn lỗi: CEFUROXIM 500MG (EFODYL 500MG) - 14,00 viên Ngày uống 2 lần, mỗi lần 1 uống (sang chieu) 2. METHYLPREDNISOLON 16 MG (MENISON 16mg) - 03,00 viên Ngày uống 1 lần, mỗi lần 1 uống (SÁNG SAU ĂN) 3. BROMHEXIN 8MG (BROMHEXIN, 8mg (Berlin, Germany) 8mg) - 21,00 Viên Ngày uống 3 lần, mỗi lần 1 Viên (,SANG, CHIEU ,TOI) 4. PARACETAMOL 500MG + CAFFEINE 65MG (PANADOI EXTRA 500mg+65mg (Sanofi Việt nam) ) - 21,00 Viên Ngày uống 3 lần, mỗi lần 1 Viên ( sang chieu -toi) 5. DORITHRICIN 05+1+15MG (RENTSCHLER GERMANY) - 20,00 Viên (bên cạnh có chữ viết tay "hết") (DORITHRICIN, 0,5+1+1,5mg (Rentschler, Germany) ) Ngày ngậm 4 lần, mỗi lần 1 Viên ( sang chieu -toi)"""

data = json.dumps({'message': msg, 'provider': 'gemini', 'chat_history': []}).encode('utf-8')
req = urllib.request.Request('http://127.0.0.1:8000/api/chat', data=data, headers={'Content-Type': 'application/json'})

try:
    res = urllib.request.urlopen(req, timeout=30)
    response_data = json.loads(res.read().decode('utf-8'))
    print("KEYS IN RESPONSE:", list(response_data.keys()))
    if 'prescription_explanation' in response_data:
        print("TABLE LENGTH:", len(response_data['prescription_explanation']))
        print("TABLE CONTENT:\n", response_data['prescription_explanation'][:200])
    else:
        print("MISSING prescription_explanation!")
    print("MESSAGE:", response_data.get('message', ''))
except Exception as e:
    print("ERROR:", e)
