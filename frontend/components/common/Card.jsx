import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function Card({ children, className, title, subtitle, action, hover = true, ...props }) {
  return (
    <div
      className={twMerge(
        'bg-white rounded-xl p-5 border border-slate-200 shadow-xs text-slate-800',
        hover && 'saas-card-hover',
        className
      )}
      {...props}
    >
      {(title || action) && (
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
          <div>
            {title && <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2 tracking-tight">{title}</h3>}
            {subtitle && <p className="text-xs text-slate-500 mt-0.5 font-normal">{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      {children}
    </div>
  );
}
