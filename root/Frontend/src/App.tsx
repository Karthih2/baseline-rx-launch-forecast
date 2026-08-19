import { RouterProvider, createBrowserRouter, useRouteError } from "react-router-dom"
import Layout from "./components/Layout"
import Home from "./pages/Home"
import NewForecast from "./pages/Upload"
import Dashboard from "./pages/Dashboard"
import ChatAssistant from "./pages/ChatAssistant"
import { AlertTriangle, RotateCcw } from "lucide-react"

function ErrorFallback() {
  const error = useRouteError() as { statusText?: string; message?: string }

  return (
    <div className="min-h-screen bg-[#F5EFEB] flex items-center justify-center p-6 text-[#2F4156]">
      <div className="bg-white border border-[#C8D9E6] rounded-2xl p-8 max-w-md w-full shadow-2xl text-center space-y-4">
        <div className="w-14 h-14 rounded-full bg-[#FCEEED] text-[#C25450] flex items-center justify-center mx-auto border border-[#F2B8B6]">
          <AlertTriangle className="w-7 h-7" />
        </div>
        <div>
          <h2 className="font-serif text-2xl font-medium text-[#2F4156]">
            Application Recovered
          </h2>
          <p className="text-xs text-[#567C8D] mt-1 font-mono">
            {error?.statusText || error?.message || "An unexpected view error occurred."}
          </p>
        </div>
        <button
          onClick={() => (window.location.href = "/")}
          className="w-full bg-[#2F4156] hover:bg-[#1D2A37] text-white text-xs font-semibold py-3 rounded-xl transition-colors flex items-center justify-center gap-2 border border-[#567C8D]/40 cursor-pointer"
        >
          <RotateCcw className="w-4 h-4 text-[#C8D9E6]" />
          Return to Forecast Dashboard
        </button>
      </div>
    </div>
  )
}

const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    errorElement: <ErrorFallback />,
    children: [
      { index: true, element: <Home /> },
      { path: "home", element: <Home /> },
      { path: "dashboard", element: <Dashboard /> },
      { path: "upload", element: <NewForecast /> },
      { path: "about", element: <Home /> },
      { path: "chat", element: <ChatAssistant /> },
      { path: "*", element: <Home /> },
    ],
  },
])

export default function App() {
  return <RouterProvider router={router} />
}
