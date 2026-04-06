import { Link } from "react-router-dom"
import { ArrowUpRight, Database, Box, Clock, Search } from "lucide-react"
import { Card, CardHeader, CardBody, Button } from "@/components/ui"
import { mockOntologies, mockActivities, mockDataSources } from "@/data/mock"

const statusColors = {
  published: "bg-[var(--status-success)]",
  draft: "bg-[var(--text-tertiary)]",
  archived: "bg-[var(--text-tertiary)] opacity-50",
}

const activityColors = {
  success: "bg-[var(--status-success)]",
  primary: "bg-[var(--brand-primary)]",
  secondary: "bg-[var(--brand-secondary)]",
  accent: "bg-[var(--brand-accent)]",
  warning: "bg-[var(--status-warning)]",
}

export default function Dashboard() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-[var(--text-primary)]">仪表盘</h1>
          <p className="text-sm text-[var(--text-tertiary)] mt-1">企业本体数据平台运行概览</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="secondary" size="sm">
            <Clock className="w-4 h-4 mr-1" />
            刷新
          </Button>
          <Link
            to="/ontologies"
            className="inline-flex items-center justify-center gap-2 h-9 px-4 text-sm font-medium bg-[var(--brand-primary)] text-white rounded-md hover:bg-[var(--brand-primary-hover)] transition-colors"
          >
            + 新建本体
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-4 gap-4">
        <Card className="!p-4">
          <div className="text-xs text-[var(--text-tertiary)] uppercase tracking-wider mb-2">数据源</div>
          <div className="text-3xl font-semibold text-[var(--text-primary)]">{mockDataSources.length}</div>
          <div className="text-xs text-[var(--status-success)] mt-1">↑ 全部连接正常</div>
        </Card>
        <Card className="!p-4">
          <div className="text-xs text-[var(--text-tertiary)] uppercase tracking-wider mb-2">本体总数</div>
          <div className="text-3xl font-semibold text-[var(--text-primary)]">{mockOntologies.length}</div>
          <div className="text-xs text-[var(--status-success)] mt-1">↑ 2 个已发布</div>
        </Card>
        <Card className="!p-4">
          <div className="text-xs text-[var(--text-tertiary)] uppercase tracking-wider mb-2">对象类型</div>
          <div className="text-3xl font-semibold text-[var(--text-primary)]">24</div>
          <div className="text-xs text-[var(--status-success)] mt-1">↑ 较上周 +3</div>
        </Card>
        <Card className="!p-4">
          <div className="text-xs text-[var(--text-tertiary)] uppercase tracking-wider mb-2">今日查询</div>
          <div className="text-3xl font-semibold text-[var(--text-primary)]">1,247</div>
          <div className="text-xs text-[var(--status-success)] mt-1">↑ 12.5% 较昨日</div>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader title="快捷操作" />
        <CardBody className="!py-4">
          <div className="grid grid-cols-4 gap-4">
            <Link
              to="/data-sources"
              className="flex flex-col items-center justify-center p-6 bg-[var(--bg-tertiary)] border border-[var(--border-primary)] rounded-lg hover:border-[var(--brand-primary)] hover:bg-[var(--bg-hover)] transition-colors"
            >
              <div className="w-10 h-10 rounded-lg bg-[rgba(59,130,246,0.1)] flex items-center justify-center text-[var(--brand-primary)] mb-3">
                <Database className="w-5 h-5" />
              </div>
              <span className="text-sm font-medium text-[var(--text-primary)]">连接数据源</span>
            </Link>
            <Link
              to="/ontologies"
              className="flex flex-col items-center justify-center p-6 bg-[var(--bg-tertiary)] border border-[var(--border-primary)] rounded-lg hover:border-[var(--brand-secondary)] hover:bg-[var(--bg-hover)] transition-colors"
            >
              <div className="w-10 h-10 rounded-lg bg-[rgba(139,92,246,0.1)] flex items-center justify-center text-[var(--brand-secondary)] mb-3">
                <Box className="w-5 h-5" />
              </div>
              <span className="text-sm font-medium text-[var(--text-primary)]">创建本体</span>
            </Link>
            <Link
              to="/query"
              className="flex flex-col items-center justify-center p-6 bg-[var(--bg-tertiary)] border border-[var(--border-primary)] rounded-lg hover:border-[var(--brand-accent)] hover:bg-[var(--bg-hover)] transition-colors"
            >
              <div className="w-10 h-10 rounded-lg bg-[rgba(6,182,212,0.1)] flex items-center justify-center text-[var(--brand-accent)] mb-3">
                <Search className="w-5 h-5" />
              </div>
              <span className="text-sm font-medium text-[var(--text-primary)]">语义查询</span>
            </Link>
            <Link
              to="/nl-query"
              className="flex flex-col items-center justify-center p-6 bg-[var(--bg-tertiary)] border border-[var(--border-primary)] rounded-lg hover:border-[var(--status-success)] hover:bg-[var(--bg-hover)] transition-colors"
            >
              <div className="w-10 h-10 rounded-lg bg-[rgba(16,185,129,0.1)] flex items-center justify-center text-[var(--status-success)] mb-3">
                <ArrowUpRight className="w-5 h-5" />
              </div>
              <span className="text-sm font-medium text-[var(--text-primary)]">AI 对话查询</span>
            </Link>
          </div>
        </CardBody>
      </Card>

      {/* Two Column Layout */}
      <div className="grid grid-cols-2 gap-6">
        {/* Recent Ontologies */}
        <Card>
          <CardHeader
            title="最近本体"
            action={
              <Link to="/ontologies" className="text-sm text-[var(--brand-primary)] hover:underline">
                查看全部 →
              </Link>
            }
          />
          <CardBody className="!p-0">
            <table className="w-full">
              <thead>
                <tr className="bg-[var(--bg-tertiary)]">
                  <th className="px-4 py-3 text-left text-xs font-semibold text-[var(--text-tertiary)] uppercase tracking-wider">名称</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-[var(--text-tertiary)] uppercase tracking-wider">状态</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-[var(--text-tertiary)] uppercase tracking-wider">对象数</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-[var(--text-tertiary)] uppercase tracking-wider">更新时间</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--border-primary)]">
                {mockOntologies.map((ontology) => (
                  <tr key={ontology.id} className="hover:bg-[var(--bg-hover)] transition-colors">
                    <td className="px-4 py-3 text-sm font-medium text-[var(--brand-primary)]">{ontology.name}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium text-white ${statusColors[ontology.status as keyof typeof statusColors]}`}>
                        {ontology.status === "published" ? "已发布" : ontology.status === "draft" ? "草稿" : "已归档"}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-[var(--text-secondary)]">{ontology.objectCount}</td>
                    <td className="px-4 py-3 text-sm text-[var(--text-tertiary)]">{ontology.updatedAt}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardBody>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader title="最近活动" action={<Button variant="ghost" size="sm">筛选</Button>} />
          <CardBody className="!p-0">
            <div className="divide-y divide-[var(--border-primary)]">
              {mockActivities.map((activity) => (
                <div key={activity.id} className="flex items-start gap-3 px-5 py-3">
                  <div className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${activityColors[activity.type as keyof typeof activityColors]}`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-[var(--text-primary)]">
                      {activity.text}
                    </p>
                    <p className="text-xs text-[var(--text-tertiary)] mt-0.5">
                      {activity.time} · {activity.user}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  )
}
