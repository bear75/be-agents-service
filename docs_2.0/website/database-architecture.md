# Database Architecture

## Core Tables

### users

Primary table for all user data and consent management

```sql
create table public.users (
  id uuid default gen_random_uuid() primary key,
  email text unique not null,
  name text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
  global_consent boolean default false,
  global_status text check (global_status in ('active', 'inactive', 'blocked')) default 'active'
);
```

### user_consents

Tracks all consent-related activities for GDPR compliance

```sql
create table public.user_consents (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references public.users(id) not null,
  consent_type text not null check (consent_type in ('newsletter', 'marketing', 'contact', 'whitepaper')),
  status boolean default true,
  given_at timestamp with time zone default timezone('utc'::text, now()) not null,
  withdrawn_at timestamp with time zone,
  consent_source text not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  CONSTRAINT user_consents_user_id_consent_type_key UNIQUE (user_id, consent_type)
);
```

### user_communications

Tracks all communication events and preferences (including contact form submissions)

```sql
create table public.user_communications (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references public.users(id) not null,
  type text not null check (type in ('newsletter', 'whitepaper', 'contact')),
  metadata jsonb default '{}'::jsonb,
  status text check (status in ('pending', 'sent', 'failed', 'cancelled')) default 'pending',
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);
```

### newsletter_campaigns

Manages newsletter campaigns and their status

```sql
create table public.newsletter_campaigns (
  id uuid default gen_random_uuid() primary key,
  title text not null,
  content text not null,
  status text check (status in ('draft', 'scheduled', 'sent', 'cancelled')) default 'draft',
  scheduled_at timestamp with time zone,
  sent_at timestamp with time zone,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);
```

## Row Level Security (RLS) Policies

### users Table

```sql
-- Allow anonymous and authenticated users to perform all operations
create policy "Enable anonymous upsert"
  on users for all
  to anon
  using (true)
  with check (true);

create policy "Enable authenticated upsert"
  on users for all
  to authenticated
  using (true)
  with check (true);
```

### user_consents Table

```sql
-- Allow anonymous and authenticated users to perform all operations
create policy "Enable anonymous upsert"
  on user_consents for all
  to anon
  using (true)
  with check (true);

create policy "Enable authenticated upsert"
  on user_consents for all
  to authenticated
  using (true)
  with check (true);
```

### user_communications Table

```sql
-- Allow read access to authenticated users for their own communications
create policy "Users can view own communications"
  on user_communications for select
  using (auth.uid() = user_id);

-- Allow insert for new communications (public access)
create policy "Allow communication registration"
  on user_communications for insert
  with check (true);
```

## Indexes

```sql
-- users table
create index users_email_idx on users (email);
create index users_global_status_idx on users (global_status);

-- user_consents table
create index user_consents_user_id_idx on user_consents (user_id);
create index user_consents_type_idx on user_consents (consent_type);
create index user_consents_status_idx on user_consents (status);

-- user_communications table
create index user_communications_user_id_idx on user_communications (user_id);
create index user_communications_type_idx on user_communications (type);
create index user_communications_status_idx on user_communications (status);
```

## Functions and Triggers

### Update Timestamp Trigger

```sql
create or replace function public.handle_updated_at()
returns trigger as $$
begin
  new.updated_at = timezone('utc'::text, now());
  return new;
end;
$$ language plpgsql;

-- Apply to users table
create trigger handle_users_updated_at
  before update on users
  for each row
  execute function handle_updated_at();

-- Apply to user_communications table
create trigger handle_user_communications_updated_at
  before update on user_communications
  for each row
  execute function handle_updated_at();
```

## Usage Examples

### Contact Form Submission

```sql
-- Insert or update user
insert into users (email, name, global_consent)
values ('user@example.com', 'John Doe', true)
on conflict (email) do update
set name = excluded.name,
    updated_at = now()
returning id;

-- Add/update consent record
insert into user_consents (user_id, consent_type, consent_source)
values ('user-id', 'contact', 'contact_form')
on conflict (user_id, consent_type) do update
set status = true,
    given_at = now(),
    withdrawn_at = null;

-- Record the communication in user_communications
insert into user_communications (user_id, type, metadata)
values ('user-id', 'contact', '{"message": "Contact form message", "name": "John Doe"}');
```

### Newsletter Subscription

```sql
-- Insert or update user
insert into users (email, name, global_consent)
values ('user@example.com', 'John Doe', true)
on conflict (email) do update
set updated_at = now()
returning id;

-- Add/update consent record
insert into user_consents (user_id, consent_type, consent_source)
values ('user-id', 'newsletter', 'website_form')
on conflict (user_id, consent_type) do update
set status = true,
    given_at = now(),
    withdrawn_at = null;

-- Record welcome email
insert into user_communications (user_id, type, metadata)
values ('user-id', 'newsletter', '{"type": "welcome_email"}');
```

## Notes

- All contact form submissions are now stored in the `user_communications` table with type='contact'
- Legacy tables (contact_submissions, profiles, etc.) have been removed for simplicity
- RLS policies ensure proper access control while allowing necessary operations
- All tables maintain created_at/updated_at timestamps for auditing
