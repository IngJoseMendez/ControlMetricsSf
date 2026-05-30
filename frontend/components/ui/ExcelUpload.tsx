'use client';
import { useRef, useState } from 'react';
import { FileSpreadsheet, Download, Loader2 } from 'lucide-react';

const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

interface Props {
  module: string;
  onData: (data: unknown) => void;
  onError?: (msg: string) => void;
}

export function ExcelUpload({ module, onData, onError }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [loading, setLoading] = useState(false);
  const [filename, setFilename] = useState('');

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setFilename(file.name);
    setLoading(true);
    try {
      const form = new FormData();
      form.append('file', file);
      const res = await fetch(`${BASE}/api/excel/${module}`, { method: 'POST', body: form });
      const json = await res.json();
      if (!res.ok) throw new Error(json.detail ?? 'Error al leer el archivo');
      onData(json);
    } catch (err: any) {
      onError?.(err.message);
      setFilename('');
    } finally {
      setLoading(false);
      if (inputRef.current) inputRef.current.value = '';
    }
  };

  const downloadTemplate = () => {
    window.open(`${BASE}/api/excel/plantilla/${module}`, '_blank');
  };

  return (
    <div className="flex gap-2">
      {/* Upload button */}
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        disabled={loading}
        className="flex-1 flex items-center justify-center gap-2 border border-dashed border-green-600 dark:border-green-700 text-green-700 dark:text-green-400 hover:bg-green-50 dark:hover:bg-green-900/20 rounded-lg px-3 py-2 text-xs font-medium transition-colors disabled:opacity-50"
      >
        {loading
          ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
          : <FileSpreadsheet className="w-3.5 h-3.5" />}
        {loading ? 'Leyendo…' : filename ? filename : '📂 Cargar Excel'}
      </button>

      {/* Template download */}
      <button
        type="button"
        onClick={downloadTemplate}
        title="Descargar plantilla Excel"
        className="flex items-center justify-center gap-1.5 border border-gray-200 dark:border-gray-700 text-gray-500 dark:text-gray-400 hover:border-green-600 hover:text-green-700 dark:hover:text-green-400 rounded-lg px-2.5 py-2 text-xs transition-colors"
      >
        <Download className="w-3.5 h-3.5" />
        <span>Plantilla</span>
      </button>

      <input
        ref={inputRef}
        type="file"
        accept=".xlsx,.xls"
        className="hidden"
        onChange={handleFile}
      />
    </div>
  );
}
