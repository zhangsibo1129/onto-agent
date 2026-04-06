export default function Placeholder({ title }: { title: string }) {
  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center">
        <h1 className="text-2xl font-semibold text-[var(--text-primary)] mb-2">{title}</h1>
        <p className="text-[var(--text-tertiary)]">页面开发中...</p>
      </div>
    </div>
  )
}
