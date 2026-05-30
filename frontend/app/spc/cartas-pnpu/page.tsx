'use client';
import { useState } from 'react';
import { api } from '@/lib/api';
import { ModuleShell } from '@/components/spc/ModuleShell';
import { ChartCard } from '@/components/spc/ChartCard';
import { useHistory } from '@/hooks/useHistory';

type ChartType = 'p' | 'np' | 'u';

export default function CartasPNPUPage() {
  const [chartType, setChartType] = useState<ChartType>('p');
  const [rawCounts, setRawCounts] = useState('');
  const [rawSizes, setRawSizes] = useState('');
  const [nConst, setNConst] = useState('50');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');
  const { add: addHistory } = useHistory();

  const parseList = (s: string) =>
    s.replace(/[,;\n]/g, ' ').split(/\s+/).filter(Boolean).map(Number).filter(n => !isNaN(n));

  const run = async () => {
    const counts = parseList(rawCounts);
    if (counts.length < 2) { setError('Ingrese al menos 2 muestras.'); return; }
    setError(''); setLoading(true);
    try {
      const body: any = { chart_type: chartType, counts };
      if (chartType === 'np') body.n_const = parseInt(nConst);
      else body.sizes = parseList(rawSizes);
      const res = await api.cartasPnpu.calcular(body);
      setResult(res);
      addHistory('cartas-pnpu', { chartType }, { tipo: chartType, OOC: res.ooc?.length ?? 0 });
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  const typeLabels: Record<ChartType, string> = {
    p: 'p – Proporción no conforme (n variable)',
    np: 'np – Número no conforme (n constante)',
    u: 'u – Defectos por unidad (n variable)',
  };

  return (
    <ModuleShell
      title="Cartas de Control por Atributos"
      subtitle="Proporción no conforme (p) · Número no conforme (np) · Defectos por unidad (u)"
      templateConfig={{
        module: 'cartas-pnpu',
        getParams: () => ({ chartType, rawCounts, rawSizes, nConst }),
        onLoad: (p: any) => {
          if (p.chartType) setChartType(p.chartType);
          if (p.rawCounts) setRawCounts(p.rawCounts);
          if (p.rawSizes) setRawSizes(p.rawSizes);
          if (p.nConst) setNConst(p.nConst);
        },
      }}
      leftPanel={
        <>
          <div>
            <label className="text-xs font-semibold text-gray-700 block mb-2">Tipo de carta</label>
            <div className="space-y-1.5">
              {(['p', 'np', 'u'] as ChartType[]).map(t => (
                <label key={t} className={`flex items-center gap-2.5 px-3 py-2 rounded-lg border cursor-pointer text-sm transition-colors ${chartType === t ? 'border-green-600 bg-green-50 text-green-800' : 'border-gray-200 text-gray-700 hover:bg-gray-50'}`}>
                  <input type="radio" name="type" value={t} checked={chartType === t}
                    onChange={() => { setChartType(t); setResult(null); }}
                    className="accent-green-700" />
                  {typeLabels[t]}
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-gray-700 block mb-1">
              Defectos / No conformes (un valor por línea)
            </label>
            <textarea className="w-full h-32 text-xs font-mono border border-gray-300 rounded-lg p-2 resize-none focus:outline-none focus:ring-2 focus:ring-green-600"
              value={rawCounts} onChange={e => setRawCounts(e.target.value)}
              placeholder="5&#10;3&#10;7&#10;2&#10;..." />
          </div>

          {chartType !== 'np' ? (
            <div>
              <label className="text-xs font-semibold text-gray-700 block mb-1">
                Tamaños de muestra n (un valor por línea)
              </label>
              <textarea className="w-full h-24 text-xs font-mono border border-gray-300 rounded-lg p-2 resize-none focus:outline-none focus:ring-2 focus:ring-green-600"
                value={rawSizes} onChange={e => setRawSizes(e.target.value)}
                placeholder="100&#10;100&#10;120&#10;..." />
            </div>
          ) : (
            <div>
              <label className="text-xs font-semibold text-gray-700 block mb-1">Tamaño de muestra n (constante)</label>
              <input type="number" value={nConst} onChange={e => setNConst(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-600" />
            </div>
          )}

          <button onClick={run}
            className="w-full bg-green-700 hover:bg-green-800 text-white font-semibold py-2.5 rounded-lg text-sm transition-colors">
            {loading ? 'Calculando…' : 'Calcular Carta'}
          </button>
          <button onClick={() => { setRawCounts(''); setRawSizes(''); setResult(null); setError(''); }}
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
              <h3 className="text-sm font-bold text-gray-800 mb-3">Resultados</h3>
              <div className="grid grid-cols-3 gap-3">
                {result.type === 'p' && [
                  ['Tipo', 'Carta p'], ['p̄', result.p_bar?.toFixed(4)], ['OOC', result.ooc?.length],
                ].map(([l, v]) => (
                  <div key={l} className="bg-gray-50 rounded-lg p-2.5">
                    <p className="text-xs text-gray-500">{l}</p>
                    <p className="font-semibold text-gray-900 text-sm">{v}</p>
                  </div>
                ))}
                {result.type === 'np' && [
                  ['Tipo', 'Carta np'], ['n̄p', result.np_bar?.toFixed(3)], ['p̄', result.p_bar?.toFixed(4)],
                  ['LCS', result.ucl?.toFixed(4)], ['LC', result.cl?.toFixed(4)], ['LCI', result.lcl?.toFixed(4)],
                ].map(([l, v]) => (
                  <div key={l} className="bg-gray-50 rounded-lg p-2.5">
                    <p className="text-xs text-gray-500">{l}</p>
                    <p className="font-semibold text-green-700 text-sm font-mono">{v}</p>
                  </div>
                ))}
                {result.type === 'u' && [
                  ['Tipo', 'Carta u'], ['ū', result.u_bar?.toFixed(4)], ['OOC', result.ooc?.length],
                ].map(([l, v]) => (
                  <div key={l} className="bg-gray-50 rounded-lg p-2.5">
                    <p className="text-xs text-gray-500">{l}</p>
                    <p className="font-semibold text-gray-900 text-sm">{v}</p>
                  </div>
                ))}
              </div>
              {result.ooc?.length > 0 && (
                <p className="mt-3 text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg p-2">
                  ✘ Puntos fuera de control: muestras {result.ooc.map((i: number) => i + 1).join(', ')}
                </p>
              )}
            </div>
          )}
          <ChartCard title="Carta de Control por Atributos"
            src={result?.chart} loading={loading && !result} />
        </>
      }
    />
  );
}
