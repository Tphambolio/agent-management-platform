import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Tasks from './pages/Tasks'
import Reports from './pages/Reports'
import Projects from './pages/Projects'
import AgentLab from './pages/AgentLab'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<AgentLab />} />
        <Route path="/tasks" element={<Tasks />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/projects" element={<Projects />} />
      </Routes>
    </Layout>
  )
}

export default App
