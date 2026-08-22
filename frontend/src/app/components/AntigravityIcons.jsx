"use client";
import React from "react";

/**
 * Antigravity Spatial & Custom Vector Icon Suite
 * Handcrafted 3D isometric, glassmorphic, and gradient-infused iconography.
 */

// 1. Auto-Pilot Quantum Warp Core
export function IconAutopilot({ size = 20, className = "" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={`shrink-0 ${className}`}>
      <defs>
        <linearGradient id="ap_grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#06b6d4" />
          <stop offset="50%" stopColor="#6366f1" />
          <stop offset="100%" stopColor="#a855f7" />
        </linearGradient>
      </defs>
      <circle cx="12" cy="12" r="10" stroke="url(#ap_grad)" strokeWidth="1.5" strokeDasharray="3 2" opacity="0.6" />
      <circle cx="12" cy="12" r="5.5" fill="url(#ap_grad)" />
      <path d="M12 2 L14 8 L20 10 L15 14 L16 20 L12 16 L8 20 L9 14 L4 10 L10 8 Z" fill="#ffffff" opacity="0.9" transform="scale(0.5) translate(12, 12)" />
      <circle cx="12" cy="12" r="2" fill="#ffffff" />
    </svg>
  );
}

// 2. Spatial Data Ingest Cylinder
export function IconIngest({ size = 20, className = "" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={`shrink-0 ${className}`}>
      <defs>
        <linearGradient id="ing_grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#38bdf8" />
          <stop offset="100%" stopColor="#0284c7" />
        </linearGradient>
      </defs>
      <ellipse cx="12" cy="6" rx="8" ry="3.5" fill="url(#ing_grad)" fillOpacity="0.8" stroke="#38bdf8" strokeWidth="1.2" />
      <path d="M4 6 v6 c0 2 3.6 3.5 8 3.5 s8 -1.5 8 -3.5 V6" stroke="#0284c7" strokeWidth="1.2" fill="none" />
      <path d="M4 12 v6 c0 2 3.6 3.5 8 3.5 s8 -1.5 8 -3.5 V12" stroke="#0369a1" strokeWidth="1.2" fill="none" />
      <circle cx="12" cy="6" r="1.5" fill="#ffffff" />
    </svg>
  );
}

// 3. Holographic Profiler & Scanner Eye (CP1)
export function IconProfiler({ size = 20, className = "" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={`shrink-0 ${className}`}>
      <defs>
        <linearGradient id="prof_grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#34d399" />
          <stop offset="100%" stopColor="#059669" />
        </linearGradient>
      </defs>
      <rect x="3" y="4" width="18" height="16" rx="4" stroke="url(#prof_grad)" strokeWidth="1.5" strokeDasharray="4 2" />
      <path d="M7 12 h10" stroke="#34d399" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M12 7 v10" stroke="#34d399" strokeWidth="1.2" strokeLinecap="round" opacity="0.6" />
      <circle cx="12" cy="12" r="3" fill="#10b981" />
      <circle cx="12" cy="12" r="1" fill="#ffffff" />
    </svg>
  );
}

// 4. Semantic Multi-Tier Taxonomy Dictionary (CP2)
export function IconDictionary({ size = 20, className = "" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={`shrink-0 ${className}`}>
      <defs>
        <linearGradient id="dict_grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#818cf8" />
          <stop offset="100%" stopColor="#4f46e5" />
        </linearGradient>
      </defs>
      <path d="M4 19.5 A2.5 2.5 0 0 1 6.5 17 H20" stroke="url(#dict_grad)" strokeWidth="1.5" />
      <path d="M6.5 2 H20 v20 H6.5 A2.5 2.5 0 0 1 4 19.5 v-15 A2.5 2.5 0 0 1 6.5 2 z" fill="url(#dict_grad)" fillOpacity="0.2" stroke="url(#dict_grad)" strokeWidth="1.5" />
      <line x1="8" y1="7" x2="16" y2="7" stroke="#818cf8" strokeWidth="1.5" strokeLinecap="round" />
      <line x1="8" y1="11" x2="14" y2="11" stroke="#818cf8" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}

// 5. Precision Cleaning Transformer & Critic (CP3)
export function IconCleaningPlan({ size = 20, className = "" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={`shrink-0 ${className}`}>
      <defs>
        <linearGradient id="clean_grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#f59e0b" />
          <stop offset="100%" stopColor="#d97706" />
        </linearGradient>
      </defs>
      <polygon points="12,2 15,8 21,9 17,14 18,20 12,17 6,20 7,14 3,9 9,8" fill="url(#clean_grad)" fillOpacity="0.3" stroke="url(#clean_grad)" strokeWidth="1.5" />
      <circle cx="12" cy="11" r="3" fill="#f59e0b" />
      <circle cx="12" cy="11" r="1.2" fill="#ffffff" />
    </svg>
  );
}

// 6. Cryptographic Governance Shield (CP4)
export function IconGovernance({ size = 20, className = "" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={`shrink-0 ${className}`}>
      <defs>
        <linearGradient id="gov_grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#10b981" />
          <stop offset="100%" stopColor="#047857" />
        </linearGradient>
      </defs>
      <path d="M12 2 L20 6 v6 c0 5.5 -3.5 10 -8 11 C7.5 22 4 17.5 4 12 V6 Z" fill="url(#gov_grad)" fillOpacity="0.2" stroke="url(#gov_grad)" strokeWidth="1.5" />
      <path d="M9 12 l2 2 4 -4" stroke="#10b981" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

// 7. Causal DAG & Spatial Constellation EDA
export function IconCausalEDA({ size = 20, className = "" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={`shrink-0 ${className}`}>
      <defs>
        <linearGradient id="eda_grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#c084fc" />
          <stop offset="50%" stopColor="#818cf8" />
          <stop offset="100%" stopColor="#38bdf8" />
        </linearGradient>
      </defs>
      {/* Causal DAG Nodes & Edges */}
      <line x1="6" y1="18" x2="12" y2="6" stroke="#818cf8" strokeWidth="1.5" strokeDasharray="2 2" />
      <line x1="12" y1="6" x2="18" y2="18" stroke="#c084fc" strokeWidth="1.5" />
      <line x1="6" y1="18" x2="18" y2="18" stroke="#38bdf8" strokeWidth="1.5" />
      
      <circle cx="12" cy="6" r="3.5" fill="#a855f7" stroke="#ffffff" strokeWidth="1" />
      <circle cx="6" cy="18" r="3.5" fill="#38bdf8" stroke="#ffffff" strokeWidth="1" />
      <circle cx="18" cy="18" r="3.5" fill="#6366f1" stroke="#ffffff" strokeWidth="1" />
    </svg>
  );
}

// 8. Multi-Beam Ultra-Penetration Web Radar
export function IconWebRadar({ size = 20, className = "" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={`shrink-0 ${className}`}>
      <defs>
        <linearGradient id="radar_grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#06b6d4" />
          <stop offset="100%" stopColor="#3b82f6" />
        </linearGradient>
      </defs>
      <circle cx="12" cy="12" r="10" stroke="url(#radar_grad)" strokeWidth="1.5" opacity="0.4" />
      <circle cx="12" cy="12" r="6" stroke="url(#radar_grad)" strokeWidth="1.5" opacity="0.7" />
      <circle cx="12" cy="12" r="2.5" fill="#06b6d4" />
      <path d="M12 12 L19 5" stroke="#38bdf8" strokeWidth="2" strokeLinecap="round" />
      <circle cx="19" cy="5" r="2" fill="#22d3ee" className="animate-pulse-soft" />
    </svg>
  );
}

// 9. TRIZ 39x40 Invention Prism
export function IconTrizInvention({ size = 20, className = "" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={`shrink-0 ${className}`}>
      <defs>
        <linearGradient id="triz_grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#ec4899" />
          <stop offset="50%" stopColor="#a855f7" />
          <stop offset="100%" stopColor="#6366f1" />
        </linearGradient>
      </defs>
      <polygon points="12,2 22,9 18,21 6,21 2,9" fill="url(#triz_grad)" fillOpacity="0.25" stroke="url(#triz_grad)" strokeWidth="1.5" />
      <polygon points="12,7 18,11 15,18 9,18 6,11" fill="url(#triz_grad)" fillOpacity="0.6" stroke="#ffffff" strokeWidth="0.8" />
    </svg>
  );
}

// 10. Monte Carlo Multi-Path Probability Wave
export function IconMonteCarlo({ size = 20, className = "" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={`shrink-0 ${className}`}>
      <defs>
        <linearGradient id="mc_grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#14b8a6" />
          <stop offset="100%" stopColor="#06b6d4" />
        </linearGradient>
      </defs>
      <path d="M3 18 C6 18, 9 6, 12 6 C15 6, 18 18, 21 18" stroke="url(#mc_grad)" strokeWidth="2" strokeLinecap="round" fill="none" />
      <path d="M3 14 C7 14, 10 10, 12 10 C14 10, 17 14, 21 14" stroke="#2dd4bf" strokeWidth="1.2" strokeDasharray="2 2" fill="none" opacity="0.6" />
      <circle cx="12" cy="6" r="2.5" fill="#14b8a6" />
    </svg>
  );
}

// 11. Standalone Pipeline Code Exporter Icon
export function IconCodeExporter({ size = 20, className = "" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={`shrink-0 ${className}`}>
      <defs>
        <linearGradient id="code_grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#f43f5e" />
          <stop offset="100%" stopColor="#fb7185" />
        </linearGradient>
      </defs>
      <rect x="3" y="4" width="18" height="16" rx="3" stroke="url(#code_grad)" strokeWidth="1.5" fill="url(#code_grad)" fillOpacity="0.15" />
      <path d="M8 10 L6 12 L8 14" stroke="#f43f5e" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M16 10 L18 12 L16 14" stroke="#f43f5e" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      <line x1="13" y1="9" x2="11" y2="15" stroke="#fb7185" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}
