'use client';
import Link from 'next/link';
import {
  Activity, BarChart2, TrendingUp, PieChart,
  FlaskConical, Shield, Zap, ChevronRight
} from 'lucide-react';

const modules = [
  { href: '/spc/normalidad',  label: 'Normalidad',        icon: Activity,    color: 'bg-emerald-500', desc: 'AD · SW · KS + Q-Q' },
  { href: '/spc/cartas-xr',   label: 'Cartas X̄-R',       icon: BarChart2,   color: 'bg-green-600',   desc: 'Variables · Reglas WE' },
  { href: '/spc/cartas-pnpu', label: 'Cartas p · np · u', icon: TrendingUp,  color: 'bg-teal-600',    desc: 'Atributos' },
  { href: '/spc/carta-c',     label: 'Carta C + Pareto',  icon: PieChart,    color: 'bg-amber-500',   desc: 'Defectos + 80/20' },
  { href: '/spc/capacidad',   label: 'Capacidad',         icon: FlaskConical, color: 'bg-blue-600',   desc: 'Cp · Cpk · %PNC' },
  { href: '/spc/muestreo',    label: 'Muestreo',          icon: Shield,      color: 'bg-purple-600',  desc: 'MIL-STD-105E · OC' },
  { href: '/spc/mejora',      label: 'Mejora',            icon: Zap,         color: 'bg-rose-500',    desc: 'Potencia · n óptimo' },
];

export default function SPCHome() {
  return (
    <div className="p-4 md:p-8 min-h-full bg-gray-50 dark:bg-gray-950">
      <div className="mb-6 md:mb-8">
        <h1 className="text-xl md:text-2xl font-bold text-gray-900 dark:text-gray-100">Panel de Módulos SPC</h1>
        <p className="text-sm md:text-base text-gray-500 dark:text-gray-400 mt-1">Seleccione un módulo para iniciar el análisis estadístico.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4 md:gap-5">
        {modules.map(({ href, label, icon: Icon, color, desc }) => (
          <Link key={href} href={href}
            className="group flex items-center gap-5 bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-2xl p-5 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-200">
            <div className={`w-12 h-12 rounded-xl ${color} flex items-center justify-center flex-shrink-0`}>
              <Icon className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-gray-900 dark:text-gray-100">{label}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">{desc}</p>
            </div>
            <ChevronRight className="w-5 h-5 text-gray-300 dark:text-gray-600 group-hover:text-gray-500 dark:group-hover:text-gray-400 group-hover:translate-x-0.5 transition-all flex-shrink-0" />
          </Link>
        ))}
      </div>
    </div>
  );
}
