"""重新產生 assets/manifest.json（新增或刪除圖片後執行）。遊戲啟動時依此清單預先載入所有圖片。"""
import json, os
root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
names = sorted(f[:-5] for f in os.listdir(root) if f.endswith('.webp'))
json.dump(names, open(os.path.join(root, 'manifest.json'), 'w'), ensure_ascii=False)
print(len(names), '張圖片')
