'use client';
import { useState, useEffect, useCallback } from 'react';
import { supabase, type DbTemplate } from '@/lib/supabase';
import { useAuth } from '@/contexts/AuthContext';

export function useTemplates(module: string) {
  const { user } = useAuth();
  const [templates, setTemplates] = useState<DbTemplate[]>([]);
  const [loading, setLoading] = useState(false);

  const fetch = useCallback(async () => {
    if (!user) return;
    const { data } = await supabase
      .from('templates')
      .select('*')
      .eq('user_id', user.id)
      .eq('module', module)
      .order('created_at', { ascending: false });
    setTemplates((data as DbTemplate[]) ?? []);
  }, [user, module]);

  useEffect(() => { fetch(); }, [fetch]);

  const save = async (name: string, params: Record<string, unknown>) => {
    if (!user) return;
    setLoading(true);
    await supabase.from('templates').insert({ user_id: user.id, module, name, params });
    await fetch();
    setLoading(false);
  };

  const remove = async (id: string) => {
    await supabase.from('templates').delete().eq('id', id);
    setTemplates(prev => prev.filter(t => t.id !== id));
  };

  return { templates, save, remove, loading, refresh: fetch };
}
