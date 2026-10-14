"""把老師生的獎狀底圖轉成遊戲用的 WebP：結業（綠色）、優等（金色）。
用法：python3 tools/cert_import.py "<原始圖檔資料夾>"（要有 ch4_certificate_bg.png、ch4_certificate_gold_bg.png）
輸出 assets/cert_grad.webp、assets/cert_honor.webp（原尺寸 1492×1054，列印 A4 橫式夠用）。文字都由程式疊上去。"""
import sys, pathlib
from PIL import Image
ROOT = pathlib.Path(__file__).parent.parent
SRC = pathlib.Path(sys.argv[1])
for src, out in [('ch4_certificate_bg.png', 'cert_grad'), ('ch4_certificate_gold_bg.png', 'cert_honor')]:
    im = Image.open(SRC / src).convert('RGB')
    im.save(ROOT / 'assets' / f'{out}.webp', 'WEBP', quality=90, method=6)
    print(out, im.size, (ROOT / 'assets' / f'{out}.webp').stat().st_size // 1024, 'KB')
