# 雪嶺（E4）F4 生圖提示詞 v0.1：雪線（凍傷與雪盲）

整理日期：2026 年 10 月 9 日　對應 `docs/ch4-plan.md` 第 2 節「雪線：凍傷、雪盲」。
圖片請交到 `圖檔/ch4_assets/原始圖檔/`（和 F1～F3 同一個資料夾）。共用規則同前：場景附 `ch4_camp2.webp` 當風格參考，人物附 `ch4_elder.webp` 或 `ch4_hiker.webp`，傷口圖附 `assets/w_snake.webp`。**不要紅十字、圖上不要有可讀文字、不要真實地標與宗教人物。**

## 0. F4 要幾張圖
| # | 內容 | 用途 | 尺寸 | 必要性 |
|---|---|---|---|---|
| 1 | 雪線（白天） | 主場景：凍傷、雪盲題目的地點 | 1672×941 | 必要 |
| 2 | 登山攝影師（站立，全身＋頭像） | 雪線的傷者：為了拍照脫掉手套與護目鏡 | 全身 1024×1536 左右、頭像 1254×1254 | 必要 |
| 3 | 攝影師（雪盲版，全身） | 雪盲題目情境圖（雙手遮眼、流淚、瞇眼） | 同上 | 建議 |
| 4 | 攝影師（凍傷版，全身） | 凍傷題目情境圖（縮著手、手指發白） | 同上 | 建議 |
| 5 | 傷口圖：手指凍傷 `w_frostbite` | 凍傷題目（傷口圖鑑也會收錄） | 420×420、白底 | 必要 |
| 6 | 傷口圖：臉頰與鼻頭凍傷 `w_frostface` | 凍傷題目第二張（不要臉孔，只畫局部） | 420×420、白底 | 建議 |
| 7 | 傷口圖：雪盲（眼睛紅腫流淚）`w_snowblind` | 雪盲題目 | 420×420、白底 | 必要 |

帕桑、老周、小宇沿用現有圖。傷口圖鑑會多三格，需要老師確認名稱（我暫定：手指凍傷、臉部凍傷、雪盲）。

## 1. 雪線場景（#1）
中文說明：海拔最高的雪地，空氣冷冽、陽光很強、反光刺眼，是玩家第一次看到大片冰雪的地方。比營地 2 更「白」，樹完全沒有，只剩岩石、冰壁和雪坡，遠處可以看到山屋的屋頂（提示下一站）。
- **上方左側**：一堵藍白色的冰壁與冰川，旁邊插著幾根插著紅旗的路標竿（用旗子顏色表示路線，沒有字）。
- **上方中央偏右**：一座小型石砌「避風小屋」（只有一個開口、沒有門牌），可以讓人躲風休息與保暖，門口有一小堆行李。
- **右上**：一條往上的雪坡小徑，遠處有一棟冒著煙的山屋（很小、當遠景），路口有繩索欄，**現在先不通**（F5 才開）。
- **左下**：往下回營地 2 的石階小路，路口立著木製路標（箭頭與圖案，不要字）。
- **右側**：一個石塔（cairn）、一支插在雪裡的冰斧、一小堆整齊的行李，後方遠處有雪崩警示用的紅旗竿（**只當遠景，不要畫雪崩**）。
- **中央與下半部**：一大片平坦的雪地，**完全空曠**（我要做可走遮罩）。

**共用段**
```
Match the art style of the attached reference image: hand-painted fantasy RPG game environment, wide cinematic 16:9 composition, isometric 2.5D feel viewed from about 45 degrees above, rich painterly texture, saturated but not harsh colors. A large open flat walkable ground area in the center and lower part of the image with no obstacles on it; props, rocks and cliffs are placed along the top edge and the sides only. No characters standing in the walkable area. No text, no letters, no numbers, no logos, no watermark. No red cross anywhere.
```

**#1 提示詞**（附上 `ch4_camp2.webp` 當風格參考）
```
[共用段]
A high Himalayan-inspired snow field near the snow line, very bright sunlight with strong glare on pure white snow, thin cold air, deep blue sky, no trees at all, only snow, rock and ice. Upper left: a blue-white ice wall and glacier edge, with several slim route-marker poles flying small red flags. Upper center-right: a small stone-built windbreak shelter hut with one open doorway (no sign), a small pile of luggage at its entrance. Upper right: a snowy slope path leading further up toward a tiny distant mountain lodge with a thin line of smoke, blocked at the path start by a simple rope fence. Lower left: a stone stair path leading down to the lower camp with a wooden signpost using arrows and pictograms only. Right side: a small stacked-stone cairn, an ice axe stuck upright in the snow, and a neat small pile of backpacks. The center and lower part is a wide, completely clear flat area of packed snow.
```

## 2. 登山攝影師（#2、#3、#4）
中文說明：三十歲上下的登山攝影師，熱愛拍照、拍起來就忘我。為了拍到雪線的照片，**把手套和護目鏡都脫掉**，在強烈的反光與低溫下待太久。他是雪線的示範角色：先是雪盲（眼睛），再是手指發白（凍傷）。造型中性，不特別指定性別；身上有相機與腳架，其他裝備齊全（保暖外套、毛帽、登山靴）。
- 檔名建議：`ch4_photog.png`、`ch4_photog_face.png`、`ch4_photog_snowblind.png`、`ch4_photog_cold.png`。

**全身共用段（附上 `ch4_hiker.webp` 當風格參考）**
```
Match the art style of the attached reference image: full-body fantasy RPG character, detailed painterly anime-influenced illustration, standing relaxed front-facing three-quarter pose, whole body visible from head to boots, plain light-gray background for easy cutout, soft warm lighting. No text, no letters, no logos, no watermark.
```

**#2 站立**
```
[全身共用段]
A mountain photographer around thirty, enthusiastic and absorbed in the moment, wearing a warm insulated jacket, a wool cap, trekking trousers and sturdy boots, a camera hanging on the chest and a compact tripod on the backpack, holding the camera up with bare hands (no gloves on), no goggles or sunglasses on the face, a bright excited smile.
```

**頭像**（附上剛生好的全身圖）
```
Head-and-shoulders portrait of the same character as in the attached full-body image, same art style and same outfit, bright excited smile, square 1:1 composition, plain light-gray background for easy cutout. No text, no watermark.
```

**#3 雪盲版**（附上 #2 當參考）
```
The same character as in the attached image, same outfit and same art style, now suffering from snow blindness: both hands covering the eyes, face scrunched up, eyes squeezed shut and watering with tears running down, red irritated eyelids, bending forward slightly, the camera hanging from the neck. Awake and conscious, not collapsed, not dramatic, not gory. Full body, plain light-gray background for easy cutout. No text, no letters, no watermark.
```

**#4 凍傷版**（附上 #2 當參考）
```
The same character as in the attached image, same outfit and same art style, now with very cold bare hands: hunched, both hands tucked tightly against the chest and clenched, fingers visibly pale and waxy-white, shoulders pulled up, shivering lightly, wincing. Awake and conscious, not collapsed, not dramatic, not gory. Full body, plain light-gray background for easy cutout. No text, no letters, no watermark.
```

## 3. 傷口圖（#5、#6、#7）
風格：附上 `assets/w_snake.webp`（和第三章的 `w_octopus` 等同一種畫法）。**不要血腥、不要出現黑色壞死或組織缺損**，只畫「看得出來是什麼」的程度；不要出現臉孔（臉頰那張只畫局部）。

**共用風格段（傷口圖，每次開頭貼這一段）**
```
Match the art style of the attached reference image: clean semi-realistic medical illustration, soft shading, smooth outlines, pure white background, square 1:1 composition, close-up of the affected body part cropped like a textbook figure. Educational and not gory: show the key features clearly but keep it mild. No text, no letters, no numbers, no watermark, no faces.
```

### 5. `w_frostbite` 手指凍傷
中文說明：幾根手指的指尖，皮膚發白蠟黃、有點發硬的感覺，邊緣微紅，其中一兩根指尖有一個小水泡；背景白色。
```
[共用風格段（傷口圖）]
Close-up of the fingertips of a hand with light skin showing early frostbite: several fingertips pale, waxy white-yellow and slightly hard-looking, with a faint red margin around the pale areas, and one or two fingertips with a single small clear blister. No black or dead tissue, no blood.
```

### 6. `w_frostface` 臉頰與鼻頭凍傷
中文說明：只畫「局部」：臉頰與鼻頭的一小塊皮膚，蒼白、蠟黃，邊緣泛紅；不要畫出眼睛、嘴巴、整張臉。
```
[共用風格段（傷口圖）]
Close-up of a small cropped patch of skin on a cheek and the tip of a nose with light skin (cropped so that no eyes, mouth or full face are visible), showing early frostbite: a pale, waxy white-yellow patch with a faint red margin around it. No black or dead tissue, no blood.
```

### 7. `w_snowblind` 雪盲
中文說明：只畫「一隻眼睛」的局部特寫（眼白與眼瞼），眼白佈滿紅血絲、眼瞼紅腫、眼眶有淚水；不要畫整張臉。
```
[共用風格段（傷口圖）]
Close-up of a single human eye cropped tightly to the eye and eyelids only (no other facial features visible): bloodshot white of the eye, red and slightly swollen eyelids, tears welling and running from the corner. Looks painful and irritated, mild illustration, no blood.
```

## 4. 交付後我會做的事
- 雪線場景：轉 WebP、做可行走遮罩、設定避風小屋（休息保暖）、回營地 2 的石階、往山屋的繩索欄（F5 才通）。
- 攝影師：去背、頭像裁 160×160；雪盲版、凍傷版用在題目畫面。
- 三張傷口圖：轉 420×420 WebP、加進 `content/wounds.json` 的新 key（章節程式註冊，不動核心的傷口圖鑑清單，除非你要收進圖鑑）。
- 第 4 節題目與知識卡會另外出**草稿**給你審（內容依規劃文件第 4 節：凍傷＝不搓揉、不用雪擦、移除戒指等束縛、有再凍結風險時不要先解凍、保暖並就醫；雪盲＝護目鏡預防（陰天也要）、症狀、暗處休息、取下隱形眼鏡、冷敷、不揉眼、沒好轉要就醫；**藥物與溫水浸泡的溫度與時間不教**）。
- 營地 2 右上的小徑在第 3 節完成後打開，通到雪線。

## 5. 還沒有、但之後的階段會需要
山屋室外（室內已有圖）；章末演練的場景與傷者、章末紀念物；山屋日常的公告板。到各階段再出提示詞。
