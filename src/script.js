<script>
(function(){
const A=__ASSETS__;
const WALKS=__WALKS__;
const KEY='fa-kingdom-p1-v1',MW=1672,MH=941,CELL=8;
const RM=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
document.documentElement.style.setProperty('--world',`url(${A.world})`);
document.getElementById('titleHero').src=A.hero;

/* ================= 內容資料（審核時改這裡） ================= */
const ITEMS={
 glove:{name:'拋棄式手套',ch:'套',color:'#4F8FD6',text:'#fff',price:20,w:1,desc:'處理傷口、接觸血液前先戴上，保護自己也保護傷者。'},
 gauze:{name:'無菌紗布',ch:'紗',color:'#F4F4F0',text:'#333',price:15,w:1,desc:'覆蓋傷口、直接加壓止血。'},
 elastic:{name:'彈性繃帶',ch:'繃',color:'#D9B38C',price:25,w:2,desc:'固定敷料，也能對扭傷處適度壓迫。'},
 saline:{name:'生理食鹽水',ch:'鹽',color:'#CDE7E3',price:20,w:3,desc:'沖洗傷口上的砂土髒污。'},
 bandaid:{name:'OK繃',ch:'OK',color:'#E8B87A',price:10,w:1,desc:'小傷口清潔後貼上保護。'},
 ice:{name:'冰敷袋',ch:'冰',color:'#8FD3F0',price:25,w:2,desc:'扭傷、挫傷、蜂螫腫痛時冰敷用。使用時外面要包一層布。'},
 water:{name:'開水',ch:'水',color:'#BFE3F5',w:2,desc:'煮沸放涼的乾淨開水，可以喝，也可以代替生理食鹽水沖洗傷口。'},
 sugar:{name:'方糖',ch:'糖',color:'#FFF3DC',text:'#8A5A2B',price:10,w:1,desc:'體力快用完、頭暈冒冷汗時可以吃，快速補充糖分。'},
 sling:{name:'三角巾',ch:'巾',color:'#E07A5F',text:'#fff',price:30,w:2,desc:'可做成懸臂帶支撐受傷的手臂，也能包紮固定。'},
 ration:{name:'乾糧',ch:'糧',color:'#D9B26B',w:2,desc:'用小麥做成、免烹煮的乾糧，是防災避難包的食物。要注意保存期限。'},
 cotton:{name:'雪白棉花球',ch:'棉',color:'#FFFFFF',text:'#666',price:5,w:1,fake:true,desc:'迷霧商人說：「傷口塞一團棉花，血馬上就不流了！」',
   truth:'棉花纖維容易黏在開放性傷口上，也不能有效止血。傷口要用無菌紗布覆蓋，直接加壓。'},
 toothpaste:{name:'清涼薄荷牙膏',ch:'膏',color:'#9BE0C6',price:5,w:2,fake:true,desc:'迷霧商人說：「燙傷、擦傷塗一點，涼涼的馬上不痛！」',
   truth:'牙膏不能處理燙傷或擦傷：它會把熱悶在皮膚裡，也可能增加感染風險。燙傷要先用流動的冷水沖，擦傷要先沖洗乾淨。'},
 soy:{name:'祖傳醬油',ch:'醬',color:'#6B3A22',text:'#fff',price:5,w:3,fake:true,desc:'迷霧商人說：「燙傷塗醬油，保證不留疤！」',
   truth:'燙傷不可以塗醬油等偏方：會污染傷口、增加感染風險，也可能妨礙醫護人員判斷傷勢。'}
};
const MATS={wood:{name:'木材',sell:3,icon:'i_twig'},stone:{name:'石頭',sell:2,icon:'i_pebble'},gold:{name:'金礦',sell:25,icon:'rock_gold'},wheat:{name:'小麥',sell:4,icon:'ripe'},seed:{name:'小麥種子',buy:5},
 flower:{name:'野花',sell:3,icon:'i_flower'},scrap:{name:'廢鐵片',sell:1,icon:'i_scrap'},mushroom:{name:'野生菇',icon:'i_mushroom'},rawwater:{name:'井水（未煮沸）'},pipe:{name:'銅管',buy:30,icon:'i_pipe'},gear:{name:'齒輪',buy:60,icon:'i_gear'}};
const GIFTABLE=['flower','wheat','wood','stone','gold','mushroom'];
const LIKES={grandpa:{love:'wood',hate:'mushroom',loveTxt:'木柴！爺爺年紀大了怕冷，這個最實用了。',normTxt:'謝謝你記得爺爺。',hateTxt:''},
 kid:{love:'flower',hate:'stone',loveTxt:'哇！好漂亮的花！我要插在窗邊！',normTxt:'謝謝大哥哥！',hateTxt:'……石頭？這個我不要啦。'},
 wood:{love:'wheat',loveTxt:'新鮮小麥！今晚可以烤麵包了，謝啦！',normTxt:'喔，謝謝你啊。',hateTxt:''},
 shopkeeper:{love:'gold',loveTxt:'天啊，是金礦！你真是太貼心了！',normTxt:'哎呀，謝謝你！',hateTxt:''}};
const RECIPES={
 sprinkler:{name:'自動灑水器',need:{stone:5,scrap:2,pipe:1},max:3,desc:'每天早上自動幫周圍的田澆水。'},
 harvester:{name:'自動收割機',need:{wood:15,gold:3,scrap:3,gear:1},max:1,desc:'每天早上把成熟的小麥收進農田旁的收納箱。'}};
const BENCH_WOOD=10;
const MED_FEE=100,HYPO_AT=20;
const EVENTS=[
 {id:'bee',who:'kid',intro:'嗚哇！我在花叢邊被蜜蜂叮了，手臂又紅又腫，好痛……',needs:{ice:1},
  qs:[{q:'蜂螫的針還留在皮膚上，該怎麼做？',opts:['儘快移除螫針，可以用卡片邊緣刮掉，再清洗、冰敷','塗一點醬油消腫','不用管它，等它自己掉下來'],ans:0,
  explain:'螫針留在皮膚上會持續釋放毒液，要儘快移除，再清洗、冰敷減輕腫痛。如果出現呼吸困難、臉或嘴唇腫起來，要立刻求救。'}],thanks:'不那麼痛了，謝謝大哥哥！'},
 {id:'allergy',who:'kid',after:'bee',intro:'大、大哥哥……我剛剛又被蜜蜂叮了，嘴唇好腫，喉嚨好緊，喘不過氣……',needs:{},
  qs:[{q:'小芽被叮後嘴唇腫起來、呼吸困難，你該怎麼做？',opts:['先冰敷看看，等一下就會好','立刻打 119，讓她保持舒服的姿勢；如果有醫師開的腎上腺素注射筆，協助她使用','讓她喝點水，躺下睡一覺'],ans:1,
  explain:'呼吸困難、嘴唇腫起來可能是嚴重過敏反應，會危及生命，不能等。要立刻打 119；呼吸困難時可以讓她坐起來；有醫師開立的腎上腺素注射筆就協助使用。'}],thanks:'（救護人員趕到，把小芽送去醫院。隔天她就活蹦亂跳地回來了。）'},
 {id:'nose',who:'wood',intro:'哎呀！彈回來的樹枝打到我的鼻子，鼻血一直流……',needs:{gauze:1},
  qs:[{q:'流鼻血時，正確的做法是？',opts:['頭往後仰，讓血不要流出來','身體稍微前傾，捏住鼻翼（鼻子柔軟的部分），用嘴巴呼吸','平躺下來休息'],ans:1,
  explain:'頭往後仰會讓血流進喉嚨，可能嗆到或想吐。應身體前傾、捏住鼻翼約 10 分鐘，可以用紗布接住流出的血。'}],thanks:'血止住了，還是你靠得住！'},
 {id:'tetanus',who:'wood',intro:'可惡，這把舊斧頭生鏽了，一滑就砍到我的小腿……傷口又深又髒！',needs:{glove:1,gauze:1},
  qs:[{q:'傷口還在流血，第一步該怎麼做？',opts:['戴上手套，用無菌紗布直接加壓止血','先塗醬油消毒','用泥土把傷口蓋住'],ans:0,explain:'出血時先直接加壓止血。'},
      {q:'血止住了，但傷口又深又髒，斧頭還生鏽。接下來呢？',opts:['貼上 OK 繃就好，不用管它','清洗傷口後就醫，讓醫師評估是否需要追加破傷風疫苗','再塗一點薄荷牙膏'],ans:1,
  explain:'被生鏽的工具、泥土弄髒的深傷口有感染破傷風的風險，清洗後要就醫，讓醫師評估是否需要追加破傷風疫苗。'}],thanks:'好，我這就去給醫生看看。多虧你提醒！'},
 {id:'snake',who:'wood',intro:'啊！草叢裡有蛇，我的腳踝被咬了！',needs:{},
  qs:[{q:'阿木被蛇咬了，下列哪個做法正確？',opts:['用嘴把毒液吸出來','用繩子把腿綁緊，阻止毒液流動','讓他保持冷靜少動，固定被咬的部位，取下束縛物，記下蛇的特徵，儘速送醫'],ans:2,
  explain:'用嘴吸毒、切開傷口、綁緊止血帶、冰敷都不正確。應讓傷者保持冷靜、少動，被咬的部位固定、約與心臟同高或略低，取下戒指手錶，記下蛇的特徵，儘速送醫。'}],thanks:'（阿木被送去醫院打了血清，兩天後就回來砍樹了。）'},
 {id:'cut',who:'shopkeeper',intro:'唉呀，剛剛切菜切到手指了，流了一些血……',needs:{glove:1,bandaid:1},
  qs:[{q:'小傷口在流血，第一步該怎麼做？',opts:['撒一點麵粉上去止血','用嘴巴吸傷口','戴上手套，用乾淨的布直接按壓止血'],ans:2,
  explain:'小傷口一樣以直接加壓止血為優先，止血後用清水沖洗，再貼上 OK 繃。撒麵粉等偏方會污染傷口，用嘴吸也可能造成感染。'}],thanks:'謝謝你，下次切菜我會小心的！'}];
const STORIES={
 shopkeeper:{card:'burn',text:['跟你說個祕密。我年輕時在廚房打翻一鍋熱湯，當時聽人說塗牙膏最有效……結果傷口發炎，留下了疤。','後來團長教我「沖、脫、泡、蓋、送」，我一輩子都記得。你也要記住喔。']},
 wood:{card:'spine',text:['我年輕時從樹上摔下來，脖子痛得要命。同伴急著把我扶起來，幸好你爺爺大喊「別動他！」','醫生說，那時如果亂動，我可能再也站不起來了。']},
 kid:{card:'choke',text:['上次弟弟吃糖果噎到，臉都發紫了！','是爺爺從後面抱住他，在肚子上用力一壓，糖果就噴出來了。爺爺說這叫哈姆立克法！']},
 grandpa:{card:'cpr',text:['騎士團的第一件神器「心跳之匣」，守護的是停止的心跳。總有一天你會需要它。','來，爺爺先教你，看到有人突然倒下時該怎麼做。']}};
const VICTIMS={
 guard:{situ:'落石砸中頭部，頭皮裂開，血流不止。',needs:{glove:1,gauze:2},
  q:'你用紗布加壓，但紗布很快被血浸濕了。接下來？',opts:['拿掉濕紗布，換一塊新的','不要移除，直接在上面再加一層紗布，持續加壓','先停下來，看看還有沒有在流血'],ans:1,
  explain:'拿掉浸濕的紗布會扯掉剛形成的血塊。應該在上面再加紗布，持續加壓。',ok:'血止住了……謝謝你，小勇者。'},
 cook:{situ:'被倒下的櫃子壓到，前臂變形、劇烈疼痛。',needs:{sling:1},
  q:'疑似前臂骨折，你該怎麼做？',opts:['把變形的骨頭推回原位','維持原本姿勢，用三角巾做懸臂帶支撐固定','請她甩甩手，確認還能不能動'],ans:1,
  explain:'疑似骨折不要自行復位，也不要讓傷者活動患肢。應維持原姿勢固定、支撐，再送醫。',ok:'手臂固定好就沒那麼痛了，謝謝你啊！'},
 soldier:{situ:'逃跑時扭傷腳踝，腫得站不起來。',needs:{ice:1,elastic:1},
  q:'要幫他冰敷，哪種方式正確？',opts:['冰敷袋直接貼皮膚，敷越久越好','冰敷袋外面包一層布，每次約 15 到 20 分鐘','天氣冷，不用冰敷'],ans:1,
  explain:'冰敷袋直接接觸皮膚、敷太久可能凍傷。應隔一層布，每次約 15 到 20 分鐘，並把腳抬高。',ok:'謝、謝謝你……我以後也要學急救！'}};
const RATION_NEED=3,RATION_SELL=15,WATER_NEED=3;
const SIGNS={village:[{x:1520,y:330,t:()=>S.f.p3?'往河谷 →':'往河谷 →（落石擋路）'},{x:890,y:870,t:()=>'↓ 南方森林'}],
 forest:[{x:950,y:150,t:()=>'↑ 綠葉村'},{x:830,y:880,t:()=>S.step>=7?'↓ 爺爺的農田':'↓ 雜草叢生'}],
 farm:[{x:865,y:150,t:()=>'↑ 南方森林'},{x:935,y:880,t:()=>'↓ 礦坑'}],
 mine_out:[{x:90,y:280,t:()=>'← 爺爺的農田'}],
 river:[{x:110,y:400,t:()=>'← 綠葉村'},{x:1560,y:430,t:()=>'東方草原 →'}],
 plain:[{x:110,y:370,t:()=>'← 河谷'},{x:940,y:150,t:()=>'↑ 落石之城'}],
 gate:[{x:760,y:880,t:()=>'↓ 東方草原'}],ruin:[{x:838,y:900,t:()=>'↓ 東方草原'}]};
function autoWater(){let n=0;(S.spr||[]).map(i=>SPRINKLER_SLOTS[i]).forEach(sl=>sl.plots.forEach(i=>{const p=S.plots[i];if(p&&(p.st==='tilled'||(p.st==='planted'&&p.g<GROW_DAYS))&&!p.wet){p.wet=true;n++;}}));return n;}
const SPRINKLER_AREA=['左上角 4 塊田','右上角 3 塊田','下排 4 塊田'];
const SPRINKLER_SLOTS=[{x:585,y:470,plots:[0,1,3,4]},{x:1180,y:420,plots:[2,5,6]},{x:960,y:670,plots:[7,8,9,10]}];
const FORAGE_SPOTS={village:[[620,330],[1350,470],[900,700],[420,390],[1550,330],[880,560]],
 forest:[[480,440],[1300,520],[1200,380],[720,700],[880,850],[1000,120],[420,620]],
 farm:[[250,480],[900,790],[1400,640],[640,300],[300,650],[860,120]]};
const FORAGE_N={village:2,forest:3,farm:2};
const SHOP_MED=['glove','gauze','elastic','saline','bandaid','sling','ice','sugar'];
const MERCHANT_GOODS=['cotton','toothpaste','soy'];
const MAT_UP=[{cap:20,cost:40},{cap:30,cost:90},{cap:40,cost:160}];
const KIT_UP=[{cap:6,cost:60},{cap:8,cost:120},{cap:10,cost:200},{cap:12,cost:280},{cap:14,cost:360}];
const LOAD_OK=8,LOAD_HEAVY=12;           /* 負重：8 以下正常，9～12 變慢，超過 12 很慢 */
const STA_MAX=100,COST={chop:4,mine:5,till:3,water:3,plant:2};
const GROW_DAYS=3,RATION_WHEAT=3,RATION_LIFE=10,MACHINE_WOOD=20,MACHINE_COIN=100;

const CARDS={
 legend:{title:'救護騎士團的傳說',text:'百年前，救護騎士團不靠魔法，而是靠正確的急救知識和三件神器守護王國：心跳之匣、守護之囊、療癒之箱。騎士團解散後，神器的內容物散落各地。'},
 bleed:{title:'外出血怎麼處理',text:'先確認環境安全、戴上手套保護自己。用無菌紗布覆蓋傷口，直接用力加壓。紗布被血浸濕時不要拿掉，在上面再加一層繼續加壓，再用繃帶固定。手邊沒有用品時，可先用乾淨的布直接壓住傷口並求救。'},
 scrape:{title:'擦傷怎麼處理',text:'先用生理食鹽水或乾淨的清水，把傷口上的砂土沖乾淨，再用 OK 繃或敷料覆蓋。不要塗牙膏等偏方，也不要用嘴吹傷口。'},
 mushroom:{title:'野生菇不能隨便吃',text:'許多有毒的菇類和可以吃的菇長得很像，無法用顏色、外觀或「煮熟」來判斷是否安全。不要採食來路不明的野生菇。誤食後如果出現噁心、嘔吐、腹瀉、腹痛等症狀，要儘速就醫，並把剩下的菇帶去給醫師辨識。'},
 fracture:{title:'疑似骨折怎麼辦',text:'受傷部位變形、劇烈疼痛、不能活動時，可能是骨折。不要把骨頭推回原位，也不要讓傷者活動受傷的部位。維持原本的姿勢固定，手臂可以用三角巾做懸臂帶支撐，再儘快送醫。'},
 sprain:{title:'扭傷初期怎麼處理',text:'冰敷（冰敷袋外面包一層布，每次約 15 到 20 分鐘）、用彈性繃帶適度壓迫，並把受傷的部位抬高。受傷初期不要熱敷，也不要用力按摩。'},
 bee:{title:'被蜜蜂叮了怎麼辦',text:'先離開蜂群附近。螫針如果還留在皮膚上，要儘快移除，可以用卡片邊緣刮掉，再用清水清洗、冰敷減輕腫痛。如果出現呼吸困難、臉或嘴唇腫起來、全身起疹子，可能是嚴重過敏，要立刻打 119 求救。'},
 allergy:{title:'嚴重過敏反應',text:'被叮咬或吃了某些東西後，如果出現呼吸困難、喉嚨緊、臉或嘴唇腫起來、全身起疹子、頭暈想昏倒，可能是嚴重過敏反應，要立刻打 119。讓傷者保持舒服的姿勢（呼吸困難時可以坐起來）；如果他有醫師開立的腎上腺素注射筆，協助他使用。'},
 nose:{title:'流鼻血怎麼處理',text:'身體稍微前傾，用手指捏住鼻翼（鼻子柔軟的部分）約 10 分鐘，用嘴巴呼吸。不要把頭往後仰，血會流進喉嚨。如果流血超過 20 分鐘停不下來，或是頭部被重擊後流鼻血，要就醫。'},
 cut:{title:'小傷口流血',text:'戴上手套，用乾淨的紗布或布直接按壓止血；止血後用清水沖洗，再貼上 OK 繃。不要撒麵粉、咖啡粉等偏方，也不要用嘴吸傷口。'},
 tetanus:{title:'髒傷口與破傷風',text:'被生鏽的工具、泥土等弄髒的深傷口，有感染破傷風的風險。先止血、清洗，再就醫讓醫師評估是否需要追加破傷風疫苗。成人的破傷風疫苗一般約每 10 年追加一次；傷口很髒而且距離上次注射超過 5 年，醫師可能會建議追加。'},
 snake:{title:'被蛇咬傷',text:'保持冷靜、遠離蛇，記下蛇的外觀特徵（顏色、花紋、頭形）。讓傷者少動、保持冷靜，把被咬的部位固定不動、約與心臟同高或略低，並取下戒指、手錶等束縛物，儘速送醫。不可以用嘴吸毒液、切開傷口、綁緊止血帶、冰敷或喝酒。'},
 hypo:{title:'頭暈冒冷汗、可能是低血糖',text:'空腹或過度勞動時，可能出現頭暈、冒冷汗、發抖、心跳加快、很餓等症狀（低血糖在糖尿病患者身上比較常見）。如果意識清醒、能吞嚥，可以吃方糖、糖果或喝果汁，休息約 15 分鐘；沒有改善就再補充並就醫。如果意識不清，不可以餵食，以免嗆到，要讓他側躺並打 119。'},
 faint:{title:'有人昏倒、意識不清',text:'先確認環境安全，大聲呼叫、拍肩確認反應，並請人打 119。如果有正常呼吸，讓他側躺（復甦姿勢），避免嘔吐物嗆到。不要餵食、餵水或催吐。如果是誤食造成的，把剩下的東西一起帶給醫護人員。'},
 burn:{title:'燒燙傷：沖、脫、泡、蓋、送',text:'沖：用流動的冷水沖洗傷處約 15 到 30 分鐘。脫：在冷水中小心脫去衣物，黏住的部分不要硬扯，可以剪開。泡：在冷水中持續浸泡約 15 到 30 分鐘。蓋：用乾淨的布或紗布覆蓋。送：儘快送醫。不要塗牙膏、醬油等偏方。'},
 spine:{title:'懷疑頭頸部受傷',text:'懷疑頭部、頸部或背部受傷時，除非現場有立即的危險（例如火災、落石），不要任意移動傷者，儘量讓他的頭頸保持不動，並立刻打 119 求救。'},
 choke:{title:'被東西噎住',text:'如果還能咳嗽、說話，鼓勵他用力咳嗽。如果不能說話、不能咳嗽、無法呼吸，要立刻請人打 119，並使用哈姆立克法（從背後環抱，在肚臍上方向內上方快速擠壓）。一歲以下的嬰兒則改用拍背和壓胸。'},
 cpr:{title:'看到有人突然倒下',text:'先確認環境安全，拍打肩膀大聲呼叫，確認有沒有反應。沒有反應就請旁人打 119、拿 AED。如果沒有正常呼吸，立刻開始胸部按壓，用力壓、快快壓。AED 送到就打開電源，依照語音指示操作。'},
 water:{title:'乾淨的水',text:'井水、山泉水、河水等未經處理的水，看起來清澈也可能含有細菌或寄生蟲，要煮沸後再喝。沖洗傷口可以用生理食鹽水、乾淨的自來水，或煮沸放涼的開水。防災包裡也要準備至少三天份的飲用水。'},
 food:{title:'防災包的食物',text:'防災避難包的食物要選免烹煮、易開封、耐保存的種類。常見建議至少準備三天份的食物與飲水。放進包裡後要定期檢查保存期限，快過期就吃掉並換新。'}
};
const REQUESTS=[
 {from:'shopkeeper',who:'雜貨店老闆',text:'貨架壞了，需要木材修理。',item:'wood',n:4,pay:25},
 {from:'grandpa',who:'爺爺',text:'晚上冷，幫爺爺補充柴火。',item:'wood',n:6,pay:35},
 {from:'kid',who:'小芽',text:'我想做一個木頭小馬！',item:'wood',n:2,pay:12},
 {from:'shopkeeper',who:'雜貨店老闆',text:'要做新的木箱裝貨。',item:'wood',n:8,pay:50},
 {from:'kid',who:'小芽',text:'想幫媽媽做一張小板凳。',item:'wood',n:5,pay:28},
 {from:'wood',who:'樵夫阿木',text:'要幾塊石頭磨斧頭。',item:'stone',n:4,pay:20,p2:true},
 {from:'shopkeeper',who:'雜貨店老闆',text:'想進一批新鮮小麥。',item:'wheat',n:3,pay:22,p2:true},
 {from:'grandpa',who:'爺爺',text:'屋頂漏水，需要石頭修補。',item:'stone',n:6,pay:30,p2:true},
 {from:'kid',who:'小芽',text:'想要一塊亮晶晶的金礦當寶物！',item:'gold',n:1,pay:40,p2:true}
];
const PEOPLE={
 grandpa:{name:'爺爺',img:'grandpa',face:'grandpa_face',hk:1.0},
 kid:{name:'小芽',img:'kid',face:'kid_face',hk:.72},
 wood:{name:'樵夫阿木',img:'wood',face:'wood_face',hk:1.08},
 shopkeeper:{name:'雜貨店老闆',img:'shopkeeper',face:'shopkeeper_face',hk:1.0},
 merchant:{name:'迷霧商人',img:'merchant',face:'merchant_face',hk:1.05},
 hunt:{name:'獵人阿鹿',img:'hunt',face:'hunt_face',hk:1.02},
 guard:{name:'城堡守衛',img:'guard',face:'guard_face',hk:1.06},
 cook:{name:'廚娘',img:'cook',face:'cook_face',hk:.98},
 soldier:{name:'見習小兵',img:'soldier',face:'soldier_face',hk:.95}
};
const RATIO={hunt:.594,cook:.618,guard:.644,soldier:.451,hero:.634,grandpa:.658,kid:.573,wood:.578,shopkeeper:.651,merchant:.639,tree:.889,stump:1.48,bed:.97,machine:.974,sprinkler:1.474,harvester:1.227,bench:1.139,bin:.959,rock:1.254,rock_gold:1.235,rubble:1.772,soil_dry:1.391,soil_wet:1.391,sprout:1.368,tall:1.239,ripe:1.232};

/* 場景：座標為原圖像素 */
const PLOTS=[[430,396],[712,362],[1051,327],[459,551],[758,517],[1039,482],[1326,442],[505,706],[815,677],[1108,643],[1395,603]];
const ROCKS=[[520,430],[780,330],[1040,320],[1300,420],[680,580],[1080,560]];
const SCENES={
 home:{name:'爺爺的家',spawn:[1010,690],bg:'home',heroH:240,
   npcs:[{id:'grandpa',x:1180,y:560,flip:true}],
   things:[{kind:'fire',x:800,y:335,label:'用爐火煮水'},{kind:'shelf',x:430,y:450,label:'查看書架'},{kind:'oldchest',x:1250,y:430,label:'打開舊箱子'},{kind:'bed',x:390,y:640,label:'睡覺'}],
   exits:[{test:(x,y)=>y>845,to:'village',at:[1045,305]}]},
 village:{name:'綠葉村',spawn:[1045,305],bg:'village',heroH:118,
   npcs:[{id:'kid',x:560,y:480},{id:'merchant',x:725,y:250,flip:true}],
   things:[{kind:'door',x:1045,y:290,label:'進入爺爺的家',to:'home',at:[840,770]},{kind:'door',x:330,y:338,label:'進入雜貨店',to:'shop',at:[840,760]},{kind:'board',x:1215,y:452,label:'查看委託板'},{kind:'well',x:765,y:515,label:'水井'}],
   exits:[{test:(x,y)=>y>925,to:'forest',at:[950,70]},{test:(x,y)=>x>1645,to:'river',at:[60,440],need:()=>S.f.p3,block:'往河谷的路被落石擋住了，之後才能通過。'}]},
 forest:{name:'南方森林',spawn:[950,300],bg:'forest',heroH:140,
   npcs:[{id:'wood',x:990,y:640,flip:true}],
   things:[{kind:'fchest',x:360,y:432,label:'打開寶箱'}],
   trees:[{id:'t1',x:470,y:565},{id:'t2',x:620,y:700},{id:'t3',x:1250,y:600},{id:'t4',x:1370,y:470},{id:'t5',x:1120,y:300}],
   exits:[{test:(x,y)=>y<22,to:'village',at:[890,900]},{test:(x,y)=>y>925,to:'farm',at:[865,60],need:()=>S.step>=7,block:'森林南邊的小路雜草叢生，先完成村子裡的事情再說吧。'}]},
 shop:{name:'雜貨店',spawn:[840,700],bg:'shop',heroH:220,
   npcs:[{id:'shopkeeper',x:600,y:500}],things:[],
   exits:[{test:(x,y)=>y>790,to:'village',at:[335,350]}]},
 farm:{name:'爺爺的農田',spawn:[865,120],bg:'farm',heroH:120,npcs:[],
   things:[{kind:'well',x:600,y:258,label:'水井'},{kind:'shed',x:1263,y:300,label:'查看工具棚'},{kind:'machine',x:300,y:560,label:'乾糧製造機'}],
   plots:true,
   exits:[{test:(x,y)=>y<22,to:'forest',at:[830,900]},{test:(x,y)=>y>925,to:'mine_out',at:[70,300]}]},
 mine_out:{name:'礦坑入口',spawn:[400,420],bg:'mine_out',heroH:130,npcs:[],
   things:[{kind:'toolbox',x:830,y:380,label:'查看工具箱'},{kind:'door',x:1160,y:360,label:'進入礦坑',to:'mine_in',at:[860,690]}],
   exits:[{test:(x,y)=>x<35,to:'farm',at:[935,900]}]},
 river:{name:'河谷',spawn:[60,440],bg:'river',heroH:140,npcs:[],things:[{kind:'tablet',x:380,y:350,label:'查看石碑'}],
   exits:[{test:(x,y)=>x<30,to:'village',at:[1540,380]},{test:(x,y)=>x>1642,to:'plain',at:[60,400]}]},
 plain:{name:'東方草原',spawn:[60,400],bg:'plain',heroH:130,npcs:[{id:'hunt',x:1148,y:620,flip:true}],things:[],
   exits:[{test:(x,y)=>x<30,to:'river',at:[1610,450]},{test:(x,y)=>y<25,to:()=>S.quake?'ruin':'gate',at:[760,880]}]},
 gate:{name:'落石之城',spawn:[760,860],bg:'gate',heroH:120,npcs:[{id:'guard',x:712,y:445,flip:true}],things:[{kind:'gatedoor',x:861,y:405,label:'進入城堡'}],
   exits:[{test:(x,y)=>y>920,to:'plain',at:[940,60]}]},
 ruin:{name:'落石之城（地震後）',spawn:[838,880],bg:'ruin',heroH:120,npcs:[{id:'guard',x:643,y:482},{id:'cook',x:1183,y:597,flip:true},{id:'soldier',x:540,y:650}],things:[],
   exits:[{test:(x,y)=>y>920,to:'plain',at:[940,60]}]},
 mine_in:{name:'礦坑深處',spawn:[860,650],bg:'mine_in',heroH:150,npcs:[],rocks:true,things:[],
   exits:[{test:(x,y)=>y>905,to:'mine_out',at:[1150,400]}]}
};

/* ================= 狀態 ================= */
let S=null,busy=true;
function newState(){return migrate({v:1,scene:'home',pos:{x:1010,y:690},coins:0,earned:0,matCap:10,matLv:0,kit:[],kitCap:4,kitLv:0,
  step:0,trees:{},chests:{},cards:{},hearts:{grandpa:0,kid:0,wood:0,shopkeeper:0},req:[0,2,1],reqNext:3,started:false,ctrl:'joy',warned:{}});}
function migrate(o){
  if(!o.mat)o.mat={wood:o.wood||0,stone:0,gold:0,wheat:0,seed:0};delete o.wood;
  if(o.day==null)o.day=1;if(o.sta==null)o.sta=STA_MAX;
  o.tools=o.tools||{};o.plots=o.plots||{};o.rocks=o.rocks||{};
  ['flower','scrap','mushroom','pipe','gear'].forEach(k=>{if(o.mat[k]==null)o.mat[k]=0;});
  o.gifted=o.gifted||{};if(!o.spr){o.spr=[];for(let i=0;i<(o.sprinklers||0);i++)o.spr.push(i);}o.f=o.f||{};o.story=o.story||{};o.rescue=o.rescue||{};['hunt','guard','cook','soldier'].forEach(k=>{if(o.hearts[k]==null)o.hearts[k]=0;});o.sprinklers=o.sprinklers||0;o.bin=o.bin||0;if(!o.forage){o.forage={};o.forageDay=0;}
  Object.values(o.trees||{}).forEach(t=>{if(t.regrow&&t.regrow>1e6)t.regrow=o.day+1;});
  o.v=2;return o;}
function save(){try{localStorage.setItem(KEY,JSON.stringify(S));}catch(e){}}
function load(){try{const r=localStorage.getItem(KEY);if(r){const o=JSON.parse(r);if(o&&(o.v===1||o.v===2))return migrate(o);}}catch(e){}return null;}
const $=id=>document.getElementById(id);
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const base=k=>k.split('@')[0];
const expiry=k=>+(k.split('@')[1]||0);
const expired=k=>base(k)==='ration'&&S.day>expiry(k);
const kitCount=k=>S.kit.filter(x=>base(x)===k&&!expired(x)).length;
const load_=()=>S.kit.reduce((s,k)=>s+ITEMS[base(k)].w,0);
const matUsed=()=>Object.values(S.mat).reduce((a,b)=>a+b,0);
const matFree=()=>S.matCap-matUsed();
function speedMul(){const l=load_();return l>LOAD_HEAVY?.5:l>LOAD_OK?.72:1;}
function badge(k,lg){const it=ITEMS[base(k)];return `<span class="badge ${lg?'lg':''}" style="--c:${it.color};--tc:${it.text||'#1b1b1b'}" aria-hidden="true">${it.ch}</span>`;}
function hearts(id){const n=Math.min(5,S.hearts[id]||0);return '♥'.repeat(n)+'♡'.repeat(5-n);}
function addHeart(id,n){if(id in S.hearts)S.hearts[id]=Math.min(5,S.hearts[id]+n);}
function toast(m){const t=$('toast');t.textContent=m;t.classList.add('on');clearTimeout(toast.t);toast.t=setTimeout(()=>t.classList.remove('on'),1800);}
async function useSta(n){
  if(S.sta<=0){S.pendingFaint='work';return false;}
  const before=S.sta;S.sta=Math.max(0,S.sta-n);refresh();
  if(S.sta<=0){S.pendingFaint='work';return true;}
  if(before>=HYPO_AT&&S.sta<HYPO_AT&&S.hypoDay!==S.day){S.hypoDay=S.day;await hypoWarn();}
  return true;}
async function hypoWarn(){
  const has=kitCount('sugar')>0;
  const i=await say({p:'hero',html:'<p class="warn">從早上工作到現在都沒吃東西……頭好暈、冒冷汗、手在發抖，心跳也好快，肚子好餓。</p>'+(has?'<p>背包裡有方糖。</p>':'<p class="small">如果背包裡有方糖就好了……</p>'),
    buttons:has?[{label:'吃一顆方糖，休息一下',primary:true},{label:'不管它，繼續工作'}]:[{label:'知道了',primary:true}]});
  if(has&&i===0){S.kit.splice(S.kit.findIndex(k=>base(k)==='sugar'),1);S.sta=Math.min(STA_MAX,S.sta+30);refresh();
    const isNew=!S.cards.hypo;S.cards.hypo=true;
    await say({p:'hero',html:`<p>吃了方糖、坐下來休息了一會兒，頭暈和發抖慢慢好轉了。</p><p class="good">體力恢復 30</p><div class="card"><b>${CARDS.hypo.title}</b><p>${CARDS.hypo.text}</p></div>${isNew?'<p class="good">獲得知識卡</p>':''}`});}
  else if(!has)await say({p:'hero',html:'<p class="small">體力歸零就會昏倒。雜貨店有賣方糖，可以放在急救背包裡備用。</p>'});
}
async function faint(reason){
  stopInput();
  await say({icon:'…',who:'',html:reason==='mushroom'?'<p class="bad">吃下野生菇後，肚子絞痛、全身冒冷汗，眼前一黑……</p>':'<p class="bad">眼前突然一片黑，雙腳一軟，倒在地上……</p>'});
  $('fade').classList.add('on');await sleep(RM?0:800);
  const summary=nextDay();
  S.scene='home';S.pos={x:420,y:660};buildScene();S.sta=Math.round(STA_MAX*.6);
  S.coins-=MED_FEE;refresh();$('fade').classList.remove('on');
  if(reason==='mushroom'){
    await say({p:'grandpa',html:'<p>你終於醒了！村人發現你倒在地上，意識不清。大家趕快打電話找醫生，讓你側躺，免得吐出來的東西嗆到，還把剩下的菇拿給醫生看。</p>'});
    await say({p:'grandpa',html:'<p>醫生說你是吃了有毒的野生菇。孩子，野生菇絕對不能隨便吃！</p>'});
    S.cards.mushroom=true;S.cards.faint=true;
    await say({p:'grandpa',html:`<div class="card"><b>${CARDS.faint.title}</b><p>${CARDS.faint.text}</p></div><div class="card"><b>${CARDS.mushroom.title}</b><p>${CARDS.mushroom.text}</p></div><p class="good">獲得知識卡</p>`});}
  else{
    await say({p:'grandpa',html:'<p>你終於醒了！你空著肚子工作過度，昏倒在路邊。醫生來家裡看過了，說是太累又沒吃東西。</p><p>以後頭暈、冒冷汗、發抖的時候就要停下來休息，吃點糖。急救背包裡也可以放幾顆方糖。</p>'});
    S.cards.hypo=true;
    await say({p:'grandpa',html:`<div class="card"><b>${CARDS.hypo.title}</b><p>${CARDS.hypo.text}</p></div>`});}
  await say({icon:'￥',who:'醫療費',html:`<p>醫生的診療費 ${MED_FEE} 金幣。</p>${S.coins<0?`<p class="bad">金幣不夠，先欠著 ${-S.coins} 金幣。還清之前不能在商店買東西。</p>`:`<p>剩下 ${S.coins} 金幣。</p>`}<p class="small">今天是第 ${S.day} 天，體力恢復到 ${S.sta}。</p>`});
  if(summary)await say({icon:'☀',who:`第 ${S.day} 天`,html:summary});
  save();refresh();
}
function matIcon(k,s){const ic=MATS[k].icon;return ic?`<img alt="" src="${A[ic]}" style="width:${s||34}px;height:${s||34}px;object-fit:contain;vertical-align:middle">`:'';}
function matList(){return Object.entries(S.mat).filter(([k,n])=>n>0).map(([k,n])=>`${MATS[k].name} ×${n}`).join('、')||'空的';}

function genForage(){S.forage={};Object.entries(FORAGE_SPOTS).forEach(([sc,spots])=>{
  const pick=spots.slice().sort(()=>Math.random()-.5).slice(0,FORAGE_N[sc]);
  S.forage[sc]=pick.map(([x,y])=>{const r=Math.random();let t=r<.3?'twig':r<.55?'pebble':r<.75?'flower':'scrap';
    if(sc==='forest'&&Math.random()<.35)t='mushroom';return {x,y,t};});});S.forageDay=S.day;}
const PICK={twig:{mat:'wood',txt:'撿到樹枝（木材 +1）',icon:'i_twig'},pebble:{mat:'stone',txt:'撿到小石頭（石頭 +1）',icon:'i_pebble'},flower:{mat:'flower',txt:'摘到一束野花',icon:'i_flower'},scrap:{mat:'scrap',txt:'撿到廢鐵片',icon:'i_scrap'},mushroom:{mat:'mushroom',txt:'採到一朵看起來很好吃的野生菇',icon:'i_mushroom'}};
/* ================= 對話框 ================= */
let dlgResolve=null;
function finish(v){$('dialog').hidden=true;const r=dlgResolve;dlgResolve=null;r&&r(v);}
function say(o){return new Promise(res=>{
  dlgResolve=res;const f=$('dFace');const p=o.p&&PEOPLE[o.p];
  const faceKey=o.p==='hero'?'hero_face':(p?p.face:null);
  if(faceKey){f.style.backgroundImage=`url(${A[faceKey]})`;f.textContent='';}else{f.style.backgroundImage='none';f.textContent=o.icon||'';}
  const nm=o.who||(o.p==='hero'?'你':(p?p.name:''));
  $('dWho').innerHTML=`<span>${nm}</span>`+(p&&o.p in S.hearts?`<span class="hearts" aria-label="好感度 ${S.hearts[o.p]}">${hearts(o.p)}</span>`:'');
  $('dText').innerHTML=o.html||'';
  const bs=$('dBtns');bs.innerHTML='';
  (o.buttons||[{label:'繼續',primary:true}]).forEach((b,i)=>{const el=document.createElement('button');el.type='button';
    el.className='btn'+(b.primary?' primary':'')+(b.danger?' danger':'');el.textContent=b.label;if(b.disabled)el.disabled=true;el.onclick=()=>finish(i);bs.appendChild(el);});
  $('dialog').hidden=false;if(o.onRender)o.onRender($('dText'),finish);
  const fb=bs.querySelector('button:not([disabled])');fb&&fb.focus({preventScroll:true});
});}
async function lines(p,arr){for(const t of arr)await say({p,html:`<p>${t}</p>`});}

/* ================= 場景繪製 ================= */
const plane=$('plane');
let heroEl,heroImg,ringEl,npcEls={},treeEls={},plotEls=[],rockEls=[],machineEl=null,benchEl=null,binEl=null,harvEl=null,sprEls=[],forageEls=[];
function sc(){return SCENES[S.scene];}
function sprite(cls,src,x,y,h,wRatio){const e=document.createElement('div');e.className='ent spr '+cls;
  e.style.setProperty('--x',x);e.style.setProperty('--y',y);e.style.setProperty('--h',h);e.style.setProperty('--w',Math.round(h*wRatio));
  e.style.zIndex=Math.round(y);e.innerHTML=`<img alt="" src="${src||''}">`;plane.appendChild(e);return e;}
function setSprite(e,key,h){e.style.setProperty('--h',h);e.style.setProperty('--w',Math.round(h*RATIO[key]));e.querySelector('img').src=A[key];}
function buildScene(){
  const s=sc();plane.innerHTML='';plane.style.backgroundImage=`url(${A[s.bg]})`;npcEls={};treeEls={};plotEls=[];rockEls=[];machineEl=null;benchEl=null;binEl=null;harvEl=null;sprEls=[];forageEls=[];
  ringEl=document.createElement('div');ringEl.className='ent ring';plane.appendChild(ringEl);
  const H=s.heroH;
  (s.npcs||[]).forEach(n=>{const P=PEOPLE[n.id];const e=sprite('npc shadow',A[P.img],n.x,n.y,Math.round(H*P.hk),RATIO[P.img]);
    if(n.flip)e.querySelector('img').classList.add('flip');
    const tg=document.createElement('div');tg.className='tag';e.appendChild(tg);npcEls[n.id]=e;});
  (s.trees||[]).forEach(t=>{treeEls[t.id]=sprite('tree shadow','',t.x,t.y+6,Math.round(H*1.9),RATIO.tree);});
  if(S.scene==='home'){const b=sprite('','',270,700,290,RATIO.bed);b.querySelector('img').src=A.bed;b.style.zIndex=600;}
  if(s.plots)PLOTS.forEach((p,i)=>{const e=sprite('plot','',p[0],p[1]+95,190,1);e.style.zIndex=Math.round(p[1]);e.hidden=true;plotEls.push(e);});
  if(s.plots){machineEl=sprite('','',300,560,Math.round(H*1.9),RATIO.machine);machineEl.querySelector('img').src=A.machine;}
  if(s.rocks)ROCKS.forEach(r=>rockEls.push(sprite('tree','',r[0],r[1]+20,Math.round(H*.95),RATIO.rock)));
  if(s.plots){benchEl=sprite('','',600,300,Math.round(H*1.05),RATIO.bench);benchEl.querySelector('img').src=A.bench;
    binEl=sprite('','',1450,390,Math.round(H*.95),RATIO.bin);binEl.querySelector('img').src=A.bin;
    harvEl=sprite('','',1480,580,Math.round(H*1.25),RATIO.harvester);harvEl.querySelector('img').src=A.harvester;
    sprEls=SPRINKLER_SLOTS.map(p=>{const e=sprite('','',p.x,p.y,Math.round(H*.9),RATIO.sprinkler);e.querySelector('img').src=A.sprinkler;return e;});}
  if(S.forageDay!==S.day)genForage();
  (S.forage[S.scene]||[]).forEach(f=>{const e=sprite('','',f.x,f.y+14,Math.round(H*.34),1);e.querySelector('img').src=A[PICK[f.t].icon];e.querySelector('img').style.filter='drop-shadow(0 0 6px rgba(255,240,170,.95))';forageEls.push(e);});
  (SIGNS[S.scene]||[]).forEach(g=>{const e=document.createElement('div');e.className='ent signpost';e.style.transform=`translate(${g.x}px,${g.y}px) translate(-50%,-50%)`;e.textContent=g.t();plane.appendChild(e);});
  heroEl=sprite('shadow','',S.pos.x,S.pos.y,H,RATIO.hero);heroEl.id='hero';heroImg=heroEl.querySelector('img');heroImg.src=A.hero;
  refresh();fit();
}
function treeState(t){const st=S.trees[t.id]||{hp:3,regrow:0};if(st.hp<=0&&st.regrow&&S.day>=st.regrow){st.hp=3;st.regrow=0;}S.trees[t.id]=st;return st;}
function rockState(i){let r=S.rocks[i];if(!r||(r.hp<=0&&S.day>=r.regrow)){r={hp:3,gold:Math.random()<.34,regrow:0};S.rocks[i]=r;}return r;}
function plotState(i){return S.plots[i]||{st:'wild'};}
function plotKey(p){ /* 對應圖片 */
  if(p.st==='wild')return null;
  if(p.st==='tilled')return p.wet?'soil_wet':'soil_dry';
  if(p.g>=GROW_DAYS)return 'ripe';if(p.g>=2)return 'tall';if(p.g>=1)return 'sprout';return p.wet?'soil_wet':'soil_dry';}
function refresh(){
  const s=sc(),H=s.heroH;
  (s.trees||[]).forEach(t=>{const st=treeState(t),e=treeEls[t.id];const alive=st.hp>0;setSprite(e,alive?'tree':'stump',alive?Math.round(H*1.9):Math.round(H*.62));});
  plotEls.forEach((e,i)=>{const p=plotState(i),k=plotKey(p);e.hidden=!k;if(!k)return;
    const w=270;e.style.setProperty('--w',w);e.style.setProperty('--h',Math.round(w/RATIO[k]));e.querySelector('img').src=A[k];
    let extra='';if(p.st==='planted'&&p.g<GROW_DAYS&&p.wet)extra+='<span class="drop" aria-hidden="true">水</span>';
    if(p.st==='planted'&&p.g===0)extra+='<span class="seeds">已播種</span>';
    e.querySelectorAll('.drop,.seeds').forEach(x=>x.remove());e.insertAdjacentHTML('beforeend',extra);});
  if(machineEl)machineEl.classList.toggle('ghost',!S.machine);
  if(benchEl)benchEl.classList.toggle('ghost',!S.bench);
  if(binEl)binEl.hidden=!S.harvester;if(harvEl)harvEl.hidden=!S.harvester;
  sprEls.forEach((e,i)=>e.hidden=!S.spr.includes(i));
  rockEls.forEach((e,i)=>{const r=rockState(i);setSprite(e,r.hp>0?(r.gold?'rock_gold':'rock'):'rubble',r.hp>0?Math.round(H*.95):Math.round(H*.55));});
  Object.entries(npcEls).forEach(([id,e])=>{e.querySelector('.tag').innerHTML=PEOPLE[id].name+(npcHasNews(id)?'<span class="bang">!</span>':'');});
  $('place').textContent=s.name;$('coins').textContent=S.coins;$('coins').style.color=S.coins<0?'var(--bad)':'';$('day').textContent=S.day;
  $('sta').textContent=S.sta;const sb=$('staBar');sb.style.width=(S.sta/STA_MAX*100)+'%';sb.classList.toggle('low',S.sta<20);
  $('bagInfo').textContent=`${S.kit.length}/${S.kitCap}`;$('cardInfo').textContent=Object.keys(S.cards).length;
  $('joy').hidden=S.ctrl!=='joy';$('dpad').hidden=S.ctrl!=='pad';
  $('goal').innerHTML='<b>目標</b>'+goalText();
}
function placeHero(){heroEl.style.setProperty('--x',S.pos.x);heroEl.style.setProperty('--y',S.pos.y);heroEl.style.zIndex=Math.round(S.pos.y);}
let scale=1;
function fit(){if($('game').hidden)return;const v=$('view');scale=Math.max(v.clientWidth/MW,v.clientHeight/MH);camera();}
function camera(){const v=$('view'),w=v.clientWidth,h=v.clientHeight;
  let tx=w/2-S.pos.x*scale,ty=h/2-(S.pos.y-sc().heroH*.4)*scale;
  tx=Math.min(0,Math.max(w-MW*scale,tx));ty=Math.min(0,Math.max(h-MH*scale,ty));
  plane.style.transform=`translate(${tx}px,${ty}px) scale(${scale})`;}
window.addEventListener('resize',fit);

/* ================= 劇情 ================= */
function goalText(){switch(S.step){
  case 0:return '和爺爺說話。';
  case 1:return '到村子南邊的森林找樵夫阿木，向他借斧頭。';
  case 2:return '砍樹收集木材，拿到雜貨店賣掉。';
  case 3:return '接委託板的工作賺金幣，到雜貨店擴充包包。';
  case 4:return '回南方森林看看阿木。';
  case 5:{const a=S.flagWoodDone?'✓':'□',b=S.flagKidDone?'✓':'□';return `到雜貨店買急救用品，幫助受傷的村民。${a} 阿木　${b} 小芽`;}
  case 6:return '回家告訴爺爺這個好消息。';
  case 7:return '穿過南方森林，到爺爺的農田拿工具、種小麥。';
  case 8:return `建造乾糧製造機（木材 ${MACHINE_WOOD} 份＋${MACHINE_COIN} 金幣）。`;
  case 9:return `收成小麥，用乾糧製造機做出第一包乾糧（小麥 ${RATION_WHEAT} 份）。`;
  default:{if(S.coins<0)return `你還欠醫療費 ${-S.coins} 金幣，賺錢還清之前不能買東西。`;
    if(S.f.p3&&!S.f.final){if(S.castleDone)return '回綠葉村，把救援的經過告訴爺爺。';if(!S.f.tablet)return '往東走，到河谷看看那塊古老的石碑。';if(!S.f.hunter)return '到東方草原找獵人阿鹿。';if(!S.f.guard)return '往北走到落石之城，和守衛說話。';return `準備好急救背包、${RATION_NEED} 包有效的乾糧和 ${WATER_NEED} 瓶開水，再進入落石之城。`;}
    if(S.step>=10&&!S.f.p3)return '回家和爺爺說說話，好像有新的消息。';
    if(!S.bench)return `在農田蓋一座工作台（木材 ${BENCH_WOOD} 份），之後就能做自動化機器。`;
    if(!S.spr.length||!S.harvester)return '用工作台製作自動灑水器和自動收割機；記得每天送禮給村民。';
    return '農場自動化完成！繼續送禮、接委託，準備好你的背包。';}}}
function npcHasNews(id){
  if(S.event&&S.event.day===S.day&&!S.event.done&&EVENTS.find(e=>e.id===S.event.id).who===id&&S.step>=7)return true;
  if(S.scene==='ruin'&&VICTIMS[id]&&!S.rescue[id])return true;
  if(id==='hunt')return !S.f.hunter;if(id==='guard')return S.scene==='gate'&&!S.f.guard;
  if(STORIES[id]&&S.hearts[id]>=3&&!S.story[id]&&S.step>=7)return true;
  if(id==='grandpa'&&((S.step>=10&&!S.f.p3)||(S.castleDone&&!S.f.final)))return true;
  if(id==='grandpa')return S.step===0||S.step===6||S.step===9&&kitCount('ration')>0;
  if(id==='wood')return S.step===1||(S.step===5&&!S.flagWoodDone);
  if(id==='kid')return S.step===5&&!S.flagKidDone;
  if(id==='shopkeeper')return S.step===2&&S.mat.wood>0;
  return false;}
async function introGrandpa(){
  await lines('grandpa',['你醒啦。坐吧，爺爺有件事一定要告訴你。',
    '百年前，王國有一支救護騎士團。他們不靠魔法，而是靠正確的急救知識，和三件神器守護人民。',
    '騎士團解散後，神器的內容物散落各地。現在東南方的浮空島又出現了災厄之霧……聽說還有個迷霧商人，到處賣奇怪的偏方。']);
  await say({p:'grandpa',html:`<p>這個背包，是當年療癒之箱的外殼。它現在是空的，要靠你自己一件一件裝滿。</p><p>另外這個素材袋給你，砍的木材、挖的礦石都放這裡。</p><p class="small">獲得：急救背包（${S.kitCap} 格）、素材袋（${S.matCap} 格）</p>`,buttons:[{label:'收下',primary:true}]});
  await say({p:'grandpa',html:`<p>先去村子南邊的森林找樵夫阿木，跟他借把斧頭。賺點錢，把包包弄大一點，冒險才走得遠。</p><p class="small">用左下角的${S.ctrl==='joy'?'搖桿':'方向鍵'}走路，靠近人或東西時按右下角的按鈕互動。做事會消耗體力，累了就回家睡覺。</p>`,buttons:[{label:'出發',primary:true}]});
  S.cards.legend=true;S.step=1;
}
async function accident(){
  busy=true;
  try{
    await say({p:'wood',html:'<p>嘿，你來啦！看我示範一下正確的砍法——</p>'});
    await say({icon:'！',who:'',html:'<p class="bad">斧頭一滑，阿木的前臂割開一道口子，鮮血直流！</p>'});
    await say({p:'wood',html:'<p>唔……好痛！你、你身上有沒有什麼可以用的東西？</p>'});
    await say({p:'hero',html:'<p>（翻開急救背包……裡面什麼都沒有。）</p>'});
    const i=await say({p:'merchant',html:'<p>哎呀呀，真巧。我這裡有上等的雪白棉花球，往傷口裡一塞，血馬上就不流了。一顆只要 5 金幣喔。</p>',
      buttons:[{label:'買棉花球塞進傷口'},{label:'不買。請阿木用他乾淨的手帕直接壓住傷口，我去叫爺爺'}]});
    if(i===0){await say({p:'grandpa',html:'<p class="bad">住手！</p><p>棉花的纖維會黏在傷口上，也止不了血。手邊沒有用品的時候，先用乾淨的布直接用力壓住傷口，再找人幫忙。</p>'});}
    else{await say({p:'grandpa',html:'<p class="good">做得好。</p><p>手邊沒有用品的時候，先用乾淨的布直接用力壓住傷口，再找人幫忙。這是正確的判斷。</p>'});addHeart('wood',1);}
    await say({p:'merchant',html:'<p>嘖……真是個不懂行情的老頭。我們後會有期。</p>'});
    await say({p:'grandpa',html:'<p>血暫時壓住了，但傷口還需要好好處理。孩子，這就是急救背包空著的代價。</p><p>去雜貨店買<b>拋棄式手套、無菌紗布、彈性繃帶</b>回來幫阿木包紮。書架上那本外出血的書，爺爺也幫你翻出來了。</p>'});
    S.cards.bleed=true;S.step=5;
    await say({icon:'★',who:'新的內容',html:'<p>雜貨店開始販售急救用品。</p><p class="small">迷霧商人也在村子裡擺起了攤……</p>'});
  }finally{busy=false;save();refresh();}
}

/* ================= 互動 ================= */
function interactables(){const s=sc(),L=[];
  (s.npcs||[]).forEach(n=>{if(npcEls[n.id])L.push({kind:'npc',x:n.x,y:n.y,label:n.id==='merchant'?'看看商品':n.id==='shopkeeper'?'購物':'對話',id:n.id});});
  (s.things||[]).forEach(t=>L.push(Object.assign({},t,t.kind==='machine'?{label:S.machine?'使用乾糧製造機':'建造乾糧製造機'}:{})));
  (s.trees||[]).forEach(t=>{const st=treeState(t);if(st.hp>0)L.push({kind:'tree',x:t.x,y:t.y,label:S.axe?'砍樹':'需要斧頭',t});});
  if(s.plots)PLOTS.forEach((p,i)=>{const ps=plotState(i);let label;
    if(ps.st==='wild')label='翻土';else if(ps.st==='tilled')label=ps.wet?'播種':'澆水';
    else label=ps.g>=GROW_DAYS?'收成':(ps.wet?'今天澆過水了':'澆水');
    L.push({kind:'plot',x:p[0],y:p[1]+40,label,i});});
  if(s.rocks)ROCKS.forEach((r,i)=>{if(rockState(i).hp>0)L.push({kind:'rock',x:r[0],y:r[1],label:S.tools.pick?'敲礦石':'需要十字鎬',i});});
  if(s.plots&&S.step>=10){L.push({kind:'bench',x:600,y:300,label:S.bench?'使用工作台':'建造工作台'});if(S.harvester)L.push({kind:'bin',x:1450,y:390,label:`收納箱（${S.bin}）`});}
  if(s.plots)(S.spr||[]).forEach(si=>L.push({kind:'spr',x:SPRINKLER_SLOTS[si].x,y:SPRINKLER_SLOTS[si].y,label:'移動灑水器',si}));
  (S.forage[S.scene]||[]).forEach((f,i)=>L.push({kind:'pick',x:f.x,y:f.y,label:'撿起來',i}));
  return L;}
let near=null;
function updateNear(){const H=sc().heroH;let best=null,bd=H*.95;
  for(const it of interactables()){const d=Math.hypot(it.x-S.pos.x,(it.y-S.pos.y)*1.3);if(d<bd){bd=d;best=it;}}
  near=best;const a=$('act');
  if(best){a.classList.add('ready');a.textContent=best.label;ringEl.classList.add('on');ringEl.style.setProperty('--x',best.x);ringEl.style.setProperty('--y',best.y);ringEl.style.setProperty('--r',Math.round(H*.45));ringEl.style.zIndex=Math.round(best.y)-1;}
  else{a.classList.remove('ready');a.textContent='動作';ringEl.classList.remove('on');}}
async function doAction(){
  if(busy||$('game').hidden||!near)return;
  const it=near;busy=true;stopInput();
  try{
    if(it.kind==='npc')await talk(it.id);
    else if(it.kind==='door')await go(it.to,it.at);
    else if(it.kind==='board')await board();
    else if(it.kind==='tree')await chop(it.t);
    else if(it.kind==='shelf')await shelf();
    else if(it.kind==='oldchest')await oldChest();
    else if(it.kind==='fchest')await forestChest();
    else if(it.kind==='bed')await bed();
    else if(it.kind==='shed')await shed();
    else if(it.kind==='toolbox')await toolbox();
    else if(it.kind==='plot')await farmPlot(it.i);
    else if(it.kind==='rock')await mine(it.i);
    else if(it.kind==='machine')await machine();
    else if(it.kind==='bench')await bench();
    else if(it.kind==='bin')await takeBin();
    else if(it.kind==='pick')await pickUp(it.i);
    else if(it.kind==='tablet')await tablet();
    else if(it.kind==='spr')await moveSpr(it.si);
    else if(it.kind==='well')await well();
    else if(it.kind==='fire')await boil();
    else if(it.kind==='gatedoor')await gateDoor();
    if(S.pendingFaint){const r=S.pendingFaint;S.pendingFaint=null;await faint(r);}
  }finally{busy=false;save();refresh();updateNear();}
}
async function go(to,at){
  if(typeof to==='function')to=to();
  $('fade').classList.add('on');await sleep(RM?0:280);
  S.scene=to;S.pos={x:at[0],y:at[1]};buildScene();save();
  await sleep(RM?0:60);$('fade').classList.remove('on');
  if(to==='forest'&&S.step===3&&(S.earned>=60||S.matLv+S.kitLv>0))S.step=4;
  if(to==='forest'&&S.step===4){await sleep(RM?0:300);await accident();}
}
function hit(e){e.classList.remove('hit');void e.offsetWidth;e.classList.add('hit');}
async function chop(t){
  if(!S.axe){await say({p:'hero',html:'<p>徒手沒辦法砍樹。先去找樵夫阿木借斧頭吧。</p>'});return;}
  if(matFree()<=0){await say({p:'hero',html:`<p class="warn">素材袋已經滿了（${S.matCap} 格）。</p><p>先把素材賣掉，或到雜貨店擴充素材袋。</p>`});return;}
  if(!await useSta(COST.chop))return;
  const st=treeState(t);hit(treeEls[t.id]);st.hp--;
  if(st.hp>0){toast(`砍！再 ${st.hp} 下`);await sleep(RM?0:160);return;}
  const got=Math.min(3,matFree());S.mat.wood+=got;st.regrow=S.day+1;
  toast(`獲得木材 ×${got}（素材袋 ${matUsed()}/${S.matCap}）`);
  if(S.step===2&&S.mat.wood>=3&&!S.warned.sellHint){S.warned.sellHint=true;await say({p:'hero',html:'<p>收集到木材了。拿去村子的雜貨店賣賣看吧。</p><p class="small">樹木砍倒後，隔天會重新長出來。</p>'});}
}
async function mine(i){
  if(!S.tools.pick){await say({p:'hero',html:'<p>沒有十字鎬敲不動。礦坑入口的工具箱裡也許有。</p>'});return;}
  if(matFree()<=0){await say({p:'hero',html:'<p class="warn">素材袋已經滿了。</p>'});return;}
  if(!await useSta(COST.mine))return;
  const r=rockState(i);hit(rockEls[i]);r.hp--;
  if(r.hp>0){toast(`敲！再 ${r.hp} 下`);await sleep(RM?0:160);return;}
  r.regrow=S.day+1;let msg='';
  if(r.gold&&matFree()>0){S.mat.gold++;msg='金礦 ×1';}
  const s=Math.min(2,matFree());if(s>0){S.mat.stone+=s;msg+=(msg?'、':'')+`石頭 ×${s}`;}
  toast(`獲得 ${msg||'（素材袋滿了）'}`);
}
async function farmPlot(i){
  if(!S.tools.hoe){await say({p:'hero',html:'<p>沒有農具。先到農田旁邊的工具棚看看。</p>'});return;}
  const p=Object.assign({st:'wild'},S.plots[i]);
  if(p.st==='wild'){if(!await useSta(COST.till))return;p.st='tilled';p.wet=false;toast('翻好土了');}
  else if(p.st==='tilled'&&!p.wet){if(!await useSta(COST.water))return;p.wet=true;toast('澆水完成');}
  else if(p.st==='tilled'&&p.wet){if(S.mat.seed<1){await say({p:'hero',html:'<p>沒有種子。到雜貨店買小麥種子吧。</p>'});return;}
    if(!await useSta(COST.plant))return;S.mat.seed--;p.st='planted';p.g=0;if(S.step===7)S.step=8;toast(`播種完成，再 ${GROW_DAYS} 天成熟（每天都要澆水）`);}
  else if(p.st==='planted'&&p.g>=GROW_DAYS){const n=Math.min(3,matFree());if(n<=0){await say({p:'hero',html:'<p class="warn">素材袋已經滿了。</p>'});return;}
    S.mat.wheat+=n;p.st='tilled';p.wet=false;p.g=0;toast(`收成小麥 ×${n}`);}
  else if(p.st==='planted'&&!p.wet){if(!await useSta(COST.water))return;p.wet=true;toast('澆水完成');}
  else{toast('今天已經澆過水了');}
  S.plots[i]=p;autoWater();
}
async function shed(){
  if(S.tools.hoe){await say({p:'hero',html:'<p>工具棚裡整齊地掛著爺爺的舊農具。</p>'});return;}
  S.tools.hoe=true;S.tools.can=true;
  await say({p:'hero',html:'<p>工具棚裡有爺爺年輕時用的鋤頭和澆水壺。</p><p class="good">獲得：鋤頭、澆水壺</p><p class="small">種田的步驟：翻土 → 澆水 → 播種（種子在雜貨店買），之後每天澆水，3 天就能收成。</p>'});
}
async function toolbox(){
  if(S.tools.pick){await say({p:'hero',html:'<p>工具箱裡只剩一些生鏽的釘子。</p>'});return;}
  S.tools.pick=true;
  await say({p:'hero',html:'<p>工具箱裡有一把礦工留下的舊十字鎬，還能用。</p><p class="good">獲得：十字鎬</p><p class="small">礦坑裡的石頭敲三下就會碎，閃著金光的是金礦，可以賣到好價錢。</p>'});
}
async function machine(){
  if(!S.machine){
    const ok=S.mat.wood>=MACHINE_WOOD&&S.coins>=MACHINE_COIN;
    const i=await say({p:'hero',who:'乾糧製造機（建造）',html:`<p>爺爺說，把收成的小麥放進這台機器，就能做成免烹煮、耐保存的乾糧。</p><p>需要：木材 ×${MACHINE_WOOD}（有 ${S.mat.wood}）、金幣 ${MACHINE_COIN}（有 ${S.coins}）</p>`,
      buttons:[{label:ok?'建造':'材料不足',primary:true,disabled:!ok},{label:'離開'}]});
    if(i!==0)return;S.mat.wood-=MACHINE_WOOD;S.coins-=MACHINE_COIN;S.machine=true;if(S.step>=7&&S.step<9)S.step=9;
    await say({icon:'★',who:'建造完成',html:'<p>乾糧製造機完成了！</p><p class="small">放入 3 份小麥，就能做出 1 包乾糧。</p>'});return;}
  const ok=S.mat.wheat>=RATION_WHEAT,full=S.kit.length>=S.kitCap;
  const i=await say({p:'hero',who:'乾糧製造機',html:`<p>放入小麥 ×${RATION_WHEAT}，做出 1 包乾糧，會直接放進急救背包。</p><p>小麥：${S.mat.wheat}　急救背包：${S.kit.length}/${S.kitCap}</p><p class="small">乾糧做好後 ${RATION_LIFE} 天內有效。</p>`,
    buttons:[{label:!ok?'小麥不足':full?'急救背包已滿':'製作乾糧',primary:true,disabled:!ok||full},{label:'離開'}]});
  if(i!==0)return;S.mat.wheat-=RATION_WHEAT;S.kit.push('ration@'+(S.day+RATION_LIFE));
  toast(`做好乾糧！保存到第 ${S.day+RATION_LIFE} 天`);
}
async function bed(){
  const i=await say({p:'hero',who:'床',html:`<p>要睡覺進入下一天嗎？</p><p class="small">體力會恢復，作物會成長（前提是今天有澆水），委託板也會換新。</p>`,buttons:[{label:'睡覺',primary:true},{label:'還不想睡'}]});
  if(i!==0)return;
  $('fade').classList.add('on');await sleep(RM?0:500);
  const html=nextDay();S.sta=STA_MAX;refresh();$('fade').classList.remove('on');
  await say({icon:'☀',who:`第 ${S.day} 天`,html:'<p>早安！體力恢復了。</p>'+html});
}
function nextDay(){
  S.day++;let grown=0,dry=0;
  Object.values(S.plots).forEach(p=>{if(p.st==='planted'&&p.g<GROW_DAYS){if(p.wet){p.g++;grown++;}else dry++;}p.wet=false;});
  S.req=S.req.map(()=>nextReq());
  let auto=0,harv=0;
  if(S.harvester)Object.values(S.plots).forEach(p=>{if(p.st==='planted'&&p.g>=GROW_DAYS){S.bin+=3;harv+=3;p.st='tilled';p.g=0;}});
  auto=autoWater();
  genForage();
  let evMsg='';
  if(S.event&&!S.event.done&&S.event.day===S.day-1){const ev=EVENTS.find(e=>e.id===S.event.id);evMsg=`<p class="small">昨天${PEOPLE[ev.who].name}的傷，後來自己去看了醫生。</p>`;}
  S.event=null;
  if(S.step>=7&&Math.random()<.6){const pool=EVENTS.filter(e=>!e.after||S.cards[e.after]);const ev=pool[Math.floor(Math.random()*pool.length)];S.event={id:ev.id,day:S.day};evMsg+=`<p class="warn">聽說${PEOPLE[ev.who].name}好像出了點小意外……</p>`;}
  if(S.quake&&S.castleDone){S.quake=false;evMsg+='<p class="small">落石之城修復完成了。</p>';}
  const exp=S.kit.filter(k=>base(k)==='ration'&&expiry(k)===S.day-1).length;
  return `${grown?`<p>有 ${grown} 塊田的小麥長大了。</p>`:''}${dry?`<p class="warn">有 ${dry} 塊田昨天沒澆水，所以沒有長大。</p>`:''}${exp?`<p class="bad">背包裡有 ${exp} 包乾糧過期了，已經不能吃。</p>`:''}${auto?`<p>自動灑水器幫 ${auto} 塊田澆好水了。</p>`:''}${harv?`<p>自動收割機收了小麥 ×${harv}，放在收納箱裡。</p>`:''}${evMsg}<p class="small">委託板有新的工作，路邊也出現了新的東西可以撿。</p>`;
}
async function pickUp(i){
  const f=S.forage[S.scene][i],P=PICK[f.t];
  if(matFree()<=0){await say({p:'hero',html:'<p class="warn">素材袋已經滿了。</p>'});return;}
  S.mat[P.mat]++;S.forage[S.scene].splice(i,1);buildScene();toast(P.txt);
  if(f.t==='mushroom'&&!S.warned.mush){S.warned.mush=true;await say({p:'hero',html:'<p>這朵菇顏色好漂亮，聞起來也很香……</p><p class="small">放進素材袋了。要怎麼處理呢？</p>'});}
}
async function bench(){
  if(!S.bench){const ok=S.mat.wood>=BENCH_WOOD;
    const i=await say({p:'hero',who:'工作台（建造）',html:`<p>有了工作台，就能用材料製作自動化機器。</p><p>需要：木材 ×${BENCH_WOOD}（有 ${S.mat.wood}）</p>`,buttons:[{label:ok?'建造':'木材不足',primary:true,disabled:!ok},{label:'離開'}]});
    if(i!==0)return;S.mat.wood-=BENCH_WOOD;S.bench=true;toast('工作台完成！');return;}
  for(;;){let pick=null;
    const html=Object.entries(RECIPES).map(([k,r])=>{const have=k==='sprinkler'?S.spr.length:(S.harvester?1:0);const done=have>=r.max;
      const ok=!done&&Object.entries(r.need).every(([m,n])=>S.mat[m]>=n);
      const need=Object.entries(r.need).map(([m,n])=>`${matIcon(m,24)}${MATS[m].name} ${S.mat[m]}/${n}`).join('　');
      return `<div class="row"><img alt="" src="${A[k]}" style="width:64px;height:48px;object-fit:contain"><div class="info"><b>${r.name}（已有 ${have}/${r.max}）</b><span>${r.desc}</span><span>${need}</span></div><button type="button" data-k="${k}" ${ok?'':'disabled'}>${done?'已達上限':'製作'}</button></div>`;}).join('');
    const r=await say({p:'hero',who:'工作台',html:html+'<p class="small">銅管、齒輪可以在雜貨店買；廢鐵片可以在路邊撿到。</p>',buttons:[{label:'離開',primary:true}],
      onRender:(root,fin)=>root.querySelectorAll('button[data-k]').forEach(b=>b.onclick=()=>{pick=b.dataset.k;fin('pick');})});
    if(r!=='pick')break;
    Object.entries(RECIPES[pick].need).forEach(([m,n])=>S.mat[m]-=n);
    if(pick==='sprinkler'){const si=await pickSlot('要把新的灑水器裝在哪裡？');S.spr.push(si);S.sprinklers=S.spr.length;const n=autoWater();refresh();await say({p:'hero',who:'自動灑水器',html:`<p>自動灑水器裝好了，負責<b>${SPRINKLER_AREA[si]}</b>。</p><p>範圍內翻好土或種了小麥的田，會一直保持濕潤${n?`（剛剛已經幫 ${n} 塊田澆好水）`:''}。</p><p class="small">還沒翻土的田不會澆。</p>`});}else S.harvester=true;
    refresh();toast(`${RECIPES[pick].name}完成！`);}
}
async function takeBin(){
  if(!S.bin){await say({p:'hero',html:'<p>收納箱是空的。自動收割機每天早上會把成熟的小麥收進來。</p>'});return;}
  const n=Math.min(S.bin,matFree());if(n<=0){await say({p:'hero',html:'<p class="warn">素材袋已經滿了。</p>'});return;}
  S.bin-=n;S.mat.wheat+=n;toast(`從收納箱拿出小麥 ×${n}${S.bin?`（還剩 ${S.bin}）`:''}`);
}
async function eatMushroom(){
  if(Math.random()<.5){S.mat.mushroom--;S.pendingFaint=null;await faint('mushroom');return;}
  S.mat.mushroom--;S.sta=0;refresh();
  await say({p:'hero',html:'<p>烤得香噴噴的野生菇，看起來很好吃……吃下去了。</p>'});
  await say({icon:'！',who:'',html:'<p class="bad">過了一會兒，肚子開始絞痛，頭暈、想吐……</p><p class="small">體力歸零了。</p>'});
  await say({p:'grandpa',html:'<p>傻孩子！野生菇怎麼能隨便吃！爺爺馬上帶你去給醫生看，剩下的菇也要一起帶去，讓醫生知道你吃了什麼。</p>'});
  await say({p:'grandpa',html:`<p>${CARDS.mushroom.text}</p><p class="good">獲得知識卡：${CARDS.mushroom.title}</p>`});
  S.cards.mushroom=true;
}
async function gift(id){
  if(S.gifted[id]===S.day){await say({p:id,html:'<p>今天已經收過你的禮物了，明天再來聊吧！</p>'});return;}
  const opts=GIFTABLE.filter(k=>S.mat[k]>0);
  if(!opts.length){await say({p:'hero',html:'<p>素材袋裡沒有可以送的東西。野花、小麥、木材、石頭、金礦都可以當禮物。</p>'});return;}
  let pick=null;
  const html=opts.map(k=>`<div class="row">${matIcon(k)}<div class="info"><b>${MATS[k].name}</b><span>有 ${S.mat[k]} 份</span></div><button type="button" data-k="${k}">送這個</button></div>`).join('');
  const r=await say({p:id,who:`送禮給${PEOPLE[id].name}`,html,buttons:[{label:'算了',primary:true}],onRender:(root,fin)=>root.querySelectorAll('button[data-k]').forEach(b=>b.onclick=()=>{pick=b.dataset.k;fin('pick');})});
  if(r!=='pick')return;
  const L=LIKES[id]||{};
  if(pick==='mushroom'){
    await say({p:id,html:`<p>野生菇？這可不能亂吃，也不能亂送人啊！</p><p>${CARDS.mushroom.text}</p><p class="good">獲得知識卡：${CARDS.mushroom.title}</p>`});
    S.cards.mushroom=true;S.mat.mushroom--;return;}
  S.mat[pick]--;S.gifted[id]=S.day;
  if(pick===L.love){addHeart(id,2);await say({p:id,html:`<p>${L.loveTxt}</p><p class="good">好感度大幅提升！</p>`});}
  else if(pick===L.hate){await say({p:id,html:`<p>${L.hateTxt}</p><p class="small">好像不太喜歡……</p>`});}
  else{addHeart(id,1);await say({p:id,html:`<p>${L.normTxt||'謝謝你！'}</p>`});}
}
async function chatMenu(id,text){
  const st=STORIES[id];
  if(st&&S.hearts[id]>=3&&!S.story[id]&&S.step>=7){
    for(const t of st.text)await say({p:id,html:`<p>${t}</p>`});
    const c=CARDS[st.card];S.cards[st.card]=true;S.story[id]=true;
    await say({p:id,html:`<div class="card"><b>${c.title}</b><p>${c.text}</p></div><p class="good">獲得知識卡：${c.title}</p>`});return;}
  const canGift=S.step>=7;
  const i=await say({p:id,html:`<p>${text}</p>`,buttons:canGift?[{label:'送禮',primary:true},{label:'再見'}]:[{label:'再見',primary:true}]});
  if(canGift&&i===0)await gift(id);
}
async function pickSlot(title,exclude){
  const free=SPRINKLER_SLOTS.map((_,i)=>i).filter(i=>!S.spr.includes(i)&&i!==exclude);
  if(free.length<=1)return free[0];
  let pick=null;
  await say({p:'hero',who:'選擇位置',html:`<p>${title}</p>`+free.map(i=>`<div class="row"><div class="info"><b>${SPRINKLER_AREA[i]}</b></div><button type="button" data-s="${i}">裝在這裡</button></div>`).join(''),buttons:[],
    onRender:(root,fin)=>root.querySelectorAll('button[data-s]').forEach(b=>b.onclick=()=>{pick=+b.dataset.s;fin('p');})});
  return pick;}
async function moveSpr(si){
  const free=SPRINKLER_SLOTS.map((_,i)=>i).filter(i=>!S.spr.includes(i));
  if(!free.length){await say({p:'hero',who:'自動灑水器',html:`<p>這台灑水器負責<b>${SPRINKLER_AREA[si]}</b>。</p><p class="small">三個位置都已經裝了灑水器，沒有空位可以移動。</p>`});return;}
  let pick=null;
  const r=await say({p:'hero',who:'移動灑水器',html:`<p>這台灑水器目前負責<b>${SPRINKLER_AREA[si]}</b>。要移到哪裡？</p>`+free.map(i=>`<div class="row"><div class="info"><b>${SPRINKLER_AREA[i]}</b></div><button type="button" data-s="${i}">移到這裡</button></div>`).join(''),buttons:[{label:'不移動',primary:true}],
    onRender:(root,fin)=>root.querySelectorAll('button[data-s]').forEach(b=>b.onclick=()=>{pick=+b.dataset.s;fin('p');})});
  if(r!=='p')return;
  S.spr=S.spr.map(x=>x===si?pick:x);const n=autoWater();refresh();toast(`灑水器移到${SPRINKLER_AREA[pick]}${n?`，澆了 ${n} 塊田`:''}`);
}
async function well(){
  const first=!S.cards.water;
  const i=await say({p:'hero',who:'水井',html:`<p>清涼的井水，看起來很清澈。</p><p class="small">素材袋 ${matUsed()}/${S.matCap}　井水 ${S.mat.rawwater||0} 份</p>`,
    buttons:[{label:'打一桶井水（體力 2）',primary:true,disabled:matFree()<=0},{label:'直接喝一口'},{label:'離開'}]});
  if(i===0){if(!await useSta(2))return;S.mat.rawwater=(S.mat.rawwater||0)+1;toast('打了一桶井水');
    if(first){S.cards.water=true;await say({p:'grandpa',html:`<p>井水要拿回家用爐火煮開再用喔。</p><div class="card"><b>${CARDS.water.title}</b><p>${CARDS.water.text}</p></div><p class="good">獲得知識卡：${CARDS.water.title}</p>`});}}
  else if(i===1){
    if(Math.random()<.5){S.sta=Math.max(0,S.sta-15);refresh();await say({p:'hero',html:'<p class="bad">喝完沒多久，肚子開始咕嚕咕嚕地痛……</p><p class="small">體力 -15</p>'});if(S.sta<=0)S.pendingFaint='work';}
    else await say({p:'hero',html:'<p>咕嚕咕嚕……好像沒什麼事。不過這次沒事，不代表下次也沒事。</p>'});
    S.cards.water=true;await say({p:'grandpa',html:`<p>傻孩子，井水怎麼能直接喝！</p><div class="card"><b>${CARDS.water.title}</b><p>${CARDS.water.text}</p></div>`});}
}
async function boil(){
  const raw=S.mat.rawwater||0,space=S.kitCap-S.kit.length;
  if(!raw){await say({p:'hero',who:'爐火',html:'<p>暖暖的爐火。可以把打回來的井水煮沸，變成乾淨的開水。</p><p class="small">水井在村子廣場和農田。</p>'});return;}
  const n=Math.min(raw,space);
  const i=await say({p:'hero',who:'用爐火煮水',html:`<p>把井水煮沸、放涼，就是可以喝、也可以沖洗傷口的開水，會放進急救背包。</p><p>井水 ${raw} 份　急救背包空位 ${space} 格</p>`,
    buttons:[{label:n?`煮 ${n} 份`:'急救背包已滿',primary:true,disabled:!n},{label:'離開'}]});
  if(i!==0)return;S.mat.rawwater-=n;for(let k=0;k<n;k++)S.kit.push('water');S.cards.water=true;toast(`煮好開水 ×${n}`);
}
async function tablet(){
  const c=CARDS.fracture,isNew=!S.cards.fracture;S.cards.fracture=true;S.f.tablet=true;
  await say({icon:'碑',who:'救護騎士團的石碑',html:`<p>石碑上刻著褪色的文字，還有一幅手臂被三角巾吊起來的圖……</p><div class="card"><b>${c.title}</b><p>${c.text}</p></div>${isNew?`<p class="good">獲得知識卡：${c.title}</p>`:''}`});
}
async function hunter(){
  if(!S.f.hunter){
    const needs={ice:1,elastic:1};
    await say({p:'hunt',html:'<p>啊，有人來了……我追兔子時踩空，腳踝扭到了，腫得好厲害。</p>'});
    const miss=needCheck(needs);
    if(miss.length){await say({p:'hunt',html:`<p>需要：${needTxt(needs)}。</p><p class="warn">你的背包還缺：${miss.map(([k,n])=>ITEMS[k].name+' ×'+(n-kitCount(k))).join('、')}</p><p class="small">冰敷袋在雜貨店買得到。</p>`});return;}
    await quiz('hunt','扭傷初期，哪一種處理正確？',['立刻熱敷，促進血液循環','用力按摩，把瘀血揉開','冰敷，用彈性繃帶適度壓迫，並把腳抬高'],2,
      '急性扭傷初期應冰敷、壓迫、抬高，減輕腫脹。熱敷和按摩可能讓腫脹更嚴重。冰敷袋外面要包一層布。');
    takeKit(needs);S.f.hunter=true;S.coins+=30;S.earned+=30;addHeart('hunt',2);S.cards.sprain=true;
    await say({p:'hunt',html:'<p>好多了！我叫阿鹿，是這片草原的獵人。這 30 金幣你收下。</p><p>往北走就是落石之城，最近那裡常常地鳴，你要小心。</p><p class="good">獲得知識卡：扭傷初期怎麼處理</p>'});return;}
  return chatMenu('hunt','草原上的風真舒服。要去落石之城的話，往北走就到了。');
}
async function guardTalk(){
  if(S.scene==='gate'&&!S.f.guard){
    await lines('guard',['站住！……原來是團長的孫子。','最近地底常常轟隆作響，城牆都出現裂縫了。城裡的人卻沒幾個懂急救，真讓人擔心。',`如果你要進城，最好先把急救背包準備好，也帶上 ${RATION_NEED} 包乾糧和 ${WATER_NEED} 瓶乾淨的水。萬一被困住，救援可能要好幾天才能進來。`]);
    S.f.guard=true;return;}
  return chatMenu('guard','城門隨時為你開著。進城前，再確認一次背包吧。');
}
function quakeFx(){if(RM)return;$('game').classList.add('quake');setTimeout(()=>$('game').classList.remove('quake'),900);}
async function gateDoor(){
  if(!S.f.guard){await say({p:'guard',html:'<p>等一下，先過來跟我說話。</p>'});return;}
  const valid=S.kit.filter(k=>base(k)==='ration'&&!expired(k)).length;
  const first=!S.castleDone;
  const i=await say({p:'hero',who:first?'落石之城':'再次挑戰落石之城',html:`<p>${first?'城堡深處傳來低沉的轟隆聲。進去之後，災難可能隨時發生。':'城堡已經修好了。要再進行一次地震救援挑戰嗎？'}</p>
    <p>急救背包：${S.kit.length}/${S.kitCap}　有效乾糧：${valid} 包　開水：${kitCount('water')} 瓶</p><p class="small">背包裡的東西在救援中用掉就沒了，確定準備好了嗎？</p>`,buttons:[{label:'進入城堡',primary:true},{label:'再準備一下'}]});
  if(i!==0)return;
  quakeFx();await say({icon:'！',who:'',html:'<p class="bad">轟隆隆隆——！</p><p>大地劇烈搖晃，城牆崩落，塵土漫天！</p>'});
  await say({p:'hero',html:'<p>（先趴下、掩護、穩住……搖晃停了。）</p><p>確認周圍環境安全後，發現有三個人受傷倒在廣場上！</p>'});
  S.quake=true;S.rescue={};S.rescueMiss={};S.fakesAtStart=[...new Set(S.kit.filter(k=>ITEMS[base(k)].fake).map(base))];S.expiredAtStart=S.kit.filter(expired).length;
  await go('ruin',[838,880]);quakeFx();
}
async function victim(id){
  const v=VICTIMS[id];
  if(S.rescue[id]){await say({p:id,html:`<p>${S.rescue[id]==='ok'?v.ok:'……謝謝你，你已經盡力了。'}</p>`});return;}
  const miss=needCheck(v.needs);
  if(miss.length){
    await say({p:id,html:`<p>${v.situ}</p><p>處理這個傷需要：${needTxt(v.needs)}</p><p class="bad">背包裡缺少：${miss.map(([k,n])=>ITEMS[k].name+' ×'+(n-kitCount(k))).join('、')}</p><p>你沒辦法好好處理這個傷……</p>`});
    S.rescue[id]='missing';S.rescueMiss[id]=miss.map(([k,n])=>ITEMS[k].name+' ×'+(n-kitCount(k)));}
  else{
    await say({p:id,html:`<p>${v.situ}</p><p class="small">使用：${needTxt(v.needs)}</p>`,buttons:[{label:'拿出用品處理',primary:true}]});
    takeKit(v.needs);
    const i=await say({p:id,html:`<p class="q">${v.q}</p>`,buttons:v.opts.map(o=>({label:o}))});
    const ok=i===v.ans;
    await say({p:id,html:`<p class="${ok?'good':'bad'}">${ok?'處置正確！':'這個做法不對。'}</p><p>${v.explain}</p>`});
    S.rescue[id]=ok?'ok':'wrong';if(ok)addHeart(id,2);}
  refresh();
  if(Object.keys(VICTIMS).every(k=>S.rescue[k]))await rationPhase();
}
async function rationPhase(){
  await lines('guard',['大家的傷都處理過了……但是城門被落石完全堵住了。','外面的救援隊說，要三天後才能挖通。這三天，大家需要食物撐下去。']);
  const valid=S.kit.filter(k=>base(k)==='ration'&&!expired(k)).length;
  let ok=false;
  if(valid>=RATION_NEED){for(let n=0;n<RATION_NEED;n++)S.kit.splice(S.kit.findIndex(k=>base(k)==='ration'&&!expired(k)),1);ok=true;
    await say({p:'hero',html:`<p>你從背包拿出 ${RATION_NEED} 包乾糧分給大家。</p><p class="good">三天份的食物，足夠撐到救援隊進來！</p>`});}
  else await say({p:'hero',html:`<p>你翻遍背包，只找到 ${valid} 包還能吃的乾糧${S.expiredAtStart?`（另外有 ${S.expiredAtStart} 包已經過期）`:''}。</p><p class="bad">食物不夠三天份，大家只能餓著肚子等待……</p>`});
  S.rescue.rations=ok?'ok':'missing';
  await say({p:'guard',html:'<p>還有……城裡的水井被震垮了，井水混濁得不能用。大家這三天也需要喝水。</p>'});
  const w=kitCount('water');
  if(w>=WATER_NEED){for(let n=0;n<WATER_NEED;n++)S.kit.splice(S.kit.findIndex(k=>base(k)==='water'),1);S.rescue.water='ok';
    await say({p:'hero',html:`<p>你拿出 ${WATER_NEED} 瓶煮過的開水。</p><p class="good">三天份的飲用水準備充足！</p>`});}
  else{S.rescue.water='missing';await say({p:'hero',html:`<p>你的背包裡只有 ${w} 瓶開水。</p><p class="bad">水不夠三天份，大家只能省著喝……</p>`});}
  const stars=['guard','cook','soldier','rations','water'].filter(k=>S.rescue[k]==='ok').length;
  S.castleDone=true;S.castleBest=Math.max(S.castleBest||0,stars);refresh();
  await castleReport(stars);
}
async function castleReport(stars){
  const name={guard:'城堡守衛（頭皮出血）',cook:'廚娘（疑似前臂骨折）',soldier:'見習小兵（腳踝扭傷）'};
  const col=r=>r==='ok'?'var(--ok)':r==='wrong'?'var(--warn)':'var(--bad)';
  const rows=Object.keys(name).map(k=>{const r=S.rescue[k];return `<div class="row"><div class="info"><b>${name[k]}</b><span style="color:${col(r)}">${r==='ok'?'救援成功':r==='wrong'?'有用品，但處置方式有誤':'缺少 '+(S.rescueMiss[k]||[]).join('、')}</span></div></div>`;}).join('')+
    `<div class="row"><div class="info"><b>三天份的乾糧</b><span style="color:${col(S.rescue.rations)}">${S.rescue.rations==='ok'?'準備充足':'不足'}</span></div></div><div class="row"><div class="info"><b>三天份的飲用水</b><span style="color:${col(S.rescue.water)}">${S.rescue.water==='ok'?'準備充足':'不足'}</span></div></div>`;
  const fk=S.fakesAtStart||[];
  const fakeHtml=fk.length?`<h4>你帶進城的偏方</h4>${fk.map(k=>`<div class="card"><b>${ITEMS[k].name}</b><p>${ITEMS[k].truth}</p></div>`).join('')}`:'<p class="good">你沒有把任何偏方帶進城。</p>';
  await say({p:'hero',who:'救援報告',html:`<div style="font-size:40px;color:var(--gold);letter-spacing:.1em">${'★'.repeat(stars)}${'☆'.repeat(5-stars)}</div>${rows}${fakeHtml}${S.expiredAtStart?`<p class="warn">背包裡有 ${S.expiredAtStart} 包過期的乾糧，要記得定期檢查。</p>`:''}<p class="small">最佳紀錄：${S.castleBest} 顆星。睡一覺之後城堡會修好，可以再挑戰一次。</p>`,buttons:[{label:'完成',primary:true}]});
}
async function doEvent(ev){
  await say({p:ev.who,html:`<p>${ev.intro}</p>`});
  const miss=needCheck(ev.needs);
  if(miss.length){await say({p:ev.who,html:`<p>需要：${needTxt(ev.needs)}</p><p class="warn">你的背包還缺：${miss.map(([k,n])=>ITEMS[k].name+' ×'+(n-kitCount(k))).join('、')}</p><p class="small">今天之內帶用品回來還來得及。急救背包要隨時備著喔。</p>`});return;}
  for(const q of ev.qs)await quiz(ev.who,q.q,q.opts,q.ans,q.explain);
  takeKit(ev.needs);S.event.done=true;S.coins+=20;S.earned+=20;addHeart(ev.who,1);
  const isNew=!S.cards[ev.id];S.cards[ev.id]=true;
  await say({p:ev.who,html:`<p>${ev.thanks}</p><p class="good">獲得 20 金幣${isNew?`、知識卡：${CARDS[ev.id].title}`:''}</p>`});
}
async function forestChest(){
  if(S.chests.f1){await say({p:'hero',html:'<p>寶箱已經空了。</p>'});return;}
  S.chests.f1=true;S.coins+=30;S.earned+=30;
  await say({icon:'◆',who:'打開寶箱',html:'<p>寶箱裡有一個舊錢袋。</p><p class="good">獲得 30 金幣</p>'});
}
async function oldChest(){
  if(S.chests.home){await say({p:'hero',html:'<p>爺爺的舊箱子，裡面放著褪色的騎士團制服。</p>'});return;}
  S.chests.home=true;S.coins+=20;S.earned+=20;
  await say({p:'grandpa',html:'<p>那是爺爺的舊箱子。裡面的零錢你拿去用吧。</p><p class="good">獲得 20 金幣</p>'});
}
async function shelf(){
  const books=[['legend',true],['bleed',S.step>=5],['scrape',S.step>=5],['food',S.step>=10]];
  const html=books.map(([k,ok])=>ok?`<div class="card"><b>${CARDS[k].title}</b><p>${CARDS[k].text}</p></div>`:'').join('');
  books.forEach(([k,ok])=>{if(ok)S.cards[k]=true;});
  await say({icon:'書',who:'爺爺的書架',html:html+(S.step<10?'<p class="small">其他書的字跡太模糊了，也許之後爺爺會幫你翻出來。</p>':''),buttons:[{label:'闔上書',primary:true}]});
}

/* 委託板 */
function nextReq(){const pool=REQUESTS.map((r,i)=>i).filter(i=>!REQUESTS[i].p2||S.step>=7);
  let r;do{r=pool[S.reqNext%pool.length];S.reqNext++;}while(S.req.includes(r)&&pool.length>3);return r;}
async function board(){
  for(;;){
    let pick=-1;
    const rows=S.req.map((ri,i)=>{const r=REQUESTS[ri];const ok=S.mat[r.item]>=r.n;
      return `<div class="row"><div class="info"><b>${r.who}：${r.text}</b><span>交付${MATS[r.item].name} ×${r.n}　報酬 ${r.pay} 金幣＋好感度</span></div><button type="button" data-i="${i}" ${ok?'':'disabled'}>${ok?'交付':'數量不足'}</button></div>`;}).join('');
    const r=await say({icon:'板',who:'委託板',html:`${rows}<p class="small">素材袋：${matList()}</p>`,buttons:[{label:'離開',primary:true}],
      onRender:(root,fin)=>root.querySelectorAll('button[data-i]').forEach(b=>b.onclick=()=>{pick=+b.dataset.i;fin('pick');})});
    if(r!=='pick')break;
    const q=REQUESTS[S.req[pick]];S.mat[q.item]-=q.n;S.coins+=q.pay;S.earned+=q.pay;addHeart(q.from,1);
    S.req[pick]=nextReq();toast(`完成委託！獲得 ${q.pay} 金幣`);refresh();
  }
}

/* 商店 */
async function shopMenu(){
  let msg='',keepScroll=0;
  if(S.step===2&&!S.warned.firstSell){S.warned.firstSell=true;
    await say({p:'shopkeeper',html:'<p>哎呀，是團長家的孫子！要賣木材嗎？一份 3 金幣。</p><p>賺了錢記得來擴充包包喔，我這裡的背包可是全村最耐用的。對了，村口的委託板也常有人需要木材，報酬更好。</p>'});
    if(!S.mat.wood)return;}
  for(;;){
    let pick=null;
    const matNext=MAT_UP[S.matLv],kitNext=KIT_UP[S.kitLv];
    const full0=S.kit.length>=S.kitCap;
    const debt=S.coins<0?`<p class="bad">你還欠醫療費 ${-S.coins} 金幣，還清之前不能買東西，但可以賣素材。</p>`:'';
    let html=(msg?`<p class="good" style="position:sticky;top:-18px;z-index:2;background:#1d3a2a;border:1.5px solid var(--ok);border-radius:10px;padding:8px 12px;margin-top:0">${msg}</p>`:'')+`<p class="small">金幣 <b style="color:var(--gold)">${S.coins}</b>　急救背包 <b style="color:${full0?'var(--bad)':'var(--gold)'}">${S.kit.length}/${S.kitCap}</b>${full0?'（已滿，可以擴充背包，或打開背包丟掉用不到的東西）':''}　素材袋 ${matUsed()}/${S.matCap}</p>`+debt+'<h4>賣出素材</h4>'+['wood','stone','gold','wheat','flower','scrap'].filter(k=>k==='wood'||S.step>=7).map(k=>`<div class="row"><div class="info"><b>${MATS[k].name}</b><span>一份 ${MATS[k].sell} 金幣，素材袋裡有 ${S.mat[k]} 份</span></div><button type="button" data-a="sell:${k}" ${S.mat[k]?'':'disabled'}>全部賣出</button></div>`).join('');
    if(S.step>=7)html+=`<h4>種子</h4><div class="row"><div class="info"><b>小麥種子</b><span>${MATS.seed.buy} 金幣一包，放進素材袋；一包種一塊田</span></div><button type="button" data-a="seed" ${S.coins>=MATS.seed.buy&&matFree()>0?'':'disabled'}>購買</button></div>`;
    {const good=S.kit.filter(k=>base(k)==='ration'&&!expired(k)).length,bad=S.kit.filter(expired).length;
     if(S.step>=7&&(good||bad))html+=`<div class="row">${badge('ration')}<div class="info"><b>乾糧</b><span>一包 ${RATION_SELL} 金幣，急救背包裡有 ${good} 包${bad?`（另有 ${bad} 包過期，不能賣）`:''}。會先賣最快過期的</span></div><button type="button" data-a="ration" ${good?'':'disabled'}>賣 1 包</button></div>`;}
    if(S.step>=7&&S.mat.mushroom)html+=`<div class="row">${matIcon('mushroom')}<div class="info"><b>野生菇</b><span>素材袋裡有 ${S.mat.mushroom} 朵</span></div><button type="button" data-a="mush">賣賣看</button></div>`;
    if(S.step>=10)html+=`<h4>機器零件</h4>`+['pipe','gear'].map(k=>`<div class="row">${matIcon(k)}<div class="info"><b>${MATS[k].name}</b><span>${MATS[k].buy} 金幣，放進素材袋</span></div><button type="button" data-a="part:${k}" ${S.coins>=MATS[k].buy&&matFree()>0?'':'disabled'}>購買</button></div>`).join('');
    html+=`<h4>擴充包包</h4>`;
    html+=`<div class="row"><div class="info"><b>素材袋 ${S.matCap} → ${matNext?matNext.cap:'已達上限'} 格</b><span>${matNext?matNext.cost+' 金幣':''}</span></div>${matNext?`<button type="button" data-a="mat" ${S.coins>=matNext.cost?'':'disabled'}>擴充</button>`:''}</div>`;
    html+=`<div class="row"><div class="info"><b>急救背包 ${S.kitCap} → ${kitNext?kitNext.cap:'已達上限'} 格</b><span>${kitNext?kitNext.cost+' 金幣。格數變多，但裝太重會走得比較慢':'背包已經是最大尺寸'}</span></div>${kitNext?`<button type="button" data-a="kit" ${S.coins>=kitNext.cost?'':'disabled'}>擴充</button>`:''}</div>`;
    if(S.step>=5){html+=`<h4>急救用品</h4>`+SHOP_MED.map(k=>{const it=ITEMS[k];const full=S.kit.length>=S.kitCap;
      return `<div class="row">${badge(k)}<div class="info"><b>${it.name}　<span style="color:var(--gold)">背包裡有 ${kitCount(k)} 個</span></b><span>${it.price} 金幣　重量 ${it.w}　${it.desc}</span></div><button type="button" data-a="buy:${k}" ${S.coins>=it.price&&!full?'':'disabled'}>${full?'背包已滿':S.coins<it.price?'金幣不足':'買 1 個'}</button></div>`;}).join('');}
    else html+=`<p class="small">急救用品目前缺貨中。</p>`;
    const r=await say({p:'shopkeeper',html,buttons:[{label:'離開',primary:true}],onRender:(root,fin)=>{const box=root.closest('.box');box.scrollTop=keepScroll;root.querySelectorAll('button[data-a]').forEach(b=>b.onclick=()=>{keepScroll=box.scrollTop;pick=b.dataset.a;fin('pick');});}});
    if(r!=='pick')break;
    msg='';
    if(pick.startsWith('sell:')){const k=pick.slice(5),g=S.mat[k]*MATS[k].sell;S.coins+=g;S.earned+=g;msg=`✓ 賣出${MATS[k].name} ×${S.mat[k]}，獲得 ${g} 金幣`;S.mat[k]=0;if(S.step===2&&k==='wood')S.step=3;}
    else if(pick==='ration'){const list=S.kit.map((k,i)=>[k,i]).filter(([k])=>base(k)==='ration'&&!expired(k)).sort((a,b)=>expiry(a[0])-expiry(b[0]));const [k,i]=list[0];S.kit.splice(i,1);S.coins+=RATION_SELL;S.earned+=RATION_SELL;msg=`✓ 賣出乾糧 ×1（保存到第 ${expiry(k)} 天），獲得 ${RATION_SELL} 金幣`;}
    else if(pick==='mush'){await say({p:'shopkeeper',html:'<p>野生菇？不行不行，我不收來路不明的野生菇。萬一有毒，吃了會出人命的！</p>'});}
    else if(pick.startsWith('part:')){const k=pick.slice(5);S.coins-=MATS[k].buy;S.mat[k]++;msg=`✓ 已購買：${MATS[k].name} ×1`;}
    else if(pick==='seed'){S.coins-=MATS.seed.buy;S.mat.seed++;msg=`✓ 已購買：小麥種子 ×1（共 ${S.mat.seed} 包）`;}
    else if(pick==='mat'){S.coins-=matNext.cost;S.matCap=matNext.cap;S.matLv++;addHeart('shopkeeper',1);msg=`✓ 素材袋擴充為 ${S.matCap} 格`;}
    else if(pick==='kit'){S.coins-=kitNext.cost;S.kitCap=kitNext.cap;S.kitLv++;addHeart('shopkeeper',1);msg=`✓ 急救背包擴充為 ${S.kitCap} 格`;}
    else if(pick.startsWith('buy:')){const k=pick.slice(4);S.coins-=ITEMS[k].price;S.kit.push(k);msg=`✓ 已購買：${ITEMS[k].name} ×1（急救背包 ${S.kit.length}/${S.kitCap}）`;}
    refresh();
  }
}
async function merchantMenu(){
  if(S.step<5){await say({p:'merchant',html:'<p>呵呵……時候還沒到。我們很快就會再見面的，小勇者。</p>'});return;}
  let mmsg='';
  for(;;){let pick=null;
    const html=(mmsg?`<p class="warn">${mmsg}</p>`:'')+`<p class="small">急救背包 ${S.kit.length}/${S.kitCap}</p>`+(S.step>=7?'<p>對了，森林裡長的野生菇，烤一烤可香了，我自己天天吃呢，呵呵。</p>':'')+'<p>便宜又有效的祖傳祕方，別人都不知道喔。</p>'+MERCHANT_GOODS.map(k=>{const it=ITEMS[k];const full=S.kit.length>=S.kitCap;
      return `<div class="row">${badge(k)}<div class="info"><b>${it.name}</b><span>${it.price} 金幣　重量 ${it.w}　${it.desc}</span></div><button type="button" data-a="${k}" ${S.coins>=it.price&&!full?'':'disabled'}>${full?'背包已滿':'購買'}</button></div>`;}).join('');
    const r=await say({p:'merchant',html,buttons:[{label:'離開',primary:true}],onRender:(root,fin)=>root.querySelectorAll('button[data-a]').forEach(b=>b.onclick=()=>{pick=b.dataset.a;fin('pick');})});
    if(r!=='pick')break;S.coins-=ITEMS[pick].price;S.kit.push(pick);mmsg=`已買下：${ITEMS[pick].name} ×1（急救背包 ${S.kit.length}/${S.kitCap}）`;refresh();}
}

/* 問答 */
async function quiz(p,q,opts,ans,explain){
  for(;;){const i=await say({p,html:`<p class="q">${q}</p>`,buttons:opts.map(o=>({label:o}))});
    const ok=i===ans;await say({p,html:`<p class="${ok?'good':'bad'}">${ok?'處置正確！':'這個做法不對。'}</p><p>${explain}</p>`,buttons:[{label:ok?'繼續':'再選一次',primary:true}]});
    if(ok)return;}}
const ALT={saline:['water']};
const haveN=k=>kitCount(k)+(ALT[k]||[]).reduce((a,b)=>a+kitCount(b),0);
function needCheck(needs){return Object.entries(needs).filter(([k,n])=>haveN(k)<n).map(([k,n])=>[k,n-haveN(k)+kitCount(k)]);}
function takeKit(needs){for(const [k,n] of Object.entries(needs))for(let i=0;i<n;i++){let j=S.kit.findIndex(x=>base(x)===k&&!expired(x));if(j<0)for(const a of (ALT[k]||[])){j=S.kit.findIndex(x=>base(x)===a);if(j>=0)break;}if(j>=0)S.kit.splice(j,1);}}
const needTxt=needs=>Object.entries(needs).map(([k,n])=>`${ITEMS[k].name} ×${n}${ALT[k]?'（或開水）':''}`).join('、');

async function talk(id){
  if(S.scene==='ruin'&&VICTIMS[id])return victim(id);
  if(S.event&&S.event.day===S.day&&!S.event.done&&S.step>=7){const ev=EVENTS.find(e=>e.id===S.event.id);if(ev.who===id)return doEvent(ev);}
  if(id==='hunt')return hunter();
  if(id==='guard')return guardTalk();
  if(id==='shopkeeper'){if(S.step>=7){const i=await say({p:'shopkeeper',html:'<p>歡迎光臨！今天想買點什麼？</p>',buttons:[{label:'購物',primary:true},{label:'送禮'},{label:'離開'}]});if(i===0)return shopMenu();if(i===1)return gift('shopkeeper');return;}return shopMenu();}
  if(id==='merchant')return merchantMenu();
  if(id==='grandpa'){
    if(S.step===0)return introGrandpa();
    const fakes=[...new Set(S.kit.filter(k=>ITEMS[base(k)].fake))];
    if(fakes.length){const k=fakes[0];
      const i=await say({p:'grandpa',html:`<p>等等，你背包裡怎麼有「${ITEMS[k].name}」？</p><p>${ITEMS[k].truth}</p>`,buttons:[{label:'把它丟掉',primary:true},{label:'先留著'}]});
      if(i===0){S.kit=S.kit.filter(x=>x!==k);addHeart('grandpa',1);toast(`丟掉了 ${ITEMS[k].name}`);}return;}
    const old=S.kit.filter(expired);
    if(old.length){const i=await say({p:'grandpa',html:`<p>你背包裡有 ${old.length} 包乾糧已經過期了。過期的食物不能吃，防災包裡的食物要定期檢查、換新。</p>`,buttons:[{label:'把過期乾糧丟掉',primary:true},{label:'先留著'}]});
      if(i===0){S.kit=S.kit.filter(k=>!expired(k));addHeart('grandpa',1);}return;}
    if(S.castleDone&&!S.f.final){
      const st=S.castleBest||0;
      await lines('grandpa',[`你回來了！聽說你在落石之城救了人，拿到了 ${st} 顆星。`,
        '急救不是魔法。是你平常就把背包準備好、把知識記在心裡，災難來的時候才救得了人。',
        '療癒之箱和守護之囊都亮起來了。孩子，你已經是一名真正的救護見習騎士了。']);
      await say({icon:'★',who:'序章完成',html:'<p>恭喜完成序章「綠葉谷」！</p><p>你可以繼續在綠葉谷生活、接委託、幫助村民，也可以再挑戰一次落石之城，爭取更多星星。</p><p class="small">世界地圖上的其他區域，將隨課程單元陸續開放。</p>'});
      S.f.final=true;return;}
    if(S.step>=10&&!S.f.p3){
      await lines('grandpa',['最近地底常常傳來轟隆聲……落石之城那邊的地鳴越來越頻繁了。',
        '阿木幫忙把往河谷的落石清開了。從村子往東走，經過河谷和東方草原，就能到落石之城。',
        '河谷有一塊騎士團留下的石碑，記得去看看。還有，災難不會等你準備好，背包要隨時備妥。']);
      await say({icon:'★',who:'新的區域',html:`<p>綠葉村往東的道路開放了：河谷、東方草原、落石之城。</p><p class="small">進城前，準備好急救背包、${RATION_NEED} 包還在保存期限內的乾糧，以及 ${WATER_NEED} 瓶開水。</p>`});
      S.f.p3=true;return;}
    if(S.step===6){
      await lines('grandpa',['阿木和小芽都跟我說了，你做得很好。療癒之箱開始發出微光了。',
        '不過，災難來的時候，光有急救用品還不夠。人要活下去，還需要食物和水。',
        '穿過南方森林，再往南走，有爺爺年輕時的農田。去種些小麥，再用木材做一台乾糧製造機。那附近還有一座舊礦坑，挖到金礦可以換不少錢。']);
      await say({icon:'★',who:'新的區域',html:'<p>南方森林往南的小路開放了：爺爺的農田、礦坑。</p><p class="small">做事會消耗體力，回家睡覺就能恢復並進入下一天。</p>'});
      S.step=7;return;}
    if(S.step===9&&kitCount('ration')>0){
      await lines('grandpa',['這就是你親手做的乾糧啊。','記住，防災包裡的食物要選免烹煮、耐保存的，還要定期檢查保存期限。我把這本書放在書架上了，有空讀一讀。']);
      S.step=10;S.cards.food=true;
      await say({icon:'★',who:'第二階段完成',html:'<p>你學會了種田、挖礦，還做出了第一包乾糧。</p><p>背包裡的「療癒之箱」和「守護之囊」都開始發出微光……</p><p class="small">下一階段將開放：河谷、東方草原、落石之城。</p>'});return;}
    const tip=S.step>=10?(S.bench?'自動化機器能幫你省下很多時間。有空就多陪村裡的人聊聊天吧。':'農田那邊可以蓋一座工作台，用材料做些省力的機器。'):S.step===7?'先去工具棚拿農具，翻土、澆水、播種。每天都要澆水，小麥才會長大。':S.step===8?`乾糧製造機需要木材 ${MACHINE_WOOD} 份和 ${MACHINE_COIN} 金幣，多砍點樹、挖點礦吧。`:S.step===9?'小麥收成後放進乾糧製造機，做好了拿給爺爺看看。':S.step===5?'阿木和小芽都需要幫忙，記得先確認背包裡的用品夠不夠。':'多砍點木材、接委託賺錢，把包包擴充起來吧。累了就回來睡一覺。';
    return chatMenu('grandpa',tip);
  }
  if(id==='wood'){
    if(S.step===1){await say({p:'wood',html:'<p>喔！團長的孫子啊，要借斧頭？拿去吧，這把是我年輕時用的。</p><p>砍樹的時候靠近樹，連按三下就能砍倒。木材可以拿去雜貨店賣錢。</p><p class="good">獲得：斧頭</p>'});S.axe=true;S.step=2;addHeart('wood',1);return;}
    if(S.step===5&&!S.flagWoodDone){
      const needs={glove:1,gauze:1,elastic:1};const miss=needCheck(needs);
      if(miss.length){await say({p:'wood',html:`<p>手臂還隱隱作痛……需要：${needTxt(needs)}。</p><p class="warn">你的背包還缺：${miss.map(([k,n])=>ITEMS[k].name+' ×'+(n-kitCount(k))).join('、')}</p>`});return;}
      await say({p:'wood',html:'<p>你把用品都帶來了！麻煩你幫我好好包紮。</p>'});
      await quiz('wood','打開手帕，傷口又開始滲血。你已經戴上手套，接下來應該？',
        ['用無菌紗布覆蓋傷口，直接加壓止血，再用彈性繃帶固定','先把傷口旁邊的血跡擦乾淨，看清楚傷口多深','塗一點清涼薄荷牙膏，減輕疼痛'],0,
        '出血時以直接加壓止血為優先，止住後再用繃帶固定敷料。偏方不能處理傷口。');
      takeKit(needs);S.flagWoodDone=true;S.coins+=40;S.earned+=40;addHeart('wood',2);
      await say({p:'wood',html:'<p>包得真好，一點都不鬆！這 40 金幣你收下。以後砍樹我會小心的。</p>'});
      if(S.flagKidDone){S.step=6;await prologueDone();}
      return;}
    return chatMenu('wood',S.step>=7?'聽說你在種田？森林南邊那條路我幫你清乾淨了。':'多砍點樹，素材袋滿了就拿去賣！');
  }
  if(id==='kid'){
    if(S.step===5&&!S.flagKidDone){
      const needs={saline:1,bandaid:1};const miss=needCheck(needs);
      await say({p:'kid',html:'<p>嗚嗚……我剛剛跑太快跌倒了，膝蓋磨破皮，上面都是沙子……</p>'});
      if(miss.length){await say({p:'kid',html:`<p class="warn">你的背包還缺：${miss.map(([k,n])=>ITEMS[k].name+' ×'+(n-kitCount(k))).join('、')}</p><p class="small">需要：${needTxt(needs)}</p>`});return;}
      await quiz('kid','傷口上有沙土，該怎麼處理？',['用生理食鹽水沖乾淨，再貼上 OK 繃','塗一點清涼薄荷牙膏，涼涼的比較不痛','吹一吹，直接貼上 OK 繃'],0,
        '擦傷要先把砂土沖洗乾淨，可用生理食鹽水或乾淨的清水。不要塗牙膏等偏方，也不要用嘴吹傷口。');
      takeKit(needs);S.flagKidDone=true;S.coins+=20;S.earned+=20;addHeart('kid',2);
      await say({p:'kid',html:'<p>不痛了！謝謝大哥哥！這是我存的零用錢，給你！</p><p class="good">獲得 20 金幣</p>'});
      if(S.flagWoodDone){S.step=6;await prologueDone();}
      return;}
    return chatMenu('kid',S.step>=6?'大哥哥好厲害，我長大也要當救護騎士！':'大哥哥要去冒險嗎？好好喔！');
  }
}
async function prologueDone(){
  await say({icon:'★',who:'序章完成',html:'<p>你幫助了阿木和小芽，綠葉村的人開始信任你了。</p><p>回家告訴爺爺吧。</p>'});
}

/* 背包 */
async function bag(){if(busy)return;busy=true;stopInput();
  try{for(;;){let pick=-1;const l=load_();const pct=Math.min(100,l/LOAD_HEAVY*100);
    const slots=S.kit.length?S.kit.map((k,i)=>{const b=base(k);const note=b==='ration'?(expired(k)?'<span style="color:var(--bad)">已過期</span>':`保存到第 ${expiry(k)} 天`):'';
      return `<div class="row">${badge(k)}<div class="info"><b>${ITEMS[b].name}</b><span>重量 ${ITEMS[b].w}　${note}</span></div>${b==='water'?`<button type="button" data-d="${i}">喝</button> `:''}<button type="button" data-i="${i}">丟掉</button></div>`;}).join(''):'<p class="small">急救背包是空的。</p>';
    const tools=[S.axe&&'斧頭',S.tools.hoe&&'鋤頭',S.tools.can&&'澆水壺',S.tools.pick&&'十字鎬'].filter(Boolean).join('、')||'沒有';
    const r=await say({p:'hero',who:'我的包包',html:`<h4>急救背包 ${S.kit.length}/${S.kitCap}</h4><div class="meter"><i class="${l>LOAD_HEAVY?'over':l>LOAD_OK?'heavy':''}" style="width:${pct}%"></i></div>
      <p class="small">負重 ${l}　${l>LOAD_HEAVY?'太重了，走得很慢':l>LOAD_OK?'有點重，走路變慢':'輕鬆好走'}</p>${slots}
      <h4>素材袋 ${matUsed()}/${S.matCap}</h4>${Object.entries(S.mat).filter(([k,n])=>n>0).map(([k,n])=>`<div class="row">${matIcon(k)}<div class="info"><b>${MATS[k].name} ×${n}</b></div>${k==='mushroom'?'<button type="button" data-m="eat">吃掉</button> <button type="button" data-m="toss">丟掉</button>':''}</div>`).join('')||'<p class="small">空的</p>'}<h4>工具</h4><p>${tools}</p>`,buttons:[{label:'關閉',primary:true}],
      onRender:(root,fin)=>{root.querySelectorAll('button[data-i]').forEach(b=>b.onclick=()=>{pick=+b.dataset.i;fin('pick');});root.querySelectorAll('button[data-m]').forEach(b=>b.onclick=()=>fin(b.dataset.m));root.querySelectorAll('button[data-d]').forEach(b=>b.onclick=()=>{pick=+b.dataset.d;fin('drink');});}});
    if(r==='drink'){if(S.drinkDay!==S.day){S.drinkDay=S.day;S.drinks=0;}S.kit.splice(pick,1);if(S.drinks<3){S.drinks++;S.sta=Math.min(STA_MAX,S.sta+10);toast('喝了開水，體力 +10');}else toast('喝了開水，已經不渴了');refresh();continue;}
    if(r==='eat'){await eatMushroom();continue;}if(r==='toss'){S.mat.mushroom--;toast('丟掉了野生菇');continue;}
    if(r!=='pick')break;S.kit.splice(pick,1);refresh();}}
  finally{busy=false;save();refresh();}}
async function cards(){if(busy)return;busy=true;stopInput();
  try{const ks=Object.keys(S.cards);await say({p:'hero',who:'知識卡',html:ks.length?ks.map(k=>`<div class="card"><b>${CARDS[k].title}</b><p>${CARDS[k].text}</p></div>`).join(''):'<p class="small">還沒有知識卡。</p>',buttons:[{label:'關閉',primary:true}]});}
  finally{busy=false;}}
async function settings(){if(busy)return;busy=true;stopInput();let reset=false;
  try{const i=await say({p:'hero',who:'設定',html:`<p>移動方式：<b>${S.ctrl==='joy'?'虛擬搖桿':'方向鍵'}</b></p><p class="small">用電腦玩時，可以用鍵盤方向鍵走路、空白鍵互動。</p>`,buttons:[{label:S.ctrl==='joy'?'改用方向鍵':'改用虛擬搖桿',primary:true},{label:'卡住了？回到這個場景的入口'},{label:'全部重新開始',danger:true},{label:'關閉'}]});
    if(i===0)S.ctrl=S.ctrl==='joy'?'pad':'joy';
    else if(i===1){const sp=sc().spawn;S.pos={x:sp[0],y:sp[1]};placeHero();camera();toast('已回到入口');}
    else if(i===2){const j=await say({p:'hero',who:'重新開始',html:'<p>所有進度都會清除。</p>',buttons:[{label:'重新開始',danger:true},{label:'取消',primary:true}]});if(j===0){const c=S.ctrl;S=newState();S.ctrl=c;S.started=true;reset=true;}}}
  finally{busy=false;save();if(reset){buildScene();startScene();}else refresh();}}

/* ================= 移動 ================= */
function walkable(x,y){const rows=WALKS[S.scene];const j=Math.floor(y/CELL),i=Math.floor(x/CELL);return j>=0&&j<rows.length&&i>=0&&i<rows[0].length&&rows[j].charCodeAt(i)===49;}
function blockers(){const s=sc(),H=s.heroH,B=[];
  (s.trees||[]).forEach(t=>{const st=treeState(t);B.push([t.x,t.y,H*(st.hp>0?.32:.22)]);});
  if(s.rocks)ROCKS.forEach((r,i)=>{if(rockState(i).hp>0)B.push([r[0],r[1],H*.34]);});
  if(s.plots){B.push([300,540,H*.45]);if(S.bench)B.push([600,290,H*.5]);if(S.harvester){B.push([1450,380,H*.4]);B.push([1480,565,H*.6]);}}
  return B;}
function free(x,y){const H=sc().heroH,r=H*.12;
  if(!(walkable(x,y)&&walkable(x-r,y)&&walkable(x+r,y)&&walkable(x,y-r*.5)&&walkable(x,y+r*.5)))return false;
  for(const [bx,by,rx] of blockers()){if(((x-bx)/rx)**2+((y-by)/(rx*.5))**2<1)return false;}
  return true;}
const input={jx:0,jy:0,keys:{},pad:{}};
function stopInput(){input.jx=input.jy=0;input.pad={};input.keys={};resetKnob();if(walking){walking=false;heroEl&&heroEl.classList.remove('walking');}}
function inputVec(){let x=input.jx,y=input.jy;const k=input.keys,p=input.pad;
  if(k.ArrowLeft||k.a||p.left)x-=1;if(k.ArrowRight||k.d||p.right)x+=1;if(k.ArrowUp||k.w||p.up)y-=1;if(k.ArrowDown||k.s||p.down)y+=1;
  const m=Math.hypot(x,y);if(m>1){x/=m;y/=m;}return [x,y];}
let last=0,walking=false,saveT=0,exiting=false;const trail=[];
function loop(t){const dt=Math.min(.05,(t-last)/1000||0);last=t;
  if(!$('game').hidden&&!busy&&heroEl){
    const [vx,vy]=inputVec();
    if(Math.hypot(vx,vy)>.12){const sp=sc().heroH*1.8*speedMul();
      const nx=S.pos.x+vx*sp*dt,ny=S.pos.y+vy*sp*dt;
      if(!free(S.pos.x,S.pos.y)){S.pos.x=Math.max(20,Math.min(MW-20,nx));S.pos.y=Math.max(20,Math.min(MH-20,ny));}
      else{const dx=nx-S.pos.x,dy=ny-S.pos.y;
        if(free(nx,S.pos.y))S.pos.x=nx;
        else if(Math.abs(dx)>Math.abs(dy)*.3){for(const m of [1,2,3,-1,-2,-3]){const sy=m*Math.abs(dx);if(free(nx,S.pos.y+sy)){S.pos.x=nx;S.pos.y+=sy;break;}}}
        if(free(S.pos.x,ny))S.pos.y=ny;
        else if(Math.abs(dy)>Math.abs(dx)*.3){for(const m of [1,2,3,-1,-2,-3]){const sx=m*Math.abs(dy);if(free(S.pos.x+sx,ny)){S.pos.y=ny;S.pos.x+=sx;break;}}}}
      trail.push([S.pos.x,S.pos.y]);if(trail.length>60)trail.shift();
      if(Math.abs(vx)>.2)heroImg.classList.toggle('flip',vx<0);
      if(!walking){walking=true;heroEl.classList.add('walking');}
      placeHero();camera();checkExit();saveT+=dt;if(saveT>2){saveT=0;save();}
    }else if(walking){walking=false;heroEl.classList.remove('walking');save();}
    updateNear();}
  requestAnimationFrame(loop);}
async function checkExit(){if(exiting)return;
  for(const ex of (sc().exits||[])){if(ex.test(S.pos.x,S.pos.y)){
    exiting=true;busy=true;const px=S.pos.x,py=S.pos.y;stopInput();
    try{if(ex.block&&(!ex.need||!ex.need())){await say({p:'hero',html:`<p>${ex.block}</p>`});
        let back=null;for(let k=trail.length-1;k>=0;k--){const [tx,ty]=trail[k];if(!ex.test(tx,ty)&&free(tx,ty)&&Math.hypot(tx-px,ty-py)>30){back=[tx,ty];break;}}
        if(!back)back=sc().spawn;S.pos={x:back[0],y:back[1]};trail.length=0;placeHero();camera();}
      else await go(ex.to,ex.at);}
    finally{busy=false;exiting=false;save();refresh();}
    return;}}}

/* ================= 操控 ================= */
const joy=$('joy'),knob=joy.querySelector('.knob');let joyId=null;
function resetKnob(){knob.style.setProperty('--kx','0px');knob.style.setProperty('--ky','0px');input.jx=input.jy=0;joyId=null;}
function joyMove(e){const r=joy.getBoundingClientRect(),cx=r.left+r.width/2,cy=r.top+r.height/2,max=r.width/2-30;
  let dx=e.clientX-cx,dy=e.clientY-cy;const d=Math.hypot(dx,dy);if(d>max){dx*=max/d;dy*=max/d;}
  knob.style.setProperty('--kx',dx+'px');knob.style.setProperty('--ky',dy+'px');input.jx=dx/max;input.jy=dy/max;}
joy.addEventListener('pointerdown',e=>{joyId=e.pointerId;joy.setPointerCapture(e.pointerId);joyMove(e);e.preventDefault();});
joy.addEventListener('pointermove',e=>{if(e.pointerId===joyId)joyMove(e);});
['pointerup','pointercancel','lostpointercapture'].forEach(ev=>joy.addEventListener(ev,e=>{if(e.pointerId===joyId)resetKnob();}));
$('dpad').querySelectorAll('button').forEach(b=>{const d=b.dataset.d;
  const on=e=>{input.pad[d]=true;b.classList.add('on');try{b.setPointerCapture(e.pointerId);}catch(_){}e.preventDefault();};
  const off=()=>{input.pad[d]=false;b.classList.remove('on');};
  b.addEventListener('pointerdown',on);['pointerup','pointercancel','lostpointercapture'].forEach(ev=>b.addEventListener(ev,off));});
window.addEventListener('keydown',e=>{if(!$('dialog').hidden)return;const k=e.key.length===1?e.key.toLowerCase():e.key;
  if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','w','a','s','d'].includes(k)){input.keys[k]=true;e.preventDefault();}
  if((k===' '||k==='Enter')&&!$('game').hidden){doAction();e.preventDefault();}});
window.addEventListener('keyup',e=>{const k=e.key.length===1?e.key.toLowerCase():e.key;input.keys[k]=false;});
window.addEventListener('blur',stopInput);
$('act').addEventListener('click',doAction);
$('btnBag').onclick=bag;$('btnCards').onclick=cards;$('btnSettings').onclick=settings;

/* ================= 啟動 ================= */
async function startScene(){busy=false;if(S.step===0){busy=true;await sleep(RM?0:400);try{await introGrandpa();}finally{busy=false;save();refresh();}}}
S=load()||newState();
if(S.started)$('btnStart').textContent='繼續冒險';
$('btnStart').onclick=()=>{S.started=true;$('title').hidden=true;$('game').hidden=false;buildScene();save();startScene();};
requestAnimationFrame(loop);
if(location.hash==='#debug')window.__fa={moveSpr,well,boil,bag,needCheck,takeKit,faint,hypoWarn,doEvent,EVENTS,victim,gateDoor,tablet,hunter,guardTalk,gift,bench,takeBin,pickUp,eatMushroom,get S(){return S},go,talk,doAction,bed,machine,farmPlot,mine,shopMenu,refresh,buildScene};
})();
</script>
</body>
</html>
