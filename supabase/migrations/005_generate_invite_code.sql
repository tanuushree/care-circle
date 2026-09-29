create or replace function public.create_circle_invitation(
  p_circle_id uuid
)
returns text
language plpgsql
security definer
set search_path = public
as $$
declare
  invitation_code text;
begin
  -- Caller must be logged in
  if auth.uid() is null then
    raise exception 'Not authenticated';
  end if;

  -- Caller must have permission to manage members
  if not exists (
    select 1
    from public.circle_members
    where circle_id = p_circle_id
      and user_id = auth.uid()
      and can_manage_members = true
  ) then
    raise exception 'You do not have permission to invite members';
  end if;

  -- Generate a unique invitation code
  loop
    invitation_code :=
      'FAM-' || upper(substr(md5(gen_random_uuid()::text), 1, 6));

    exit when not exists (
      select 1
      from public.circle_invitations
      where code = invitation_code
    );
  end loop;

  -- Create invitation
  insert into public.circle_invitations (
    circle_id,
    invited_by_user_id,
    code,
    role
  )
  values (
    p_circle_id,
    auth.uid(),
    invitation_code,
    'caregiver'
  );

  return invitation_code;
end;
$$;

revoke all on function public.create_circle_invitation(uuid) from public;

grant execute
on function public.create_circle_invitation(uuid)
to authenticated;