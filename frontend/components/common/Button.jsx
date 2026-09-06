import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

const buttonVariants = {
  primary: 'bg-blue-600 hover:bg-blue-700 text-white font-semibold shadow-xs border border-blue-700/30',
  secondary: 'bg-white hover:bg-slate-50 text-slate-700 font-medium border border-slate-300 shadow-2xs',
  success: 'bg-emerald-600 hover:bg-emerald-700 text-white font-medium shadow-xs border border-emerald-700/30',
  danger: 'bg-rose-600 hover:bg-rose-700 text-white font-medium shadow-xs border border-rose-700/30',
  warning: 'bg-amber-500 hover:bg-amber-600 text-slate-950 font-semibold shadow-xs border border-amber-600/30',
  ghost: 'bg-transparent hover:bg-slate-100 text-slate-600'
};

const sizeVariants = {
  sm: 'px-2.5 py-1 text-xs rounded-md',
  md: 'px-3.5 py-1.5 text-xs rounded-lg',
  lg: 'px-4 py-2 text-sm rounded-xl'
};

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  icon: Icon,
  className,
  disabled,
  isLoading,
  ...props
}) {
  return (
    <button
      disabled={disabled || isLoading}
      className={twMerge(
        'inline-flex items-center justify-center gap-1.5 cursor-pointer transition-all duration-150 active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none',
        buttonVariants[variant],
        sizeVariants[size],
        className
      )}
      {...props}
    >
      {isLoading ? (
        <span className="w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin" />
      ) : Icon ? (
        <Icon className="w-3.5 h-3.5" />
      ) : null}
      {children}
    </button>
  );
}
