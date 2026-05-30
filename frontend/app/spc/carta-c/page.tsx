'use client';
import { useState } from 'react';
import { api } from '@/lib/api';
import { ModuleShell } from '@/components/spc/ModuleShell';
import { ChartCard } from '@/components/spc/ChartCard';
import { useHistory } from '@/hooks/useHistory';
import { ExcelUpload } from '@/components/ui/ExcelUpload';

export default function CartaCPage() {
  const [rawDefects, setRawDefects] = useState('');
  const [rawTipos, setRawTipos] = useState('');
  const [acept, setAcept] = useState('2');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');
  const { add: addHistory } = useHistory();

  const parseDefects = () =>
    rawDefects.replace(/[,;\n]/g, ' ').split(/\s+/).filter(Boolean).map(Number).filter(n => !isNaN(n)).map(Math.round);

  const parseTipos = (): Record<string, number> => {
    const out: Record<string, number> = {};
    rawTipos.trim().split('\n').forEach(line => {
      const parts = line.split(/[,\t]+/);
      if (parts.length >= 2) {
        const name = parts[0].trim();
        const freq = parseInt(parts[1].trim());
        if (name && !isNaN(freq)) out[name] = freq;
      }
    });
    return out;
  };

  const run = async () => {
    const defects = parseDefects();
    if (defects.length < 2) { setError('Ingrese al menos 2 cajas.'); return; }
    setError(''); setLoading(true);
    try {
      const res = await api.cartaC.calcular({
        defects,
        tipos: Object.keys(parseTipos()).length ? parseTipos() : undefined,
        acept: parseInt(acept),
      });
      setResult(res);
      addHistory('carta-c', { acept }, { 'C̄': res.c_bar?.toFixed(3), OOC: res.ooc?.length ?? 0 });
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  const loadDemo = async () => {
    const d = await api.cartaC.demo();
    setRawDefects(d.defects.join('\n'));
    setRawTipos(Object.entries(d.tipos).map(([k, v]) => `${k},${v}`).join('\n'));
  };

  return (
    <ModuleShell
      title="Carta C + Diagrama de Pareto"
      subtitle="Defectos por unidad (distribución de Poisson) · Análisis 80/20"
      templateConfig={{
        module: 'carta-c',
        getParams: () => ({ rawDefects, rawTipos, acept }),
        onLoad: (p: any) => {
          if (p.rawDefects) setRawDefects(p.rawDefects);
          if (p.rawTipos) setRawTipos(p.rawTipos);
          if (p.acept) setAcept(p.acept);
        },
      }}
      leftPanel={
        <>
          <div>
            <label className="text-xs font-semibold text-gray-700 block mb-1">
              Criterio de aceptación (máx. defectos/caja)
            </label>
            <input type="number" min={0} value={acept} onChange={e => setAcept(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-600" />
          </div>
          <div>
            <label className="text-xs font-semibold text-gray-700 block mb-1">
              Defectos por caja (un valor por línea)
            </label>
            <textarea className="w-full h-32 text-xs font-mono border border-gray-300 rounded-lg p-2 resize-none focus:outline-none focus:ring-2 focus:ring-green-600"
              value={rawDefects} onChange={e => setRawDefects(e.target.value)}
              placeholder="2&#10;1&#10;0&#10;1&#10;2&#10;..." />
          </div>
          <div>
            <label className="text-xs font-semibold text-gray-700 block mb-1">
              Tipos de defecto para Pareto (Nombre,Frecuencia por línea)
            </label>
            <textarea className="w-full h-28 text-xs font-mono border border-gray-300 rounded-lg p-2 resize-none focus:outline-none focus:ring-2 focus:ring-green-600"
              value={rawTipos} onChange={e => setRawTipos(e.target.value)}
              placeholder="Speckling,5&#10;Trips,4&#10;Mancha roja,3&#10;..." />
          </div>
          <ExcelUpload
            module="carta-c"
            onData={(d: any) => {
              if (d.cajas) setRawDefects(d.cajas.join('\n'));
              if (d.tipos) setRawTipos(Object.entries(d.tipos).map(([k, v]) => `${k},${v}`).join('\n'));
            }}
            onError={setError}
          />
          <button onClick={run}
            className="w-full bg-green-700 hover:bg-green-800 text-white font-semibold py-2.5 rounded-lg text-sm">
            {loading ? 'Calculando…' : 'Calcular'}
          </button>
          <button onClick={loadDemo}
            className="w-full bg-amber-100 hover:bg-amber-200 text-amber-800 font-medium py-2 rounded-lg text-sm">
            Datos del estudio
          </button>
          <button onClick={() => { setRawDefects(''); setRawTipos(''); setResult(null); setError(''); }}
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
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold text-gray-800">Resultados – Carta C</h3>
                <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${result.ooc?.length === 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                  {result.ooc?.length === 0 ? '✔ Bajo control' : `✘ ${result.ooc?.length} OOC`}
                </span>
              </div>
              <div className="grid grid-cols-3 gap-2">
                {[
                  ['Cajas', result.n_cajas], ['C̄', result.c_bar?.toFixed(4)],
                  ['LCS', result.ucl?.toFixed(4)], ['LCI', result.lcl?.toFixed(4)],
                  ['No conf.', `${result.nc_cajas} (${result.nc_pct}%)`], ['Criterio', `≤ ${acept}`],
                ].map(([l, v]) => (
                  <div key={l} className="bg-gray-50 rounded-lg p-2.5">
                    <p className="text-xs text-gray-500">{l}</p>
                    <p className="font-semibold text-green-700 text-sm">{v}</p>
                  </div>
                ))}
              </div>
              {result.conformidad && (
                <div className="mt-3 flex flex-wrap gap-1.5 max-h-24 overflow-y-auto">
                  {result.conformidad.map((ok: boolean, i: number) => (
                    <span key={i}
                      className={`inline-flex items-center text-xs px-2 py-0.5 rounded-full ${ok ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                      C{i + 1}: {ok ? '✔' : '✘'}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}
          <ChartCard title="Carta C y Diagrama de Pareto"
            src={result?.charts?.combined} loading={loading && !result} />
        </>
      }
    />
  );
}
