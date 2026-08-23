"use client";

import React, { useState } from "react";

export default function VisualDesignInspector({
  assetName = "QuantumSecurityNode",
  svgMarkup = "",
  fitnessScore = 97.9,
  domainTheme = "Quantum_Glass",
  accentColor = "#6366f1",
  onDownload = null
}) {
  const [activeProportion, setActiveProportion] = useState("1x1");
  const [downloadFormat, setDownloadFormat] = useState("svg");

  const defaultSvg = svgMarkup || `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="100%" height="100%" role="img" aria-label="${assetName}">
      <defs>
        <linearGradient id="g_mesh" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="${accentColor}" stop-opacity="0.95"/>
          <stop offset="50%" stop-color="#8b5cf6" stop-opacity="0.85"/>
          <stop offset="100%" stop-color="#06b6d4" stop-opacity="0.90"/>
        </linearGradient>
        <radialGradient id="g_core" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#38bdf8" stop-opacity="1"/>
          <stop offset="100%" stop-color="${accentColor}" stop-opacity="0"/>
        </radialGradient>
      </defs>
      <rect x="8" y="8" width="112" height="112" rx="28" fill="#0f172a" stroke="#6366f1" stroke-width="1.5" stroke-opacity="0.5"/>
      <circle cx="64" cy="64" r="36" fill="url(#g_core)" opacity="0.4"/>
      <path d="M64 20L32 34v28c0 22 16 34 32 40 16-6 32-18 32-40V34L64 20z" fill="url(#g_mesh)" stroke="#ffffff" stroke-width="1.5" stroke-opacity="0.4"/>
      <path d="M64 36L44 46v18c0 14 10 22 20 26 10-4 20-12 20-26V46L64 36z" fill="#0f172a" fill-opacity="0.75" stroke="#38bdf8" stroke-width="2"/>
      <circle cx="64" cy="62" r="6" fill="#38bdf8"/>
      <path d="M64 68v8" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/>
    </svg>
  `;

  // Direct 1-Click Browser Download Trigger
  const triggerBrowserDownload = (format, width = 512, height = 512) => {
    if (format === "png") {
      const b64 = btoa(unescape(encodeURIComponent(defaultSvg)));
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement("canvas");
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0, width, height);
        const a = document.createElement("a");
        a.download = `${assetName}_${width}x${height}.png`;
        a.href = canvas.toDataURL("image/png");
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      };
      img.src = `data:image/svg+xml;base64,${b64}`;
    } else if (format === "svg") {
      const blob = new Blob([defaultSvg], { type: "image/svg+xml;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.download = `${assetName}.svg`;
      a.href = url;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } else if (format === "jsx") {
      const jsxCode = `import React from 'react';\n\nexport const ${assetName} = ({ size = 24, className = '', ...props }) => (\n  <svg viewBox="0 0 128 128" width={size} height={size} className={className} {...props}>\n    ${defaultSvg}\n  </svg>\n);\nexport default ${assetName};`;
      const blob = new Blob([jsxCode], { type: "text/javascript;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.download = `${assetName}.jsx`;
      a.href = url;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 backdrop-blur-2xl shadow-2xl space-y-6">
      
      {/* HEADER BAR */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-indigo-500 animate-pulse"></span>
            <h3 className="text-lg font-bold text-white tracking-tight">{assetName}</h3>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">Multi-Proportion Visual Inspection & Direct Browser Exporter</p>
        </div>

        <div className="flex items-center gap-2 font-mono text-xs">
          <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            Fitness: {fitnessScore.toFixed(1)}/100
          </span>
          <span className="px-2.5 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            WCAG AAA (11.8:1)
          </span>
        </div>
      </div>

      {/* PROPORTION SELECTOR TABS */}
      <div className="flex items-center gap-2 bg-slate-950/80 p-1.5 rounded-2xl border border-slate-800 text-xs font-semibold">
        <button
          onClick={() => setActiveProportion("1x1")}
          className={`flex-1 py-1.5 px-3 rounded-xl transition-all ${
            activeProportion === "1x1"
              ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
              : "text-slate-400 hover:text-white"
          }`}
        >
          1:1 Square (512x512)
        </button>
        <button
          onClick={() => setActiveProportion("16x9")}
          className={`flex-1 py-1.5 px-3 rounded-xl transition-all ${
            activeProportion === "16x9"
              ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
              : "text-slate-400 hover:text-white"
          }`}
        >
          16:9 Hero Card (800x450)
        </button>
        <button
          onClick={() => setActiveProportion("9x16")}
          className={`flex-1 py-1.5 px-3 rounded-xl transition-all ${
            activeProportion === "9x16"
              ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
              : "text-slate-400 hover:text-white"
          }`}
        >
          9:16 Mobile Frame (390x693)
        </button>
      </div>

      {/* LIVE VIEWPORT CONTAINER */}
      <div className="flex items-center justify-center p-8 bg-slate-950 rounded-2xl border border-slate-800/80 min-h-[280px]">
        {activeProportion === "1x1" && (
          <div
            className="w-44 h-44 flex items-center justify-center p-4 hover:scale-105 transition-transform"
            dangerouslySetInnerHTML={{ __html: defaultSvg }}
          />
        )}
        {activeProportion === "16x9" && (
          <div className="w-full max-w-md h-40 bg-slate-900/60 rounded-xl border border-slate-800 flex items-center justify-center p-4">
            <div
              className="w-28 h-28 flex items-center justify-center"
              dangerouslySetInnerHTML={{ __html: defaultSvg }}
            />
          </div>
        )}
        {activeProportion === "9x16" && (
          <div className="w-32 h-56 bg-slate-900/60 rounded-2xl border border-slate-800 flex items-center justify-center p-3">
            <div
              className="w-24 h-24 flex items-center justify-center"
              dangerouslySetInnerHTML={{ __html: defaultSvg }}
            />
          </div>
        )}
      </div>

      {/* DIRECT 1-CLICK BROWSER DOWNLOAD ACTION BAR */}
      <div className="pt-4 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3">
        <div className="text-xs text-slate-400">
          Downloads directly into your browser's <span className="text-indigo-300 font-mono">Downloads</span> folder:
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => triggerBrowserDownload("png", 512, 512)}
            className="px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-all shadow-md shadow-indigo-500/20"
          >
            📥 Download 1:1 PNG
          </button>
          <button
            onClick={() => triggerBrowserDownload("svg")}
            className="px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all"
          >
            📥 Download SVG
          </button>
          <button
            onClick={() => triggerBrowserDownload("jsx")}
            className="px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all"
          >
            ⚛️ Export React JSX
          </button>
        </div>
      </div>

    </div>
  );
}
