'use client';
import { Lock, UserPlus } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useLang } from '@/contexts/LangContext';

interface Props {
  type: 'templates' | 'history';
}

export function GuestBanner({ type }: Props) {
  const { mode } = useAuth();
  const { t } = useLang();

  if (mode === 'user') return null;

  const cfg = type === 'templates'
    ? { title: t.templates.guestTitle, desc: t.templates.guestDesc, cta: t.templates.signUp }
    : { title: t.history.guestTitle, desc: t.history.guestDesc, cta: t.history.signUp };

  return (
    <div className="rounded-xl border border-dashed border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 p-4 text-center">
      <div className="w-10 h-10 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center mx-auto mb-3">
        <Lock className="w-5 h-5 text-gray-500 dark:text-gray-400" />
      </div>
      <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">{cfg.title}</p>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-3 leading-relaxed">{cfg.desc}</p>
      <a href="#" onClick={e => { e.preventDefault(); window.location.reload(); }}
        className="inline-flex items-center gap-1.5 bg-green-700 hover:bg-green-800 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition-colors">
        <UserPlus className="w-3.5 h-3.5" />
        {cfg.cta}
      </a>
    </div>
  );
}
