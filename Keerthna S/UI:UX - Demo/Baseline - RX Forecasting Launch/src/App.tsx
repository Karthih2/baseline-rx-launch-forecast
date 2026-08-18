import { RouterProvider, createBrowserRouter } from "react-router-dom"
import Layout from "./components/Layout"
import Home from "./pages/Home"
import NewForecast from "./pages/Upload"
import About from "./pages/About"

const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      { index: true, element: <Home /> },
      { path: "upload", element: <NewForecast /> },
      { path: "about", element: <About /> },
    ],
  },
])

export default function App() {
  return <RouterProvider router={router} />
}
