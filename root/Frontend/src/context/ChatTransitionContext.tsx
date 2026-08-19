import React, { createContext, useContext, useState, ReactNode } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import { motion, AnimatePresence } from "framer-motion"
import { Bot, Sparkles } from "lucide-react"

interface ChatTransitionContextType {
  openChat: () => void
  closeChat: () => void
  isTransitioning: boolean
  transitionMode: "idle" | "expanding" | "shrinking"
}

const ChatTransitionContext = createContext<ChatTransitionContextType>({
  openChat: () => {},
  closeChat: () => {},
  isTransitioning: false,
  transitionMode: "idle",
})

export const useChatTransition = () => useContext(ChatTransitionContext)

interface ChatTransitionProviderProps {
  children: ReactNode
}

export function ChatTransitionProvider({ children }: ChatTransitionProviderProps) {
  const navigate = useNavigate()
  const location = useLocation()
  const [transitionMode, setTransitionMode] = useState<"idle" | "expanding" | "shrinking">("idle")
  const [returnPath, setReturnPath] = useState<string>("/dashboard")

  const openChat = () => {
    if (transitionMode !== "idle") return
    // Save current path to return to later
    if (location.pathname !== "/chat") {
      setReturnPath(location.pathname)
    }
    setTransitionMode("expanding")

    // Wait for iris to fully bloom, then navigate
    setTimeout(() => {
      navigate("/chat")
      // Give the chat page a moment to mount, then dissolve overlay
      setTimeout(() => {
        setTransitionMode("idle")
      }, 500)
    }, 800)
  }

  const closeChat = () => {
    if (transitionMode !== "idle") return
    setTransitionMode("shrinking")

    // Shrink down towards the bottom-right circle button position
    setTimeout(() => {
      navigate(returnPath || "/dashboard")
      setTimeout(() => {
        setTransitionMode("idle")
      }, 500)
    }, 800)
  }

  return (
    <ChatTransitionContext.Provider
      value={{
        openChat,
        closeChat,
        isTransitioning: transitionMode !== "idle",
        transitionMode,
      }}
    >
      {children}

      {/* ── EXPANDING / SHRINKING CIRCLE MORPH OVERLAY ── */}
      <AnimatePresence>
        {transitionMode !== "idle" && (
          <motion.div
            key="chat-transition-portal"
            initial={
              transitionMode === "expanding"
                ? {
                    clipPath: "circle(28px at calc(100% - 48px) calc(100% - 48px))",
                    opacity: 1,
                  }
                : {
                    clipPath: "circle(150% at 50% 50%)",
                    opacity: 1,
                  }
            }
            animate={
              transitionMode === "expanding"
                ? {
                    clipPath: "circle(150% at 50% 50%)",
                    opacity: 1,
                  }
                : {
                    clipPath: "circle(28px at calc(100% - 48px) calc(100% - 48px))",
                    opacity: 1,
                  }
            }
            exit={{
              opacity: 0,
              transition: { duration: 0.5, ease: "easeInOut" },
            }}
            transition={{
              duration: 0.80,
              ease: [0.25, 0.46, 0.45, 0.94], // smooth, natural arc — not too snappy
            }}
            className="fixed inset-0 z-[9999] pointer-events-auto flex flex-col items-center justify-center overflow-hidden"
            style={{
              backgroundColor: "#2F4156",
              backgroundImage:
                "radial-gradient(ellipse 100% 100% at 50% 50%, #2F4156 0%, #1D2A37 100%)",
            }}
          >
            {/* Subtle background dot spots */}
            <div
              className="dot-spots-dark absolute inset-0 pointer-events-none opacity-30"
              style={{
                maskImage: "radial-gradient(circle at 50% 50%, black 40%, transparent 80%)",
                WebkitMaskImage: "radial-gradient(circle at 50% 50%, black 40%, transparent 80%)",
              }}
            />

            {/* Glowing animated center icon & text */}
            <motion.div
              initial={
                transitionMode === "expanding"
                  ? { scale: 0.65, opacity: 0, y: 24 }
                  : { scale: 1, opacity: 1, y: 0 }
              }
              animate={
                transitionMode === "expanding"
                  ? { scale: 1, opacity: 1, y: 0 }
                  : { scale: 0.65, opacity: 0, y: 24 }
              }
              transition={{
                duration: 0.60,
                delay: transitionMode === "expanding" ? 0.22 : 0,
                ease: [0.16, 1, 0.3, 1],
              }}
              className="relative z-10 flex flex-col items-center text-center p-6"
            >
              {/* Bot Circular Emblem */}
              <div className="relative mb-5">
                <motion.div
                  animate={{ scale: [1, 1.06, 1], rotate: [0, 2, -2, 0] }}
                  transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }}
                  className="w-20 h-20 rounded-full bg-[#1D2A37] border-2 border-[#C8D9E6] flex items-center justify-center text-white shadow-2xl relative"
                  style={{
                    boxShadow:
                      "0 0 35px rgba(86, 124, 141, 0.45), inset 0 0 15px rgba(47, 65, 86, 0.6)",
                  }}
                >
                  <Bot className="w-10 h-10 text-[#C8D9E6]" />
                </motion.div>

                {/* Sparkling accent */}
                <motion.div
                  animate={{ scale: [0.8, 1.2, 0.8], opacity: [0.7, 1, 0.7] }}
                  transition={{ repeat: Infinity, duration: 2.5, ease: "easeInOut" }}
                  className="absolute -top-1 -right-1 bg-[#567C8D] text-white p-1.5 rounded-full shadow-lg"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                </motion.div>
              </div>

              {/* Title & Subtitle */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.45, delay: 0.30 }}
                className="space-y-1"
              >
                <h2 className="font-serif text-3xl font-bold tracking-tight text-white">
                  BLU
                </h2>
                <div className="text-[13px] font-mono text-[#C8D9E6] font-semibold tracking-wider uppercase">
                  Base Line Unit
                </div>
                <div className="text-[11px] font-mono text-[#E2ECF4] mt-2 max-w-xs">
                  {transitionMode === "expanding"
                    ? "Initializing deterministic launch intelligence..."
                    : "Returning to forecast workspace..."}
                </div>
              </motion.div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </ChatTransitionContext.Provider>
  )
}
