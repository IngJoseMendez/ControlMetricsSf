const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? 'Error del servidor');
  }
  return res.json();
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(res.statusText);
  return res.json();
}

export const api = {
  normalidad: {
    analizar: (data: number[], alpha = 0.05) =>
      post('/api/normalidad', { data, alpha }),
    demo: () => get<{ data: number[] }>('/api/normalidad/demo'),
  },
  cartasXR: {
    calcular: (body: object) => post('/api/cartas-xr', body),
    power: (body: object) => post('/api/cartas-xr/power', body),
    demoFase1: () => get<{ data: number[][] }>('/api/cartas-xr/demo/fase1'),
    demoFase2: () => get<{ data: number[][] }>('/api/cartas-xr/demo/fase2'),
  },
  cartasPnpu: {
    calcular: (body: object) => post('/api/cartas-pnpu', body),
  },
  cartaC: {
    calcular: (body: object) => post('/api/carta-c', body),
    demo: () => get<{ defects: number[]; tipos: Record<string, number> }>('/api/carta-c/demo'),
  },
  capacidad: {
    calcular: (body: object) => post('/api/capacidad', body),
    demo: () => get<{ data: number[]; sigma: number }>('/api/capacidad/demo'),
  },
  muestreo: {
    calcular: (body: object) => post('/api/muestreo', body),
    demo: () => get<{ n_lote: number; nac: number }>('/api/muestreo/demo'),
  },
  mejora: {
    calcular: (body: object) => post('/api/mejora', body),
  },
};
