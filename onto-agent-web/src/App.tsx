import { BrowserRouter, Routes, Route } from "react-router-dom"
import { AppLayout } from "@/components/layout"
import Dashboard from "@/pages/Dashboard"
import DataSources from "@/pages/DataSources"
import Ontologies from "@/pages/Ontologies"
import Placeholder from "@/pages/Placeholder"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/data-sources" element={<DataSources />} />
          <Route path="/data-sources/:id" element={<Placeholder title="数据源详情" />} />
          <Route path="/ontologies" element={<Ontologies />} />
          <Route path="/ontologies/:id" element={<Placeholder title="本体建模" />} />
          <Route path="/mapping" element={<Placeholder title="数据映射" />} />
          <Route path="/query" element={<Placeholder title="语义查询" />} />
          <Route path="/nl-query" element={<Placeholder title="自然语言查询" />} />
          <Route path="/workbench" element={<Placeholder title="查询工作台" />} />
          <Route path="/versions" element={<Placeholder title="版本管理" />} />
          <Route path="/sync" element={<Placeholder title="数据同步" />} />
          <Route path="/permissions" element={<Placeholder title="权限管理" />} />
          <Route path="/api-management" element={<Placeholder title="API 管理" />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
