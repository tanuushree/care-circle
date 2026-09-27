import { supabase } from './supabase';
import { CareCircleMembership } from '../types/circle';

/**
 * All circles the given user belongs to, with their role/permissions in
 * each. A user can belong to more than one circle (e.g. a caregiver for
 * two different family members), so this always returns an array.
 */
export async function getMyCircleMemberships(
  userId: string
): Promise<CareCircleMembership[]> {
  const { data, error } = await supabase
    .from('circle_members')
    .select(
      `
      circle_id,
      role,
      can_manage_medications,
      can_view_health_data,
      can_manage_members,
      can_trigger_sos,
      receives_sos_alerts,
      care_circles ( name )
    `
    )
    .eq('user_id', userId);

  if (error) throw error;

  return (data ?? []).map((row: any) => ({
    circle_id: row.circle_id,
    circle_name: row.care_circles?.name ?? 'Care Circle',
    role: row.role,
    can_manage_medications: row.can_manage_medications,
    can_view_health_data: row.can_view_health_data,
    can_manage_members: row.can_manage_members,
    can_trigger_sos: row.can_trigger_sos,
    receives_sos_alerts: row.receives_sos_alerts,
  }));
}

/**
 * Creates a brand-new care circle with the given user as its patient,
 * with full permissions (patients get can_trigger_sos = true; the schema's
 * check constraint blocks that for caregivers).
 */
export async function createCareCircle(
  patientUserId: string,
  name: string
): Promise<CareCircleMembership> {
  const { data: circle, error: circleError } = await supabase
    .from('care_circles')
    .insert({ patient_user_id: patientUserId, name })
    .select()
    .single();

  if (circleError) throw circleError;

  const { error: memberError } = await supabase.from('circle_members').insert({
    circle_id: circle.id,
    user_id: patientUserId,
    role: 'patient',
    can_manage_medications: true,
    can_view_health_data: true,
    can_manage_members: true,
    can_trigger_sos: true,
    receives_sos_alerts: true,
  });

  if (memberError) throw memberError;

  return {
    circle_id: circle.id,
    circle_name: circle.name,
    role: 'patient',
    can_manage_medications: true,
    can_view_health_data: true,
    can_manage_members: true,
    can_trigger_sos: true,
    receives_sos_alerts: true,
  };
}

/**
 * TODO: not yet implemented. Redeeming a circle_invitations code
 **/
export async function joinCareCircleWithCode(
  _userId: string,
  _code: string
): Promise<never> {
  throw new Error(
    'Joining via invite code requires a server-side Edge Function (not yet built). See TODO in services/circle.ts.'
  );
}
