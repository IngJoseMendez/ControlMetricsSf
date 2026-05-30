'use client';
import { useState } from 'react';
import { api } from '@/lib/api';
import { ModuleShell } from '@/components/spc/ModuleShell';
import { ChartCard } from '@/components/spc/ChartCard';
import { useHistory } from '@/hooks/useHistory';
import { ExcelUpload } from '@/components/ui/ExcelUpload';

export default function CapacidadPage() {
  const [raw, setRaw] = useState('');
  const [lie, setLie] = useState('3.15');
  const [lse, setLse] = useState('3.30');
  const [target, setTarget] = useState('3.225');
  const [sigmaMode, setSigmaMode] = useState<'data' | 'manual'>('data');
  const [sigmaVal, setSigmaVal] = useState('0.09865');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');
  const { add: addHistory } = useHistory();

  const parseData = () =>
    raw.replace(/[,;\n]/g, ' ').split(/\s+/).filter(Boolean).map(Number).filter(n => !isNaN(n));

  const run = async () => {
    const data = parseData();
    if (data.length < 5) { setError('Ingrese al menos 5 valores.'); return; }
    const lieN = parseFloat(lie), lseN = parseFloat(lse);
    if (lieN >= lseN) { setError('LIE debe ser menor que LSE.'); return; }
    setError(''); setLoading(true);
    try {
      const res = await api.capacidad.calcular({
        data,
        lie: lieN,
        lse: lseN,
        target: parseFloat(target) || undefined,
        sigma: sigmaMode === 'manual' ? parseFloat(sigmaVal) : undefined,
      });
      setResult(res);
      addHistory('capacidad', { lie, lse, target }, { Cpk: res.cpk, nivel: res.nivel });
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  const loadDemo = async () => {
    const d = await api.capacidad.demo();
    setRaw(d.data.join('\n'));
    setSigmaVal(String(d.sigma));
    setSigmaMode('manual');
  };

  const nivelColor: Record<string, string> = {
    excellent: 'bg-green-100 text-green-800',
    capable:   'bg-blue-100 text-blue-800',
    marginal:  'bg-yellow-100 text-yellow-800',
    incapable: 'bg-orange-100 text-orange-800',
    critical:  'bg-red-100 text-red-700',
  };

  return (
    <ModuleShell
      title="Capacidad del Proceso"
      subtitle="Cp · Cpk · Cpu · Cpl · Nivel Sigma · % No Conformes"
      templateConfig={{
        module: 'capacidad',
        getParams: () => ({ raw, lie, lse, target, sigmaMode, sigmaVal }),
        onLoad: (p: any) => {
          if (p.raw) setRaw(p.raw);
          if (p.lie) setLie(p.lie);
          if (p.lse) setLse(p.lse);
          if (p.target) setTarget(p.target);
          if (p.sigmaMode) setSigmaMode(p.sigmaMode);
          if (p.sigmaVal) setSigmaVal(p.sigmaVal);
        },
      }}
      leftPanel={
        <>
          <div>
            <label className="text-xs font-semibold text-gray-700 block mb-1">
              Datos de peso (lb) — un valor por línea
            </label>
            <textarea
              className="w-full h-36 text-xs font-mono border border-gray-300 rounded-lg p-2 resize-none focus:outline-none focus:ring-2 focus:ring-green-600"
              value={raw} onChange={e => setRaw(e.target.value)}
              placeholder="3.22&#10;3.18&#10;3.25&#10;..." />
          </div>

          <div className="grid grid-cols-3 gap-2">
            {[['LIE (lb)', lie, setLie], ['LSE (lb)', lse, setLse], ['Obj. (lb)', target, setTarget]].map(([l, v, set]) => (
              <div key={l as string}>
                <label className="text-xs text-gray-600 block mb-1">{l as string}</label>
                <input value={v as string} onChange={e => (set as any)(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-green-600" />
              </div>
            ))}
          </div>

          <div>
            <label className="text-xs font-semibold text-gray-700 block mb-2">Fuente de σ</label>
            <div className="flex gap-2">
              {(['data', 'manual'] as const).map(m => (
                <label key={m} className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg border cursor-pointer text-xs transition-colors ${sigmaMode === m ? 'border-green-600 bg-green-50 text-green-800' : 'border-gray-200 text-gray-700'}`}>
                  <input type="radio" name="sigma" value={m} checked={sigmaMode === m}
                    onChange={() => setSigmaMode(m)} className="accent-green-700" />
                  {m === 'data' ? 'Desde datos' : 'Manual'}
                </label>
              ))}
            </div>
            {sigmaMode === 'manual' && (
              <input type="number" step="0.00001" value={sigmaVal}
                onChange={e => setSigmaVal(e.target.value)}
                className="mt-2 w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-600"
                placeholder="σ (ej. 0.09865)" />
            )}
          </div>

          <ExcelUpload
            module="capacidad"
            onData={(d: any) => setRaw(d.data.join('\n'))}
            onError={setError}
          />
          <button onClick={run}
            className="w-full bg-green-700 hover:bg-green-800 text-white font-semibold py-2.5 rounded-lg text-sm transition-colors">
            {loading ? 'Calculando…' : 'Calcular Capacidad'}
          </button>
          <button onClick={loadDemo}
            className="w-full bg-amber-100 hover:bg-amber-200 text-amber-800 font-medium py-2 rounded-lg text-sm">
            Datos del estudio
          </button>
          <button onClick={() => { setRaw(''); setResult(null); setError(''); }}
            className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-2 rounded-lg text-sm">
            Limpiar
          </button>
          {error && <p className="text-red-600 text-xs bg-red-50 border border-red-200 rounded-lg p-2">{error}</p>}
        </>
      }
      rightPanel={
        <>
          {result && (
            <>
              {/* Evaluación */}
              <div className={`rounded-xl border p-3.5 ${nivelColor[result.nivel] ?? 'bg-gray-100 text-gray-800'}`}>
                <p className="text-xs font-bold uppercase tracking-wide opacity-70 mb-0.5">Evaluación del proceso</p>
                <p className="font-semibold text-sm">{result.evaluacion}</p>
              </div>

              {/* Índices principales */}
              <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
                <h3 className="text-sm font-bold text-gray-800 mb-3">Índices de Capacidad</h3>
                <div className="grid grid-cols-2 gap-2 mb-3">
                  {[
                    ['Cp', result.cp?.toFixed(4)],
                    ['Cpk', result.cpk?.toFixed(4)],
                    ['Cpu', result.cpu?.toFixed(4)],
                    ['Cpl', result.cpl?.toFixed(4)],
                  ].map(([l, v]) => (
                    <div key={l} className="bg-gray-50 rounded-lg p-2.5">
                      <p className="text-xs text-gray-500">{l}</p>
                      <p className={`font-bold text-lg font-mono ${parseFloat(v as string) >= 1.33 ? 'text-green-700' : parseFloat(v as string) >= 1.00 ? 'text-yellow-600' : 'text-red-600'}`}>{v}</p>
                    </div>
                  ))}
                </div>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    ['n', result.n],
                    ['μ (lb)', result.mu?.toFixed(5)],
                    ['σ (lb)', result.sigma?.toFixed(5)],
                    ['Nivel σ', `${result.sigma_level}σ`],
                    ['%NC sup', `${result.pnc_sup?.toFixed(4)}%`],
                    ['%NC inf', `${result.pnc_inf?.toFixed(4)}%`],
                  ].map(([l, v]) => (
                    <div key={l} className="bg-gray-50 rounded-lg p-2.5">
                      <p className="text-xs text-gray-500">{l}</p>
                      <p className="font-semibold text-gray-900 text-sm font-mono">{v}</p>
                    </div>
                  ))}
                </div>
                <div className="mt-2 bg-gray-50 rounded-lg p-2.5">
                  <p className="text-xs text-gray-500">% Total No Conformes</p>
                  <p className={`font-bold text-base font-mono ${result.pnc_total < 0.1 ? 'text-green-700' : result.pnc_total < 1 ? 'text-yellow-600' : 'text-red-600'}`}>
                    {result.pnc_total?.toFixed(4)}%
                  </p>
                </div>
              </div>
            </>
          )}

          <ChartCard title="Curva de Capacidad y Distribución de No Conformes"
            src={result?.charts?.combined} loading={loading && !result} />
        </>
      }
    />
  );
}
