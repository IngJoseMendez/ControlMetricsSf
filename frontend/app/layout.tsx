import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers/Providers";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ControlMetrics – Software SPC",
  description: "Plataforma de Control Estadístico de Procesos para la industria agroexportadora. Cartas de control, capacidad de proceso, muestreo MIL-STD-105E y más.",
  keywords: ["SPC", "control estadístico", "calidad", "Cp", "Cpk", "cartas de control", "normalidad"],
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es" className="h-full antialiased" suppressHydrationWarning>
      <body className={`${inter.className} min-h-full flex flex-col`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
