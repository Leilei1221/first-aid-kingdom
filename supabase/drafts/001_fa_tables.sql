-- 急救王國 階段 B：雲端存檔用資料表（草稿，尚未套用）
-- 目標專案：教室管理系統（Leilei1221's Project）。只新增 fa_ 開頭的物件，不修改任何 hc_ 既有表。
-- 沿用教室系統的慣例：以 email 對應學生（auth.jwt()->>'email'）、老師用 hc_teaches_student_email() 讀學生資料。

-- ── 訪客名單：校外朋友等，由老師在 Supabase 後台手動加入 email ─────────────
-- 沒有任何 RLS policy＝一般登入者完全讀寫不到，只有下面的 SECURITY DEFINER 函式與後台（SQL）碰得到。
-- 加入範例：insert into public.fa_guests(email, note) values ('friend@gmail.com', '朋友');
create table public.fa_guests (
  email    text primary key check (email = lower(email)),
  note     text,
  added_at timestamptz not null default now()
);
alter table public.fa_guests enable row level security;
revoke all on public.fa_guests from anon, authenticated;

-- ── 誰可以存檔：名單內在學學生、老師白名單（限學校網域），或訪客名單 ──────────
create or replace function public.fa_can_play()
returns boolean
language sql stable security definer
set search_path to 'public', 'pg_temp'
as $$
  select (
    lower(coalesce(auth.jwt() ->> 'email', '')) like '%@hlhs.hlc.edu.tw'
    and (
      public.hc_is_allowed_teacher()
      or exists (
        select 1
        from public.hc_students s
        join public.hc_classes c on c.id = s.class_id
        where lower(coalesce(s.login_email, s.email)) = lower(auth.jwt() ->> 'email')
          and s.is_active and c.is_active
      )
    )
  )
  or exists (
    select 1 from public.fa_guests g
    where g.email = lower(coalesce(auth.jwt() ->> 'email', ''))
  );
$$;

create or replace function public.fa_touch_updated_at()
returns trigger language plpgsql
set search_path to 'public', 'pg_temp'
as $$ begin new.updated_at := now(); return new; end $$;

-- ── 最新進度：每位學生一列 ────────────────────────────────────────
create table public.fa_saves (
  email      text primary key check (email = lower(email)),
  state      jsonb not null check (octet_length(state::text) < 500000),
  updated_at timestamptz not null default now()
);
create trigger fa_saves_touch before update on public.fa_saves
  for each row execute function public.fa_touch_updated_at();

-- ── 每日存檔點：每位學生每個遊戲日一列，只保留最近 7 天 ───────────────
create table public.fa_checkpoints (
  email      text not null check (email = lower(email)),
  day        integer not null,
  state      jsonb not null check (octet_length(state::text) < 500000),
  created_at timestamptz not null default now(),
  primary key (email, day)
);
create or replace function public.fa_trim_checkpoints()
returns trigger language plpgsql security definer
set search_path to 'public', 'pg_temp'
as $$ begin
  delete from public.fa_checkpoints where email = new.email and day < new.day - 7;
  return null;
end $$;
create trigger fa_checkpoints_trim after insert on public.fa_checkpoints
  for each row execute function public.fa_trim_checkpoints();

-- ── 失敗記錄：救援失敗時寫一筆（給老師端統計最常犯的錯）──────────────
create table public.fa_failures (
  id         bigint generated always as identity primary key,
  email      text not null check (email = lower(email)),
  scenario   text not null,          -- 例如 flood、typhoon、hypothermia、drowning、electric
  choice     text not null,          -- 學生選的那個選項文字
  created_at timestamptz not null default now()
);
create index fa_failures_scenario_idx on public.fa_failures (scenario, created_at desc);

-- ── RLS：學生只能碰自己的列；老師只能讀自己班上的學生 ─────────────────
alter table public.fa_saves       enable row level security;
alter table public.fa_checkpoints enable row level security;
alter table public.fa_failures    enable row level security;

revoke all on public.fa_saves, public.fa_checkpoints, public.fa_failures from anon;

create policy fa_saves_own on public.fa_saves for all to authenticated
  using (email = lower(auth.jwt() ->> 'email'))
  with check (email = lower(auth.jwt() ->> 'email') and public.fa_can_play());
create policy fa_saves_teacher_read on public.fa_saves for select to authenticated
  using (public.hc_teaches_student_email(email));

create policy fa_checkpoints_own on public.fa_checkpoints for all to authenticated
  using (email = lower(auth.jwt() ->> 'email'))
  with check (email = lower(auth.jwt() ->> 'email') and public.fa_can_play());

create policy fa_failures_insert_own on public.fa_failures for insert to authenticated
  with check (email = lower(auth.jwt() ->> 'email') and public.fa_can_play());
create policy fa_failures_read_own on public.fa_failures for select to authenticated
  using (email = lower(auth.jwt() ->> 'email'));
create policy fa_failures_teacher_read on public.fa_failures for select to authenticated
  using (public.hc_teaches_student_email(email));
