import { useEffect, useState } from 'react';
import { View, Text, FlatList, Button, StyleSheet } from 'react-native';
import { supabase } from '../services/supabase';
import { useCareCircle } from '../contexts/CareCircleContext';

interface CircleMember {
  user_id: string;
  full_name: string;
  role: string;
}

export default function InviteMemberScreen({ navigation }: any) {
  const { activeCircle } = useCareCircle();
  const [circleMembers, setCircleMembers] = useState<CircleMember[]>([]);

  useEffect(() => {
    if (!activeCircle) return;

    const loadMembers = async () => {
      const { data, error } = await supabase
        .from('circle_members')
        .select(`
          user_id,
          role,
          users (
            full_name
          )
        `)
        .eq('circle_id', activeCircle.circle_id);

      if (error) {
        console.error('Error loading circle members:', error);
        return;
      }

      const members = (data ?? []).map((member: any) => ({
        user_id: member.user_id,
        full_name: member.users?.full_name ?? 'Unknown member',
        role: member.role,
      }));

      setCircleMembers(members);
    };

    loadMembers();
  }, [activeCircle?.circle_id]);

  if (!activeCircle) return null;

  return (
    <View style={styles.container}>
      <Text style={styles.circleName}>
        {activeCircle.circle_name}
      </Text>

      <Text style={styles.role}>
        You are a {activeCircle.role} in this circle
      </Text>

      <Text style={styles.title}>
        Your Circle Members
      </Text>

      <FlatList
        data={circleMembers}
        keyExtractor={(item) => item.user_id}
        renderItem={({ item }) => (
          <View style={styles.row}>
            <Text>{item.full_name}</Text>
            <Text style={styles.memberRole}>
              {item.role}
            </Text>
          </View>
        )}
        ListEmptyComponent={
          <Text style={styles.empty}>
            No members in circle yet.
          </Text>
        }
      />

      <Text style={styles.title}>
        Invite a caregiver
      </Text>

      <Text style={styles.description}>
        Generate an invitation code and share it with the caregiver you
        want to add to this circle.
      </Text>

      <Button
        title="Generate Invite"
        onPress={() => {
          // We'll implement this next.
        }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },

  circleName: {
    fontSize: 24,
    fontWeight: '700',
  },

  role: {
    color: '#777',
    marginBottom: 24,
    textTransform: 'capitalize',
  },

  title: {
    fontSize: 22,
    fontWeight: '600',
    marginBottom: 12,
    marginTop: 16,
  },

  description: {
    color: '#666',
    marginBottom: 16,
    lineHeight: 20,
  },

  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },

  memberRole: {
    color: '#777',
    textTransform: 'capitalize',
  },

  empty: {
    color: '#999',
    fontStyle: 'italic',
    paddingVertical: 8,
  },
});
