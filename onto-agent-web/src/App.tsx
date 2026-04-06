import { BrowserRouter, Routes, Route } from "react-router-dom"
import { AppLayout } from "@/components/layout"
import Dashboard from "@/pages/Dashboard"
import DataSources from "@/pages/DataSources"
import DatasourceDetail from "@/pages/DatasourceDetail"
import Ontologies from "@/pages/Ontologies"
import Mapping from "@/pages/Mapping"
import Query from "@/pages/Query"
import NLQuery from "@/pages/NLQuery"
import Workbench from "@/pages/Workbench"
import Versions from "@/pages/Versions"
import Sync from "@/pages/Sync"
import Permissions from "@/pages/Permissions"
import ApiManagement from "@/pages/ApiManagement"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/data-sources" element={<DataSources />} />
          <Route path="/data-sources/:id" element={<DatasourceDetail />} />
          <Route path="/ontologies" element={<Ontologies />} />
          <Route path="/ontologies/:id" element={<Placeholder title="本体建模" />} />
          <Route path="/mapping" element={<Mapping />} />
          <Route path="/query" element={<Query />} />
          <Route path="/nl-query" element={<NLQuery />} />
          <Route path="/workbench" element={<Workbench />} />
          <Route path="/versions" element={<Versions />} />
          <Route path="/sync" element={<Sync />} />
          <Route path="/permissions" element={<Permissions />} />
          <Route path="/api-management" element={<ApiManagement />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

function Placeholder({ title }: { title: string }) {
  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center">
        <h1 className="text-2xl font-semibold text-[var(--text-primary)] mb-2">{title}</h1>
        <p className="text-[var(--text-tertiary)]">页面开发中...</p>
      </div>
    </div>
  )
}

export default App