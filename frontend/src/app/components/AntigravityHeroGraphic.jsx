"use client";
import React from "react";

export default function AntigravityHeroGraphic({ className = "" }) {
  return (
    <div className={`relative flex items-center justify-center ${className}`}>
      {/* Ambient background glow */}
      <div className="absolute -inset-4 rounded-full bg-gradient-to-r from-cyan-500/20 via-indigo-500/20 to-purple-500/20 blur-2xl animate-pulse-soft" />

      {/* Vector SVG Antigravity Spatial Graphic */}
      <svg
        viewBox="0 0 400 240"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="relative w-full max-w-md animate-float drop-shadow-[0_15px_30px_rgba(0,0,0,0.35)]"
      >
        <defs>
          <linearGradient id="orbGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.9" />
            <stop offset="50%" stopColor="#6366f1" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#a855f7" stopOpacity="0.9" />
          </linearGradient>

          <linearGradient id="planeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#818cf8" stopOpacity="0.05" />
          </linearGradient>

          <filter id="glowFilter" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="6" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* Isometric Grid Floor */}
        <g opacity="0.35">
          <path d="M 50 180 L 200 110 L 350 180 L 200 235 Z" fill="url(#planeGrad)" stroke="#6366f1" strokeWidth="1" strokeDasharray="4 4" />
          <line x1="200" y1="110" x2="200" y2="235" stroke="#06b6d4" strokeWidth="1" opacity="0.5" />
          <line x1="125" y1="145" x2="275" y2="207" stroke="#a855f7" strokeWidth="0.8" opacity="0.4" />
          <line x1="275" y1="145" x2="125" y2="207" stroke="#a855f7" strokeWidth="0.8" opacity="0.4" />
        </g>

        {/* Orbit Rings (3D Ellipses) */}
        <ellipse
          cx="200"
          cy="95"
          rx="120"
          ry="45"
          fill="none"
          stroke="#06b6d4"
          strokeWidth="1.5"
          strokeDasharray="6 8"
          transform="rotate(-15 200 95)"
          opacity="0.75"
        />
        <ellipse
          cx="200"
          cy="95"
          rx="90"
          ry="32"
          fill="none"
          stroke="#a855f7"
          strokeWidth="1.5"
          transform="rotate(25 200 95)"
          opacity="0.6"
        />

        {/* Central Weightless Core Orb */}
        <circle cx="200" cy="95" r="32" fill="url(#orbGrad)" filter="url(#glowFilter)" />
        <circle cx="188" cy="85" r="10" fill="#ffffff" opacity="0.45" />

        {/* Floating Data Cubes / Isometric Nodes */}
        {/* Node 1: Left */}
        <g transform="translate(100, 70)" className="animate-pulse-soft">
          <polygon points="15,0 30,8 15,16 0,8" fill="#38bdf8" opacity="0.9" />
          <polygon points="0,8 15,16 15,32 0,24" fill="#0284c7" opacity="0.8" />
          <polygon points="30,8 15,16 15,32 30,24" fill="#0369a1" opacity="0.8" />
        </g>

        {/* Node 2: Top Right */}
        <g transform="translate(270, 45)" className="animate-pulse-soft">
          <polygon points="12,0 24,6 12,12 0,6" fill="#c084fc" opacity="0.9" />
          <polygon points="0,6 12,12 12,24 0,18" fill="#9333ea" opacity="0.8" />
          <polygon points="24,6 12,12 12,24 24,18" fill="#7e22ce" opacity="0.8" />
        </g>

        {/* Node 3: Bottom Center Floating */}
        <g transform="translate(235, 140)">
          <polygon points="10,0 20,5 10,10 0,5" fill="#34d399" opacity="0.9" />
          <polygon points="0,5 10,10 10,20 0,15" fill="#059669" opacity="0.8" />
          <polygon points="20,5 10,10 10,20 20,15" fill="#047857" opacity="0.8" />
        </g>

        {/* Causal Vector Connecting Beams */}
        <path d="M 115 85 Q 160 90 180 95" stroke="#38bdf8" strokeWidth="1.2" strokeDasharray="3 3" opacity="0.8" />
        <path d="M 280 60 Q 240 75 220 90" stroke="#c084fc" strokeWidth="1.2" strokeDasharray="3 3" opacity="0.8" />
        <path d="M 200 127 Q 215 140 245 150" stroke="#34d399" strokeWidth="1.2" strokeDasharray="3 3" opacity="0.8" />
      </svg>
    </div>
  );
}
