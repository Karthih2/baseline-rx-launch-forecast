import { useState } from "react"
import { Outlet, NavLink } from "react-router-dom"
import { Menu, X } from "lucide-react"
import baselineLogo from "../imports/Screenshot_2026-08-17_at_2.22.59_PM-removebg-preview.png"

const links = [
  { name: "Home", path: "/" },
  { name: "About", path: "/about" },
  { name: "New Forecast", path: "/upload" },
]

export default function Layout() {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-[#F6F7F9] font-sans text-[#14213D]">
      <header className="bg-white border-b border-[#E3E6EC] sticky top-0 z-50">
        <div className="flex items-center px-4 sm:px-8 h-[76px]">
          {/* Logo — black, no filter */}
          <div className="flex-shrink-0">
            <img
              src={baselineLogo}
              alt="Baseline"
              className="h-[62px] sm:h-[70px] w-auto object-contain"
            />
          </div>

          {/* Desktop nav — centered */}
          <nav className="hidden md:flex flex-1 items-center justify-center gap-1">
            {links.map((link) => (
              <NavLink
                key={link.name}
                to={link.path}
                className={({ isActive }) =>
                  `px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-[#2B6777] text-white"
                      : "text-[#5C6478] hover:bg-[#E7F0F1] hover:text-[#2B6777]"
                  }`
                }
              >
                {link.name}
              </NavLink>
            ))}
          </nav>

          {/* Mobile hamburger */}
          <button
            className="md:hidden ml-auto text-[#2B6777] p-2"
            onClick={() => setMenuOpen((o) => !o)}
            aria-label="Toggle menu"
          >
            {menuOpen ? (
              <X className="w-6 h-6" />
            ) : (
              <Menu className="w-6 h-6" />
            )}
          </button>
        </div>

        {menuOpen && (
          <nav className="md:hidden bg-white border-t border-[#E3E6EC] px-4 py-3 flex flex-col gap-1">
            {links.map((link) => (
              <NavLink
                key={link.name}
                to={link.path}
                onClick={() => setMenuOpen(false)}
                className={({ isActive }) =>
                  `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-[#2B6777] text-white"
                      : "text-[#5C6478] hover:bg-[#E7F0F1] hover:text-[#2B6777]"
                  }`
                }
              >
                {link.name}
              </NavLink>
            ))}
          </nav>
        )}
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-8 py-6 sm:py-10">
        <Outlet />
      </main>
    </div>
  )
}
