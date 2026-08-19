import { useState, useEffect, useCallback } from "react"
import { motion, AnimatePresence } from "framer-motion"

interface Ripple {
  id: number
  x: number
  y: number
}

export default function RippleEffect() {
  const [ripples, setRipples] = useState<Ripple[]>([])

  const handleClick = useCallback((e: MouseEvent) => {
    // Avoid triggering ripple on interactive text selection or rapid dragging
    const newRipple: Ripple = {
      id: Date.now() + Math.random(),
      x: e.clientX,
      y: e.clientY,
    }

    setRipples((prev) => [...prev.slice(-12), newRipple])
  }, [])

  useEffect(() => {
    window.addEventListener("click", handleClick)
    return () => window.removeEventListener("click", handleClick)
  }, [handleClick])

  const removeRipple = (id: number) => {
    setRipples((prev) => prev.filter((r) => r.id !== id))
  }

  return (
    <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
      <AnimatePresence>
        {ripples.map((ripple) => (
          <motion.div
            key={ripple.id}
            initial={{ scale: 0, opacity: 0.85 }}
            animate={{ scale: 3.5, opacity: 0 }}
            exit={{ opacity: 0 }}
            transition={{
              duration: 0.75,
              ease: [0.25, 0.46, 0.45, 0.94],
            }}
            onAnimationComplete={() => removeRipple(ripple.id)}
            className="absolute rounded-full border-2 border-white/60 pointer-events-none"
            style={{
              left: ripple.x - 24,
              top: ripple.y - 24,
              width: 48,
              height: 48,
              background:
                "radial-gradient(circle, rgba(200, 217, 230, 0.45) 0%, rgba(86, 124, 141, 0.20) 50%, transparent 75%)",
              boxShadow:
                "0 0 16px rgba(86, 124, 141, 0.25), inset 0 0 8px rgba(200, 217, 230, 0.4)",
            }}
          />
        ))}
      </AnimatePresence>
    </div>
  )
}
