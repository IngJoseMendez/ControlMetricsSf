'use client';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';
import { useLang } from '@/contexts/LangContext';

export function ThemeToggle({ className = '' }: { className?: string }) {
  const { theme, toggle } = useTheme();
  const { t } = useLang();

  return (
    <button onClick={toggle}
      title={theme === 'dark' ? t.ui.lightMode : t.ui.darkMode}
      className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all
        bg-white/10 hover:bg-white/20 text-white ${className}`}>
      {theme === 'dark'
        ? <Sun className="w-4 h-4 text-amber-300" />
        : <Moon className="w-4 h-4 text-blue-200" />}
      <span className="hidden sm:inline">{theme === 'dark' ? t.ui.lightMode : t.ui.darkMode}</span>
    </button>
  );
}
