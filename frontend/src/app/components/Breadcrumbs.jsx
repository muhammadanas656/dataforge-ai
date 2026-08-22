"use client";
import Link from "next/link";
import { Fragment } from "react";
import { ChevronRight } from "lucide-react";

export function Breadcrumbs({ crumbs }) {
  if (!crumbs || crumbs.length === 0) return null;

  return (
    <nav className="mb-4 flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 select-none">
      {crumbs.map((c, i) => (
        <Fragment key={i}>
          {i > 0 && <ChevronRight size={12} className="text-slate-300 dark:text-slate-600" />}
          {c.href ? (
            <Link href={c.href} className="hover:text-indigo-600 dark:hover:text-indigo-400 transition font-medium">
              {c.label}
            </Link>
          ) : (
            <span className="font-semibold text-slate-800 dark:text-slate-200">
              {c.label}
            </span>
          )}
        </Fragment>
      ))}
    </nav>
  );
}
