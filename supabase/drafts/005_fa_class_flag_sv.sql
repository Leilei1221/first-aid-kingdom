-- 急救王國 雪嶺「抉擇與求生」：老師端班級控制新增「雪嶺求生」開關（草稿，尚未套用）
-- 由老師在 Supabase SQL Editor 執行（Claude Code 不套用）。只改 fa_class_flags 的 flag 檢查條件，不改任何資料，不碰其他表。
-- 004 之後的檢查條件是 ch2／ch3／ch4／ch5／wild／relief；這裡把 sv 加進去。學生端讀取開關的函式（fa_my_control）是把表裡所有列都整理起來，不用改。
-- 沒有開關 ＝ 有班級的學生看不到求生玩法（氣象預報、落石、白茫茫、山屋暴風雪、指南針）；不屬於任何班的人（老師、訪客、沒登入）預設看得到。

alter table public.fa_class_flags drop constraint if exists fa_class_flags_flag_check;
alter table public.fa_class_flags
  add constraint fa_class_flags_flag_check check (flag in ('ch2', 'ch3', 'ch4', 'ch5', 'sv', 'wild', 'relief'));

-- 還原用（需要時才執行）：
-- delete from public.fa_class_flags where flag = 'sv';
-- alter table public.fa_class_flags drop constraint fa_class_flags_flag_check;
-- alter table public.fa_class_flags add constraint fa_class_flags_flag_check check (flag in ('ch2', 'ch3', 'ch4', 'ch5', 'wild', 'relief'));
