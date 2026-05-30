'use client';
import { ReactNode } from 'react';
import { TemplatePanel } from '@/components/spc/TemplatePanel';

export interface TemplateConfig {
  module: string;
  getParams: () => Record<string, unknown>;
  onLoad: (params: Record<string, unknown>) => void;
}

interface Props {
  title: string;
  subtitle: string;
  leftPanel: ReactNode;
  rightPanel: ReactNode;
  templateConfig?: TemplateConfig;
}

export function ModuleShell({ title, subtitle, leftPanel, rightPanel, templateConfig }: Props) {
  return (
    <div className="flex flex-col md:h-full">
      {/* Header */}
      <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 px-4 md:px-6 py-3 md:py-4 flex-shrink-0">
        <h1 className="text-base md:text-lg font-bold text-gray-900 dark:text-gray-100 leading-tight">{title}</h1>
        <p className="text-xs md:text-sm text-gray-500 dark:text-gray-400 mt-0.5">{subtitle}</p>
      </div>

      {/* Body */}
      <div className="flex flex-col md:flex-row flex-1 md:overflow-hidden">
        {/* Left panel */}
        <aside className="w-full md:w-72 flex-shrink-0 bg-white dark:bg-gray-900 border-b md:border-b-0 md:border-r border-gray-200 dark:border-gray-800 md:overflow-y-auto">
          <div className="p-4 md:p-5 space-y-4">
            {leftPanel}
            {templateConfig && (
              <TemplatePanel
                module={templateConfig.module}
                getParams={templateConfig.getParams}
                onLoad={templateConfig.onLoad}
              />
            )}
          </div>
        </aside>

        {/* Right panel */}
        <section className="flex-1 bg-gray-50 dark:bg-gray-950 md:overflow-y-auto">
          <div className="p-4 md:p-5 space-y-4 md:space-y-5">{rightPanel}</div>
        </section>
      </div>
    </div>
  );
}
