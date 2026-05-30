'use client';
import { useState } from 'react';
import { Mail, Lock, User, CheckCircle, XCircle, Eye, EyeOff, BarChart2, Activity, FlaskConical } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useLang } from '@/contexts/LangContext';

type Tab = 'login' | 'register' | 'guest';

function BrandPanel() {
  return (
    <div className="hidden md:flex md:w-[340px] flex-shrink-0 relative flex-col justify-between overflow-hidden"
      style={{ background: 'linear-gradient(145deg, #052e16 0%, #064e3b 50%, #0f3d22 100%)' }}>

      {/* Dot grid overlay */}
      <div className="absolute inset-0 opacity-[0.12]"
        style={{ backgroundImage:'radial-gradient(circle at 1.5px 1.5px,#fff 1px,transparent 0)', backgroundSize:'24px 24px' }} />
      {/* Glow blobs */}
      <div className="absolute top-0 right-0 w-56 h-56 bg-amber-400/10 rounded-full blur-[80px]" />
      <div className="absolute bottom-0 left-0 w-48 h-48 bg-teal-400/10 rounded-full blur-[70px]" />

      <div className="relative z-10 p-8">
        {/* Logo */}
        <div className="flex items-center gap-3 mb-10">
          <img
            src="https://res.cloudinary.com/dxl97cptv/image/upload/v1780110707/WhatsApp_Image_2026-05-29_at_9.45.19_PM_kho7wo.jpg"
            alt="Logo"
            className="w-11 h-11 rounded-xl object-cover ring-2 ring-white/20"
          />
          <div>
            <p className="font-extrabold text-white text-lg leading-none tracking-tight">ControlMetrics</p>
            <p className="text-green-400 text-xs mt-0.5 font-medium">SPC Software</p>
          </div>
        </div>

        <h2 className="text-2xl font-extrabold text-white mb-2 leading-tight tracking-tight">
          Control estadístico<br />a su alcance.
        </h2>
        <p className="text-green-300/70 text-sm leading-relaxed mb-8">
          7 módulos SPC con metodología internacional, gráficas profesionales y análisis completo.
        </p>

        {/* Features */}
        <div className="space-y-3">
          {[
            { icon: Activity,     label: 'Cartas de control X̄-R, p, np, u, c' },
            { icon: FlaskConical, label: 'Capacidad Cp, Cpk y nivel sigma' },
            { icon: BarChart2,    label: 'Historial y plantillas por usuario' },
          ].map(({ icon: Icon, label }) => (
            <div key={label} className="flex items-center gap-3">
              <div className="w-7 h-7 rounded-lg bg-white/10 border border-white/10 flex items-center justify-center flex-shrink-0">
                <Icon className="w-3.5 h-3.5 text-amber-400" />
              </div>
              <span className="text-green-200/80 text-sm leading-snug">{label}</span>
            </div>
          ))}
          <div className="flex items-center gap-3 opacity-50">
            <div className="w-7 h-7 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center flex-shrink-0">
              <XCircle className="w-3.5 h-3.5 text-green-400" />
            </div>
            <span className="text-green-400/80 text-sm">Invitados sin historial ni plantillas</span>
          </div>
        </div>
      </div>

      {/* Mini mockup card at bottom */}
      <div className="relative z-10 mx-6 mb-8 bg-white/8 border border-white/12 rounded-xl p-3 backdrop-blur-sm">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-5 h-5 rounded bg-emerald-500/20 flex items-center justify-center">
            <CheckCircle className="w-3 h-3 text-emerald-400" />
          </div>
          <span className="text-white/50 text-xs">Proceso bajo control</span>
        </div>
        <div className="flex items-end gap-0.5 h-6">
          {[50,65,80,90,85,75,88,92,85,78,70,82].map((h,i) => (
            <div key={i} className="flex-1 rounded-sm bg-emerald-400/50" style={{ height:`${h}%` }} />
          ))}
        </div>
        <div className="flex justify-between mt-1.5">
          <span className="text-white/25 text-xs">Cpk = 1.45</span>
          <span className="text-amber-400/70 text-xs font-semibold">✓ Capaz</span>
        </div>
      </div>
    </div>
  );
}

export function AuthModal() {
  const { signIn, signUp, continueAsGuest } = useAuth();
  const { t } = useLang();
  const [tab, setTab] = useState<Tab>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(''); setSuccess(''); setLoading(true);
    try {
      if (tab === 'login') {
        const err = await signIn(email, password);
        if (err) setError(t.auth.errorInvalid);
      } else {
        const err = await signUp(email, password, name);
        if (err) setError(err);
        else setSuccess('¡Cuenta creada! Revisa tu correo para confirmar.');
      }
    } finally { setLoading(false); }
  };

  return (
    <div className="fixed inset-0 z-50 bg-gray-950/85 backdrop-blur-sm flex items-center justify-center p-3 sm:p-4">
      <div className="w-full max-w-3xl bg-white dark:bg-gray-900 rounded-2xl shadow-2xl overflow-hidden flex flex-col md:flex-row max-h-[calc(100dvh-1.5rem)] md:max-h-[88vh]">

        <BrandPanel />

        {/* ── Form panel ── */}
        <div className="flex-1 flex flex-col overflow-y-auto">

          {/* Mobile header */}
          <div className="md:hidden flex items-center gap-3 px-5 pt-5 pb-4 border-b border-gray-100 dark:border-gray-800 flex-shrink-0">
            <img
              src="https://res.cloudinary.com/dxl97cptv/image/upload/v1780110707/WhatsApp_Image_2026-05-29_at_9.45.19_PM_kho7wo.jpg"
              alt="Logo" className="w-8 h-8 rounded-lg object-cover"
            />
            <div>
              <p className="font-bold text-sm text-gray-900 dark:text-gray-100 leading-none">ControlMetrics</p>
              <p className="text-green-600 dark:text-green-400 text-xs mt-0.5">SPC Software</p>
            </div>
          </div>

          <div className="p-5 md:p-8 flex flex-col flex-1">

            {/* Header */}
            <div className="mb-6">
              <h3 className="text-xl font-extrabold text-gray-900 dark:text-gray-100 tracking-tight">
                {tab === 'login' ? 'Bienvenido de nuevo' : tab === 'register' ? 'Crear cuenta' : 'Acceso de invitado'}
              </h3>
              <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">
                {tab === 'login' ? 'Inicia sesión para acceder a tus datos guardados.' :
                 tab === 'register' ? 'Crea tu cuenta gratuita en segundos.' :
                 'Accede sin cuenta, con funciones limitadas.'}
              </p>
            </div>

            {/* Tabs */}
            <div className="flex rounded-xl bg-gray-100 dark:bg-gray-800 p-1 mb-6 gap-1">
              {(['login', 'register', 'guest'] as Tab[]).map(tKey => (
                <button key={tKey}
                  onClick={() => { setTab(tKey); setError(''); setSuccess(''); setShowPw(false); }}
                  className={`flex-1 py-2 text-xs sm:text-sm font-semibold rounded-lg transition-all duration-200 ${
                    tab === tKey
                      ? 'bg-white dark:bg-gray-700 text-green-800 dark:text-green-300 shadow-sm'
                      : 'text-gray-400 dark:text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
                  }`}>
                  {tKey === 'login' ? t.auth.loginTab : tKey === 'register' ? t.auth.registerTab : t.auth.guestTab}
                </button>
              ))}
            </div>

            {/* Guest panel */}
            {tab === 'guest' && (
              <div className="flex flex-col flex-1 justify-center text-center py-4">
                <div className="w-16 h-16 rounded-2xl bg-amber-50 dark:bg-amber-900/20 border border-amber-100 dark:border-amber-800/30 flex items-center justify-center mx-auto mb-5">
                  <User className="w-8 h-8 text-amber-500" />
                </div>
                <h4 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-2">Continuar como invitado</h4>
                <p className="text-gray-500 dark:text-gray-400 text-sm mb-4 max-w-xs mx-auto leading-relaxed">
                  Accede a todos los módulos de cálculo sin restricciones.
                </p>
                <div className="inline-flex items-start gap-2.5 bg-amber-50 dark:bg-amber-900/15 border border-amber-200 dark:border-amber-800/40 rounded-xl px-4 py-3 mb-6 text-amber-700 dark:text-amber-400 text-sm text-left mx-auto">
                  <XCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                  <span>Sin historial ni plantillas guardadas. Regístrate gratis para habilitarlos.</span>
                </div>
                <button onClick={continueAsGuest}
                  className="w-full bg-gray-900 dark:bg-gray-700 hover:bg-gray-800 dark:hover:bg-gray-600 text-white font-semibold py-3 rounded-xl text-sm transition-colors shadow-sm">
                  {t.auth.guest}
                </button>
                <button onClick={() => setTab('register')}
                  className="mt-3 text-sm text-green-700 dark:text-green-400 hover:underline font-medium">
                  {t.auth.noAccount}
                </button>
              </div>
            )}

            {/* Login / Register */}
            {tab !== 'guest' && (
              <form onSubmit={submit} className="flex flex-col flex-1 space-y-4">

                {tab === 'register' && (
                  <div>
                    <label className="text-xs font-semibold text-gray-600 dark:text-gray-400 block mb-1.5">{t.auth.name}</label>
                    <div className="relative">
                      <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                      <input required type="text" value={name} onChange={e => setName(e.target.value)}
                        className="w-full pl-10 pr-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-xl text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-300 dark:placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-green-600 focus:border-transparent transition-shadow"
                        placeholder="José Mendez" />
                    </div>
                  </div>
                )}

                <div>
                  <label className="text-xs font-semibold text-gray-600 dark:text-gray-400 block mb-1.5">{t.auth.email}</label>
                  <div className="relative">
                    <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                    <input required type="email" value={email} onChange={e => setEmail(e.target.value)}
                      className="w-full pl-10 pr-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-xl text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-300 dark:placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-green-600 focus:border-transparent transition-shadow"
                      placeholder="correo@ejemplo.com" />
                  </div>
                </div>

                <div>
                  <label className="text-xs font-semibold text-gray-600 dark:text-gray-400 block mb-1.5">{t.auth.password}</label>
                  <div className="relative">
                    <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                    <input required type={showPw ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)}
                      className="w-full pl-10 pr-10 py-2.5 border border-gray-200 dark:border-gray-700 rounded-xl text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-300 dark:placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-green-600 focus:border-transparent transition-shadow"
                      placeholder="••••••••" minLength={6} />
                    <button type="button" onClick={() => setShowPw(v => !v)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors p-0.5">
                      {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {error && (
                  <div className="flex items-start gap-2 text-red-600 dark:text-red-400 text-xs bg-red-50 dark:bg-red-900/15 border border-red-200 dark:border-red-800/40 rounded-xl px-3 py-2.5">
                    <XCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                    {error}
                  </div>
                )}
                {success && (
                  <div className="flex items-start gap-2 text-green-700 dark:text-green-400 text-xs bg-green-50 dark:bg-green-900/15 border border-green-200 dark:border-green-800/40 rounded-xl px-3 py-2.5">
                    <CheckCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                    {success}
                  </div>
                )}

                <div className="flex-1" />

                <button type="submit" disabled={loading}
                  className="w-full bg-green-700 hover:bg-green-800 disabled:opacity-60 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl text-sm transition-all duration-200 shadow-sm shadow-green-900/20 hover:shadow-md hover:-translate-y-px active:translate-y-0">
                  {loading
                    ? <span className="inline-flex items-center gap-2"><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />Procesando…</span>
                    : tab === 'login' ? t.auth.login : t.auth.register}
                </button>

                <button type="button" onClick={() => setTab(tab === 'login' ? 'register' : 'login')}
                  className="w-full text-sm text-green-700 dark:text-green-400 hover:underline py-1 font-medium">
                  {tab === 'login' ? t.auth.noAccount : t.auth.hasAccount}
                </button>

                <div className="border-t border-gray-100 dark:border-gray-800 pt-3">
                  <button type="button" onClick={() => setTab('guest')}
                    className="w-full text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 py-1 transition-colors">
                    {t.auth.guest} →
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
