import React from 'react'
import { cn } from '@/lib/utils'
import { Loader2 } from 'lucide-react'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'danger' | 'ghost' | 'success'
  size?: 'sm' | 'md' | 'lg'
  isLoading?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      className,
      variant = 'primary',
      size = 'md',
      isLoading = false,
      disabled,
      leftIcon,
      rightIcon,
      type = 'button',
      ...props
    },
    ref
  ) => {
    const baseStyles =
      'inline-flex items-center justify-center font-medium transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed select-none rounded-lg border'

    const sizeStyles = {
      sm: 'text-xs px-2.5 py-1.5 gap-1.5 h-8',
      md: 'text-sm px-3.5 py-2 gap-2 h-9',
      lg: 'text-base px-5 py-2.5 gap-2.5 h-11',
    }

    const variantStyles = {
      primary:
        'bg-blue-600 text-white border-blue-600 hover:bg-blue-700 active:bg-blue-800 focus-visible:ring-blue-600 shadow-xs',
      secondary:
        'bg-white text-slate-700 border-slate-300 hover:bg-slate-50 hover:text-slate-900 active:bg-slate-100 focus-visible:ring-slate-400 shadow-xs',
      outline:
        'bg-transparent text-slate-700 border-slate-300 hover:bg-slate-50 hover:border-slate-400 focus-visible:ring-slate-400',
      danger:
        'bg-rose-600 text-white border-rose-600 hover:bg-rose-700 active:bg-rose-800 focus-visible:ring-rose-500 shadow-xs',
      success:
        'bg-emerald-600 text-white border-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 focus-visible:ring-emerald-500 shadow-xs',
      ghost:
        'bg-transparent text-slate-600 border-transparent hover:bg-slate-100 hover:text-slate-900 focus-visible:ring-slate-400',
    }

    return (
      <button
        ref={ref}
        type={type}
        disabled={disabled || isLoading}
        className={cn(baseStyles, sizeStyles[size], variantStyles[variant], className)}
        {...props}
      >
        {isLoading ? (
          <Loader2 className="w-4 h-4 animate-spin shrink-0" />
        ) : (
          leftIcon && <span className="shrink-0">{leftIcon}</span>
        )}
        <span>{children}</span>
        {!isLoading && rightIcon && <span className="shrink-0">{rightIcon}</span>}
      </button>
    )
  }
)

Button.displayName = 'Button'
