'use client';
import { useState } from 'react';
import { BookmarkPlus, FolderOpen, Trash2, ChevronDown, ChevronUp } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useLang } from '@/contexts/LangContext';
import { useTemplates } from '@/hooks/useTemplates';
import { GuestBanner } from '@/components/auth/GuestBanner';

interface Props {
  module: string;
  getParams: () => Record<string, unknown>;
  onLoad: (params: Record<string, unknown>) => void;
}

export function TemplatePanel({ module, getParams, onLoad }: Props) {
  const { mode } = useAuth();
  const { t } = useLang();
  const { templates, save, remove, loading } = useTemplates(module);
  const [open, setOpen] = useState(false);
  const [nameInput, setNameInput] = useState('');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleSave = async () => {
    if (!nameInput.trim()) return;
    setSaving(true);
    await save(nameInput.trim(), getParams());
    setNameInput('');
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
    setSaving(false);
  };

  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden">
      <button onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-3 py-2.5 bg-gray-50 dark:bg-gray-800 text-xs font-semibold text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-750 transition-colors">
        <div className="flex items-center gap-2">
          <FolderOpen className="w-3.5 h-3.5 text-green-700 dark:text-green-400" />
          {t.templates.title}
          {mode === 'user' && templates.length > 0 && (
            <span className="bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 px-1.5 py-0.5 rounded-full text-xs">
              {templates.length}
            </span>
          )}
        </div>
        {open ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
      </button>

      {open && (
        <div className="p-3 bg-white dark:bg-gray-900 space-y-3">
          {mode !== 'user' ? (
            <GuestBanner type="templates" />
          ) : (
            <>
              {/* Save new template */}
              <div className="flex gap-2">
                <input
                  value={nameInput}
                  onChange={e => setNameInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && handleSave()}
                  placeholder={t.templates.namePlaceholder}
                  className="flex-1 text-xs border border-gray-200 dark:border-gray-700 rounded-lg px-2.5 py-1.5 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-green-600" />
                <button onClick={handleSave} disabled={saving || !nameInput.trim()}
                  className="flex items-center gap-1 bg-green-700 hover:bg-green-800 disabled:opacity-50 text-white text-xs font-medium px-2.5 py-1.5 rounded-lg transition-colors whitespace-nowrap">
                  <BookmarkPlus className="w-3.5 h-3.5" />
                  {saved ? '✔' : t.templates.save.split(' ')[0]}
                </button>
              </div>

              {/* Template list */}
              {loading ? (
                <p className="text-xs text-gray-400 text-center py-2">…</p>
              ) : templates.length === 0 ? (
                <p className="text-xs text-gray-400 text-center py-2">{t.templates.none}</p>
              ) : (
                <div className="space-y-1.5 max-h-36 overflow-y-auto">
                  {templates.map(tpl => (
                    <div key={tpl.id}
                      className="flex items-center justify-between gap-2 bg-gray-50 dark:bg-gray-800 rounded-lg px-2.5 py-1.5">
                      <span className="text-xs text-gray-700 dark:text-gray-300 truncate flex-1">{tpl.name}</span>
                      <div className="flex gap-1 flex-shrink-0">
                        <button onClick={() => onLoad(tpl.params)}
                          className="text-xs text-green-700 dark:text-green-400 hover:underline font-medium">
                          {t.templates.load}
                        </button>
                        <button onClick={() => remove(tpl.id)}
                          className="text-gray-400 hover:text-red-500 transition-colors">
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
