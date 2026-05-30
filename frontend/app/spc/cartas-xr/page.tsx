'use client';
import { useState } from 'react';
import { api } from '@/lib/api';
import { ModuleShell } from '@/components/spc/ModuleShell';
import { ChartCard } from '@/components/spc/ChartCard';

export default function CartasXRPage() {
  const [rawRows, setRawRows] = useState('');
  const [n, setN] = useState('6');
  const [lie, setLie] = useState('3.15');
  const [lse, setLse] = useState('3.30');
  const [target, setTarget] = useState('3.225');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const parseSubgroups = () => {
    const nv = parseInt(n);
    return rawRows.trim().split('\n').map(line =>
      line.trim().replace(/,/g, '.').split(/\s+/).map(Number).filter(v => !isNaN(v))
    ).filter(row => row.length === nv);
  };

  const run = async () => {
    const data = parseSubgroups();
    if (data.length < 2) { setError('Ingrese al menos 2 subgrupos completos.'); return; }
    setError(''); setLoading(true);
    try {
      const res = await api.cartasXR.calcular({
        data, n: parseInt(n),
        lie: parseFloat(lie) || undefined,
        lse: parseFloat(lse) || undefined,
        target: parseFloat(target) || undefined,
      });
      setResult(res);
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  const loadFase1 = async () => {
    const d = await api.cartasXR.demoFase1();
    setRawRows(d.data.map((r: number[]) => r.join('\t')).join('\n'));
    setN(String(d.data[0]?.length ?? 6));
  };

  const loadFase2 = async () => {
    const d = await api.cartasXR.demoFase2();
    setRawRows(d.data.map((r: number[]) => r.join('\t')).join('\n'));
    setN(String(d.data[0]?.length ?? 6));
  };

  const lim = result?.limits;
  const oocTotal = (result?.ooc_x?.length ?? 0) + (result?.ooc_r?.length ?? 0);

  return (
    <ModuleShell
      title="Cartas de Control X̄ – R"
      subtitle="Variables · Subgrupos · Reglas de Western Electric · Curva de Potencia"
      leftPanel={
        <>
          <div>
            <label className="text-xs font-semibold text-gray-700 block mb-1">
              Tamaño de subgrupo (n)
            </label>
            <input type="number" min={2} max={10} value={n} onChange={e => setN(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-600" />
          </div>
          <div>
            <label className="text-xs font-semibold text-gray-700 block mb-1">
              Subgrupos — una fila por subgrupo, valores separados por tabulación/espacio
            </label>
            <textarea
              className="w-full h-44 text-xs font-mono border border-gray-300 rounded-lg p-2 resize-none focus:outline-none focus:ring-2 focus:ring-green-600"
              value={rawRows} onChange={e => setRawRows(e.target.value)}
              placeholder="3.14 3.12 3.27 3.20 3.23 3.35&#10;3.24 3.21 3.33 3.35 3.26 3.21&#10;..." />
          </div>
          <div className="grid grid-cols-3 gap-2">
            {[['LIE', lie, setLie], ['LSE', lse, setLse], ['Obj.', target, setTarget]].map(([l, v, set]) => (
              <div key={l as string}>
                <label className="text-xs text-gray-600 block mb-1">{l as string} (lb)</label>
                <input value={v as string} onChange={e => (set as any)(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-green-600" />
              </div>
            ))}
          </div>
          <button onClick={run}
            className="w-full bg-green-700 hover:bg-green-800 text-white font-semibold py-2.5 rounded-lg text-sm transition-colors">
            {loading ? 'Calculando…' : 'Calcular Cartas'}
          </button>
          <div className="flex gap-2">
            <button onClick={loadFase1}
              className="flex-1 bg-amber-100 hover:bg-amber-200 text-amber-800 font-medium py-2 rounded-lg text-xs transition-colors">
              Fase I
            </button>
            <button onClick={loadFase2}
              className="flex-1 bg-orange-100 hover:bg-orange-200 text-orange-800 font-medium py-2 rounded-lg text-xs transition-colors">
              Fase II
            </button>
          </div>
          <button onClick={() => { setRawRows(''); setResult(null); setError(''); }}
            className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-2 rounded-lg text-sm transition-colors">
            Limpiar
          </button>
          {error && <p className="text-red-600 text-xs bg-red-50 border border-red-200 rounded-lg p-2">{error}</p>}
        </>
      }
      rightPanel={
        <>
          {/* Límites de control */}
          {lim && (
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold text-gray-800">Límites de Control Calculados</h3>
                <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${oocTotal === 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                  {oocTotal === 0 ? '✔ Bajo control' : `✘ ${oocTotal} punto(s) OOC`}
                </span>
              </div>
              <div className="grid grid-cols-3 gap-2">
                {[
                  ['X̄̄', lim.xbar_bar?.toFixed(4)], ['R̄', lim.r_bar?.toFixed(4)], ['σ̂', lim.sigma_est?.toFixed(5)],
                  ['LCS X̄', lim.ucl_x?.toFixed(4)], ['LC X̄', lim.cl_x?.toFixed(4)], ['LCI X̄', lim.lcl_x?.toFixed(4)],
                  ['LCS R', lim.ucl_r?.toFixed(4)], ['LC R', lim.cl_r?.toFixed(4)], ['LCI R', lim.lcl_r?.toFixed(4)],
                ].map(([label, val]) => (
                  <div key={label} className="bg-gray-50 rounded-lg p-2.5">
                    <p className="text-xs text-gray-500">{label}</p>
                    <p className="font-semibold text-green-700 text-sm font-mono">{val ?? '—'}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Subgrupos calculados */}
          {result?.xbars && (
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
              <div className="px-4 py-3 bg-green-900">
                <h3 className="text-sm font-bold text-white">Tabla de Subgrupos (X̄ y R calculados)</h3>
              </div>
              <div className="overflow-x-auto max-h-52 overflow-y-auto">
                <table className="w-full text-xs">
                  <thead className="bg-gray-50 sticky top-0">
                    <tr>
                      {['SG', 'X̄', 'R', 'Estado X̄', 'Estado R'].map(h =>
                        <th key={h} className="px-3 py-2 text-left font-semibold text-gray-600">{h}</th>
                      )}
                    </tr>
                  </thead>
                  <tbody>
                    {result.xbars.map((xb: number, i: number) => {
                      const oocX = result.ooc_x?.includes(i);
                      const oocR = result.ooc_r?.includes(i);
                      return (
                        <tr key={i} className={`border-t border-gray-100 ${oocX || oocR ? 'bg-red-50' : ''}`}>
                          <td className="px-3 py-1.5 font-medium">{i + 1}</td>
                          <td className="px-3 py-1.5 font-mono">{xb.toFixed(4)}</td>
                          <td className="px-3 py-1.5 font-mono">{result.ranges[i]?.toFixed(4)}</td>
                          <td className="px-3 py-1.5">{oocX ? <span className="text-red-600 font-semibold">✘ OOC</span> : '✔'}</td>
                          <td className="px-3 py-1.5">{oocR ? <span className="text-red-600 font-semibold">✘ OOC</span> : '✔'}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          <ChartCard title="Carta X̄ y Carta R"
            src={result?.charts?.combined} loading={loading && !result} />
        </>
      }
    />
  );
}
