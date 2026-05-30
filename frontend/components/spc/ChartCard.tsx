'use client';

interface Props {
  title: string;
  src?: string;
  loading?: boolean;
}

export function ChartCard({ title, src, loading }: Props) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-100 bg-green-900">
        <h3 className="text-sm font-semibold text-white">{title}</h3>
      </div>
      <div className="p-3">
        {loading && (
          <div className="h-48 flex items-center justify-center text-gray-400 text-sm animate-pulse">
            Calculando…
          </div>
        )}
        {!loading && !src && (
          <div className="h-48 flex items-center justify-center text-gray-300 text-sm">
            Sin datos
          </div>
        )}
        {!loading && src && (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={src} alt={title} className="chart-img" />
        )}
      </div>
    </div>
  );
}
