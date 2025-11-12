import { NavLink } from 'react-router-dom'
import { Home, Users, CheckSquare, FileText, Folder, BookOpen } from 'lucide-react'

const navigation = [
  { name: 'Dashboard', to: '/', icon: Home },
  { name: 'Agents', to: '/agents', icon: Users },
  { name: 'Tasks', to: '/tasks', icon: CheckSquare },
  { name: 'Research Lab', to: '/research', icon: BookOpen },
  { name: 'Reports', to: '/reports', icon: FileText },
  { name: 'Projects', to: '/projects', icon: Folder },
]

export default function Layout({ children }) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                🤖 Agent Management Platform
              </h1>
            </div>
            <div className="text-sm text-gray-500">
              v1.0.0
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-8">
          {/* Sidebar */}
          <nav className="w-64 flex-shrink-0">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <div className="space-y-1">
                {navigation.map((item) => {
                  const Icon = item.icon
                  return (
                    <NavLink
                      key={item.name}
                      to={item.to}
                      end={item.to === '/'}
                      className={({ isActive }) =>
                        `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                          isActive
                            ? 'bg-primary-50 text-primary-700'
                            : 'text-gray-700 hover:bg-gray-50'
                        }`
                      }
                    >
                      <Icon size={20} />
                      {item.name}
                    </NavLink>
                  )
                })}
              </div>
            </div>
          </nav>

          {/* Main Content */}
          <main className="flex-1 min-w-0">
            {children}
          </main>
        </div>
      </div>
    </div>
  )
}
