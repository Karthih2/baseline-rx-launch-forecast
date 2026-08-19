import { useState, useRef, useEffect } from "react"
import { NavLink, useLocation } from "react-router-dom"
import { motion, AnimatePresence } from "framer-motion"
import {
  LayoutDashboard,
  PlusCircle,
  Info,
  X,
  Activity,
  Home,
} from "lucide-react"
import logoImg from "../assets/logo.png"

export default function FloatingNav() {
  const [isOpen, setIsOpen] = useState(false)
  const location = useLocation()
  const navRef = useRef<HTMLDivElement>(null)

  const navItems = [
    {
      name: "Home",
      path: "/home",
      icon: Home,
      subtitle: "Methodology & Architecture",
    },
    {
      name: "New Forecast",
      path: "/upload",
      icon: PlusCircle,
      subtitle: "Upload & Assumptions",
    },
    {
      name: "Dashboard",
      path: "/dashboard",
      icon: LayoutDashboard,
      subtitle: "12-Month Forecast",
    },
  ]

  // Find active item icon
  const currentActiveItem =
    navItems.find((item) =>
      item.path === "/home"
        ? location.pathname === "/" || location.pathname.startsWith("/home")
        : location.pathname.startsWith(item.path)
    ) || navItems[0]

  const ActiveIcon = currentActiveItem.icon

  // Close when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (navRef.current && !navRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside)
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
    }
  }, [isOpen])

  // Close on route change
  useEffect(() => {
    setIsOpen(false)
  }, [location.pathname])

  // Completely hide navigation on chatbot page as requested
  if (location.pathname === "/chat") {
    return null
  }

  return (
    <div
      ref={navRef}
      className="fixed z-50 bottom-6 left-6 md:bottom-auto md:left-auto md:top-6 md:right-6 font-sans"
    >
      <AnimatePresence mode="wait">
        {!isOpen ? (
          /* ── COLLAPSED CIRCULAR TRIGGER (56px x 56px) ── */
          <motion.button
            key="collapsed"
            layoutId="floating-nav-container"
            onClick={() => setIsOpen(true)}
            whileHover={{ scale: 1.06 }}
            whileTap={{ scale: 0.94 }}
            className="w-14 h-14 rounded-full bg-white/95 text-[#2F4156] shadow-xl border border-[#C8D9E6] flex items-center justify-center cursor-pointer relative group transition-colors hover:border-[#567C8D] backdrop-blur-md"
            style={{
              boxShadow: "0 10px 30px -5px rgba(47, 65, 86, 0.18), 0 0 15px rgba(86, 124, 141, 0.12)",
            }}
            aria-label="Open Navigation Menu"
          >
            {/* Active page icon */}
            <ActiveIcon className="w-6 h-6 text-[#2F4156] transition-transform group-hover:scale-110 group-hover:text-[#567C8D]" />

            {/* Active state indicator ring (#567C8D) */}
            <span className="absolute -top-0.5 -right-0.5 flex h-3.5 w-3.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#567C8D] opacity-75" />
              <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-[#567C8D] border-2 border-white" />
            </span>
          </motion.button>
        ) : (
          /* ── EXPANDED CAPSULE / CARD PANEL (Light Glass) ── */
          <motion.div
            key="expanded"
            layoutId="floating-nav-container"
            transition={{
              type: "spring",
              stiffness: 350,
              damping: 25,
            }}
            className="bg-white/95 backdrop-blur-xl text-[#2F4156] p-3.5 rounded-2xl shadow-2xl border border-[#C8D9E6] min-w-[270px] sm:min-w-[290px] flex flex-col gap-2 origin-bottom-left md:origin-top-right overflow-hidden"
            style={{
              boxShadow: "0 20px 40px -10px rgba(47, 65, 86, 0.18), 0 0 25px rgba(86, 124, 141, 0.15)",
            }}
          >
            {/* Panel Header */}
            <div className="flex items-center justify-between px-2 py-1 border-b border-[#C8D9E6]/70 pb-2.5">
              <div className="flex items-center gap-2.5">
                <div className="h-8 w-8 flex items-center justify-center flex-shrink-0">
                  <img src={logoImg} alt="Baseline Logo" className="h-8 w-8 object-contain" />
                </div>
                <div>
                  <span className="font-serif text-sm font-semibold text-[#2F4156] leading-none block">
                    BaseLine
                  </span>
                </div>
              </div>

              <button
                onClick={() => setIsOpen(false)}
                className="text-[#7A92A2] hover:text-[#2F4156] p-1 rounded-lg hover:bg-[#EBF1F4] transition-colors cursor-pointer"
                aria-label="Close navigation"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Navigation Options with layoutId active pill highlight */}
            <nav className="flex flex-col gap-1 py-1">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive =
                    item.path === "/home"
                      ? location.pathname === "/" || location.pathname.startsWith("/home")
                    : location.pathname.startsWith(item.path)

                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    onClick={() => setIsOpen(false)}
                    className={`relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all group ${
                      isActive ? "text-white" : "text-[#2F4156] hover:text-[#2F4156] hover:bg-[#EBF1F4]"
                    }`}
                  >
                    {/* Active Pill Highlight Animation */}
                    {isActive && (
                      <motion.div
                        layoutId="activePill"
                        transition={{
                          type: "spring",
                          stiffness: 350,
                          damping: 25,
                        }}
                        className="absolute inset-0 bg-[#567C8D] rounded-xl shadow-xs"
                      />
                    )}

                    <div className="relative z-10 flex items-center justify-center">
                      <Icon className={`w-5 h-5 ${isActive ? "text-white" : "text-[#567C8D] group-hover:text-[#2F4156]"}`} />
                    </div>

                    <div className="relative z-10 flex flex-col text-left flex-1">
                      <span className="font-semibold text-xs leading-tight">{item.name}</span>
                      <span className={`text-[10px] font-mono leading-tight ${isActive ? "text-[#E2ECF4]" : "text-[#7A92A2] group-hover:text-[#567C8D]"}`}>
                        {item.subtitle}
                      </span>
                    </div>

                    {isActive && (
                      <div className="relative z-10 w-2 h-2 rounded-full bg-[#C8D9E6]" />
                    )}
                  </NavLink>
                )
              })}
            </nav>

            {/* Telemetry Status Footer */}
            <div className="pt-2 border-t border-[#C8D9E6]/70 px-2 flex items-center justify-between text-[10px] font-mono text-[#567C8D]">
              <div className="flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-[#567C8D]" />
                <span>Analog + Bass</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
