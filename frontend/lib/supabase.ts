import { createClient } from '@supabase/supabase-js';

export const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

export type DbTemplate = {
  id: string;
  user_id: string;
  module: string;
  name: string;
  params: Record<string, unknown>;
  created_at: string;
};

export type DbHistory = {
  id: string;
  user_id: string;
  module: string;
  params: Record<string, unknown> | null;
  summary: Record<string, unknown> | null;
  created_at: string;
};
