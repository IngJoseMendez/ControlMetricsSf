'use client';
import { useState } from 'react';
import { Mail, Lock, User, CheckCircle, XCircle } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useLang } from '@/contexts/LangContext';

type Tab = 'login' | 'register' | 'guest';

export function AuthModal() {
  const { signIn, signUp, continueAsGuest } = useAuth();
  const { t } = useLang();
  const [tab, setTab] = useState<Tab>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
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
    <div className="fixed inset-0 z-50 bg-gray-950/80 backdrop-blur-sm flex items-center justify-center p-3 sm:p-4">
      <div className="w-full max-w-4xl bg-white dark:bg-gray-900 rounded-2xl shadow-2xl overflow-hidden flex flex-col md:flex-row max-h-[calc(100dvh-1.5rem)] md:max-h-[90vh]">

        {/* ── Left brand panel — desktop only ── */}
        <div className="hidden md:flex md:w-80 bg-green-900 text-white p-8 flex-col justify-between flex-shrink-0">
          <div>
            <div className="flex items-center gap-3 mb-8">
              <img
                src="https://res.cloudinary.com/dxl97cptv/image/upload/v1780110707/WhatsApp_Image_2026-05-29_at_9.45.19_PM_kho7wo.jpg"
                alt="Logo"
                className="w-10 h-10 rounded-xl object-cover"
              />
              <div>
                <p className="font-bold text-lg leading-none">ControlMetrics</p>
                <p className="text-green-400 text-xs mt-0.5">SPC Software</p>
              </div>
            </div>

            <h2 className="text-2xl font-bold mb-3 leading-tight">{t.auth.welcome}</h2>
            <p className="text-green-300 text-sm leading-relaxed">{t.auth.subtitle}</p>

            <div className="mt-8 space-y-3">
              {[t.auth.guestFeature1, t.auth.guestFeature2].map(f => (
                <div key={f} className="flex items-start gap-2.5">
                  <CheckCircle className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" />
                  <span className="text-green-200 text-sm">{f}</span>
                </div>
              ))}
              <div className="flex items-start gap-2.5 opacity-60">
                <XCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                <span className="text-green-300 text-sm">{t.auth.guestLimited}</span>
              </div>
            </div>
          </div>

          <p className="text-green-600 text-xs mt-8">Montgomery (2020) · MIL-STD-105E · ISO 7870</p>
        </div>

        {/* ── Right form panel ── */}
        <div className="flex-1 flex flex-col overflow-y-auto">

          {/* Mobile header — logo + name */}
          <div className="md:hidden flex items-center gap-3 px-5 pt-5 pb-3 border-b border-gray-100 dark:border-gray-800 flex-shrink-0">
            <img
              src="https://res.cloudinary.com/dxl97cptv/image/upload/v1780110707/WhatsApp_Image_2026-05-29_at_9.45.19_PM_kho7wo.jpg"
              alt="Logo"
              className="w-8 h-8 rounded-lg object-cover"
            />
            <div>
              <p className="font-bold text-sm text-gray-900 dark:text-gray-100 leading-none">ControlMetrics</p>
              <p className="text-green-600 dark:text-green-400 text-xs mt-0.5">SPC Software</p>
            </div>
          </div>

          <div className="p-5 md:p-8">
            {/* Tabs */}
            <div className="flex rounded-xl bg-gray-100 dark:bg-gray-800 p-1 mb-5 md:mb-8">
              {(['login', 'register', 'guest'] as Tab[]).map(tKey => (
                <button key={tKey}
                  onClick={() => { setTab(tKey); setError(''); setSuccess(''); }}
                  className={`flex-1 py-2 text-xs md:text-sm font-medium rounded-lg transition-all ${
                    tab === tKey
                      ? 'bg-white dark:bg-gray-700 text-green-800 dark:text-green-300 shadow-sm'
                      : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
                  }`}>
                  {tKey === 'login' ? t.auth.loginTab : tKey === 'register' ? t.auth.registerTab : t.auth.guestTab}
                </button>
              ))}
            </div>

            {/* Guest panel */}
            {tab === 'guest' && (
              <div className="text-center py-4 md:py-6">
                <div className="w-14 h-14 md:w-16 md:h-16 rounded-full bg-amber-50 dark:bg-amber-900/30 flex items-center justify-center mx-auto mb-4">
                  <User className="w-7 h-7 md:w-8 md:h-8 text-amber-600" />
                </div>
                <h3 className="text-lg md:text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                  {t.auth.guestTab}
                </h3>
                <p className="text-gray-500 dark:text-gray-400 text-sm mb-3">
                  {t.auth.guestFeature1}
                </p>
                <div className="inline-flex items-center gap-2 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl px-4 py-2.5 mb-5 text-amber-700 dark:text-amber-400 text-sm">
                  <XCircle className="w-4 h-4 flex-shrink-0" />
                  {t.auth.guestLimited}
                </div>
                <button onClick={continueAsGuest}
                  className="w-full bg-gray-800 dark:bg-gray-700 hover:bg-gray-900 dark:hover:bg-gray-600 text-white font-semibold py-3 rounded-xl text-sm transition-colors">
                  {t.auth.guest}
                </button>
                <button onClick={() => setTab('register')}
                  className="mt-3 text-sm text-green-700 dark:text-green-400 hover:underline">
                  {t.auth.noAccount}
                </button>
              </div>
            )}

            {/* Login / Register form */}
            {tab !== 'guest' && (
              <form onSubmit={submit} className="space-y-4">
                {tab === 'register' && (
                  <div>
                    <label className="text-xs font-semibold text-gray-600 dark:text-gray-400 block mb-1.5">
                      {t.auth.name}
                    </label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <input required type="text" value={name} onChange={e => setName(e.target.value)}
                        className="w-full pl-10 pr-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-xl text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-green-600"
                        placeholder="José Mendez" />
                    </div>
                  </div>
                )}

                <div>
                  <label className="text-xs font-semibold text-gray-600 dark:text-gray-400 block mb-1.5">
                    {t.auth.email}
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input required type="email" value={email} onChange={e => setEmail(e.target.value)}
                      className="w-full pl-10 pr-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-xl text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-green-600"
                      placeholder="correo@ejemplo.com" />
                  </div>
                </div>

                <div>
                  <label className="text-xs font-semibold text-gray-600 dark:text-gray-400 block mb-1.5">
                    {t.auth.password}
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input required type="password" value={password} onChange={e => setPassword(e.target.value)}
                      className="w-full pl-10 pr-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-xl text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-green-600"
                      placeholder="••••••••" minLength={6} />
                  </div>
                </div>

                {error && (
                  <p className="text-red-600 dark:text-red-400 text-xs bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg px-3 py-2">
                    {error}
                  </p>
                )}
                {success && (
                  <p className="text-green-700 dark:text-green-400 text-xs bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg px-3 py-2">
                    {success}
                  </p>
                )}

                <button type="submit" disabled={loading}
                  className="w-full bg-green-700 hover:bg-green-800 disabled:opacity-60 text-white font-semibold py-3 rounded-xl text-sm transition-colors">
                  {loading ? '…' : tab === 'login' ? t.auth.login : t.auth.register}
                </button>

                <button type="button" onClick={() => setTab(tab === 'login' ? 'register' : 'login')}
                  className="w-full text-sm text-green-700 dark:text-green-400 hover:underline py-1">
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
