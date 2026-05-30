-- ControlMetrics – Supabase Database Setup
-- Run this in: Supabase Dashboard → SQL Editor → New Query

-- Templates table
create table if not exists public.templates (
  id          uuid default gen_random_uuid() primary key,
  user_id     uuid references auth.users on delete cascade not null,
  module      varchar(50) not null,
  name        varchar(100) not null,
  params      jsonb not null default '{}',
  created_at  timestamptz default now()
);

-- History table
create table if not exists public.history (
  id          uuid default gen_random_uuid() primary key,
  user_id     uuid references auth.users on delete cascade not null,
  module      varchar(50) not null,
  params      jsonb,
  summary     jsonb,
  created_at  timestamptz default now()
);

-- Row Level Security
alter table public.templates enable row level security;
alter table public.history   enable row level security;

-- Policies: users can only see/write their own data
create policy "templates: own rows"
  on public.templates for all
  using  (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create policy "history: own rows"
  on public.history for all
  using  (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- Indexes for performance
create index if not exists idx_templates_user_module on public.templates (user_id, module);
create index if not exists idx_history_user_date     on public.history   (user_id, created_at desc);
