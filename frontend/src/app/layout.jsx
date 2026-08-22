import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "./components/theme";
import { DatasetProvider } from "./components/DatasetContext";
import Sidebar from "./components/Sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "DataForge AI — Autonomous Governed Data Preparation",
  description: "Intelligent, governed, frugal data preparation & EDA Studio",
};

import AssistantWidget from "./components/AssistantWidget";

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} antialiased bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100 min-h-screen`}>
        <ThemeProvider>
          <DatasetProvider>
            <div className="flex min-h-screen">
              <Sidebar />
              <div className="flex-1 min-w-0 pt-14 lg:pt-0 lg:pl-60 overflow-x-hidden">{children}</div>
            </div>
            <AssistantWidget />
          </DatasetProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
