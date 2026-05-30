'use client';
import { useLang } from '@/contexts/LangContext';

export function LangToggle({ className = '' }: { className?: string }) {
  const { lang, setLang } = useLang();

  return (
    <div className={`flex rounded-lg overflow-hidden border border-white/20 text-xs font-semibold ${className}`}>
      {(['es', 'en'] as const).map(l => (
        <button key={l} onClick={() => setLang(l)}
          className={`px-2.5 py-1.5 transition-colors ${
            lang === l
              ? 'bg-white text-green-900'
              : 'text-white/70 hover:text-white hover:bg-white/10'
          }`}>
          {l.toUpperCase()}
        </button>
      ))}
    </div>
  );
}
