import { useLocation } from "react-router-dom"
import { motion } from "framer-motion"
import { Bot } from "lucide-react"
import { useChatTransition } from "../context/ChatTransitionContext"

export default function FloatingChatButton() {
  const location = useLocation()
  const { openChat, isTransitioning } = useChatTransition()

  // Only render on pages other than the chatbot interface page
  const isChatPage = location.pathname === "/chat"

  if (isChatPage) return null

  return (
    <div className="fixed z-40 bottom-6 right-6 font-sans">
      <motion.button
        onClick={openChat}
        disabled={isTransitioning}
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.8 }}
        whileHover={{ scale: 1.1, y: -2 }}
        whileTap={{ scale: 0.92 }}
        transition={{ type: "spring", stiffness: 450, damping: 25 }}
        className="w-14 h-14 rounded-full bg-[#2F4156] text-white shadow-2xl border border-[#C8D9E6]/60 flex items-center justify-center cursor-pointer relative group transition-colors hover:border-[#567C8D]"
        style={{
          boxShadow:
            "0 12px 35px -5px rgba(47, 65, 86, 0.45), 0 0 20px rgba(86, 124, 141, 0.30)",
        }}
        aria-label="Open BLU - Base Line Unit Chatbot"
        title="Open BLU - Base Line Unit"
      >
        {/* Subtle glowing ring */}
        <div className="absolute inset-0 rounded-full bg-[#567C8D]/30 group-hover:bg-[#567C8D]/60 transition-colors" />

        {/* Bot Icon */}
        <Bot className="w-6 h-6 text-white group-hover:text-[#C8D9E6] transition-colors relative z-10 group-hover:scale-110 transform transition-transform" />

        {/* Active state indicator ring (#567C8D) */}
        <span className="absolute -top-0.5 -right-0.5 flex h-3.5 w-3.5 z-20">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#567C8D] opacity-75" />
          <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-[#567C8D] border-2 border-[#2F4156]" />
        </span>
      </motion.button>
    </div>
  )
}
