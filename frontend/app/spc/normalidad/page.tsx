'use client';
import { useState } from 'react';
import { api } from '@/lib/api';
import { ModuleShell } from '@/components/spc/ModuleShell';
import { ChartCard } from '@/components/spc/ChartCard';
import { useHistory } from '@/hooks/useHistory';
import { ExcelUpload } from '@/components/ui/ExcelUpload';

export default function NormalidadPage() {
  const [raw, setRaw] = useState('');
  const [alpha, setAlpha] = useState('0.05');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');
  const { add: addHistory } = useHistory();

  const parseData = () =>
    raw.replace(/[,;\n]/g, ' ').split(/\s+/).filter(Boolean).map(Number).filter(n => !isNaN(n));

  const run = async () => {
    const data = parseData();
    if (data.length < 3) { setError('Ingrese al menos 3 valores.'); return; }
    setError(''); setLoading(true);
    try {
      const res = await api.normalidad.analizar(data, parseFloat(alpha));
      setResult(res);
      addHistory('normalidad', { alpha, n: data.length }, {
        'AD normal': res.tests?.AD?.normal ? '✔' : '✘',
        'n': data.length,
      });
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  const loadDemo = async () => {
    const d = await api.normalidad.demo();
    setRaw(d.data.join('\n'));
  };

  const s = result?.stats;
  const tests = result?.tests;
  const ind = result?.independence;

  const testLabel = (ok: boolean) => ok
    ? <span className="text-green-700 font-semibold">✔ Normal</span>
    : <span className="text-red-600 font-semibold">✘ No normal</span>;

  return (
    <ModuleShell
      title="Análisis de Normalidad"
      subtitle="Anderson-Darling · Shapiro-Wilk · Kolmogorov-Smirnov · Pruebas de independencia"
      templateConfig={{
        module: 'normalidad',
        getParams: () => ({ raw, alpha }),
        onLoad: (p: any) => { if (p.raw) setRaw(p.raw); if (p.alpha) setAlpha(p.alpha); },
      }}
      leftPanel={
        <>
          <div>
            <label className="text-xs font-semibold text-gray-700 block mb-1">Datos de peso (lb) — un valor por línea</label>
            <textarea
              className="w-full h-40 text-xs font-mono border border-gray-300 rounded-lg p-2 resize-none focus:outline-none focus:ring-2 focus:ring-green-600"
              value={raw} onChange={e => setRaw(e.target.value)}
              placeholder="3.22&#10;3.18&#10;3.25&#10;..." />
          </div>
          <div>
            <label className="text-xs font-semibold text-gray-700 block mb-1">Nivel de significancia (α)</label>
            <select className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-600"
              value={alpha} onChange={e => setAlpha(e.target.value)}>
              <option value="0.01">0.01</option>
              <option value="0.05">0.05</option>
              <option value="0.10">0.10</option>
            </select>
          </div>
          <ExcelUpload
            module="normalidad"
            onData={(d: any) => setRaw(d.data.join('\n'))}
            onError={setError}
          />
          <button onClick={run}
            className="w-full bg-green-700 hover:bg-green-800 text-white font-semibold py-2.5 rounded-lg text-sm transition-colors">
            {loading ? 'Analizando…' : 'Analizar'}
          </button>
          <button onClick={loadDemo}
            className="w-full bg-amber-100 hover:bg-amber-200 text-amber-800 font-semibold py-2 rounded-lg text-sm transition-colors">
            Cargar datos del estudio
          </button>
          <button onClick={() => { setRaw(''); setResult(null); setError(''); }}
            className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-2 rounded-lg text-sm transition-colors">
            Limpiar
          </button>
          {error && <p className="text-red-600 text-xs bg-red-50 border border-red-200 rounded-lg p-2">{error}</p>}
        </>
      }
      rightPanel={
        <>
          {s && (
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
              <h3 className="text-sm font-bold text-gray-800 mb-3">Estadísticas Descriptivas</h3>
              <div className="grid grid-cols-3 gap-3">
                {[
                  ['n', s.n], ['Media (μ)', s.mean?.toFixed(4) + ' lb'],
                  ['Desv. Est. (σ)', s.std?.toFixed(5) + ' lb'], ['Mediana', s.median?.toFixed(4) + ' lb'],
                  ['Mínimo', s.min?.toFixed(4) + ' lb'], ['Máximo', s.max?.toFixed(4) + ' lb'],
                ].map(([label, val]) => (
                  <div key={label as string} className="bg-gray-50 rounded-lg p-2.5">
                    <p className="text-xs text-gray-500">{label}</p>
                    <p className="font-semibold text-gray-900 text-sm">{val}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
          {tests && (
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
              <div className="px-4 py-3 bg-green-900">
                <h3 className="text-sm font-bold text-white">Pruebas de Normalidad (H₀: distribución normal)</h3>
              </div>
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>{['Prueba', 'Estadístico', 'Valor-p', 'α', 'Conclusión'].map(h =>
                    <th key={h} className="text-left px-3 py-2 text-xs font-semibold text-gray-600">{h}</th>)}</tr>
                </thead>
                <tbody>
                  {[['AD', 'Anderson-Darling'], ['SW', 'Shapiro-Wilk'], ['KS', 'Kolmogorov-Smirnov']].map(([k, name]) => {
                    const tt = tests[k];
                    return (
                      <tr key={k} className="border-t border-gray-100">
                        <td className="px-3 py-2 font-medium">{name}</td>
                        <td className="px-3 py-2 font-mono text-xs">{tt?.statistic?.toFixed(4)}</td>
                        <td className="px-3 py-2 font-mono text-xs">{tt?.p_value?.toFixed(4)}</td>
                        <td className="px-3 py-2 font-mono text-xs">{alpha}</td>
                        <td className="px-3 py-2">{testLabel(tt?.normal)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
          {ind && (
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
              <div className="px-4 py-3 bg-slate-700">
                <h3 className="text-sm font-bold text-white">Pruebas de Independencia y Aleatoriedad</h3>
              </div>
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>{['Prueba', 'Estadístico', 'Detalle', 'Conclusión'].map(h =>
                    <th key={h} className="text-left px-3 py-2 text-xs font-semibold text-gray-600">{h}</th>)}</tr>
                </thead>
                <tbody>
                  <tr className="border-t border-gray-100">
                    <td className="px-3 py-2 font-medium">Durbin-Watson</td>
                    <td className="px-3 py-2 font-mono text-xs">{ind.dw?.statistic?.toFixed(4)}</td>
                    <td className="px-3 py-2 text-xs text-gray-500">{ind.dw?.interpretation}</td>
                    <td className="px-3 py-2">{testLabel(ind.dw?.independent)}</td>
                  </tr>
                  <tr className="border-t border-gray-100">
                    <td className="px-3 py-2 font-medium">Prueba de Rachas</td>
                    <td className="px-3 py-2 font-mono text-xs">Z = {ind.runs?.z?.toFixed(4)}</td>
                    <td className="px-3 py-2 text-xs text-gray-500">Rachas={ind.runs?.runs} · p={ind.runs?.p_value?.toFixed(4)}</td>
                    <td className="px-3 py-2">{testLabel(ind.runs?.independent)}</td>
                  </tr>
                  <tr className="border-t border-gray-100">
                    <td className="px-3 py-2 font-medium">Autocorr. lag-1</td>
                    <td className="px-3 py-2 font-mono text-xs">r₁ = {ind.acf?.r1?.toFixed(4)}</td>
                    <td className="px-3 py-2 text-xs text-gray-500">p = {ind.acf?.p_value?.toFixed(4)}</td>
                    <td className="px-3 py-2">{testLabel(ind.acf?.independent)}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          )}
          <ChartCard title="Histograma + Curva Normal + Gráfico Q-Q"
            src={result?.charts?.combined} loading={loading && !result} />
        </>
      }
    />
  );
}
