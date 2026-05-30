'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Activity, BarChart2, TrendingUp, PieChart,
  FlaskConical, Shield, Zap, Home, ChevronLeft
} from 'lucide-react';

const nav = [
  { href: '/spc/normalidad',  label: 'Normalidad',     icon: Activity },
  { href: '/spc/cartas-xr',   label: 'Cartas X̄-R',    icon: BarChart2 },
  { href: '/spc/cartas-pnpu', label: 'Cartas p·np·u',  icon: TrendingUp },
  { href: '/spc/carta-c',     label: 'Carta C / Pareto', icon: PieChart },
  { href: '/spc/capacidad',   label: 'Capacidad',       icon: FlaskConical },
  { href: '/spc/muestreo',    label: 'Muestreo',        icon: Shield },
  { href: '/spc/mejora',      label: 'Mejora',          icon: Zap },
];

export default function SPCLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-60 flex-shrink-0 bg-green-900 text-white flex flex-col shadow-xl z-10">
        {/* Logo */}
        <div className="px-5 py-5 border-b border-green-800">
          <div className="flex items-center gap-2.5 mb-4">
            <div className="w-8 h-8 rounded-lg bg-amber-400 flex items-center justify-center">
              <BarChart2 className="w-4.5 h-4.5 text-gray-900" />
            </div>
            <div>
              <p className="font-bold text-sm leading-none">ControlMetrics</p>
              <p className="text-green-400 text-xs mt-0.5">SPC Software</p>
            </div>
          </div>
          <Link href="/"
            className="flex items-center gap-1.5 text-green-400 hover:text-white text-xs transition-colors">
            <ChevronLeft className="w-3.5 h-3.5" /> Inicio
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          <p className="text-green-500 text-xs font-semibold uppercase tracking-wider px-2 mb-3">
            Módulos SPC
          </p>
          {nav.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link key={href} href={href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                  active
                    ? 'bg-white text-green-900 shadow-sm'
                    : 'text-green-200 hover:bg-green-800 hover:text-white'
                }`}>
                <Icon className={`w-4 h-4 flex-shrink-0 ${active ? 'text-green-700' : ''}`} />
                {label}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="px-5 py-4 border-t border-green-800">
          <p className="text-green-500 text-xs">ControlMetrics v1.0.0</p>
          <p className="text-green-600 text-xs mt-0.5">Montgomery (2020)</p>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  );
}
