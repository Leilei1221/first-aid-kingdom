-- 急救王國 階段 D5：老師端班級控制（草稿，尚未套用）
-- 由老師在 Supabase SQL Editor 執行（Claude Code 不套用）。只新增 fa_ 開頭的物件，不改任何既有表。
-- 沿用教室系統慣例：班級擁有者 = hc_classes.teacher_id = auth.uid()（或 hc_is_admin()）；老師身分用 hc_is_allowed_teacher() 把關。

-- ── 班級功能開關：每班每個功能一列 ───────────────────────────────
-- flag：ch2＝第二章；wild＝野外項目（營火、溺水、裝溪水、阿鹿支線）；relief＝村長救災物資。之後章節（ch3…）再加。
-- 沒有列＝這個班沒設定，遊戲用程式裡的預設（chapters/index.json 與 content/weather.json）。
create table public.fa_class_flags (
  class_id   uuid not null references public.hc_classes(id) on delete cascade,
  flag       text not null check (flag in ('ch2', 'wild', 'relief')),
  enabled    boolean not null,
  updated_at timestamptz not null default now(),
  primary key (class_id, flag)
);

-- ── 班級天災發布：老師按「發布」就多一列；取消＝cancelled = true ──────────
-- 學生遊戲讀到「比自己處理過的更新的一筆」，就把它排成自己遊戲的「明天」天災（每則公告每位學生只套用一次）。
create table public.fa_class_weather (
  id           bigint generated always as identity primary key,
  class_id     uuid not null references public.hc_classes(id) on delete cascade,
  type         text not null check (type in ('typhoon', 'flood', 'fog')),
  published_at timestamptz not null default now(),
  cancelled    boolean not null default false
);
create index fa_class_weather_class_idx on public.fa_class_weather (class_id, id desc);

alter table public.fa_class_flags   enable row level security;
alter table public.fa_class_weather enable row level security;
revoke all on public.fa_class_flags, public.fa_class_weather from anon;

-- 老師：只能管自己班（admin 例外）。學生沒有任何 policy＝讀寫不到，只能透過下面的函式讀「自己班」的內容。
create policy fa_class_flags_owner on public.fa_class_flags for all to authenticated
  using (exists (select 1 from public.hc_classes c where c.id = class_id and (c.teacher_id = auth.uid() or public.hc_is_admin())))
  with check (exists (select 1 from public.hc_classes c where c.id = class_id and ((c.teacher_id = auth.uid() and public.hc_is_allowed_teacher()) or public.hc_is_admin())));
create policy fa_class_weather_owner on public.fa_class_weather for all to authenticated
  using (exists (select 1 from public.hc_classes c where c.id = class_id and (c.teacher_id = auth.uid() or public.hc_is_admin())))
  with check (exists (select 1 from public.hc_classes c where c.id = class_id and ((c.teacher_id = auth.uid() and public.hc_is_allowed_teacher()) or public.hc_is_admin())));

create trigger fa_class_flags_touch before update on public.fa_class_flags
  for each row execute function public.fa_touch_updated_at();

-- ── 學生讀自己班的設定（遊戲啟動、每天早上各讀一次）─────────────────────
-- 傳回 {"class_id":…, "flags":{"ch2":true,…}, "weather":{"id":12,"type":"typhoon"}|null}
-- 不是在學學生（老師、訪客）class_id 為 null、flags 為空 → 遊戲用預設。
create or replace function public.fa_my_class_control()
returns jsonb
language sql stable security definer
set search_path to 'public', 'pg_temp'
as $$
  with me as (
    select s.class_id
    from public.hc_students s
    join public.hc_classes c on c.id = s.class_id
    where lower(coalesce(s.login_email, s.email)) = lower(coalesce(auth.jwt() ->> 'email', ''))
      and s.is_active and c.is_active
    order by c.academic_year desc, c.semester desc
    limit 1
  )
  select jsonb_build_object(
    'class_id', (select class_id from me),
    'flags', coalesce((select jsonb_object_agg(f.flag, f.enabled)
                       from public.fa_class_flags f where f.class_id = (select class_id from me)), '{}'::jsonb),
    'weather', (select jsonb_build_object('id', w.id, 'type', w.type)
                from public.fa_class_weather w
                where w.class_id = (select class_id from me) and not w.cancelled
                order by w.id desc limit 1)
  );
$$;
revoke all on function public.fa_my_class_control() from public, anon;
grant execute on function public.fa_my_class_control() to authenticated;
