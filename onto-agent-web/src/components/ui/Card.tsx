import { type ReactNode } from "react"
import "./Card.css"

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
  style?: React.CSSProperties
}

interface CardFooterProps {
  children: ReactNode
  className?: string
}

function Card({ children, className = "" }: CardProps) {
  return <div className={`card ${className}`}>{children}</div>
}

function CardHeader({ title, action, children, className = "" }: CardHeaderProps) {
  return (
    <div className={`card-header ${className}`}>
      {children || <span className="card-title">{title}</span>}
      {action}
    </div>
  )
}

function CardBody({ children, className = "", style }: CardBodyProps) {
  return (
    <div className={`card-body ${className}`} style={style}>
      {children}
    </div>
  )
}

function CardFooter({ children, className = "" }: CardFooterProps) {
  return <div className={`card-footer ${className}`}>{children}</div>
}

export { Card, CardHeader, CardBody, CardFooter }
