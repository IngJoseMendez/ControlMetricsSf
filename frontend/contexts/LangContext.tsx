'use client';
import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { type Lang, translations } from '@/lib/i18n';

interface Ctx { lang: Lang; setLang: (l: Lang) => void; t: typeof translations.es; }
const LangContext = createContext<Ctx>({ lang: 'es', setLang: () => {}, t: translations.es as typeof translations.es });

export function LangProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>('es');

  useEffect(() => {
    const saved = localStorage.getItem('cm-lang') as Lang | null;
    if (saved === 'es' || saved === 'en') setLangState(saved);
  }, []);

  const setLang = (l: Lang) => {
    setLangState(l);
    localStorage.setItem('cm-lang', l);
  };

  return (
    <LangContext.Provider value={{ lang, setLang, t: translations[lang] as typeof translations.es }}>
      {children}
    </LangContext.Provider>
  );
}

export const useLang = () => useContext(LangContext);
