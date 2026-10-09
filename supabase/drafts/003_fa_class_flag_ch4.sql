-- 急救王國 E4：老師端班級控制新增「第四章（雪嶺）」開關（草稿，尚未套用）
-- 由老師在 Supabase SQL Editor 執行（Claude Code 不套用）。只改 fa_class_flags 的 flag 檢查條件，不改任何資料，不碰其他表。
-- 002 建表時的檢查條件只允許 ch2／ch3／wild／relief；這裡把 ch4 加進去。學生端讀取開關的函式（fa_my_control）是把表裡所有列都整理起來，不用改。
-- 執行前請先確認：雪嶺章節的內容已經審核完、決定要開放給學生（沒有開關 ＝ 有班級的學生預設看不到；不屬於任何班的人，目前由程式內的草稿擋門擋住，正式開放時才會拿掉）。

alter table public.fa_class_flags drop constraint if exists fa_class_flags_flag_check;
alter table public.fa_class_flags
  add constraint fa_class_flags_flag_check check (flag in ('ch2', 'ch3', 'ch4', 'wild', 'relief'));

-- 還原用（需要時才執行）：
-- delete from public.fa_class_flags where flag = 'ch4';
-- alter table public.fa_class_flags drop constraint fa_class_flags_flag_check;
-- alter table public.fa_class_flags add constraint fa_class_flags_flag_check check (flag in ('ch2', 'ch3', 'wild', 'relief'));
