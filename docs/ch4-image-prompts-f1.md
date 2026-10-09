# 雪嶺（E4）F1 生圖提示詞 v0.1

整理日期：2026 年 10 月 9 日　用途：貼到 ChatGPT 生圖，提示詞以英文為主，旁邊附中文說明。對應 `docs/ch4-plan.md` 第 9 節 F1（章節骨架）。
圖片交到 `~/Library/CloudStorage/OneDrive-個人/健康與護理作業/115/多元選修/急救王國/圖檔/` 下的新資料夾「第四章圖卡」，檔名不拘；我收到後轉檔去背、命名、做遮罩、接進遊戲（比照 `tools/ch3_import_e3_images.py`）。

## 0. F1 要幾張圖
| # | 內容 | 用途 | 尺寸 | 背景 |
|---|---|---|---|---|
| 1 | 山腳村（室外場景） | 抵達與出發地點，有旅店門、裝備攤、上山路標、回藍堡的碼頭口 | 1672×941 | 完整場景 |
| 2 | 山腳旅店（室內場景） | 住處（睡覺、防災包） | 1672×941 | 完整場景 |
| 3 | 帕桑嚮導（全身） | 同行嚮導，主場景 NPC | 330×520 左右 | 淺灰底（我去背） |
| 4 | 帕桑嚮導（頭像） | 對話框 | 160×160 | 淺灰底 |
| 5 | 旅店老闆娘（全身＋頭像） | 住處店主，之後賣暖暖包、熱飲 | 同上 | 淺灰底 |

之後 F2～F6 的營地、雪線、山屋場景與傷口圖另出提示詞。

## 1. 使用前先看
- **風格參考**：場景附 `chapters/ch3/assets/ch3_harbor.webp`（藍堡港口）；人物附 `chapters/ch3/assets/ch3_m_np.webp`（帕桑商人版）與 `ch3_lifeg.webp`。
- **標誌**：不要紅十字；急救標誌一律綠底白十字。
- **文字**：圖上不要有可讀的文字、字母、數字（招牌、旗幟用圖案代替）。
- **世界觀**：以尼泊爾山區為靈感的虛構村莊（石牆、木造陽台、經幡、犛牛、梯田），**不要真實地標、不要宗教人物與神像**。經幡只當作五色布條的裝飾。
- **氣候**：山腳村是微冷、有薄雪點綴的晴天（不是暴風雪），因為玩家要在這裡走動、補買裝備。

## 2. 場景共用段
```
Match the art style of the attached reference image: hand-painted fantasy RPG game environment, wide cinematic 16:9 composition, isometric 2.5D feel viewed from about 45 degrees above, rich painterly texture, warm morning light, saturated but not harsh colors. A large open flat walkable ground area in the center and lower part of the image with no obstacles on it; buildings, cliffs and props are placed along the top edge and the sides only. No characters, no animals standing in the walkable area. No text, no letters, no numbers, no logos, no watermark. No red cross anywhere.
```

### 2.1 山腳村（室外）
中文說明：山谷裡的小村，後方是雪山，中央是一片平坦的石板廣場（可走動）。
- **上方正中偏右**：兩層木石旅店，門口亮著暖光（門是互動點）。
- **右側**：一個露天裝備攤（掛著外套、毛帽、手套、繩索，攤位上沒有字）。
- **上方左側**：一條往上的石階山路，路口立著木製路標（用箭頭與小圖案，不要字），之後通往營地 1。
- **下方（靠畫面底部中央）**：通往回藍堡船隻的小碼頭或河岸渡口，一艘小船繫在木樁上（出口）。
- 廣場上不要放石頭、柵欄、水桶，這些會擋住走路。

```
[Scene shared block]
A small Himalayan-inspired mountain foothill village in a valley, snow-capped peaks looming behind, thin patches of snow on the ground. In the upper center-right: a two-story stone-and-timber inn with a warm glowing doorway and a balcony hung with colorful prayer-flag-like cloth strings. On the right side: an open-air outfitter stall with a wooden canopy, with parkas, wool beanies, gloves and coiled ropes hanging on it, no signs with words. In the upper left: a stone staircase path leading uphill, with a wooden signpost at its start using arrows and simple pictograms only. At the bottom center: a small riverbank landing with a little wooden boat tied to posts. Stone retaining walls and terraced fields along the far edges. The center is a wide flat flagstone plaza, completely clear.
```

### 2.2 山腳旅店（室內）
中文說明：溫暖的木頭旅店大廳兼房間，有爐火與床，要有一塊放防災包的位置。
- **上方**：牆邊的壁爐與櫃檯（老闆娘站的位置，在畫面上方偏左）。
- **右上**：一張乾淨的單人床（睡覺互動點）。
- **左下角或右下角**：一個門（出口，回室外）。
- **中央與下半部**：大片空地木地板（可走動），中間可以放一張矮桌，但不要擋路，且桌子靠牆。
- 靠牆的角落留一個放背包的位置（空木箱或架子）。

```
[Scene shared block]
The interior of a cozy Himalayan mountain lodge room, warm timber walls, wool rugs on a wooden floor, a stone fireplace with a glowing fire on the upper wall, a wooden reception counter at the upper left, a clean single bed with a thick wool blanket at the upper right, a wooden shelf and an empty low wooden chest in a back corner (place for a backpack), colorful woven wall hangings, a small window showing snowy peaks, a wooden door at the lower-left corner as the exit. The center and lower part of the floor is a wide clear empty wooden floor.
```

## 3. 人物共用段

### 全身圖共用段
```
Match the art style of the attached reference image: full-body fantasy RPG character, detailed painterly anime-influenced illustration, standing relaxed front-facing three-quarter pose, whole body visible from head to boots, plain light-gray background for easy cutout, soft warm lighting. No text, no letters, no logos, no watermark.
```

### 頭像共用段（各 160×160，附上剛生好的全身圖當參考）
```
Head-and-shoulders portrait of the same character as in the attached full-body image, same art style and same outfit, friendly expression, square 1:1 composition, plain light-gray background for easy cutout. No text, no watermark.
```

### 3.1 帕桑（嚮導版，附 `ch3_m_np.webp` 當角色參考）
中文說明：同一個人，但現在在自己的家鄉、以嚮導身分帶隊：服裝比商人版精簡（不背大商品包），改背中型登山包，胸前掛哨子（之後求救訊號會用到），手持冰斧，腰間有繩索。要讓人一眼認得出是第三章那位商人（同樣的臉、紅色針織帽、圍巾）。
```
[Full-body shared block]
The same Nepali mountain guide as in the attached reference image (same face, same age in his forties, same red-patterned knitted cap with ear flaps and thick scarf), now dressed as a professional mountain guide in his home mountains: a layered wool-and-shell jacket, insulated trousers, sturdy boots, a medium-size framed backpack (not the big merchant load), a metal whistle hanging on a cord on his chest, an ice axe in one hand, a coiled rope at his waist, a green-and-white first-aid pouch at his belt (green background with a white cross, not red). Calm, reliable and kind expression.
```
檔名建議：`ch4_guide.png`、`ch4_guide_face.png`

### 3.2 旅店老闆娘（附 `ch3_fishwife.webp` 當風格參考）
中文說明：山村旅店的老闆娘，五十多歲，穿傳統風格的條紋圍裙與厚羊毛衫，頭巾，笑容溫暖，手捧一個熱飲杯。
```
[Full-body shared block]
A warm-hearted Himalayan village innkeeper woman in her fifties, wearing a thick hand-knitted wool cardigan, a striped woven apron in muted red, blue and ochre stripes, a patterned headscarf, sturdy felt boots, holding a steaming ceramic cup in both hands, kind motherly smile.
```
檔名建議：`ch4_innk.png`、`ch4_innk_face.png`

## 4. 交付後我會做的事
- 場景：轉 WebP、依場景描述做可行走遮罩（`tools/ch3_masks.py` 同款）、設出口與互動點位置；若碼頭、旅店門、路標的位置和上面描述差很多，我會告訴你，不用重生，改程式座標即可。
- 人物：去背、轉 WebP、頭像裁成 160×160。
- 圖檔會放 `chapters/ch4/assets/`，key 前綴 `ch4_`，並加進 `ratios.json` 與 `chapter.json` 的 `assets`。
- 圖沒到之前，我可以先用現有圖當暫時背景把 F1 的程式與測試做完，圖到再替換（你決定要不要先做）。
