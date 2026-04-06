import { type ButtonHTMLAttributes, forwardRef } from "react"
import { cn } from "@/lib/utils"

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger" | "success"
  size?: "sm" | "md" | "lg"
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", disabled, children, ...props }, ref) => {
    const baseStyles = "inline-flex items-center justify-center gap-2 font-medium rounded-md border-none cursor-pointer transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed"

    const variants = {
      primary: "bg-[var(--brand-primary)] text-white hover:bg-[var(--brand-primary-hover)]",
      secondary: "bg-[var(--bg-tertiary)] text-[var(--text-primary)] border border-[var(--border-primary)] hover:bg-[var(--bg-hover)]",
      ghost: "bg-transparent text-[var(--text-primary)] hover:bg-[var(--bg-hover)]",
      danger: "bg-[var(--status-error)] text-white hover:brightness-110",
      success: "bg-[var(--status-success)] text-white hover:brightness-110",
    }

    const sizes = {
      sm: "h-7 px-3 text-xs",
      md: "h-9 px-4 text-sm",
      lg: "h-11 px-6 text-base",
    }

    return (
      <button
        ref={ref}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        disabled={disabled}
        {...props}
      >
        {children}
      </button>
    )
  }
)

Button.displayName = "Button"

export { Button }
