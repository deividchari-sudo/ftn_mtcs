import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import { Dashboard } from './pages/Dashboard'
import { AdvancedAnalytics } from './pages/AdvancedAnalytics'
import { Calendar } from './pages/Calendar'
import { Goals } from './pages/Goals'
import { Wellness } from './pages/Wellness'
import { AIChat } from './pages/AIChat'
import { Details } from './pages/Details'
import { Config } from './pages/Config'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="advanced" element={<AdvancedAnalytics />} />
          <Route path="calendar" element={<Calendar />} />
          <Route path="goals" element={<Goals />} />
          <Route path="wellness" element={<Wellness />} />
          <Route path="ai-chat" element={<AIChat />} />
          <Route path="details" element={<Details />} />
          <Route path="config" element={<Config />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App
