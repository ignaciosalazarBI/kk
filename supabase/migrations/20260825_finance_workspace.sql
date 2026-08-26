-- Private Finance workspace for authenticated users.
-- No anonymous access: every row is scoped to auth.uid() by RLS.

create table if not exists public.finance_profiles (
    user_id uuid primary key references auth.users(id) on delete cascade,
    business_name text not null check (char_length(business_name) between 2 and 120),
    currency text not null default 'CLP' check (currency in ('CLP')),
    initial_cash numeric(18,2) not null default 0,
    monthly_revenue_goal numeric(18,2) not null default 0 check (monthly_revenue_goal >= 0),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.finance_transactions (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    tx_date date not null,
    kind text not null check (kind in ('ingreso','gasto')),
    status text not null check (status in ('pagado','pendiente')),
    category text not null check (char_length(category) between 2 and 80),
    counterparty text not null default '' check (char_length(counterparty) <= 120),
    amount numeric(18,2) not null check (amount > 0),
    notes text not null default '' check (char_length(notes) <= 500),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists finance_transactions_user_date_idx
    on public.finance_transactions (user_id, tx_date desc, created_at desc);

alter table public.finance_profiles enable row level security;
alter table public.finance_transactions enable row level security;

revoke all on public.finance_profiles from anon;
revoke all on public.finance_transactions from anon;

grant select, insert, update on public.finance_profiles to authenticated;
grant select, insert, update, delete on public.finance_transactions to authenticated;

drop policy if exists finance_profiles_select_own on public.finance_profiles;
create policy finance_profiles_select_own
on public.finance_profiles for select to authenticated
using ((select auth.uid()) = user_id);

drop policy if exists finance_profiles_insert_own on public.finance_profiles;
create policy finance_profiles_insert_own
on public.finance_profiles for insert to authenticated
with check ((select auth.uid()) = user_id);

drop policy if exists finance_profiles_update_own on public.finance_profiles;
create policy finance_profiles_update_own
on public.finance_profiles for update to authenticated
using ((select auth.uid()) = user_id)
with check ((select auth.uid()) = user_id);

drop policy if exists finance_transactions_select_own on public.finance_transactions;
create policy finance_transactions_select_own
on public.finance_transactions for select to authenticated
using ((select auth.uid()) = user_id);

drop policy if exists finance_transactions_insert_own on public.finance_transactions;
create policy finance_transactions_insert_own
on public.finance_transactions for insert to authenticated
with check ((select auth.uid()) = user_id);

drop policy if exists finance_transactions_update_own on public.finance_transactions;
create policy finance_transactions_update_own
on public.finance_transactions for update to authenticated
using ((select auth.uid()) = user_id)
with check ((select auth.uid()) = user_id);

drop policy if exists finance_transactions_delete_own on public.finance_transactions;
create policy finance_transactions_delete_own
on public.finance_transactions for delete to authenticated
using ((select auth.uid()) = user_id);
