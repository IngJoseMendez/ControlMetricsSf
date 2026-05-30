'use client';
import { useState } from 'react';
import { api } from '@/lib/api';
import { ModuleShell } from '@/components/spc/ModuleShell';
import { ChartCard } from '@/components/spc/ChartCard';
import { useHistory } from '@/hooks/useHistory';

export default function MejoraPage() {
  const [xbar,        setXbar]        = useState('3.2400');
  const [sigma,       setSigma]       = useState('0.09865');
  const [n,           setN]           = useState('6');
  const [t,           setT]           = useState('15.0');
  const [ucl,         setUcl]         = useState('3.3608');
  const [lcl,         setLcl]         = useState('3.1192');
  const [xbarNew,     setXbarNew]     = useState('3.30');
  const [targetPower, setTargetPower] = useState('98.0');
  const [k,           setK]           = useState('3.0');
  const [loading,     setLoading]     = useState(false);
  const [result,      setResult]      = useState<any>(null);
  const [error,       setError]       = useState('');
  const { add: addHistory } = useHistory();

  const run = async () => {
    setError(''); setLoading(true);
    try {
      const res = await api.mejora.calcular({
        xbar:         parseFloat(xbar),
        sigma:        parseFloat(sigma),
        n:            parseInt(n),
        t:            parseFloat(t),
        ucl:          parseFloat(ucl),
        lcl:          parseFloat(lcl),
        xbar_new:     parseFloat(xbarNew),
        target_power: parseFloat(targetPower),
        k:            parseFloat(k),
      });
      setResult(res);
      addHistory('mejora', { xbar, sigma, n }, { 'Potencia': `${res.sensitivity?.power}%`, 'n req': res.n_required?.n_req });
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  const sens = result?.sensitivity;
  const nreq = result?.n_required;

  const fields: [string, string, string, React.Dispatch<React.SetStateAction<string>>][] = [
    ['X̄ actual',       xbar,        'step=0.0001', setXbar],
    ['σ proceso',       sigma,       'step=0.00001', setSigma],
    ['n subgrupo',      n,           'step=1 min=1', setN],
    ['t inspecc. (min)',t,           'step=1',       setT],
    ['LCS (UCL)',        ucl,         'step=0.0001', setUcl],
    ['LCI (LCL)',        lcl,         'step=0.0001', setLcl],
    ['X̄ nuevo (objetivo)', xbarNew, 'step=0.0001', setXbarNew],
    ['Potencia objetivo (%)', targetPower, 'step=1 min=1 max=99.99', setTargetPower],
    ['k (límites, σ)',   k,           'step=0.5 min=1', setK],
  ];

  return (
    <ModuleShell
      title="Plan de Mejora"
      subtitle="Sensibilidad del sistema · Curva de potencia · Tamaño de subgrupo óptimo"
      templateConfig={{
        module: 'mejora',
        getParams: () => ({ xbar, sigma, n, t, ucl, lcl, xbarNew, targetPower, k }),
        onLoad: (p: any) => {
          if (p.xbar) setXbar(p.xbar); if (p.sigma) setSigma(p.sigma);
          if (p.n) setN(p.n); if (p.t) setT(p.t);
          if (p.ucl) setUcl(p.ucl); if (p.lcl) setLcl(p.lcl);
          if (p.xbarNew) setXbarNew(p.xbarNew);
          if (p.targetPower) setTargetPower(p.targetPower);
          if (p.k) setK(p.k);
        },
      }}
      leftPanel={
        <>
          <div className="space-y-2">
            {fields.map(([label, val, attrs, setter]) => {
              const attrsObj = Object.fromEntries(attrs.split(' ').map(a => {
                const [k, v] = a.split('=');
                return [k, v ?? true];
              }));
              return (
                <div key={label}>
                  <label className="text-xs text-gray-600 block mb-0.5">{label}</label>
                  <input type="number" value={val}
                    onChange={e => setter(e.target.value)}
                    {...attrsObj}
                    className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-600" />
                </div>
              );
            })}
          </div>

          <button onClick={run}
            className="w-full bg-green-700 hover:bg-green-800 text-white font-semibold py-2.5 rounded-lg text-sm transition-colors">
            {loading ? 'Calculando…' : 'Analizar Potencia'}
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
            <>
              {/* Corrimiento */}
              <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
                <h3 className="text-sm font-bold text-gray-800 mb-3">Corrimiento del proceso</h3>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    ['Δ real (lb)', result.delta_real?.toFixed(5)],
                    ['Δ en σ', `${result.delta_sigma?.toFixed(4)}σ`],
                  ].map(([l, v]) => (
                    <div key={l} className="bg-gray-50 rounded-lg p-2.5">
                      <p className="text-xs text-gray-500">{l}</p>
                      <p className="font-semibold text-gray-900 text-sm font-mono">{v}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Sensibilidad */}
              {sens && (
                <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
                  <h3 className="text-sm font-bold text-gray-800 mb-3">Sensibilidad con n = {n}</h3>
                  <div className="grid grid-cols-3 gap-2">
                    {[
                      ['Potencia', `${sens.power}%`],
                      ['β (error II)', `${sens.beta}%`],
                      ['ARL', sens.nrl != null ? sens.nrl.toFixed(2) : '—'],
                      ['ATS (min)', sens.ats_min != null ? sens.ats_min.toFixed(1) : '—'],
                      ['ATS (h)', sens.ats_h != null ? sens.ats_h.toFixed(2) : '—'],
                      ['z', sens.z_val != null ? sens.z_val.toFixed(4) : '—'],
                    ].map(([l, v]) => (
                      <div key={l} className="bg-gray-50 rounded-lg p-2.5">
                        <p className="text-xs text-gray-500">{l}</p>
                        <p className="font-semibold text-gray-900 text-sm font-mono">{v}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* n requerido */}
              {nreq && (
                <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
                  <h3 className="text-sm font-bold text-gray-800 mb-3">
                    Subgrupo requerido para {targetPower}% de potencia
                  </h3>
                  <div className="grid grid-cols-3 gap-2">
                    {[
                      ['n actual', n],
                      ['n requerido', nreq.n_req >= 999999 ? '∞' : nreq.n_req],
                      ['n intermedio', nreq.n_half],
                      ['Pot. actual', `${nreq.pwr_curr}%`],
                      ['Pot. n½', `${nreq.pwr_half}%`],
                      ['z₁₋β', nreq.z1b?.toFixed(4)],
                    ].map(([l, v]) => (
                      <div key={l} className="bg-gray-50 rounded-lg p-2.5">
                        <p className="text-xs text-gray-500">{l}</p>
                        <p className={`font-semibold text-sm font-mono ${l === 'n requerido' ? 'text-green-700' : 'text-gray-900'}`}>{v}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          <ChartCard title="Curva de Potencia y Potencia vs n"
            src={result?.charts?.combined} loading={loading && !result} />
        </>
      }
    />
  );
}
