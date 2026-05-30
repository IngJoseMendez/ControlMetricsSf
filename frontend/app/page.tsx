'use client';
import Link from 'next/link';
import {
  BarChart2, Activity, PieChart, FlaskConical, TrendingUp,
  CheckCircle, ChevronRight, Shield, Zap, Database
} from 'lucide-react';

const modules = [
  {
    icon: Activity,
    title: 'Pruebas de Normalidad',
    desc: 'Anderson-Darling, Shapiro-Wilk y Kolmogorov-Smirnov con histogramas, Q-Q plots y pruebas de independencia.',
    color: 'from-emerald-500 to-teal-600',
    href: '/spc/normalidad',
  },
  {
    icon: BarChart2,
    title: 'Cartas de Control X̄-R',
    desc: 'Monitoreo de variables por subgrupos. Límites de control, reglas de Western Electric y curvas de potencia.',
    color: 'from-green-600 to-emerald-700',
    href: '/spc/cartas-xr',
  },
  {
    icon: TrendingUp,
    title: 'Cartas p · np · u',
    desc: 'Control de atributos para proporciones no conformes, número de defectuosos y defectos por unidad.',
    color: 'from-teal-600 to-cyan-700',
    href: '/spc/cartas-pnpu',
  },
  {
    icon: PieChart,
    title: 'Carta C + Pareto',
    desc: 'Defectos por unidad con carta C de Poisson y diagrama de Pareto 80/20 para priorización.',
    color: 'from-amber-500 to-orange-600',
    href: '/spc/carta-c',
  },
  {
    icon: FlaskConical,
    title: 'Capacidad del Proceso',
    desc: 'Índices Cp, Cpk, Cpu, Cpl. Porcentaje de no conformes y nivel sigma del proceso.',
    color: 'from-blue-600 to-indigo-700',
    href: '/spc/capacidad',
  },
  {
    icon: Shield,
    title: 'Plan de Muestreo',
    desc: 'Norma MIL-STD-105E / ANSI Z1.4. Curva característica de operación (OC) y calidad promedio de salida (AOQ).',
    color: 'from-purple-600 to-violet-700',
    href: '/spc/muestreo',
  },
  {
    icon: Zap,
    title: 'Plan de Mejora',
    desc: 'Sensibilidad del sistema de monitoreo. Tamaño de muestra óptimo para detectar corrimientos en la media.',
    color: 'from-rose-500 to-red-600',
    href: '/spc/mejora',
  },
];

const stats = [
  { value: '7', label: 'Módulos estadísticos' },
  { value: '6+', label: 'Tipos de cartas de control' },
  { value: '3', label: 'Pruebas de normalidad' },
  { value: '100%', label: 'Basado en estándares internacionales' },
];

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen bg-white font-sans">
      {/* ── Navbar ── */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur border-b border-gray-100 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 flex items-center justify-between h-16">
          <div className="flex items-center gap-2.5">
            <img
              src="https://res.cloudinary.com/dxl97cptv/image/upload/v1780110707/WhatsApp_Image_2026-05-29_at_9.45.19_PM_kho7wo.jpg"
              alt="Logo"
              className="w-9 h-9 rounded-lg object-cover shadow-sm"
            />
            <span className="font-bold text-lg text-gray-900">ControlMetrics</span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm text-gray-600">
            <a href="#modulos" className="hover:text-green-700 transition-colors">Módulos</a>
            <a href="#como-funciona" className="hover:text-green-700 transition-colors">Cómo funciona</a>
            <a href="#estandares" className="hover:text-green-700 transition-colors">Estándares</a>
          </div>
          <Link
            href="/spc"
            className="bg-green-700 text-white px-5 py-2 rounded-lg text-sm font-semibold hover:bg-green-800 transition-colors flex items-center gap-1.5"
          >
            Abrir App <ChevronRight className="w-4 h-4" />
          </Link>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="relative pt-28 pb-24 overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-green-950 via-green-900 to-teal-900" />
        <div className="absolute inset-0 opacity-10"
          style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, #ffffff 1px, transparent 0)', backgroundSize: '32px 32px' }} />
        {/* Decorative blobs */}
        <div className="absolute top-20 right-10 w-96 h-96 bg-amber-400/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-10 w-72 h-72 bg-teal-400/10 rounded-full blur-3xl" />

        <div className="relative max-w-7xl mx-auto px-6 text-center">
          <div className="inline-flex items-center gap-2 bg-white/10 border border-white/20 text-white/90 text-sm px-4 py-1.5 rounded-full mb-8 backdrop-blur-sm">
            <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
            Control Estadístico de Procesos · Montgomery (2020)
          </div>

          <h1 className="text-5xl md:text-6xl lg:text-7xl font-extrabold text-white leading-tight tracking-tight mb-6">
            Calidad de proceso,
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-300 to-amber-500">
              decisiones con datos.
            </span>
          </h1>

          <p className="max-w-2xl mx-auto text-lg md:text-xl text-white/70 leading-relaxed mb-10">
            Plataforma SPC completa para análisis estadístico de procesos industriales.
            Cartas de control, capacidad, muestreo y más — todo en un solo lugar,
            directamente desde el navegador.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/spc"
              className="group inline-flex items-center gap-2 bg-amber-400 hover:bg-amber-300 text-gray-900 font-bold px-8 py-4 rounded-xl text-lg transition-all duration-200 shadow-lg shadow-amber-400/25 hover:shadow-amber-400/40 hover:-translate-y-0.5"
            >
              Ingresar al software
              <ChevronRight className="w-5 h-5 group-hover:translate-x-0.5 transition-transform" />
            </Link>
            <a
              href="#modulos"
              className="inline-flex items-center gap-2 text-white/80 hover:text-white font-medium px-6 py-4 rounded-xl border border-white/20 hover:border-white/40 transition-all duration-200 backdrop-blur-sm"
            >
              Ver módulos
            </a>
          </div>

          {/* Stats strip */}
          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-6">
            {stats.map((s) => (
              <div key={s.label} className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-sm">
                <div className="text-3xl font-extrabold text-amber-400 mb-1">{s.value}</div>
                <div className="text-sm text-white/60">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Módulos ── */}
      <section id="modulos" className="py-24 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-14">
            <h2 className="text-3xl md:text-4xl font-extrabold text-gray-900 mb-4">
              Módulos del software
            </h2>
            <p className="text-lg text-gray-500 max-w-2xl mx-auto">
              Cada módulo implementa metodología SPC estándar con base en
              Montgomery (2020), MIL-STD-105E y ANSI/ASQ Z1.4.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
            {modules.map((mod) => {
              const Icon = mod.icon;
              return (
                <Link
                  key={mod.href}
                  href={mod.href}
                  className="group flex flex-col bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all duration-200 overflow-hidden"
                >
                  <div className={`bg-gradient-to-br ${mod.color} p-5 flex items-center gap-3`}>
                    <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
                      <Icon className="w-5 h-5 text-white" />
                    </div>
                    <h3 className="font-bold text-white text-sm leading-tight">{mod.title}</h3>
                  </div>
                  <div className="p-5 flex-1">
                    <p className="text-sm text-gray-600 leading-relaxed">{mod.desc}</p>
                  </div>
                  <div className="px-5 pb-5">
                    <span className="inline-flex items-center gap-1 text-xs font-semibold text-green-700 group-hover:gap-2 transition-all">
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
      <section id="como-funciona" className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-14">
            <h2 className="text-3xl md:text-4xl font-extrabold text-gray-900 mb-4">
              Cómo funciona
            </h2>
            <p className="text-lg text-gray-500 max-w-xl mx-auto">
              Tres pasos para obtener análisis estadístico completo.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                step: '01',
                title: 'Ingrese sus datos',
                desc: 'Introduzca valores directamente en el formulario o cargue desde un archivo Excel con el formato predefinido.',
                icon: Database,
                color: 'bg-green-50 border-green-200',
                iconColor: 'text-green-700',
              },
              {
                step: '02',
                title: 'Calcule en un clic',
                desc: 'El motor estadístico en Python procesa los datos aplicando metodología SPC estándar (Montgomery 2020).',
                icon: Zap,
                color: 'bg-amber-50 border-amber-200',
                iconColor: 'text-amber-700',
              },
              {
                step: '03',
                title: 'Interprete los resultados',
                desc: 'Obtenga gráficas profesionales, límites de control, índices de capacidad y recomendaciones de mejora.',
                icon: CheckCircle,
                color: 'bg-blue-50 border-blue-200',
                iconColor: 'text-blue-700',
              },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.step} className={`rounded-2xl border p-8 ${item.color}`}>
                  <div className="flex items-center gap-4 mb-5">
                    <span className="text-4xl font-black text-gray-200">{item.step}</span>
                    <div className={`w-10 h-10 rounded-xl bg-white border border-gray-100 shadow-sm flex items-center justify-center ${item.iconColor}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                  </div>
                  <h3 className="text-lg font-bold text-gray-900 mb-2">{item.title}</h3>
                  <p className="text-sm text-gray-600 leading-relaxed">{item.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── Estándares ── */}
      <section id="estandares" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-extrabold text-gray-900 mb-4">Estándares y referencias</h2>
          </div>
          <div className="flex flex-wrap justify-center gap-4">
            {[
              'Montgomery, D.C. (2020). Introduction to SPC',
              'MIL-STD-105E / ANSI/ASQ Z1.4',
              'ISO 7870 – Cartas de control',
              'AIAG MSA Reference Manual',
              'Nelson Rules / Western Electric Handbook',
            ].map((std) => (
              <div key={std}
                className="flex items-center gap-2 bg-white border border-gray-200 rounded-full px-5 py-2.5 text-sm text-gray-700 shadow-sm">
                <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0" />
                {std}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA final ── */}
      <section className="py-24 bg-gradient-to-br from-green-950 via-green-900 to-teal-900 relative overflow-hidden">
        <div className="absolute inset-0 opacity-10"
          style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, #ffffff 1px, transparent 0)', backgroundSize: '32px 32px' }} />
        <div className="relative max-w-3xl mx-auto px-6 text-center">
          <h2 className="text-4xl font-extrabold text-white mb-4">
            Listo para controlar su proceso
          </h2>
          <p className="text-white/70 text-lg mb-10">
            Acceda ahora a todos los módulos SPC — sin instalación, directamente en el navegador.
          </p>
          <Link
            href="/spc"
            className="inline-flex items-center gap-2 bg-amber-400 hover:bg-amber-300 text-gray-900 font-bold px-10 py-4 rounded-xl text-lg transition-all duration-200 shadow-lg shadow-amber-400/25"
          >
            Ingresar al software <ChevronRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="bg-gray-900 text-gray-400 py-8 text-center text-sm">
        <p className="mb-1">ControlMetrics SPC v1.0.0 · Software de Control Estadístico de Procesos</p>
        <p>Desarrollado con Python · FastAPI · Next.js · Metodología Montgomery (2020)</p>
      </footer>
    </div>
  );
}
