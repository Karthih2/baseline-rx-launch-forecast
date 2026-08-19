import { Outlet, useLocation } from "react-router-dom"
import { AnimatePresence } from "framer-motion"
import FloatingNav from "./FloatingNav"
import FloatingChatButton from "./FloatingChatButton"
import SheetPullWrapper from "./SheetPullWrapper"
import RippleEffect from "./RippleEffect"
import { ChatTransitionProvider } from "../context/ChatTransitionContext"

export default function Layout() {
  const location = useLocation()
  const isAboutPage = location.pathname === "/" || location.pathname.startsWith("/about")

  return (
    <ChatTransitionProvider>
      <div
        className="min-h-screen font-sans antialiased relative overflow-x-hidden pt-4 sm:pt-6 transition-colors duration-500"
        style={{
          backgroundColor: "#263B4D",
          backgroundImage:
            "radial-gradient(ellipse 80% 50% at 50% -10%, rgba(200, 217, 230, 0.45) 0%, transparent 80%), radial-gradient(ellipse 60% 40% at 90% 90%, rgba(86, 124, 141, 0.10) 0%, transparent 70%)",
        }}
      >
        {/* ── Global Interactive Water Ripple on Click ── */}
        <RippleEffect />

        {/* ── Top-Left Corner Dot Spots (Gentle & Visible) ── */}
        <div
          className="dot-spots fixed top-0 left-0 z-0 pointer-events-none"
          style={{
            width: "360px",
            height: "360px",
            opacity: 100000000.55,
            maskImage:
              "radial-gradient(ellipse 100% 100% at 0% 0%, black 100%, transparent 10%)",
            WebkitMaskImage:
              "radial-gradient(ellipse 100% 100% at 0% 0%, black 100%, transparent 10%)",
          }}
        />

        {/* ── Bottom-Right Corner Dot Spots (Gentle & Visible) ── */}
        <div
          className="dot-spots fixed bottom-0 right-0 z-0 pointer-events-none"
          style={{
            width: "360px",
            height: "360px",
            opacity: 100000000.55,
            maskImage:
              "radial-gradient(ellipse 100% 100% at 100% 100%, black 100%, transparent 10%)",
            WebkitMaskImage:
              "radial-gradient(ellipse 100% 100% at 100% 100%, black 100%, transparent 10%)",
          }}
        />

        {/* ── Dynamic Floating Navigation ── */}
        <FloatingNav />

        {/* ── Floating AI Copilot Trigger (Visible on all pages except /chat) ── */}
        <FloatingChatButton />

        {/* ── Main Content Workspace with Page Transition ── */}
        <main className="max-w-[1320px] mx-auto px-2 sm:px-4 relative z-10">
          <AnimatePresence mode="wait">
            <SheetPullWrapper key={location.pathname} isChat={location.pathname === "/chat"}>
              <Outlet />
            </SheetPullWrapper>
          </AnimatePresence>
        </main>
      </div>
    </ChatTransitionProvider>
  )
}
