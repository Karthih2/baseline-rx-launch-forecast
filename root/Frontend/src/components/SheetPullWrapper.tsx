import { ReactNode } from "react"
import { useLocation } from "react-router-dom"
import { motion } from "framer-motion"

interface SheetPullWrapperProps {
  children: ReactNode
  isChat?: boolean
}

export default function SheetPullWrapper({ children, isChat = false }: SheetPullWrapperProps) {
  const location = useLocation()
  const isAbout = location.pathname === "/" || location.pathname.startsWith("/about")

  // Chat page: no horizontal animation — handled by the iris transition instead
  if (isChat) {
    return (
      <div
        className="w-full rounded-t-[28px] border-t border-x min-h-[calc(100vh-2rem)] p-5 sm:p-8 md:p-10 relative overflow-hidden backdrop-blur-xl transition-colors duration-500"
        style={{
          backgroundColor: "#FAF7F5",
          borderColor: "rgba(200, 217, 230, 0.85)",
          boxShadow:
            "0 -16px 50px -8px rgba(47, 65, 86, 0.08), 0 -4px 18px rgba(47, 65, 86, 0.04), inset 0 1px 0 rgba(255, 255, 255, 0.95)",
        }}
      >
        {/* ── Very subtle dotted grid inside the page surface ── */}
        <div
          className="dot-spots-subtle absolute inset-0 pointer-events-none z-0"
          style={{
            opacity: 0.25,
            maskImage: "linear-gradient(to bottom, black 30%, transparent 95%)",
            WebkitMaskImage: "linear-gradient(to bottom, black 30%, transparent 95%)",
          }}
        />
        <div className="relative z-10">{children}</div>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ x: -32, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: 24, opacity: 0 }}
      transition={{
        duration: 0.60,
        ease: [0.25, 0.46, 0.45, 0.94], // smooth ease-out — gentle, no jolt
      }}
      className="w-full rounded-t-[28px] border-t border-x min-h-[calc(100vh-2rem)] p-5 sm:p-8 md:p-10 relative overflow-hidden backdrop-blur-xl transition-colors duration-500"
      style={{
        backgroundColor: "#FAF7F5",
        borderColor: "rgba(200, 217, 230, 0.85)",
        boxShadow:
          "0 -16px 50px -8px rgba(47, 65, 86, 0.08), 0 -4px 18px rgba(47, 65, 86, 0.04), inset 0 1px 0 rgba(255, 255, 255, 0.95)",
      }}
    >
      {/* ── Very subtle dotted grid inside the page surface ── */}
      <div
        className="dot-spots-subtle absolute inset-0 pointer-events-none z-0"
        style={{
          opacity: 0.25,
          maskImage: "linear-gradient(to bottom, black 30%, transparent 95%)",
          WebkitMaskImage: "linear-gradient(to bottom, black 30%, transparent 95%)",
        }}
      />

      <div className="relative z-10">{children}</div>
    </motion.div>
  )
}
