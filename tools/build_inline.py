"""把 src/ 與 assets/ 組回單一 HTML（重現目前 claude.ai 發布的版本，供比對用）。
用法：python tools/build_inline.py            -> dist/first-aid-kingdom.html（含 #debug 測試掛鉤）
      python tools/build_inline.py prod       -> 移除 #debug 測試掛鉤"""
import base64,json,re,sys,os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A=os.path.join(ROOT,'assets')
assets={os.path.splitext(f)[0]:'data:image/webp;base64,'+base64.b64encode(open(os.path.join(A,f),'rb').read()).decode() for f in os.listdir(A) if f.endswith('.webp')}
t=open(os.path.join(ROOT,'src','head.html'),encoding='utf-8').read()+open(os.path.join(ROOT,'src','script.js'),encoding='utf-8').read()
t=t.replace('__ASSETS__',json.dumps(assets)).replace('__WALKS__',open(os.path.join(ROOT,'src','walks.json'),encoding='utf-8').read())
if len(sys.argv)>1 and sys.argv[1]=='prod': t=re.sub(r"\nif\(location\.hash==='#debug'\)window\.__fa=\{.*?\};\n","\n",t)
os.makedirs(os.path.join(ROOT,'dist'),exist_ok=True)
open(os.path.join(ROOT,'dist','first-aid-kingdom.html'),'w',encoding='utf-8').write(t)
print('built',len(t)//1024,'KB')
