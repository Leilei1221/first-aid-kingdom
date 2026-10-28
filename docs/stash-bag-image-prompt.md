# 防災包圖示：生圖提示詞

用途：取代遊戲裡目前的綠色圓形「包」字標記。出現兩處：爺爺家（序章）與第二章旅館二樓房間。同一張圖兩處共用。

## 規格
- 單一物件，正面微俯視（跟場景一致的 3/4 視角），放在地上的樣子，背包整體完整入鏡、四周留白。
- **純灰底（#808080 左右、無漸層、無地面、無陰影）**，方便去背（跟交通工具圖同做法）。
- 不要任何文字或數字。
- 正方形，建議 1024×1024；遊戲內只顯示約 90～110 px，所以輪廓要簡單、色塊要清楚。
- 風格：與爺爺、主角同一套——手繪奇幻 RPG 插畫、暖色、有質感的皮革與帆布。

## 提示詞（可直接貼）
```
Hand-painted fantasy RPG game item illustration, a sturdy emergency "go bag" (disaster-preparedness backpack) standing upright on the ground, three-quarter top-down view, centered with generous margin. Olive-green canvas body with brown leather straps and brass buckles, a rolled blanket strapped on top, a small canteen and a coiled rope on the side, a front pocket. A clean white cross inside a green rounded-square emblem sewn on the front (first-aid symbol, no text). Warm, soft lighting, rich painterly texture matching a cozy adventure game, clear readable silhouette suitable for small display size. Plain flat solid gray background (#808080), no ground, no cast shadow, no text, no watermark.
```

## 交檔後我會做
1. 去背、縮到最長邊 400，存成 `assets/escape_bag.webp`（轉檔腳本 `tools/stash_bag_import.py`）。
2. 把 `js/game.js` 爺爺家與 `chapters/ch2/chapter.js` 旅館二樓兩處的綠色圓形「包」換成這張圖（沿用原本位置與互動範圍，行為不變）。
3. 補進 `assets/manifest.json`，跑 `tools/stash_test.py` 與版面檢查。

## 備註
- 防災包畫面裡每個物品用的小圓章（`badge`）不動，只換場景裡的大標記。
