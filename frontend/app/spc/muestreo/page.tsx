'use client';
import { useState } from 'react';
import { api } from '@/lib/api';
import { ModuleShell } from '@/components/spc/ModuleShell';
import { ChartCard } from '@/components/spc/ChartCard';
import { useHistory } from '@/hooks/useHistory';
import { ExcelUpload } from '@/components/ui/ExcelUpload';

export default function MuestreoPage() {
  const [nLote, setNLote] = useState('960');
  const [nac, setNac] = useState('4.0');
  const [useManual, setUseManual] = useState(false);
  const [nPlan, setNPlan] = useState('');
  const [cPlan, setCPlan] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');
  const { add: addHistory } = useHistory();

  const run = async () => {
    const nLoteN = parseInt(nLote);
    const nacN   = parseFloat(nac);
    if (!nLoteN || nLoteN < 2) { setError('Ingrese un tamaño de lote válido.'); return; }
    if (isNaN(nacN) || nacN <= 0 || nacN >= 100) { setError('NAC debe estar entre 0 y 100%.'); return; }
    setError(''); setLoading(true);
    try {
      const body: any = { n_lote: nLoteN, nac: nacN, use_manual: useManual };
      if (useManual) {
        body.n_plan = parseInt(nPlan);
        body.c_plan = parseInt(cPlan);
      }
      const res = await api.muestreo.calcular(body);
      setResult(res);
      addHistory('muestreo', { nLote, nac }, { 'n plan': res.n, Ac: res.ac, AOQL: `${res.aoql}%` });
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  const loadDemo = async () => {
    const d = await api.muestreo.demo();
    setNLote(String(d.n_lote));
    setNac(String(d.nac));
    setUseManual(false);
  };

  return (
    <ModuleShell
      title="Plan de Muestreo por Aceptación"
      subtitle="MIL-STD-105E · Curva COP · Calidad Promedio de Salida (AOQ)"
      templateConfig={{
        module: 'muestreo',
        getParams: () => ({ nLote, nac, useManual, nPlan, cPlan }),
        onLoad: (p: any) => {
          if (p.nLote) setNLote(p.nLote);
          if (p.nac) setNac(p.nac);
          if (p.useManual !== undefined) setUseManual(p.useManual);
          if (p.nPlan) setNPlan(p.nPlan);
          if (p.cPlan) setCPlan(p.cPlan);
        },
      }}
      leftPanel={
        <>
          <div>
            <label className="text-xs font-semibold text-gray-700 block mb-1">Tamaño del lote (N)</label>
            <input type="number" min={2} value={nLote} onChange={e => setNLote(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-600" />
          </div>

          <div>
            <label className="text-xs font-semibold text-gray-700 block mb-1">
              NAC – Nivel de Calidad Aceptable (%)
            </label>
            <input type="number" step="0.1" min={0.1} max={99} value={nac}
              onChange={e => setNac(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-600" />
          </div>

          <div>
            <label className="text-xs font-semibold text-gray-700 block mb-2">Fuente del plan</label>
            <div className="flex gap-2">
              {[false, true].map(m => (
                <label key={String(m)} className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg border cursor-pointer text-xs transition-colors ${useManual === m ? 'border-green-600 bg-green-50 text-green-800' : 'border-gray-200 text-gray-700'}`}>
                  <input type="radio" name="planMode" checked={useManual === m}
                    onChange={() => setUseManual(m)} className="accent-green-700" />
                  {m ? 'Manual' : 'MIL-STD-105E'}
                </label>
              ))}
            </div>

            {useManual && (
              <div className="mt-2 grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs text-gray-600 block mb-1">n (muestra)</label>
                  <input type="number" min={1} value={nPlan} onChange={e => setNPlan(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-green-600" />
                </div>
                <div>
                  <label className="text-xs text-gray-600 block mb-1">c (Ac)</label>
                  <input type="number" min={0} value={cPlan} onChange={e => setCPlan(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-green-600" />
                </div>
              </div>
            )}
          </div>

          <ExcelUpload
            module="muestreo"
            onData={(d: any) => {
              if (d.n_lote) setNLote(String(d.n_lote));
              if (d.nac) setNac(String(d.nac));
            }}
            onError={setError}
          />
          <button onClick={run}
            className="w-full bg-green-700 hover:bg-green-800 text-white font-semibold py-2.5 rounded-lg text-sm transition-colors">
            {loading ? 'Calculando…' : 'Calcular Plan'}
          </button>
          <button onClick={loadDemo}
            className="w-full bg-amber-100 hover:bg-amber-200 text-amber-800 font-medium py-2 rounded-lg text-sm">
            Datos del estudio
          </button>
          <button onClick={() => { setResult(null); setError(''); }}
            className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-2 rounded-lg text-sm">
            Limpiar
          </button>
          {error && <p className="text-red-600 text-xs bg-red-50 border border-red-200 rounded-lg p-2">{error}</p>}
        </>
      }
      rightPanel={
        <>
          {result && (
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
              <h3 className="text-sm font-bold text-gray-800 mb-3">Plan de Muestreo</h3>

              {/* Plan summary */}
              <div className="flex gap-3 mb-3">
                {[
                  ['Letra MIL', result.letra],
                  ['n (muestra)', result.n],
                  ['Ac', result.ac],
                  ['Re', result.re],
                ].map(([l, v]) => (
                  <div key={l} className="flex-1 bg-green-50 border border-green-100 rounded-lg p-2.5 text-center">
                    <p className="text-xs text-gray-500">{l}</p>
                    <p className="font-bold text-green-800 text-lg">{v}</p>
                  </div>
                ))}
              </div>

              {/* Probabilities */}
              <div className="grid grid-cols-3 gap-2 mb-3">
                {[
                  ['Pa (p=0)', `${result.pa_0}%`],
                  ['Pa (NAC)', `${result.pa_nac}%`],
                  ['Pa (2×NAC)', `${result.pa_2nac}%`],
                  ['Riesgo α', `${result.alpha_risk}%`],
                  ['Riesgo β', `${result.beta_risk}%`],
                  ['AOQL', `${result.aoql}%`],
                ].map(([l, v]) => (
                  <div key={l} className="bg-gray-50 rounded-lg p-2.5">
                    <p className="text-xs text-gray-500">{l}</p>
                    <p className="font-semibold text-gray-900 text-sm font-mono">{v}</p>
                  </div>
                ))}
              </div>

              <p className="text-xs text-gray-500 bg-gray-50 rounded-lg p-2">
                AOQL alcanzado en p = <span className="font-semibold text-gray-700">{result.p_aoql}%</span>
              </p>
            </div>
          )}

          <ChartCard title="Curva OC y Calidad Promedio de Salida (AOQ)"
            src={result?.charts?.combined} loading={loading && !result} />
        </>
      }
    />
  );
}
