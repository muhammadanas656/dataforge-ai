"use client";
import { useEffect, useRef, useState, Fragment } from "react";
import { createPortal } from "react-dom";
import Link from "next/link";
import {
  Info,
  Search,
  Loader2,
  TrendingUp,
  TrendingDown,
  Minus,
  ChevronRight,
  Sparkles
} from "lucide-react";

const TIP_W = 256; // w-64

export function Tip({ text }) {
  const btn = useRef(null);
  const [open, setOpen] = useState(false);
  const [style, setStyle] = useState(null);

  const show = () => {
    if (!btn.current) return;
    const r = btn.current.getBoundingClientRect();
    const vw = window.innerWidth,
      vh = window.innerHeight;

    // Horizontal: center on the button, then clamp so it never crosses the edges
    let left = r.left + r.width / 2 - TIP_W / 2;
    left = Math.max(8, Math.min(left, vw - TIP_W - 8));

    // Vertical: prefer below; flip above if there isn't room
    const estH = 150;
    let top = r.bottom + 8;
    if (top + estH > vh - 8) top = Math.max(8, r.top - 8 - estH);

    setStyle({ position: "fixed", left, top, width: TIP_W, zIndex: 60 });
    setOpen(true);
  };
  const hide = () => setOpen(false);

  return (
    <>
      <button
        ref={btn}
        type="button"
        aria-label="More info"
        onMouseEnter={show}
        onMouseLeave={hide}
        onFocus={show}
        onBlur={hide}
        onKeyDown={(e) => e.key === "Escape" && hide()}
        className="rounded p-0.5 text-slate-400 hover:text-slate-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 dark:text-slate-500 dark:hover:text-slate-300 transition shrink-0"
      >
        <Info size={13} />
      </button>
      {open &&
        style &&
        typeof document !== "undefined" &&
        createPortal(
          <span
            role="tooltip"
            style={style}
            className="pointer-events-none rounded-xl bg-slate-900 p-3 text-left text-xs font-normal normal-case leading-relaxed tracking-normal text-slate-100 shadow-2xl dark:bg-slate-800 dark:border dark:border-slate-700 animate-fade-in"
          >
            {text}
          </span>,
          document.body
        )}
    </>
  );
}

// Backward compatibility alias
export const InfoTip = Tip;

const TONES = {
  good: "text-emerald-600 dark:text-emerald-400",
  warn: "text-amber-600 dark:text-amber-400",
  bad: "text-rose-600 dark:text-rose-400",
  neutral: "text-slate-900 dark:text-white",
  ai: "text-violet-600 dark:text-violet-400",
  info: "text-sky-600 dark:text-sky-400",
};

const BADGE_STYLES = {
  good: "bg-emerald-50 text-emerald-700 ring-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-300 dark:ring-emerald-500/30",
  success: "bg-emerald-50 text-emerald-700 ring-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-300 dark:ring-emerald-500/30",
  warn: "bg-amber-50 text-amber-700 ring-amber-200 dark:bg-amber-500/10 dark:text-amber-300 dark:ring-amber-500/30",
  warning: "bg-amber-50 text-amber-700 ring-amber-200 dark:bg-amber-500/10 dark:text-amber-300 dark:ring-amber-500/30",
  bad: "bg-rose-50 text-rose-700 ring-rose-200 dark:bg-rose-500/10 dark:text-rose-300 dark:ring-rose-500/30",
  danger: "bg-rose-50 text-rose-700 ring-rose-200 dark:bg-rose-500/10 dark:text-rose-300 dark:ring-rose-500/30",
  info: "bg-sky-50 text-sky-700 ring-sky-200 dark:bg-sky-500/10 dark:text-sky-300 dark:ring-sky-500/30",
  ai: "bg-violet-50 text-violet-700 ring-violet-200 dark:bg-violet-500/10 dark:text-violet-300 dark:ring-violet-500/30",
  primary: "bg-indigo-50 text-indigo-700 ring-indigo-200 dark:bg-indigo-500/10 dark:text-indigo-300 dark:ring-indigo-500/30",
  slate: "bg-slate-100 text-slate-600 ring-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:ring-slate-700",
  default: "bg-slate-100 text-slate-600 ring-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:ring-slate-700",
  indigo: "bg-indigo-50 text-indigo-700 ring-indigo-200 dark:bg-indigo-500/10 dark:text-indigo-300 dark:ring-indigo-500/30",
  green: "bg-emerald-50 text-emerald-700 ring-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-300 dark:ring-emerald-500/30",
  red: "bg-rose-50 text-rose-700 ring-rose-200 dark:bg-rose-500/10 dark:text-rose-300 dark:ring-rose-500/30",
  amber: "bg-amber-50 text-amber-700 ring-amber-200 dark:bg-amber-500/10 dark:text-amber-300 dark:ring-amber-500/30",
  blue: "bg-sky-50 text-sky-700 ring-sky-200 dark:bg-sky-500/10 dark:text-sky-300 dark:ring-sky-500/30",
  violet: "bg-violet-50 text-violet-700 ring-violet-200 dark:bg-violet-500/10 dark:text-violet-300 dark:ring-violet-500/30",
  premium: "bg-gradient-to-r from-indigo-50 to-purple-50 text-indigo-700 ring-indigo-200 dark:from-indigo-950/40 dark:to-purple-950/40 dark:text-indigo-300 dark:ring-indigo-800",
};

export function Badge({ tone, variant, children, pulse = false, size = "md", className = "" }) {
  const selectedStyle = BADGE_STYLES[tone || variant || "slate"] || BADGE_STYLES.slate;
  const sizeStyles = {
    sm: "px-2 py-0.5 text-[10px]",
    md: "px-2.5 py-0.5 text-[11px]",
    lg: "px-3 py-1 text-xs"
  };

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full font-semibold ring-1 min-w-0 ${selectedStyle} ${sizeStyles[size] || sizeStyles.md} ${
        pulse ? "animate-pulse-soft" : ""
      } ${className}`}
    >
      {children}
    </span>
  );
}

export function Card({ title, info, actions, children, className = "", pad = true, hover = false, glow = false }) {
  return (
    <section
      className={`relative min-w-0 overflow-visible rounded-2xl border border-slate-200/80 bg-white shadow-soft dark:border-slate-800 dark:bg-slate-900 transition-all duration-200 ${
        hover ? "hover-lift hover:border-slate-300 dark:hover:border-slate-700" : ""
      } ${glow ? "hover-glow" : ""} ${className}`}
    >
      {(title || actions) && (
        <header className="flex h-13 min-w-0 items-center justify-between gap-3 border-b border-slate-100 px-5 dark:border-slate-800">
          <h3 className="flex items-center gap-1.5 text-sm font-bold text-slate-800 dark:text-slate-100 min-w-0 truncate">
            <span className="truncate">{title}</span>
            {info && <Tip text={info} />}
          </h3>
          <div className="flex items-center gap-2 shrink-0">{actions}</div>
        </header>
      )}
      <div className={pad ? "p-5 min-w-0" : "min-w-0"}>{children}</div>
    </section>
  );
}

export function StatTile({
  label,
  value,
  sub,
  info,
  tone = "neutral",
  change,
  changeType = "neutral",
  icon: Icon,
  gradient = false
}) {
  const changeColors = {
    positive: "text-emerald-600 dark:text-emerald-400",
    negative: "text-rose-600 dark:text-rose-400",
    neutral: "text-slate-500 dark:text-slate-400",
  };

  const ChangeIcon =
    changeType === "positive" ? TrendingUp : changeType === "negative" ? TrendingDown : Minus;

  return (
    <div
      className={`min-w-0 rounded-2xl border border-slate-200/80 p-4 shadow-soft dark:border-slate-800 transition-all duration-200 hover-lift ${
        gradient
          ? "bg-gradient-to-br from-indigo-50/60 to-purple-50/60 dark:from-indigo-950/20 dark:to-purple-950/20"
          : "bg-white dark:bg-slate-900"
      }`}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 min-w-0 truncate">
          {Icon && (
            <div className="p-1 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 shrink-0">
              <Icon size={14} />
            </div>
          )}
          <span className="truncate">{label}</span>
          {info && <Tip text={info} />}
        </div>
        {change && (
          <div className={`flex items-center gap-0.5 text-xs font-semibold shrink-0 ${changeColors[changeType] || changeColors.neutral}`}>
            <ChangeIcon size={12} />
            <span>{change}</span>
          </div>
        )}
      </div>
      <div className={`text-2xl font-bold tabular-nums tracking-tight truncate ${TONES[tone] || TONES.neutral}`}>
        {value}
      </div>
      {sub && <div className="mt-1 text-xs text-slate-500 dark:text-slate-400 font-medium truncate">{sub}</div>}
    </div>
  );
}

/* Standardized controls */
export function Select({ value, onChange, children, className = "" }) {
  return (
    <select
      value={value}
      onChange={onChange}
      className={`h-9 rounded-xl border border-slate-200 bg-white px-3 text-xs font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-400 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 transition ${className}`}
    >
      {children}
    </select>
  );
}

export function SearchInput({ value, onChange, placeholder = "Search…", className = "" }) {
  return (
    <div className={`relative min-w-0 ${className}`}>
      <Search size={14} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
      <input
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="h-9 w-full rounded-xl border border-slate-200 bg-white pl-9 pr-3 text-xs text-slate-700 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-400 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 transition"
      />
    </div>
  );
}

export function Button({
  children,
  variant = "primary",
  size = "md",
  loading = false,
  icon: Icon,
  className = "",
  disabled,
  ...props
}) {
  const variants = {
    primary:
      "bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 text-white shadow-soft hover:shadow-medium focus:ring-indigo-500 disabled:bg-slate-300 dark:disabled:bg-slate-800",
    secondary:
      "bg-white text-slate-700 ring-1 ring-slate-200 hover:bg-slate-50 dark:bg-slate-800 dark:text-slate-200 dark:ring-slate-700 dark:hover:bg-slate-700 shadow-xs",
    danger:
      "bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-700 hover:to-red-700 text-white shadow-soft focus:ring-rose-500",
    ghost:
      "bg-transparent text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800",
  };

  const sizes = {
    sm: "h-8 px-3 text-xs gap-1.5",
    md: "h-9 px-4 text-xs gap-2",
    lg: "h-10 px-5 text-sm gap-2.5",
  };

  return (
    <button
      className={`inline-flex items-center justify-center font-bold rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-1 disabled:cursor-not-allowed disabled:opacity-50 shrink-0 ${
        variants[variant] || variants.primary
      } ${sizes[size] || sizes.md} ${className}`}
      disabled={loading || disabled}
      {...props}
    >
      {loading ? (
        <Loader2 className="animate-spin shrink-0" size={size === "sm" ? 13 : size === "lg" ? 16 : 14} />
      ) : Icon ? (
        <Icon size={size === "sm" ? 13 : size === "lg" ? 16 : 14} className="shrink-0" />
      ) : null}
      {children}
    </button>
  );
}

export function Skeleton({ className = "" }) {
  return <div className={`animate-pulse rounded-xl bg-slate-200 dark:bg-slate-800 ${className}`} />;
}

export function EmptyState({ icon: Icon, title, description, action, className = "" }) {
  return (
    <div className={`flex flex-col items-center justify-center py-12 px-4 text-center animate-fade-in ${className}`}>
      {Icon && (
        <div className="mb-4 p-3.5 rounded-2xl bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-950/40 dark:to-purple-950/40 text-indigo-600 dark:text-indigo-400 shadow-soft">
          <Icon size={36} />
        </div>
      )}
      <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100 mb-1.5">{title}</h3>
      {description && (
        <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mb-4 leading-relaxed">
          {description}
        </p>
      )}
      {action}
    </div>
  );
}

export function PageHeader({ title, subtitle, actions, breadcrumbs, className = "" }) {
  return (
    <div className={`mb-6 animate-fade-in ${className}`}>
      {breadcrumbs && (
        <nav className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 mb-2.5 font-medium">
          {breadcrumbs.map((crumb, i) => (
            <Fragment key={i}>
              {i > 0 && <ChevronRight size={12} className="text-slate-400 shrink-0" />}
              {crumb.href ? (
                <Link href={crumb.href} className="hover:text-indigo-600 dark:hover:text-indigo-400 transition truncate">
                  {crumb.label}
                </Link>
              ) : (
                <span className="font-semibold text-slate-700 dark:text-slate-300 truncate">{crumb.label}</span>
              )}
            </Fragment>
          ))}
        </nav>
      )}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-slate-100 truncate">
            {title}
          </h1>
          {subtitle && (
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">
              {subtitle}
            </p>
          )}
        </div>
        {actions && <div className="flex items-center gap-2 shrink-0">{actions}</div>}
      </div>
    </div>
  );
}

export function ResponsiveGrid({ children, cols = { sm: 1, md: 2, lg: 3, xl: 4 }, gap = 4, className = "" }) {
  return (
    <div className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 ${className}`}>
      {children}
    </div>
  );
}

export function GradientSparklesIcon({ size = 20, className = "" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
      <defs>
        <linearGradient id="sparkleGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#6366f1" />
          <stop offset="100%" stopColor="#a855f7" />
        </linearGradient>
      </defs>
      <path
        d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2Z"
        fill="url(#sparkleGradient)"
      />
    </svg>
  );
}
