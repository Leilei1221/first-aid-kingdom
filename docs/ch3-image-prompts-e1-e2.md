# 第三章擴充（E1、E2）生圖提示詞 v0.1

整理日期：2026 年 10 月 8 日　用途：貼到 ChatGPT 生圖。提示詞以英文為主（生圖較穩定），旁邊附中文說明。
**2026-10-09：E1、E2 的圖已全部接進遊戲**（轉檔腳本 `tools/ch3_import_e12_images.py`，可重跑）。

---

## 0. 使用前先看

| 項目 | 說明 |
|---|---|
| 傷口圖 | 420×420、白底、乾淨的插畫風，和現有 `w_snake.webp`（腳踝蛇咬）、`w_bee.webp` 同一種畫法。**附上 `w_snake.webp` 當風格參考**，提示詞開頭寫「Match the art style of the attached reference image」 |
| 物件圖 | 透明背景 PNG（不能透明就用純淺灰底，我來去背），厚塗奇幻 RPG 道具風，和 `ch3_aed_cabinet.webp`（綠色 AED 箱）同一種畫法。**附上 `ch3_aed_cabinet.webp` 當風格參考** |
| 標誌 | **不要紅十字**；急救標誌一律綠底白十字 |
| 文字 | 圖上不要有可讀的文字、字母、數字 |
| 分寸 | 這是高中生用的急救教學：傷口要看得出特徵，但**不要血腥、不要太噁心**，不要出現真人臉孔 |

### 共用風格段（傷口圖，每次開頭貼這一段）

```
Match the art style of the attached reference image: clean semi-realistic medical illustration, soft shading, smooth outlines, pure white background, square 1:1 composition, close-up of the affected body part cropped like a textbook figure. Educational and not gory: show the key features clearly but keep blood minimal. No text, no letters, no numbers, no watermark, no faces.
```

### 共用風格段（物件圖）

```
Match the art style of the attached reference image: hand-painted fantasy RPG game prop, chunky readable shapes, rich painterly texture, warm cinematic lighting, saturated but not harsh colors, isometric 2.5D feel viewed from about 45 degrees. Single object centered, plain flat light-gray background for easy cutout. No text, no letters, no numbers, no logos, no watermark. No red cross anywhere.
```

---

## 1. 傷口圖（E1，4 張）

遊戲位置：求助事件開場、傷口圖鑑。檔名 `w_octopus`、`w_jelly`、`w_rockcut`、`w_vibrio`；收到後我會轉成 420×420 WebP、加進 `content/wounds.json` 的對應 key。

### 1.1 w_octopus 藍環章魚咬傷

中文說明：前臂內側一個很小的咬痕（兩個小小的穿刺點），周圍輕微紅腫，旁邊畫一個很小的藍環章魚當說明圖（不是在傷口上）。咬痕本身要小，因為這種咬傷常常不痛、看起來不嚴重，這正是它危險的地方。

```
[共用風格段（傷口圖）]
Close-up of the inner forearm of a person with light skin, showing a very small bite wound: two tiny puncture marks close together with a little red swelling around them, minimal blood. In the lower-right corner of the image, a small separate inset illustration of a blue-ringed octopus (tan body with bright electric-blue rings), drawn cleanly like a textbook inset. The bite itself looks small and harmless-looking.
```

### 1.2 w_jelly 水母螫傷

中文說明：前臂上有一條一條細長、微微隆起的紅色鞭痕狀紅腫，還黏著幾根透明的絲狀物。

```
[共用風格段（傷口圖）]
Close-up of a forearm with several thin, raised, red whip-like welts forming a crisscross pattern, with a few translucent thread-like tentacle fragments still stuck to the skin, slight surrounding redness and swelling, minimal blood.
```

### 1.3 w_rockcut 岩石（牡蠣殼）割傷

中文說明：小腿外側一道不規則、有點參差的割傷，邊緣沾著細沙，有少量血，傷口旁有小小的刮痕。

```
[共用風格段（傷口圖）]
Close-up of a shin with an irregular jagged cut about the length of a finger, light bleeding, fine grains of sand stuck at the edges, a few small scratches nearby. Looks like a cut from sharp shells on rocks.
```

### 1.4 w_vibrio 海洋弧菌感染（皮膚紅腫）

中文說明：這張是重點，要看得出「傷口周圍快速擴大的紅腫」：手掌側緣原本一個小傷口，周圍大片紅腫發亮、幾個水泡、顏色偏暗紅，但不要有化膿特寫、不要噁心。

```
[共用風格段（傷口圖）]
Close-up of the side of a hand and wrist: a small original wound in the center, surrounded by a large spreading area of red, shiny, swollen skin with a few fluid-filled blisters, color darker red toward the center and lighter red at the edges, signaling a rapidly spreading infection. Clean illustration, no pus close-up, not gory.
```

---

## 2. 物件圖（E1、E2）

| 檔名 | 名稱 | 用在 | 尺寸建議 |
|---|---|---|---|
| hb_board | 港口公告板 | 港口廣場（E1） | 360×420 |
| fish_spot | 碼頭釣魚點（木箱、水桶、魚竿架） | 港口碼頭邊（E2） | 360×300 |
| fish_stall | 魚攤 | 港口市集（E2） | 480×420 |
| fish_mackerel、fish_horse、fish_snapper、fish_grouper | 4 種魚圖示 | 釣到時、魚簍（E2） | 各 256×256 |
| prot_turtle、prot_ray | 海龜、鬼蝠魟 | 保育類事件與知識卡（E2） | 各 320×320 |
| fishing_rod | 釣竿 | 商店與背包圖示（E2） | 256×256 |

### 2.1 hb_board 港口公告板

中文說明：木製公告板，有遮雨的小屋簷，板面上貼著幾張紙（沒有字，只畫出紙的形狀與圖示線條）；旁邊掛一個小小的綠底白十字牌，表示港口安全。

```
[共用風格段（物件圖）]
A wooden harbor notice board with a small shingled roof, standing on two sturdy posts, several paper notes and a rolled map pinned to the board as blank pieces of paper with only simple abstract line drawings (no words), a small green sign with a white cross hanging at the side, a coil of rope and a lantern at the base, blue-and-white seaside color accents.
```

### 2.2 fish_spot 碼頭釣魚點

```
[共用風格段（物件圖）]
A cozy fishing spot on a wooden pier: a wooden fishing rod stand holding two bamboo fishing rods, a wooden bucket with a few small fish, a small tackle box, a coil of fishing line, a folding wooden stool, a lantern on a post. Compact grouping, seaside harbor mood.
```

### 2.3 fish_stall 魚攤

中文說明：藍白條紋遮陽棚的魚攤，冰塊上擺魚，旁邊有一個小炭烤爐可以烤魚，桌上有一個大秤與幾個竹籃；**攤位旁牆上掛著一張很大的魚網，上面打一個大叉（不使用流刺網的意思）**，用圖示就好、不能有字。

```
[共用風格段（物件圖）]
A seaside fish market stall with a blue-and-white striped awning, fresh fish laid on crushed ice in wooden crates, a small charcoal grill with a fish being grilled, a hanging balance scale, bamboo baskets, a wooden counter. On the side post, a hanging sign board showing a drawing of a large fishing net with a big bold X drawn across it (pictogram only, no words). Warm friendly mood.
```

### 2.4 魚類圖示（4 張，側面、乾淨、容易辨認）

```
[共用風格段（物件圖）]
A single [FISH] seen from the side, clean readable silhouette, fresh and shiny, painterly game item icon, centered.
```
把 `[FISH]` 換成：
- **fish_mackerel**：mackerel（鯖魚，背上有藍綠色波浪紋）
- **fish_horse**：horse mackerel（竹筴魚，銀灰色、尾部有稜鱗）
- **fish_snapper**：red snapper（鯛魚，粉紅偏紅色）
- **fish_grouper**：grouper（石斑魚，體型較厚、有斑點）

### 2.5 保育類（2 張，要有尊嚴感、不要可愛過頭）

```
[共用風格段（物件圖）]
A [ANIMAL] swimming gracefully, seen from a slight top-down angle, realistic proportions in a hand-painted game style, soft blue water highlights around it, centered.
```
把 `[ANIMAL]` 換成：
- **prot_turtle**：green sea turtle（綠蠵龜）
- **prot_ray**：giant manta ray（鬼蝠魟）

### 2.6 fishing_rod 釣竿

```
[共用風格段（物件圖）]
A simple wooden fishing rod with a reel and a coil of line, lying diagonally, game item icon style, centered.
```

---

## 3. 收到圖之後我會做的事

- 傷口圖：轉成 420×420 WebP，加進 `content/wounds.json`（key：`octopus`、`jelly`、`rockcut`、`vibrio`），求助事件開場就會顯示傷口圖，也會進傷口圖鑑。
- 物件圖：去背、轉成 WebP、放進 `chapters/ch3/assets/`，換掉目前的文字徽章；魚類圖示會顯示在釣到的畫面與魚簍。
- 丟給我的方式：把檔案放在專案資料夾外面任何地方，告訴我路徑就好。

---

# E3 生圖提示詞（各國商人、商船、海圖碎片、登山裝備）

整理日期：2026 年 10 月 9 日。每一類先貼「共用段」，再貼各項那一句。

## E3-0 登山裝備的換色與穿搭（老師 2026-10-09 提問）

- **換色可以做**：衣物圖用「單一鮮豔底色（紅）＋灰白黑的配件」畫，程式用色相旋轉產生紅、橙、黃、綠、青、藍、紫、粉等顏色，不用每個顏色各畫一張；灰、白、黑色用降低飽和度做。
- **畫在主角身上的限制**：主角圖（`hero.webp`，330×520）是固定姿勢的單張圖，身上已經有披風、大背包、腰帶；疊上去的衣服只能近似對位，不是逐像素貼合。建議**先各畫一張外套、毛帽當測試**，放進遊戲看效果，OK 再畫其餘。
- 背包、裝備欄用的圖示可以直接用同一張圖。

## E3-1 三位商人（全身＋頭像）

附上 `ch3_lifeg.webp`（港口救生員）當風格參考。尼泊爾內陸國，沒有港口，所以商人是「搭別國的船來」。

**全身圖共用段**
```
Match the art style of the attached reference image: full-body fantasy RPG character, detailed painterly anime-influenced illustration, standing relaxed front-facing three-quarter pose, whole body visible from head to boots, plain light-gray background for easy cutout, soft warm lighting. No text, no letters, no logos, no watermark. A friendly traveling merchant who is also a good teacher.
```
- **merchant_jp（日本）**：`A middle-aged Japanese man in a dark indigo samue work outfit with a straw hat, a wooden fishing box and bundles of dried kelp tied on his back, a couple of fishing rods in one hand, warm smile.`
- **merchant_au（澳洲）**：`A sun-tanned Australian woman in her thirties with a wide-brim sun hat, long-sleeve sun-protection shirt and shorts, a bright first-aid satchel with a green cross on her hip, zinc sunscreen on her nose, holding a bandage roll, cheerful.`
- **merchant_np（尼泊爾）**：`A Nepali mountain guide and trader in his forties, wearing a layered wool jacket, a knitted wool cap with ear flaps, a thick scarf and sturdy boots, a big framed backpack loaded with warm clothes, an ice axe and coiled rope, calm and kind expression.`

**頭像共用段（各 160×160，附上剛生好的全身圖當參考）**
```
Head-and-shoulders portrait of the same character as in the attached full-body image, same art style and same outfit, friendly expression, square 1:1 composition, plain light-gray background for easy cutout. No text, no watermark.
```

## E3-2 商船（3 艘，各 480×360）
```
Match the art style of the attached reference image: hand-painted fantasy RPG game prop, chunky readable shapes, rich painterly texture, warm cinematic lighting, isometric 2.5D feel viewed from about 45 degrees. A small merchant sailing ship moored sideways at a pier, crates and barrels on deck, plain flat light-gray background for easy cutout. No text, no letters, no watermark. [SHIP]
```
- 日本：`Wooden ship with a battened white sail, a simple white flag with a red circle.`
- 澳洲：`White-hulled cutter with a blue flag with white stars.`
- 尼泊爾：`The same kind of small cutter, flying a crimson double-pennant flag with a blue border (it is chartered by the mountain trader).`

## E3-3 海圖碎片（256×256）
```
Match the art style of the attached reference image: hand-painted fantasy RPG item icon, rich painterly texture, warm lighting, single object centered, plain flat light-gray background for easy cutout. No text, no letters, no watermark. A torn fragment of an old parchment sea chart with coastlines, dotted routes and a corner of a compass rose, no words.
```

## E3-4 登山裝備

附上 `ch3_aed_cabinet.webp` 當風格參考。

**可穿戴衣物（主體用「鮮紅色」，拉鍊、毛邊、鞋底用灰白黑，不要用棕色；正面、左右對稱、沒有身體、懸空）**
```
Match the art style of the attached reference image: hand-painted fantasy RPG equipment piece, painterly texture, warm lighting. Front-facing view as if worn, symmetrical, floating with no body or mannequin, plain flat light-gray background for easy cutout. The main fabric is one saturated bright red; zippers, trims, fur lining and soles are neutral white, gray or black (no brown, no other colors) so it can be recolored later. No text, no letters, no logos, no watermark. [ITEM]
```
- **gear_jacket**：`A thick insulated mountaineering parka with a hood, sealed pockets and a zipper.`（先做，測試用）
- **gear_hat**：`A knitted wool beanie with a folded cuff and a small pom-pom.`（先做，測試用）
- gear_pants：`Insulated mountaineering trousers with knee reinforcement and ankle straps.`
- gear_gloves：`A pair of insulated mountaineering gloves with long cuffs.`
- gear_boots：`A pair of sturdy insulated mountaineering boots with thick gray soles.`
- gear_goggles：`Snow goggles with a wide strap and tinted gray lenses.`
- gear_pack1：`A medium-size framed mountaineering backpack with side pockets and straps.`
- gear_pack2：`A large expedition mountaineering backpack with a rolled sleeping mat and an ice axe attached.`

**圖示（4 張，各 256×256，不需要換色）**
```
Match the art style of the attached reference image: hand-painted fantasy RPG item icon, rich painterly texture, warm lighting, single object centered, plain flat light-gray background for easy cutout. No text, no letters, no watermark. [ITEM]
```
- item_handwarmer：`A small hand-warmer pouch, slightly puffy, with a gentle warm orange glow.`
- item_blanket：`A folded silver emergency thermal blanket, shiny foil texture.`
- item_headlamp：`A mountaineering headlamp on an elastic strap, lit.`
- item_socks：`A pair of thick wool hiking socks, folded.`
