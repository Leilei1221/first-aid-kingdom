# 獎狀底圖生圖提示詞 v0.1

整理日期：2026 年 10 月 14 日　用途：貼到 ChatGPT 生圖。提示詞以英文為主（生圖較穩定），旁邊附中文說明。
接進遊戲的做法：圖放 `assets/cert_grad.webp`、`assets/cert_honor.webp`，**姓名、日期、星星、標題文字都由程式疊上去**（所以圖上不能有字，也不用管姓名位置會不會對不準）。

## 0. 使用前先看

| 項目 | 說明 |
|---|---|
| 張數 | 2 張：結業獎狀（綠色系）、優等獎狀（金色系，更華麗）。兩張版型相同，只有配色與裝飾程度不同，方便程式用同一套文字位置 |
| 比例 | 橫式 A4（約 1.414 : 1）。若 ChatGPT 只能出 3:2，就用 3:2，我再裁切 |
| 風格 | 和遊戲同一種：厚塗奇幻 RPG 風、暖色光、羊皮紙質感。**附上遊戲裡任一張風格參考圖**（例如 `assets/home.webp` 或 `chapters/ch3/assets/ch3_aed_cabinet.webp`），提示詞開頭寫「Match the art style of the attached reference image」 |
| 標誌 | **不要紅十字**；急救標誌一律綠底白十字（遊戲的盾牌徽章） |
| 文字 | 圖上完全不要有字、字母、數字、假文字（lorem ipsum 風格的亂碼也不行） |
| 中間要空白 | 中央大約 70% 寬 × 60% 高要是乾淨、平整的羊皮紙，因為姓名與文字會疊上去；裝飾只放在邊框、四角、上緣與下緣 |
| 不要出現 | 真人臉孔、血、傷口、實體 BLS／AHA／紅十字會等任何機構的標誌（獎狀只是遊戲紀錄，不能讓人以為是正式證書） |

## 1. 結業獎狀（綠色系）

```
Match the art style of the attached reference image: hand-painted fantasy RPG game art, rich painterly texture, warm cinematic lighting, saturated but not harsh colors.
A landscape certificate background, A4 landscape ratio (about 1.414:1), viewed straight on, flat front view. Aged cream parchment paper with soft fibers and subtle stains. A decorative border in forest green and antique bronze: a double-line frame with vine and laurel-leaf patterns. In each of the four corners, an ornate corner piece with small golden stars. At the top center, a blank green ribbon banner with no text. At the bottom center, a small round emblem: a green shield with a white cross, flanked by two laurel branches. A faint stamp-like watermark of the same shield in the center at very low opacity. The central area (about 70% width and 60% height) must stay clean, flat, empty parchment with no decoration, so text can be added later. Calm, proud, achievement feeling, suitable for high school students. No text, no letters, no numbers, no logos, no watermark, no faces, no red cross anywhere.
```

中文說明：奶油色羊皮紙＋森林綠與古銅色雙線邊框，藤蔓與月桂葉花紋，四角小金星；上緣空白綠緞帶（標題疊上去）、下緣綠底白十字盾牌＋月桂枝；中間留白。

## 2. 優等獎狀（金色系，更華麗）

```
Match the art style of the attached reference image: hand-painted fantasy RPG game art, rich painterly texture, warm cinematic lighting, saturated but not harsh colors.
A landscape certificate background, A4 landscape ratio (about 1.414:1), viewed straight on, flat front view. Aged cream parchment paper with soft fibers and subtle stains. A richly decorated border in polished gold and deep forest green: a double-line frame with laurel wreath patterns, small gemstones set in the corners, and sparkling gold dust. In each of the four corners, an ornate golden corner piece with a larger star. At the top center, a blank golden ribbon banner with no text, with a small crown-like flourish above it. At the bottom center, a larger round emblem: a green shield with a white cross and golden wings on both sides, framed by laurel branches. A faint stamp-like watermark of the same shield in the center at very low opacity. The central area (about 70% width and 60% height) must stay clean, flat, empty parchment with no decoration, so text can be added later. Triumphant, honorable, celebratory feeling, suitable for high school students. No text, no letters, no numbers, no logos, no watermark, no faces, no red cross anywhere.
```

中文說明：同一版型，但邊框改金色並鑲小寶石、四角大星、金色緞帶加皇冠裝飾、下緣盾牌多一對金翅膀，整體更華麗。

## 3. 生出來之後

- 兩張的**留白範圍要大致一樣**（中央 70%×60%），否則程式的文字位置要分開調。
- 若某張中央還是有花紋或浮水印太深，請重生，或告訴我，我可以在程式裡加一層淡淡的米色遮罩蓋住。
- 圖給我路徑後我會：轉成 webp、接進獎狀畫面與列印頁，並跑 `tools/cert_test.py`；現有的 CSS 金框會保留成「圖片載入失敗時的備用」。
