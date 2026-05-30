'use client';
import { ReactNode } from 'react';

interface Props {
  title: string;
  subtitle: string;
  leftPanel: ReactNode;
  rightPanel: ReactNode;
}

export function ModuleShell({ title, subtitle, leftPanel, rightPanel }: Props) {
  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex-shrink-0">
        <h1 className="text-lg font-bold text-gray-900">{title}</h1>
        <p className="text-sm text-gray-500 mt-0.5">{subtitle}</p>
      </div>

      {/* Body: split layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left panel - inputs */}
        <aside className="w-72 flex-shrink-0 bg-white border-r border-gray-200 overflow-y-auto">
          <div className="p-5 space-y-4">{leftPanel}</div>
        </aside>

        {/* Right panel - results */}
        <section className="flex-1 overflow-y-auto bg-gray-50">
          <div className="p-5 space-y-5">{rightPanel}</div>
        </section>
      </div>
    </div>
  );
}
