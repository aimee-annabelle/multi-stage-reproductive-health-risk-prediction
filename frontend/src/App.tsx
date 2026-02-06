import './index.css'

function App() {
  return (
    <div className="min-h-screen flex items-center justify-center p-8">
      <div className="glass-card rounded-2xl p-12 max-w-2xl text-center">
        <h1 className="text-4xl font-bold gradient-text mb-4">
          React + TypeScript + Vite
        </h1>
        <p className="text-gray-600 mb-6">
          With TailwindCSS v4 and Zustand
        </p>
        <div className="space-y-4 text-left">
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <h3 className="font-semibold text-blue-900 mb-2">✅ React 18 + TypeScript</h3>
            <p className="text-sm text-blue-700">Type-safe component development</p>
          </div>
          <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
            <h3 className="font-semibold text-purple-900 mb-2">✅ TailwindCSS v4</h3>
            <p className="text-sm text-purple-700">Modern utility-first CSS framework</p>
          </div>
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <h3 className="font-semibold text-green-900 mb-2">✅ Zustand</h3>
            <p className="text-sm text-green-700">Lightweight state management</p>
          </div>
          <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
            <h3 className="font-semibold text-orange-900 mb-2">✅ Vite</h3>
            <p className="text-sm text-orange-700">Lightning-fast HMR and build</p>
          </div>
        </div>
        <p className="mt-8 text-sm text-gray-500">
          Edit <code className="bg-gray-100 px-2 py-1 rounded">src/App.tsx</code> to get started
        </p>
      </div>
    </div>
  )
}

export default App
