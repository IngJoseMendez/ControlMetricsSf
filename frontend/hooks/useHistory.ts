'use client';
import { useState, useEffect, useCallback } from 'react';
import { supabase, type DbHistory } from '@/lib/supabase';
import { useAuth } from '@/contexts/AuthContext';

export function useHistory() {
  const { user } = useAuth();
  const [history, setHistory] = useState<DbHistory[]>([]);

  const fetch = useCallback(async () => {
    if (!user) return;
    const { data } = await supabase
      .from('history')
      .select('*')
      .eq('user_id', user.id)
      .order('created_at', { ascending: false })
      .limit(20);
    setHistory((data as DbHistory[]) ?? []);
  }, [user]);

  useEffect(() => { fetch(); }, [fetch]);

  const add = async (
    module: string,
    params: Record<string, unknown>,
    summary: Record<string, unknown>
  ) => {
    if (!user) return;
    await supabase.from('history').insert({ user_id: user.id, module, params, summary });
    fetch();
  };

  const clear = async () => {
    if (!user) return;
    await supabase.from('history').delete().eq('user_id', user.id);
    setHistory([]);
  };

  return { history, add, clear, refresh: fetch };
}
