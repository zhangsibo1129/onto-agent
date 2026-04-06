import { BrowserRouter, Routes, Route } from "react-router-dom"
import { AppLayout } from "@/components/layout"
import Dashboard from "@/pages/Dashboard"
import DataSources from "@/pages/DataSources"
import DatasourceDetail from "@/pages/DatasourceDetail"
import Ontologies from "@/pages/Ontologies"
import OntologyModeling from "@/pages/OntologyModeling"
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
          <Route path="/ontologies/:id" element={<OntologyModeling />} />
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

export default App