"""Render the current A4 style from separately editable per-airport JSON content.
Style owners edit flyer-template.html; data owners edit flyer-data.json.
No URL, UTM or airport copy is embedded in the visual template.
"""
from pathlib import Path
from string import Template
import json,html
import qrcode,cv2
B=Path(__file__).parent;P=B/'pdf';P.mkdir(exist_ok=True)
D=json.loads((B/'flyer-data.json').read_text())['airports'];T=Template((B/'flyer-template.html').read_text());manifest=[]
for item in D:
 c=item['airport_code'];url=item['qr_url'];img=qrcode.make(url,error_correction=qrcode.constants.ERROR_CORRECT_Q,box_size=10,border=4);img.save(P/f'{c}-qr.png')
 decoded,_,_=cv2.QRCodeDetector().detectAndDecode(cv2.imread(str(P/f'{c}-qr.png')));assert decoded==url,(c,decoded)
 values={k:html.escape(str(v),quote=True) for k,v in item.items() if isinstance(v,str)}
 headline=html.escape(item['headline']);em=html.escape(item['headline_emphasis']);values['headline_html']=headline.replace(em,'<em>'+em+'</em>',1)
 values.update(qr_image=c+'-qr.png',qr_alt='QR code for '+c+' pet travel guide',bullets_html=''.join('<li><b>'+html.escape(x['heading'])+'</b><span>'+html.escape(x['body'])+'</span></li>' for x in item['bullets']))
 (P/f'{c}-flyer.html').write_text(T.substitute(values));manifest.append({'airport':c,'url':url,'qr_png_decoded':decoded})
(P/'qr-manifest.json').write_text(json.dumps(manifest,indent=2));print(f'{len(D)} flyers rendered from separate JSON data and visual template')
