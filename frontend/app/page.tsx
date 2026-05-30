'use client';
import Link from 'next/link';
import {
  BarChart2, Activity, PieChart, FlaskConical, TrendingUp,
  CheckCircle, ChevronRight, Shield, Zap, Database, ArrowRight,
} from 'lucide-react';

const modules = [
  { icon: Activity,    title: 'Pruebas de Normalidad',   desc: 'Anderson-Darling, Shapiro-Wilk y Kolmogorov-Smirnov con histogramas y Q-Q plots.',      color: 'bg-emerald-500', ring: 'ring-emerald-200', href: '/spc/normalidad' },
  { icon: BarChart2,   title: 'Cartas de Control X̄-R',  desc: 'Monitoreo de variables por subgrupos con reglas de Western Electric y curvas de potencia.', color: 'bg-green-600',   ring: 'ring-green-200',   href: '/spc/cartas-xr' },
  { icon: TrendingUp,  title: 'Cartas p · np · u',       desc: 'Control estadístico de atributos para proporciones no conformes y defectos por unidad.',    color: 'bg-teal-600',    ring: 'ring-teal-200',    href: '/spc/cartas-pnpu' },
  { icon: PieChart,    title: 'Carta C + Pareto',         desc: 'Defectos por unidad con distribución de Poisson y diagrama de Pareto 80/20.',               color: 'bg-amber-500',   ring: 'ring-amber-200',   href: '/spc/carta-c' },
  { icon: FlaskConical,title: 'Capacidad del Proceso',    desc: 'Índices Cp, Cpk, Cpu, Cpl, nivel sigma y porcentaje de no conformes del proceso.',          color: 'bg-blue-600',    ring: 'ring-blue-200',    href: '/spc/capacidad' },
  { icon: Shield,      title: 'Plan de Muestreo',         desc: 'MIL-STD-105E / ANSI Z1.4. Curva característica de operación (OC) y AOQL.',                 color: 'bg-purple-600',  ring: 'ring-purple-200',  href: '/spc/muestreo' },
  { icon: Zap,         title: 'Plan de Mejora',           desc: 'Sensibilidad del sistema, tamaño de muestra óptimo y curvas de potencia estadística.',       color: 'bg-rose-500',    ring: 'ring-rose-200',    href: '/spc/mejora' },
];

const steps = [
  { n: '01', icon: Database,    title: 'Ingrese sus datos',        desc: 'Introduzca valores directamente o cargue un archivo Excel con el formato predefinido.' },
  { n: '02', icon: Zap,         title: 'Calcule en un clic',       desc: 'El motor estadístico en Python procesa sus datos aplicando metodología SPC estándar.' },
  { n: '03', icon: CheckCircle, title: 'Interprete los resultados', desc: 'Gráficas profesionales, límites de control, índices de capacidad y recomendaciones.' },
];

function DashboardMockup() {
  return (
    <div className="relative w-full max-w-md mx-auto lg:mx-0 lg:ml-auto">
      {/* Main window */}
      <div className="bg-white/8 backdrop-blur-xl border border-white/15 rounded-2xl overflow-hidden shadow-[0_32px_80px_rgba(0,0,0,0.4)]">
        {/* Title bar */}
        <div className="flex items-center gap-1.5 px-4 py-3 bg-white/5 border-b border-white/10">
          <span className="w-2.5 h-2.5 rounded-full bg-red-400/60" />
          <span className="w-2.5 h-2.5 rounded-full bg-amber-400/60" />
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400/60" />
          <span className="ml-3 text-white/40 text-xs font-mono tracking-tight">Capacidad del Proceso</span>
        </div>
        <div className="p-4 space-y-3">
          {/* KPIs */}
          <div className="grid grid-cols-4 gap-2">
            {[['Cp','1.67'],['Cpk','1.45'],['σ nivel','4.8σ'],['%NC','0.003%']].map(([l,v]) => (
              <div key={l} className="bg-white/6 rounded-lg px-2 py-2 text-center">
                <p className="text-white/40 text-xs leading-none mb-1">{l}</p>
                <p className="text-emerald-400 font-bold text-sm leading-none">{v}</p>
              </div>
            ))}
          </div>
          {/* Distribution chart */}
          <div className="bg-white/5 rounded-xl p-3">
            <div className="flex items-end justify-center gap-[3px] h-14">
              {[6,14,30,55,78,92,88,68,42,20,9,3].map((h,i) => (
                <div key={i} className="flex-1 rounded-sm transition-all"
                  style={{ height:`${h}%`, background: (i>=2&&i<=9) ? 'rgba(52,211,153,0.55)' : 'rgba(251,191,36,0.5)' }} />
              ))}
            </div>
            <div className="flex justify-between mt-2">
              <span className="text-white/30 text-xs">LCI: 3.150 lb</span>
              <span className="text-emerald-400/80 text-xs font-semibold">μ = 3.225 lb</span>
              <span className="text-white/30 text-xs">LSE: 3.300 lb</span>
            </div>
          </div>
          {/* Status */}
          <div className="flex items-center justify-between">
            <div className="inline-flex items-center gap-1.5 bg-emerald-500/15 border border-emerald-500/20 rounded-full px-3 py-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-emerald-400 text-xs font-medium">Proceso Capaz</span>
            </div>
            <span className="text-white/30 text-xs">n = 125 muestras</span>
          </div>
        </div>
      </div>

      {/* Floating cards */}
      <div className="absolute -right-4 top-6 bg-white/10 backdrop-blur-md border border-white/20 rounded-xl px-3 py-2.5 shadow-xl hidden sm:block">
        <p className="text-white/50 text-xs leading-none mb-1">Anderson-Darling</p>
        <p className="text-emerald-400 font-bold text-sm leading-none">✓ Normal</p>
        <p className="text-white/30 text-xs mt-0.5">p-valor = 0.482</p>
      </div>
      <div className="absolute -left-4 bottom-10 bg-white/10 backdrop-blur-md border border-white/20 rounded-xl px-3 py-2.5 shadow-xl hidden sm:block">
        <p className="text-white/50 text-xs leading-none mb-1">Puntos OOC</p>
        <p className="text-emerald-400 font-bold text-sm leading-none">0 / 25</p>
        <p className="text-white/30 text-xs mt-0.5">Bajo control</p>
      </div>
    </div>
  );
}

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen bg-white font-sans antialiased">

      {/* ── Navbar ── */}
      <nav className="fixed top-0 inset-x-0 z-50 bg-white/90 backdrop-blur-md border-b border-gray-100/80 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 flex items-center justify-between h-16">
          <div className="flex items-center gap-2.5">
            <img src="https://res.cloudinary.com/dxl97cptv/image/upload/v1780110707/WhatsApp_Image_2026-05-29_at_9.45.19_PM_kho7wo.jpg"
              alt="Logo" className="w-8 h-8 rounded-lg object-cover shadow-sm" />
            <span className="font-bold text-lg text-gray-900 tracking-tight">ControlMetrics</span>
          </div>
          <div className="hidden md:flex items-center gap-7 text-sm text-gray-500 font-medium">
            <a href="#modulos" className="hover:text-gray-900 transition-colors">Módulos</a>
            <a href="#como-funciona" className="hover:text-gray-900 transition-colors">Cómo funciona</a>
            <a href="#estandares" className="hover:text-gray-900 transition-colors">Estándares</a>
          </div>
          <Link href="/spc"
            className="bg-green-700 text-white px-4 sm:px-5 py-2 rounded-lg text-sm font-semibold hover:bg-green-800 transition-all duration-200 flex items-center gap-1.5 shadow-sm shadow-green-900/20 hover:shadow-md hover:shadow-green-900/20 hover:-translate-y-px">
            Abrir App <ChevronRight className="w-4 h-4" />
          </Link>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="relative pt-24 sm:pt-28 pb-20 sm:pb-28 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-green-950 via-[#0f3d22] to-[#0c2e30]" />
        <div className="absolute inset-0 opacity-[0.07]"
          style={{ backgroundImage:'radial-gradient(circle at 1.5px 1.5px,#fff 1px,transparent 0)', backgroundSize:'28px 28px' }} />
        <div className="absolute -top-20 right-0 w-[600px] h-[600px] bg-amber-400/8 rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-teal-400/8 rounded-full blur-[100px] pointer-events-none" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex flex-col lg:flex-row items-center gap-12 lg:gap-16">

            {/* Copy */}
            <div className="flex-1 text-center lg:text-left">
              <div className="inline-flex items-center gap-2 bg-white/10 border border-white/15 text-white/80 text-xs font-medium px-4 py-1.5 rounded-full mb-7 backdrop-blur-sm">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
                Control Estadístico de Procesos · Metodología Montgomery (2020)
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-white leading-[1.1] tracking-tight mb-5">
                Decisiones de calidad{' '}
                <span className="relative whitespace-nowrap">
                  <span className="relative text-transparent bg-clip-text bg-gradient-to-r from-amber-300 via-amber-400 to-yellow-300">
                    basadas en datos.
                  </span>
                </span>
              </h1>

              <p className="text-base sm:text-lg text-white/60 leading-relaxed mb-8 max-w-xl mx-auto lg:mx-0">
                Plataforma SPC completa con 7 módulos estadísticos. Cartas de control,
                capacidad de proceso, muestreo MIL-STD-105E y más — directo desde el navegador.
              </p>

              <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-3">
                <Link href="/spc"
                  className="group w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-amber-400 hover:bg-amber-300 text-gray-900 font-bold px-7 py-3.5 rounded-xl text-base transition-all duration-200 shadow-lg shadow-amber-500/25 hover:-translate-y-0.5">
                  Ingresar al software
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                </Link>
                <a href="#modulos"
                  className="w-full sm:w-auto inline-flex items-center justify-center gap-2 text-white/70 hover:text-white font-medium px-6 py-3.5 rounded-xl border border-white/15 hover:border-white/30 transition-all duration-200 backdrop-blur-sm text-sm">
                  Ver módulos <ChevronRight className="w-4 h-4" />
                </a>
              </div>

              {/* Trust strip */}
              <div className="mt-8 flex flex-wrap items-center justify-center lg:justify-start gap-x-5 gap-y-2">
                {['7 módulos SPC', 'Basado en Montgomery (2020)', 'Gratis'].map(t => (
                  <div key={t} className="flex items-center gap-1.5 text-white/40 text-xs">
                    <CheckCircle className="w-3.5 h-3.5 text-emerald-500/70 flex-shrink-0" />
                    {t}
                  </div>
                ))}
              </div>
            </div>

            {/* Dashboard visual */}
            <div className="flex-1 w-full lg:max-w-[460px]">
              <DashboardMockup />
            </div>
          </div>

          {/* Stats */}
          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
            {[
              { value: '7', label: 'Módulos estadísticos' },
              { value: '6+', label: 'Tipos de cartas de control' },
              { value: '3', label: 'Pruebas de normalidad' },
              { value: '100%', label: 'Estándares internacionales' },
            ].map(s => (
              <div key={s.label} className="bg-white/5 border border-white/8 rounded-2xl p-4 sm:p-5 text-center backdrop-blur-sm hover:bg-white/8 transition-colors">
                <div className="text-2xl sm:text-3xl font-extrabold text-amber-400 mb-1">{s.value}</div>
                <div className="text-xs text-white/50 leading-tight">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Módulos ── */}
      <section id="modulos" className="py-20 sm:py-28 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-12 sm:mb-16">
            <p className="text-green-700 font-semibold text-sm uppercase tracking-widest mb-3">Módulos</p>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-gray-900 tracking-tight mb-4">
              Todo lo que necesita en un solo lugar
            </h2>
            <p className="text-gray-500 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed">
              Cada módulo implementa metodología SPC estándar basada en Montgomery (2020),
              MIL-STD-105E y ANSI/ASQ Z1.4.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-5">
            {modules.map((mod) => {
              const Icon = mod.icon;
              return (
                <Link key={mod.href} href={mod.href}
                  className="group flex flex-col bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-xl hover:-translate-y-1.5 transition-all duration-300 overflow-hidden">
                  <div className="p-5 flex-1">
                    <div className={`w-11 h-11 rounded-xl ${mod.color} flex items-center justify-center mb-4 shadow-sm ring-4 ${mod.ring}/30 group-hover:scale-110 transition-transform duration-300`}>
                      <Icon className="w-5 h-5 text-white" />
                    </div>
                    <h3 className="font-bold text-gray-900 text-sm leading-snug mb-2">{mod.title}</h3>
                    <p className="text-sm text-gray-500 leading-relaxed">{mod.desc}</p>
                  </div>
                  <div className="px-5 pb-4">
                    <span className="inline-flex items-center gap-1 text-xs font-semibold text-green-700 group-hover:gap-2 transition-all duration-200">
                      Abrir módulo <ChevronRight className="w-3.5 h-3.5" />
                    </span>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── Cómo funciona ── */}
      <section id="como-funciona" className="py-20 sm:py-28 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-12 sm:mb-16">
            <p className="text-green-700 font-semibold text-sm uppercase tracking-widest mb-3">Flujo de trabajo</p>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-gray-900 tracking-tight mb-4">
              Tres pasos hacia el análisis
            </h2>
            <p className="text-gray-500 text-base max-w-xl mx-auto">
              Del dato al resultado en segundos, sin instalación ni configuración.
            </p>
          </div>

          <div className="relative grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8">
            {/* Connector line — desktop only */}
            <div className="hidden md:block absolute top-12 left-[calc(16.67%+1.5rem)] right-[calc(16.67%+1.5rem)] h-px bg-gradient-to-r from-green-200 via-green-300 to-green-200" />

            {steps.map((s) => {
              const Icon = s.icon;
              return (
                <div key={s.n} className="relative flex flex-col items-center md:items-start text-center md:text-left bg-white rounded-2xl border border-gray-100 shadow-sm p-7 hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
                  <div className="relative mb-5">
                    <div className="w-12 h-12 rounded-2xl bg-green-700 flex items-center justify-center shadow-md shadow-green-900/20 z-10 relative">
                      <Icon className="w-5 h-5 text-white" />
                    </div>
                    <span className="absolute -top-2 -right-2 w-6 h-6 bg-amber-400 rounded-full text-xs font-black text-gray-900 flex items-center justify-center shadow-sm z-20">
                      {s.n.slice(1)}
                    </span>
                  </div>
                  <h3 className="text-lg font-bold text-gray-900 mb-2">{s.title}</h3>
                  <p className="text-sm text-gray-500 leading-relaxed">{s.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── Estándares ── */}
      <section id="estandares" className="py-16 sm:py-20 bg-gray-50 border-t border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <p className="text-center text-xs font-semibold uppercase tracking-widest text-gray-400 mb-8">
            Implementado bajo estándares y referencias internacionales
          </p>
          <div className="flex flex-wrap justify-center gap-3">
            {[
              'Montgomery, D.C. (2020). Introduction to SPC',
              'MIL-STD-105E / ANSI/ASQ Z1.4',
              'ISO 7870 – Cartas de control',
              'AIAG MSA Reference Manual',
              'Nelson Rules / Western Electric Handbook',
            ].map(std => (
              <div key={std}
                className="flex items-center gap-2 bg-white border border-gray-200 rounded-full px-4 sm:px-5 py-2 text-xs sm:text-sm text-gray-600 shadow-sm hover:border-green-300 hover:text-green-800 transition-colors">
                <CheckCircle className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-green-600 flex-shrink-0" />
                {std}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA final ── */}
      <section className="relative py-24 sm:py-32 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-green-950 via-[#0f3d22] to-[#0c2e30]" />
        <div className="absolute inset-0 opacity-[0.06]"
          style={{ backgroundImage:'radial-gradient(circle at 1.5px 1.5px,#fff 1px,transparent 0)', backgroundSize:'28px 28px' }} />
        <div className="absolute top-0 right-1/4 w-96 h-96 bg-amber-400/8 rounded-full blur-[100px] pointer-events-none" />

        <div className="relative max-w-3xl mx-auto px-4 sm:px-6 text-center">
          <div className="inline-flex items-center gap-2 bg-white/10 border border-white/15 text-white/70 text-xs font-medium px-4 py-1.5 rounded-full mb-8 backdrop-blur-sm">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            Sin instalación · Sin configuración · Gratis
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white mb-5 tracking-tight leading-tight">
            Listo para controlar<br className="hidden sm:block" /> su proceso
          </h2>
          <p className="text-white/60 text-base sm:text-lg mb-10 max-w-xl mx-auto leading-relaxed">
            Acceda ahora a todos los módulos SPC sin instalación, directamente desde su navegador.
          </p>
          <Link href="/spc"
            className="group inline-flex items-center gap-2.5 bg-amber-400 hover:bg-amber-300 text-gray-900 font-bold px-8 sm:px-10 py-4 rounded-xl text-base sm:text-lg transition-all duration-200 shadow-xl shadow-amber-500/20 hover:-translate-y-0.5">
            Ingresar al software
            <ArrowRight className="w-5 h-5 group-hover:translate-x-0.5 transition-transform" />
          </Link>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="bg-gray-950 text-gray-500 py-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2.5">
              <img src="https://res.cloudinary.com/dxl97cptv/image/upload/v1780110707/WhatsApp_Image_2026-05-29_at_9.45.19_PM_kho7wo.jpg"
                alt="Logo" className="w-7 h-7 rounded-md object-cover opacity-80" />
              <span className="text-gray-400 font-semibold text-sm">ControlMetrics SPC</span>
            </div>
            <div className="flex items-center gap-5 text-xs">
              <a href="#modulos" className="hover:text-gray-300 transition-colors">Módulos</a>
              <a href="#como-funciona" className="hover:text-gray-300 transition-colors">Cómo funciona</a>
              <a href="#estandares" className="hover:text-gray-300 transition-colors">Estándares</a>
            </div>
            <p className="text-xs text-gray-600 text-center sm:text-right">
              v1.0.0 · Python · FastAPI · Next.js
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
