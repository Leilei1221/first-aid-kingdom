-- 急救王國 第五章（筆試）：老師端班級控制新增「第五章（筆試）」開關（草稿，尚未套用）
-- 由老師在 Supabase SQL Editor 執行（Claude Code 不套用）。只改 fa_class_flags 的 flag 檢查條件，不改任何資料，不碰其他表。
-- 003 之後的檢查條件是 ch2／ch3／ch4／wild／relief；這裡把 ch5 加進去。學生端讀取開關的函式（fa_my_control）是把表裡所有列都整理起來，不用改。
-- 沒有開關 ＝ 有班級的學生看不到筆試；不屬於任何班的人（老師、訪客）預設看得到，但仍要登入、四關總星數達 18 顆。

alter table public.fa_class_flags drop constraint if exists fa_class_flags_flag_check;
alter table public.fa_class_flags
  add constraint fa_class_flags_flag_check check (flag in ('ch2', 'ch3', 'ch4', 'ch5', 'wild', 'relief'));

-- 還原用（需要時才執行）：
-- delete from public.fa_class_flags where flag = 'ch5';
-- alter table public.fa_class_flags drop constraint fa_class_flags_flag_check;
-- alter table public.fa_class_flags add constraint fa_class_flags_flag_check check (flag in ('ch2', 'ch3', 'ch4', 'wild', 'relief'));
