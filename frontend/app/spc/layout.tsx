'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import {
  Activity, BarChart2, TrendingUp, PieChart,
  FlaskConical, Shield, Zap, ChevronLeft,
  LogOut, User, Clock, Trash2, ChevronDown, ChevronUp
} from 'lucide-react';

import { useAuth } from '@/contexts/AuthContext';
import { useLang } from '@/contexts/LangContext';
import { useHistory } from '@/hooks/useHistory';
import { AuthModal } from '@/components/auth/AuthModal';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { GuestBanner } from '@/components/auth/GuestBanner';

const MODULE_KEYS = {
  '/spc/normalidad':  'normalidad',
  '/spc/cartas-xr':  'cartasXr',
  '/spc/cartas-pnpu':'cartasPnpu',
  '/spc/carta-c':    'cartaC',
  '/spc/capacidad':  'capacidad',
  '/spc/muestreo':   'muestreo',
  '/spc/mejora':     'mejora',
} as const;

const ICONS = [Activity, BarChart2, TrendingUp, PieChart, FlaskConical, Shield, Zap];

function formatTime(iso: string) {
  const d = new Date(iso);
  const diff = Date.now() - d.getTime();
  if (diff < 60000) return 'ahora';
  if (diff < 3600000) return `${Math.floor(diff / 60000)} min`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} h`;
  return d.toLocaleDateString('es', { day: '2-digit', month: 'short' });
}

function SummaryBadge({ summary }: { summary: Record<string, unknown> | null }) {
  if (!summary) return null;
  const entry = Object.entries(summary)[0];
  if (!entry) return null;
  const [k, v] = entry;
  return (
    <span className="text-green-300 text-xs truncate">
      {k}: <strong>{String(v)}</strong>
    </span>
  );
}

export default function SPCLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, mode, signOut } = useAuth();
  const { t } = useLang();
  const { history, clear } = useHistory();
  const [histOpen, setHistOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const navItems = Object.entries(MODULE_KEYS).map(([href, key], i) => ({
    href,
    label: t.nav[key as keyof typeof t.nav],
    icon: ICONS[i],
  }));

  if (mode === 'loading') {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-950">
        <div className="w-8 h-8 border-4 border-green-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (mode === 'unauthenticated') {
    return <AuthModal />;
  }

  return (
    <div className="flex h-screen bg-gray-950 overflow-hidden">
      {/* ── Sidebar ── */}
      <aside className="w-60 flex-shrink-0 bg-green-900 dark:bg-gray-950 text-white flex flex-col shadow-xl z-10">
        {/* Logo + controls */}
        <div className="px-4 py-4 border-b border-green-800 dark:border-gray-800">
          <div className="flex items-center gap-2.5 mb-3">
            <img
              src="https://res.cloudinary.com/dxl97cptv/image/upload/v1780110707/WhatsApp_Image_2026-05-29_at_9.45.19_PM_kho7wo.jpg"
              alt="Logo"
              className="w-8 h-8 rounded-lg object-cover flex-shrink-0"
            />
            <div className="min-w-0">
              <p className="font-bold text-sm leading-none">ControlMetrics</p>
              <p className="text-green-400 text-xs mt-0.5">SPC Software</p>
            </div>
          </div>

          {/* Theme toggle */}
          <div className="flex items-center">
            <ThemeToggle className="flex-1 justify-center" />
          </div>

          <Link href="/"
            className="mt-2 flex items-center gap-1.5 text-green-400 hover:text-white text-xs transition-colors">
            <ChevronLeft className="w-3.5 h-3.5" /> {t.nav.home}
          </Link>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-3 space-y-0.5 overflow-y-auto">
          <p className="text-green-500 dark:text-gray-500 text-xs font-semibold uppercase tracking-wider px-2 mb-2">
            {t.nav.modules}
          </p>
          {navItems.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link key={href} href={href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                  active
                    ? 'bg-white text-green-900 shadow-sm'
                    : 'text-green-200 hover:bg-green-800 dark:hover:bg-gray-800 hover:text-white'
                }`}>
                <Icon className={`w-4 h-4 flex-shrink-0 ${active ? 'text-green-700' : ''}`} />
                <span className="truncate">{label}</span>
              </Link>
            );
          })}
        </nav>

        {/* History section */}
        <div className="px-3 py-2 border-t border-green-800 dark:border-gray-800">
          <button onClick={() => setHistOpen(o => !o)}
            className="w-full flex items-center justify-between text-xs font-semibold text-green-400 dark:text-gray-400 hover:text-white py-1.5 transition-colors">
            <div className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5" />
              {t.history.title}
              {mode === 'user' && history.length > 0 && (
                <span className="bg-green-700 dark:bg-gray-700 text-white px-1.5 rounded-full text-xs">
                  {history.length}
                </span>
              )}
            </div>
            {histOpen ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>

          {histOpen && (
            <div className="mt-1.5 space-y-1 max-h-44 overflow-y-auto">
              {mode !== 'user' ? (
                <GuestBanner type="history" />
              ) : history.length === 0 ? (
                <p className="text-xs text-green-600 dark:text-gray-500 text-center py-2">{t.history.none}</p>
              ) : (
                <>
                  {history.map(h => (
                    <div key={h.id} className="flex items-start gap-2 px-2 py-1.5 rounded-lg bg-green-800/50 dark:bg-gray-800/50">
                      <div className="flex-1 min-w-0">
                        <p className="text-xs text-white font-medium truncate capitalize">{h.module}</p>
                        <SummaryBadge summary={h.summary} />
                        <p className="text-xs text-green-500 dark:text-gray-500">{formatTime(h.created_at)}</p>
                      </div>
                    </div>
                  ))}
                  <button onClick={clear}
                    className="flex items-center gap-1 text-xs text-red-400 hover:text-red-300 px-2 py-1 transition-colors">
                    <Trash2 className="w-3 h-3" /> {t.history.clear}
                  </button>
                </>
              )}
            </div>
          )}
        </div>

        {/* User menu */}
        <div className="px-3 py-3 border-t border-green-800 dark:border-gray-800">
          <button onClick={() => setUserMenuOpen(o => !o)}
            className="w-full flex items-center gap-2 hover:bg-green-800 dark:hover:bg-gray-800 rounded-lg px-2 py-2 transition-colors">
            <div className="w-7 h-7 rounded-full bg-amber-400 flex items-center justify-center flex-shrink-0">
              <User className="w-4 h-4 text-gray-900" />
            </div>
            <div className="flex-1 min-w-0 text-left">
              {mode === 'user' ? (
                <>
                  <p className="text-xs font-medium text-white truncate">
                    {user?.user_metadata?.full_name ?? user?.email?.split('@')[0]}
                  </p>
                  <p className="text-xs text-green-400 dark:text-gray-400 truncate">{user?.email}</p>
                </>
              ) : (
                <p className="text-sm text-green-300 dark:text-gray-400">{t.auth.guestMode}</p>
              )}
            </div>
            <ChevronDown className={`w-3.5 h-3.5 text-green-400 transition-transform ${userMenuOpen ? 'rotate-180' : ''}`} />
          </button>

          {userMenuOpen && (
            <div className="mt-1 bg-green-800 dark:bg-gray-800 rounded-lg overflow-hidden">
              {mode === 'user' ? (
                <button onClick={() => { signOut(); setUserMenuOpen(false); }}
                  className="w-full flex items-center gap-2 px-3 py-2.5 text-sm text-red-300 hover:bg-green-700 dark:hover:bg-gray-700 transition-colors">
                  <LogOut className="w-4 h-4" /> {t.auth.logout}
                </button>
              ) : (
                <button onClick={() => { window.location.reload(); }}
                  className="w-full flex items-center gap-2 px-3 py-2.5 text-sm text-green-200 hover:bg-green-700 dark:hover:bg-gray-700 transition-colors">
                  <User className="w-4 h-4" /> {t.auth.loginTab}
                </button>
              )}
            </div>
          )}
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto dark:bg-gray-950">
        {children}
      </main>
    </div>
  );
}
