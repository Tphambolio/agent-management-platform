import GoogleAuth from './GoogleAuth'

export default function Layout({ children }) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Minimal Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14">
            <h1 className="text-xl font-bold text-gray-900">
              Research Lab
            </h1>
            <div className="flex items-center gap-4">
              <GoogleAuth />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content - Full Width */}
      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {children}
      </main>
    </div>
  )
}
