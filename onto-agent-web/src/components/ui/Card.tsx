import { type ReactNode } from "react"
import { cn } from "@/lib/utils"

interface CardProps {
  children: ReactNode
  className?: string
}

interface CardHeaderProps {
  title?: string
  action?: ReactNode
  children?: ReactNode
  className?: string
}

interface CardBodyProps {
  children: ReactNode
  className?: string
}

interface CardFooterProps {
  children: ReactNode
  className?: string
}

function Card({ children, className }: CardProps) {
  return (
    <div className={cn(
      "bg-[var(--bg-card)] border border-[var(--border-primary)] rounded-lg overflow-hidden",
      className
    )}>
      {children}
    </div>
  )
}

function CardHeader({ title, action, children, className }: CardHeaderProps) {
  return (
    <div className={cn(
      "px-5 py-4 border-b border-[var(--border-primary)] flex items-center justify-between",
      className
    )}>
      {children || <span className="text-sm font-semibold text-[var(--text-primary)]">{title}</span>}
      {action}
    </div>
  )
}

function CardBody({ children, className }: CardBodyProps) {
  return (
    <div className={cn("px-5 py-5", className)}>
      {children}
    </div>
  )
}

function CardFooter({ children, className }: CardFooterProps) {
  return (
    <div className={cn(
      "px-5 py-3 border-t border-[var(--border-primary)] flex items-center justify-end gap-3",
      className
    )}>
      {children}
    </div>
  )
}

export { Card, CardHeader, CardBody, CardFooter }
