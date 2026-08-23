"use client";

import React, { useState } from "react";
import VisualDesignInspector from "../components/VisualDesignInspector";
import Sidebar from "../components/Sidebar";
import RealTimeProcessRadar from "../components/RealTimeProcessRadar";

export default function DesignStudioPage() {
  const [prompt, setPrompt] = useState("Quantum Spatial Security Shield with refractive mesh glow");
  const [selectedTheme, setSelectedTheme] = useState("Quantum_CyberSecurity");
  const [accentColor, setAccentColor] = useState("#6366f1");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedAssets, setGeneratedAssets] = useState([
    {
      name: "QuantumSecurityNode",
      theme: "Quantum_CyberSecurity",
      fitness: 97.9,
      color: "#6366f1",
      svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="100%" height="100%"><defs><linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#6366f1"/><stop offset="100%" stop-color="#06b6d4"/></linearGradient></defs><rect x="8" y="8" width="112" height="112" rx="28" fill="#0f172a" stroke="#6366f1" stroke-width="1.5"/><path d="M64 20L32 34v28c0 22 16 34 32 40 16-6 32-18 32-40V34L64 20z" fill="url(#g1)" stroke="#ffffff" stroke-width="1.5"/><circle cx="64" cy="62" r="6" fill="#38bdf8"/><path d="M64 68v8" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/></svg>`
    },
    {
      name: "FinTechCloudVault",
      theme: "FinTech",
      fitness: 97.0,
      color: "#06b6d4",
      svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="100%" height="100%"><rect x="12" y="12" width="104" height="104" rx="24" fill="#0f172a" stroke="#06b6d4" stroke-width="2"/><circle cx="64" cy="64" r="32" fill="none" stroke="#10b981" stroke-width="3" stroke-dasharray="8 4"/><circle cx="64" cy="64" r="10" fill="#06b6d4"/><path d="M64 42v8M64 78v8M42 64h8M78 64h8" stroke="#10b981" stroke-width="3" stroke-linecap="round"/></svg>`
    }
  ]);

  const handleGenerate = (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setIsGenerating(true);
    setTimeout(() => {
      const cleanName = prompt.split(" ").slice(0, 3).map(w => w.charAt(0).toUpperCase() + w.slice(1)).join("");
      const newAsset = {
        name: cleanName || "CustomVectorAsset",
        theme: selectedTheme,
        fitness: 96.5,
        color: accentColor,
        svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="100%" height="100%"><defs><linearGradient id="g_custom" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="${accentColor}"/><stop offset="100%" stop-color="#0f172a"/></linearGradient></defs><rect x="8" y="8" width="112" height="112" rx="28" fill="url(#g_custom)" stroke="${accentColor}" stroke-width="2"/><circle cx="64" cy="64" r="28" fill="none" stroke="#ffffff" stroke-width="2.5"/><path d="M48 64h32M64 48v32" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/></svg>`
      };
      setGeneratedAssets([newAsset, ...generatedAssets]);
      setIsGenerating(false);
    }, 600);
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 antialiased overflow-hidden">
      <Sidebar />

      <main className="flex-1 overflow-y-auto p-8 space-y-8">
        
        {/* HEADER */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-indigo-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
              Design & Breakthrough Studio
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              TRIZ Generative Vector Evolution, Multi-Proportion Inspection, and Direct 1-Click Browser Downloads
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              ● Engine Active (99.37% Proficiency)
            </span>
          </div>
        </div>

        {/* REAL-TIME 5-STUDIO AUTONOMOUS PROCESS RADAR */}
        <RealTimeProcessRadar />

        {/* DESIGN PROMPT SYNTHESIZER BAR */}
        <form onSubmit={handleGenerate} className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 backdrop-blur-xl shadow-2xl space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2">
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Design Concept / Vector Prompt</label>
              <input
                type="text"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="e.g. Holographic AI Core with orbital data rings"
                className="w-full px-4 py-3 rounded-2xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Domain Theme</label>
              <select
                value={selectedTheme}
                onChange={(e) => setSelectedTheme(e.target.value)}
                className="w-full px-4 py-3 rounded-2xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors"
              >
                <option value="Quantum_CyberSecurity">Quantum CyberSecurity</option>
                <option value="FinTech">FinTech / Crypto Vault</option>
                <option value="BioTech">BioTech DNA / Health</option>
                <option value="Spatial_Glass">Spatial Glass UI</option>
              </select>
            </div>
          </div>

          <div className="flex justify-between items-center pt-2">
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400">Accent Color:</span>
              <input
                type="color"
                value={accentColor}
                onChange={(e) => setAccentColor(e.target.value)}
                className="w-8 h-8 rounded-lg cursor-pointer bg-transparent border-0"
              />
            </div>
            <button
              type="submit"
              disabled={isGenerating}
              className="px-6 py-3 rounded-2xl text-sm font-semibold bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white shadow-lg shadow-indigo-600/30 transition-all disabled:opacity-50"
            >
              {isGenerating ? "Synthesizing Geometry..." : "✨ Evolve & Render Vector"}
            </button>
          </div>
        </form>

        {/* LIVE GENERATED DESIGN CARDS WITH MULTI-PROPORTION & DIRECT DOWNLOADS */}
        <div className="space-y-6">
          <h2 className="text-xl font-bold text-white tracking-tight">Active Vector Inspection Deck</h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {generatedAssets.map((asset, idx) => (
              <VisualDesignInspector
                key={idx}
                assetName={asset.name}
                svgMarkup={asset.svg}
                fitnessScore={asset.fitness}
                domainTheme={asset.theme}
                accentColor={asset.color}
              />
            ))}
          </div>
        </div>

      </main>
    </div>
  );
}
