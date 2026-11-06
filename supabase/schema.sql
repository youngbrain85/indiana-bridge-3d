-- Bridge inspection cloud store for the inspection app (web/inspect.html).
-- Run once in the Supabase SQL Editor of a new project. It is safe to run again.
--
-- Access model: only signed-in users (Supabase Auth) can read or write. Turn off public sign-ups
-- (Authentication > Sign In / Providers > "Allow new users to sign up") and invite each inspector instead.
-- Rows are never deleted by the app: a deleted defect or photo keeps its row with deleted = true.

create table if not exists public.inspections (
  id uuid primary key,
  bridge_id text not null,
  inspection_date date not null,
  inspection_type text not null,
  inspectors text not null default '',
  notes text not null default '',
  status text not null default 'open' check (status in ('open', 'closed')),
  deleted boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  created_by uuid default auth.uid() references auth.users (id),
  synced_at timestamptz not null default now()
);

create table if not exists public.defects (
  id uuid primary key,
  inspection_id uuid not null references public.inspections (id),
  bridge_id text not null,
  number integer not null check (number > 0),
  sheet_id text not null,
  view_id text not null,
  part text not null,                      -- mesh name in the bridge's model.glb
  element_code integer not null,           -- AASHTO MBEI element, e.g. 12, 109, 205
  defect_code integer not null,            -- AASHTO MBEI defect, e.g. 1080, 1130
  kind text not null check (kind in ('line', 'area', 'point')),
  path jsonb not null,                     -- [[u, v], ...] in the view's 0..1 coordinates (see sheets.json "mapping")
  measurements jsonb not null default '{}'::jsonb,
  quantity numeric not null check (quantity >= 0),
  unit text not null,
  quantity_manual boolean not null default false,
  quantity_basis text not null default '',
  cs smallint not null check (cs between 1 and 4),
  cs_suggested smallint check (cs_suggested between 1 and 4),
  cs_basis text not null default '',
  cs_reason text not null default '',
  structural_review boolean not null default false,
  location text not null default '',
  notes text not null default '',
  deleted boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  created_by uuid default auth.uid() references auth.users (id),
  synced_at timestamptz not null default now(),
  -- A condition state that differs from the measured suggestion needs a reason.
  constraint cs_change_explained check (cs_suggested is null or cs = cs_suggested or length(trim(cs_reason)) > 0)
);
create index if not exists defects_inspection on public.defects (inspection_id);
create index if not exists defects_bridge_synced on public.defects (bridge_id, synced_at);

create table if not exists public.defect_photos (
  id uuid primary key,
  defect_id uuid not null references public.defects (id),
  inspection_id uuid not null references public.inspections (id),
  file_name text not null,
  storage_path text,                       -- object in the private "defect-photos" bucket
  taken_at timestamptz not null,
  width integer,
  height integer,
  bytes integer,
  caption text not null default '',
  deleted boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  created_by uuid default auth.uid() references auth.users (id),
  synced_at timestamptz not null default now()
);
create index if not exists photos_inspection_synced on public.defect_photos (inspection_id, synced_at);
create index if not exists inspections_bridge_synced on public.inspections (bridge_id, synced_at);

-- synced_at is the server's clock: devices pull rows whose synced_at is newer than their last pull.
create or replace function public.touch_synced_at() returns trigger language plpgsql as $$
begin
  new.synced_at := now();
  if tg_op = 'UPDATE' then new.created_by := old.created_by; end if;
  return new;
end $$;
do $$ declare t text; begin
  foreach t in array array['inspections', 'defects', 'defect_photos'] loop
    execute format('drop trigger if exists %I_synced on public.%I', t, t);
    execute format('create trigger %I_synced before insert or update on public.%I for each row execute function public.touch_synced_at()', t, t);
  end loop;
end $$;

-- Row-level security: signed-in users read and write; nobody deletes; anonymous visitors see nothing.
alter table public.inspections enable row level security;
alter table public.defects enable row level security;
alter table public.defect_photos enable row level security;
do $$ declare t text; begin
  foreach t in array array['inspections', 'defects', 'defect_photos'] loop
    execute format('drop policy if exists "%s read" on public.%I', t, t);
    execute format('drop policy if exists "%s insert" on public.%I', t, t);
    execute format('drop policy if exists "%s update" on public.%I', t, t);
    execute format('create policy "%s read" on public.%I for select to authenticated using (true)', t, t);
    execute format('create policy "%s insert" on public.%I for insert to authenticated with check (true)', t, t);
    execute format('create policy "%s update" on public.%I for update to authenticated using (true) with check (true)', t, t);
  end loop;
end $$;
revoke all on public.inspections, public.defects, public.defect_photos from anon;
grant select, insert, update on public.inspections, public.defects, public.defect_photos to authenticated;

-- Photos: a private bucket (JPEG only, 15 MB cap). Signed-in users can read, add and replace objects.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('defect-photos', 'defect-photos', false, 15728640, array['image/jpeg'])
on conflict (id) do update set public = false, file_size_limit = excluded.file_size_limit, allowed_mime_types = excluded.allowed_mime_types;
drop policy if exists "defect photos read" on storage.objects;
drop policy if exists "defect photos insert" on storage.objects;
drop policy if exists "defect photos update" on storage.objects;
create policy "defect photos read" on storage.objects for select to authenticated using (bucket_id = 'defect-photos');
create policy "defect photos insert" on storage.objects for insert to authenticated with check (bucket_id = 'defect-photos');
create policy "defect photos update" on storage.objects for update to authenticated using (bucket_id = 'defect-photos') with check (bucket_id = 'defect-photos');

-- Element condition-state quantities per inspection (AASHTO element table), for reports and dashboards.
create or replace view public.element_condition as
select d.inspection_id, d.bridge_id, d.element_code, d.defect_code, d.unit,
       sum(d.quantity) filter (where d.cs = 1) as cs1,
       sum(d.quantity) filter (where d.cs = 2) as cs2,
       sum(d.quantity) filter (where d.cs = 3) as cs3,
       sum(d.quantity) filter (where d.cs = 4) as cs4,
       count(*) as defects
from public.defects d
where not d.deleted
group by d.inspection_id, d.bridge_id, d.element_code, d.defect_code, d.unit;
alter view public.element_condition set (security_invoker = true);
grant select on public.element_condition to authenticated;
