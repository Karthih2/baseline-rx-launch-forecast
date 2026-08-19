import { useState, useRef, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  Sparkles,
  Send,
  Bot,
  User,
  RotateCcw,
  Layers,
  ArrowRight,
  ArrowLeft,
  TrendingUp,
  Activity,
  Check,
  Copy,
  Table as TableIcon,
  BarChart2,
  Compass,
} from "lucide-react"
import logoImg from "../assets/logo.png"
import { useChatTransition } from "../context/ChatTransitionContext"

interface Message {
  id: string
  sender: "assistant" | "user"
  text: string
  timestamp: string
  structuredData?: {
    type?: "table" | "formula" | "comparison"
    title?: string
    tableHeaders?: string[]
    tableRows?: string[][]
    formula?: string
    metrics?: { label: string; value: string; color?: string }[]
    followUps?: string[]
  }
}

const STARTER_PROMPTS = [
  {
    id: "p1",
    title: "Payer Access Shock",
    prompt: "What happens if Tier 2 formulary access tightens by 15% starting in Month 6?",
    category: "Scenario Simulation",
    icon: TrendingUp,
    badge: "Bear Impact",
  },
  {
    id: "p2",
    title: "Analog Curve Weighting",
    prompt: "Why is Oral GLP-1 (ANL_014) assigned the highest similarity score of 0.91?",
    category: "Analog Intelligence",
    icon: Layers,
    badge: "Top Analog",
  },
  {
    id: "p3",
    title: "Bass Parameters Audit",
    prompt: "Explain how innovation rate p=0.0276 and imitation rate q=0.1204 affect the Month 8 peak.",
    category: "Mathematical Fit",
    icon: Activity,
    badge: "Bass Equation",
  },
  {
    id: "p4",
    title: "Bull vs. Bear Spread",
    prompt: "Compare the 12-month cumulative volume between Bull (+18.7%) and Bear (-13.2%) scenarios.",
    category: "Volume Comparison",
    icon: BarChart2,
    badge: "Revenue Spread",
  },
]

function parseInlineMarkdown(text: string, isAssistant: boolean): React.ReactNode[] {
  // Matches **bold**, *italic*, `code`
  const regex = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g
  const parts = text.split(regex)

  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong
          key={i}
          className={`font-bold ${isAssistant ? "text-[#2F4156]" : "text-white font-bold"}`}
        >
          {part.slice(2, -2)}
        </strong>
      )
    }
    if (part.startsWith("*") && part.endsWith("*")) {
      return (
        <em key={i} className="italic">
          {part.slice(1, -1)}
        </em>
      )
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code
          key={i}
          className={`font-mono text-[12px] px-1.5 py-0.5 rounded ${
            isAssistant
              ? "bg-[#EBF1F4] text-[#567C8D] border border-[#C8D9E6]"
              : "bg-white/20 text-white border border-white/30"
          }`}
        >
          {part.slice(1, -1)}
        </code>
      )
    }
    return part
  })
}

function renderMessageBody(text: string, isAssistant: boolean) {
  const paragraphs = text.split("\n\n")

  return paragraphs.map((paragraph, idx) => {
    const trimmed = paragraph.trim()

    // Heading
    if (trimmed.startsWith("### ")) {
      return (
        <h3
          key={idx}
          className={`font-serif text-[16px] font-bold mt-1 mb-1.5 ${
            isAssistant ? "text-[#2F4156]" : "text-white"
          }`}
        >
          {parseInlineMarkdown(trimmed.replace(/^###\s+/, ""), isAssistant)}
        </h3>
      )
    }

    // List items (lines starting with - or 1. / 2. / etc.)
    const lines = trimmed.split("\n")
    const isList = lines.every((line) => line.trim().startsWith("- ") || /^\d+\.\s+/.test(line.trim()))

    if (isList) {
      return (
        <div key={idx} className="space-y-1.5 my-1.5">
          {lines.map((line, lIdx) => {
            const lineTrim = line.trim()
            const isBullet = lineTrim.startsWith("- ")
            const isNumbered = /^\d+\.\s+/.test(lineTrim)
            const content = isBullet ? lineTrim.slice(2) : isNumbered ? lineTrim.replace(/^\d+\.\s+/, "") : lineTrim

            return (
              <div
                key={lIdx}
                className={`text-[13.5px] leading-relaxed pl-3 border-l-2 flex items-start gap-1.5 ${
                  isAssistant ? "border-[#567C8D]/50 text-[#2F4156]" : "border-white/50 text-white"
                }`}
              >
                {isNumbered && (
                  <span className={`font-mono text-[12px] font-bold flex-shrink-0 ${isAssistant ? "text-[#567C8D]" : "text-white"}`}>
                    {lineTrim.match(/^\d+\./)?.[0]}
                  </span>
                )}
                <span>{parseInlineMarkdown(content, isAssistant)}</span>
              </div>
            )
          })}
        </div>
      )
    }

    // Regular paragraph with potential single line breaks
    return (
      <p
        key={idx}
        className={`leading-relaxed text-[13.5px] ${
          isAssistant ? "text-[#2F4156]" : "text-white"
        }`}
      >
        {lines.map((line, lIdx) => (
          <span key={lIdx}>
            {parseInlineMarkdown(line, isAssistant)}
            {lIdx < lines.length - 1 && <br />}
          </span>
        ))}
      </p>
    )
  })
}

export default function ChatAssistant() {
  const { closeChat, isTransitioning } = useChatTransition()
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "msg-welcome",
      sender: "assistant",
      text: "Hello! I am **BLU (Base Line Unit)**, the conversational intelligence engine for the **Baseline Launch Forecasting Platform**.\n\nI have real-time access to the current **DrugX** launch forecast model, calibrated against **35 benchmark launches** with a validated **0.497 MASE score** (LOO-CV).\n\nHere is what you can ask me to analyze or simulate:",
      timestamp: "Just now",
      structuredData: {
        type: "comparison",
        title: "Active Forecast Parameters (DrugX)",
        metrics: [
          { label: "Active Model", value: "Analog + Bass Blended", color: "#567C8D" },
          { label: "Peak Month (Base)", value: "Month 8 (980.7k Rx)", color: "#567C8D" },
          { label: "12-Mo Cumulative", value: "10.98M Rx", color: "#567C8D" },
          { label: "Scenario Range", value: "-13.2% to +18.7%", color: "#2E7D5B" },
        ],
        followUps: [
          "Why is peak month occurring at Month 8?",
          "How was the 50/50 blend ratio determined?",
          "Show me top 5 analog similarity rankings",
          "What is the impact of increasing marketing spend in M4?",
        ],
      },
    },
  ])

  const [inputQuery, setInputQuery] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const [hoveredPrompt, setHoveredPrompt] = useState<string | null>(null)
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isTyping])

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const handleSend = (queryToSend?: string) => {
    const text = queryToSend || inputQuery.trim()
    if (!text || isTyping) return

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      sender: "user",
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    }

    setMessages((prev) => [...prev, userMessage])
    if (!queryToSend) setInputQuery("")
    setIsTyping(true)

    // Simulate BLU clinical-grade deterministic reasoning response
    setTimeout(() => {
      const response = generateAIResponse(text)
      setMessages((prev) => [...prev, response])
      setIsTyping(false)
    }, 950)
  }

  const generateAIResponse = (prompt: string): Message => {
    const q = prompt.toLowerCase()
    const timestamp = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })

    // 1. Payer access / Formulary scenario
    if (q.includes("payer") || q.includes("access") || q.includes("tier") || q.includes("shock")) {
      return {
        id: `asst-${Date.now()}`,
        sender: "assistant",
        text: "### Payer Access Sensitivity Analysis (Month 6 Step-down)\n\nSimulating a **15% restriction in Tier 2 access** at Month 6 shifts the adoption curve toward the **Bear Scenario trajectory** by throttling physician conversion velocity and prior-authorization throughput.",
        timestamp,
        structuredData: {
          type: "table",
          title: "Projected Impact on DrugX Key Metrics",
          tableHeaders: ["Metric", "Base Forecast", "Payer Shock (-15%)", "Variance"],
          tableRows: [
            ["Peak Month", "Month 8", "Month 5 (premature)", "-3 months"],
            ["Peak Monthly Rx", "980,741", "870,442", "-11.2%"],
            ["Month 12 Rx", "932,967", "840,120", "-9.9%"],
            ["12-Mo Cumulative", "10,978,279", "9,530,110", "-1,448,169 (-13.2%)"],
          ],
          metrics: [
            { label: "Net Volume At Risk", value: "1.45M Rx", color: "#C25450" },
            { label: "Adoption Deceleration", value: "×0.90 speed", color: "#C25450" },
          ],
          followUps: [
            "What copay card offset strategy mitigates this drop?",
            "How does this compare to ANL_030 JAK inhibitor friction?",
            "Export this sensitivity table",
          ],
        },
      }
    }

    // 2. Analog intelligence / ANL_014
    if (q.includes("analog") || q.includes("anl_014") || q.includes("similarity") || q.includes("weight")) {
      return {
        id: `asst-${Date.now()}`,
        sender: "assistant",
        text: "### Historical Analog Matching Breakdown\n\n**ANL_014 (Oral GLP-1 agonist, 2021 Launch)** receives the highest match score (**0.91 Euclidean similarity**) due to three primary adoption dynamics:\n\n1. **Early Uptake Velocity**: Months 1–5 trajectory closely mirrors DrugX's rapid commercial ramp.\n2. **Prescriber Overlap**: 78% specialty endocrinology + primary care dual-channel adoption profile.\n3. **Formulary Curve Geometry**: Minimal initial step-therapy hurdle followed by rapid Tier 2 broad uptake.",
        timestamp,
        structuredData: {
          type: "table",
          title: "Top 5 Historical Analog Ensemble",
          tableHeaders: ["Analog ID", "Drug Class & Formulation", "Launch Year", "Similarity", "Peak Share", "Curve Shape"],
          tableRows: [
            ["ANL_014", "GLP-1 agonist · Oral", "2021", "0.91", "24.5%", "Exponential Adoption"],
            ["ANL_028", "GLP-1 agonist · Injectable", "2019", "0.87", "31.2%", "High Imitation Bass"],
            ["ANL_016", "SGLT2 inhibitor · Oral", "2018", "0.82", "18.9%", "Steady Linear Peak"],
            ["ANL_022", "GLP-1 agonist · Oral", "2022", "0.79", "21.0%", "S-Curve Diffusion"],
            ["ANL_030", "JAK inhibitor · Oral", "2020", "0.74", "14.8%", "Targeted Niche Fit"],
          ],
          followUps: [
            "Why is injectable GLP-1 (ANL_028) weighted second?",
            "How does similarity threshold filter non-relevant analogs?",
            "Can I add a custom analog to the reference library?",
          ],
        },
      }
    }

    // 3. Bass equation / Parameters (p, q, m)
    if (q.includes("bass") || q.includes("parameter") || q.includes("equation") || q.includes("formula") || q.includes("p=") || q.includes("q=")) {
      return {
        id: `asst-${Date.now()}`,
        sender: "assistant",
        text: "### Calibrated Bass Diffusion Parameters\n\nThe fitted Bass model solves for innovation uptake ($p$) and word-of-mouth imitation ($q$) across the total addressable commercial ceiling ($m$):\n\n$$\\frac{dN(t)}{dt} = \\left(p + \\frac{q}{m} N(t)\\right)(m - N(t))$$\n\n- **Innovation Factor ($p = 0.0276$)**: Reflects initial trialist prescriber enthusiasm driven by launch PR and sales reps.\n- **Imitation Factor ($q = 0.1204$)**: Represents peer influence, clinical guidelines, and KOL recommendation diffusion.\n- **Market Ceiling ($m = 23.2\\text{M Rx}$)**: Total addressable eligible patient population under current label guidelines.",
        timestamp,
        structuredData: {
          type: "formula",
          title: "Dynamic Blending Objective Function",
          formula: "forecast(t) = 0.50 · AnalogCurve(t) + 0.50 · BassDiffusion(t)",
          metrics: [
            { label: "p (Innovation)", value: "0.0276", color: "#567C8D" },
            { label: "q (Imitation)", value: "0.1204", color: "#567C8D" },
            { label: "m (Market Size)", value: "23.2M", color: "#567C8D" },
            { label: "Blend Calibration", value: "13.57 factor", color: "#2E7D5B" },
          ],
          followUps: [
            "What happens if q increases to 0.1800 via KOL advocacy?",
            "How does LOO-CV validate this blend ratio?",
            "Show Month 12 cumulative volume prediction",
          ],
        },
      }
    }

    // 4. Bull vs Bear / Scenarios comparison
    if (q.includes("bull") || q.includes("bear") || q.includes("scenario") || q.includes("spread") || q.includes("compare")) {
      return {
        id: `asst-${Date.now()}`,
        sender: "assistant",
        text: "### Scenario Spread Comparison (Month 12 Horizon)\n\nThe forecast establishes three calibrated scenario bands based on market expansion variance and prescriber adoption velocity:",
        timestamp,
        structuredData: {
          type: "comparison",
          title: "Scenario Performance Comparison",
          tableHeaders: ["Scenario", "Peak Month", "Peak Monthly Rx", "Month 12 Rx", "12-Mo Cumulative", "Spread vs Base"],
          tableRows: [
            ["Bull", "Month 12", "1,353,266", "1,353,266", "12,507,866", "+18.7% (+1.53M)"],
            ["Base", "Month 8", "980,741", "932,967", "10,978,279", "Baseline benchmark"],
            ["Bear", "Month 5", "988,627", "870,442", "9,530,110", "-13.2% (-1.45M)"],
          ],
          metrics: [
            { label: "Total Scenario Envelope", value: "2.98M Rx Spread", color: "#567C8D" },
            { label: "Bull Growth Driver", value: "Market +15%, speed ×1.10", color: "#2E7D5B" },
            { label: "Bear Constraint", value: "Market -15%, speed ×0.90", color: "#C25450" },
          ],
          followUps: [
            "Explain why Bull peaks in Month 12 while Bear peaks in Month 5",
            "What competitive entry triggers the Bear scenario?",
            "How does this impact Q4 supply chain production?",
          ],
        },
      }
    }

    // Default intelligent launch copilot response
    return {
      id: `asst-${Date.now()}`,
      sender: "assistant",
      text: `### Launch Intelligence Assessment\n\nRegarding **"${prompt}"**:\n\nBased on the current **DrugX** launch dataset (5 known actual months, M1–M5), BLU projects continued strong momentum:\n\n- **Adoption Phase**: Currently transitioning from Innovator trialists to Early Majority imitation.\n- **Near-term Trajectory**: Month 6 is projected at **920,000 Rx** (Base), with an expected peak at **Month 8 (980,741 Rx)**.\n- **Confidence**: Backtested against historical validation with **0.497 MASE** error bound, indicating 50.3% error reduction over standard naive persistence models.`,
      timestamp,
      structuredData: {
        type: "comparison",
        title: "Strategic Recommendations",
        metrics: [
          { label: "Recommended Action", value: "Maintain Tier 2 Rebate Support", color: "#567C8D" },
          { label: "Signal Robustness", value: "High (5/5 Analogs Concordant)", color: "#2E7D5B" },
        ],
        followUps: [
          "Simulate a 15% payer access restriction in Month 6",
          "Explain the Bass equation coefficients (p, q, m)",
          "Why is Oral GLP-1 (ANL_014) similarity 0.91?",
          "Compare Bull, Base, and Bear scenarios",
        ],
      },
    }
  }

  const handleResetChat = () => {
    setMessages([
      {
        id: "msg-welcome-reset",
        sender: "assistant",
        text: "BLU session refreshed! Ready to evaluate launch scenarios, analog curve dynamics, and Bass diffusion parameters.",
        timestamp: "Just now",
        structuredData: {
          type: "comparison",
          title: "Quick Start Actions",
          metrics: [
            { label: "Active Forecast", value: "DrugX (5 Mo Known)", color: "#567C8D" },
            { label: "Validation Metric", value: "0.497 MASE (LOO-CV)", color: "#2E7D5B" },
          ],
          followUps: [
            "Simulate a 15% payer access restriction in Month 6",
            "Why is Oral GLP-1 (ANL_014) assigned 0.91 similarity?",
            "Explain innovation factor p and imitation factor q",
            "Show 12-month scenario comparison table",
          ],
        },
      },
    ])
  }

  return (
    <div className="space-y-7 pb-20 text-[#2F4156]">
      {/* ── TOP HEADER BAR WITH BACK BUTTON ── */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-5 border-b border-[#C8D9E6]">
        <div className="flex items-center gap-3.5">
          {/* Small Top-Left Back Button to Trigger Reverse Shrink Transition */}
          <motion.button
            onClick={closeChat}
            disabled={isTransitioning}
            whileHover={{ scale: 1.05, x: -2 }}
            whileTap={{ scale: 0.95 }}
            className="w-10 h-10 rounded-full bg-white hover:bg-[#EBF1F4] text-[#2F4156] border border-[#C8D9E6] shadow-sm flex items-center justify-center cursor-pointer transition-colors"
            title="Back to previous page"
            aria-label="Back to previous page"
          >
            <ArrowLeft className="w-5 h-5 text-[#2F4156]" />
          </motion.button>

          <div>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16 flex-shrink-0 flex items-center justify-center">
                <img src={logoImg} alt="Baseline Logo" className="w-full h-full object-contain" />
              </div>
              <h1 className="font-serif text-[26px] sm:text-[32px] font-medium leading-tight tracking-[-0.01em] text-[#2F4156]">
                BLU — Base Line Unit
              </h1>
            </div>
            <div className="mt-1 flex flex-wrap items-center gap-2 sm:gap-4 text-[12.5px] text-[#567C8D]">
              <span className="flex items-center gap-1.5 font-medium">
                <span className="w-2 h-2 rounded-full bg-[#2E7D5B] animate-pulse" />
                <b className="font-semibold text-[#2F4156]">Online</b>
              </span>
              <span className="text-[#C8D9E6]">•</span>
              <span>
                Target: <b className="font-semibold text-[#2F4156]">DrugX Forecast</b>
              </span>
              <span className="text-[#C8D9E6]">•</span>
              <span>
                Calibrated on: <b className="font-semibold text-[#2F4156]">35 Pharma Analogs</b>
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={handleResetChat}
            className="flex items-center gap-1.5 bg-[#FAF7F5] hover:bg-[#EBF1F4] active:scale-95 text-[#2F4156] text-xs font-semibold px-3.5 py-2 rounded-xl border border-[#C8D9E6] transition-all cursor-pointer shadow-xs"
            title="Reset conversation"
          >
            <RotateCcw className="w-3.5 h-3.5 text-[#567C8D]" />
            <span>Clear Session</span>
          </button>
        </div>
      </div>

      {/* ── TOP SUGGESTION TILES (With Left-to-Right Teal Fill Hover Effect) ── */}
      <div>
        <span className="font-mono text-[11px] tracking-[.08em] uppercase text-[#567C8D] mb-3 block font-bold">
          Quick Launch Intelligence Prompts
        </span>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {STARTER_PROMPTS.map((item) => {
            const Icon = item.icon
            return (
              <motion.div
                key={item.id}
                whileHover={{ y: -3 }}
                onMouseEnter={() => setHoveredPrompt(item.id)}
                onMouseLeave={() => setHoveredPrompt(null)}
                onClick={() => handleSend(item.prompt)}
                className="clean-tile-interactive rounded-[15px] p-4.5 relative overflow-hidden cursor-pointer flex flex-col justify-between"
              >
                {/* ── Left-to-Right Teal Fill Layer ── */}
                <motion.div
                  initial={false}
                  animate={{
                    clipPath:
                      hoveredPrompt === item.id
                        ? "inset(0% 0% 0% 0%)"
                        : "inset(0% 100% 0% 0%)",
                  }}
                  transition={{ duration: 0.42, ease: [0.25, 1, 0.5, 1] }}
                  className="absolute inset-0 bg-[#567C8D] p-4.5 z-10 flex flex-col justify-between text-white"
                  style={{
                    boxShadow: "inset 0 1px 0 rgba(255, 255, 255, 0.25)",
                  }}
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[11px] font-mono text-[#A3D9BE] font-semibold uppercase tracking-wider">
                        {item.category}
                      </span>
                      <Icon className="w-4 h-4 text-[#E2ECF4]" />
                    </div>
                    <div className="text-[13.5px] font-bold text-white leading-snug">
                      {item.title}
                    </div>
                    <p className="text-[11.5px] text-[#E2ECF4] mt-1.5 line-clamp-2 leading-relaxed">
                      {item.prompt}
                    </p>
                  </div>
                  <div className="flex items-center gap-1 text-[11px] font-mono text-[#A3D9BE] font-semibold mt-3 pt-2 border-t border-white/15">
                    <span>Ask BLU</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </div>
                </motion.div>

                {/* ── Base Card Content ── */}
                <div className="relative z-0 flex flex-col justify-between h-full">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[11px] font-mono text-[#567C8D] font-bold uppercase tracking-wider">
                        {item.category}
                      </span>
                      <div className="w-7 h-7 rounded-lg bg-[#EBF1F4] border border-[#C8D9E6] flex items-center justify-center text-[#567C8D]">
                        <Icon className="w-3.5 h-3.5" />
                      </div>
                    </div>
                    <div className="text-[13.5px] font-bold text-[#2F4156] leading-snug">
                      {item.title}
                    </div>
                    <p className="text-[11.5px] text-[#567C8D] mt-1.5 line-clamp-2 leading-relaxed">
                      {item.prompt}
                    </p>
                  </div>
                  <div className="flex items-center justify-between text-[11px] font-mono text-[#7A92A2] mt-3 pt-2 border-t border-[#C8D9E6]/60">
                    <span className="font-semibold text-[#567C8D]">{item.badge}</span>
                    <span className="flex items-center gap-1 text-[#567C8D] font-medium">
                      Click to ask <ArrowRight className="w-3 h-3 text-[#567C8D]" />
                    </span>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>
      </div>

      {/* ── MAIN INTERACTIVE CHAT ARENA ── */}
      <div className="clean-tile rounded-[20px] p-5 sm:p-7 shadow-lg flex flex-col min-h-[580px] border border-[#C8D9E6]">
        {/* Chat Control / Context Status Bar */}
        <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-[#C8D9E6] text-xs">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-[#2F4156] text-[#C8D9E6] border border-[#C8D9E6]/30 flex items-center justify-center">
              <Bot className="w-4 h-4" />
            </div>
            <div>
              <div className="font-bold text-[#2F4156]">BLU — Base Line Unit Dialogue</div>
              <div className="text-[11px] text-[#567C8D] font-mono">
                Context: DrugX · M1-M5 Historical Actuals · 50/50 Dual Blend
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="bg-[#E8F5EE] text-[#2E7D5B] border border-[#A3D9BE] px-2.5 py-1 rounded-full text-[11px] font-mono font-bold flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-[#2E7D5B]" />
              LOO-CV: 0.497 MASE
            </span>
          </div>
        </div>

        {/* Message Stream */}
        <div className="flex-1 overflow-y-auto py-5 space-y-5 max-h-[560px] pr-1">
          <AnimatePresence initial={false}>
            {messages.map((msg) => {
              const isAssistant = msg.sender === "assistant"
              return (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.28, ease: "easeOut" }}
                  className={`flex gap-3.5 ${isAssistant ? "items-start" : "items-start justify-end"}`}
                >
                  {isAssistant && (
                    <div className="w-8 h-8 rounded-xl bg-[#2F4156] text-[#C8D9E6] flex items-center justify-center flex-shrink-0 shadow-sm border border-[#567C8D] mt-0.5">
                      <Bot className="w-4.5 h-4.5" />
                    </div>
                  )}

                  <div className={`max-w-[88%] sm:max-w-[82%] space-y-2.5 ${isAssistant ? "text-left" : "text-right"}`}>
                    {/* Message Bubble */}
                    <div
                      className={`p-4 sm:p-5 rounded-2xl text-[13.5px] leading-relaxed shadow-sm relative group ${
                        isAssistant
                          ? "bg-white border border-[#C8D9E6] text-[#2F4156]"
                          : "bg-[#2F4156] text-white border border-[#567C8D]/40"
                      }`}
                    >
                      {/* Copy Message Action for Assistant */}
                      {isAssistant && (
                        <button
                          onClick={() => handleCopy(msg.id, msg.text)}
                          className="absolute top-3 right-3 text-[#7A92A2] hover:text-[#2F4156] p-1 rounded-md opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer bg-[#FAF7F5] border border-[#C8D9E6]"
                          title="Copy text"
                        >
                          {copiedId === msg.id ? (
                            <Check className="w-3.5 h-3.5 text-[#2E7D5B]" />
                          ) : (
                            <Copy className="w-3.5 h-3.5" />
                          )}
                        </button>
                      )}

                      {/* Formatted Message Body with Markdown Bold, Italics, Code & Lists */}
                      <div className="space-y-2">
                        {renderMessageBody(msg.text, isAssistant)}
                      </div>

                      {/* ── Structured Artifact / Table / Metrics rendering ── */}
                      {msg.structuredData && (
                        <div className="mt-3.5 pt-3.5 border-t border-[#C8D9E6] space-y-3">
                          {/* Title */}
                          {msg.structuredData.title && (
                            <div className="font-mono text-[11px] uppercase tracking-wider font-bold text-[#567C8D] flex items-center gap-1.5">
                              <TableIcon className="w-3.5 h-3.5" />
                              {msg.structuredData.title}
                            </div>
                          )}

                          {/* Metric Pill Grid */}
                          {msg.structuredData.metrics && (
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                              {msg.structuredData.metrics.map((m, i) => (
                                <div
                                  key={i}
                                  className="bg-[#FAF7F5] p-2.5 rounded-xl border border-[#C8D9E6] text-left"
                                >
                                  <div className="text-[10.5px] font-mono text-[#567C8D] font-semibold">{m.label}</div>
                                  <div
                                    className="text-[13px] font-bold font-mono mt-0.5"
                                    style={{ color: m.color || "#2F4156" }}
                                  >
                                    {m.value}
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}

                          {/* Data Table */}
                          {msg.structuredData.tableHeaders && msg.structuredData.tableRows && (
                            <div className="overflow-x-auto rounded-xl border border-[#C8D9E6] bg-[#FAF7F5]">
                              <table className="w-full text-left text-xs border-collapse font-sans">
                                <thead>
                                  <tr className="bg-[#EBF1F4] border-b border-[#C8D9E6]">
                                    {msg.structuredData.tableHeaders.map((head, hIdx) => (
                                      <th
                                        key={hIdx}
                                        className="py-2.5 px-3 font-mono font-bold text-[10.5px] uppercase text-[#567C8D] tracking-wider"
                                      >
                                        {head}
                                      </th>
                                    ))}
                                  </tr>
                                </thead>
                                <tbody>
                                  {msg.structuredData.tableRows.map((row, rIdx) => (
                                    <tr
                                      key={rIdx}
                                      className="border-b border-[#C8D9E6]/60 last:border-b-0 hover:bg-[#EBF1F4] transition-colors"
                                    >
                                      {row.map((cell, cIdx) => (
                                        <td key={cIdx} className="py-2.5 px-3 font-mono font-medium text-[#2F4156]">
                                          {cell}
                                        </td>
                                      ))}
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          )}

                          {/* Formula Box */}
                          {msg.structuredData.formula && (
                            <div
                              className="font-mono text-xs text-[#C8D9E6] p-3 rounded-xl flex items-center justify-between border border-[#C8D9E6]/20"
                              style={{ backgroundColor: "#1D2A37" }}
                            >
                              <span>{msg.structuredData.formula}</span>
                            </div>
                          )}

                          {/* Follow-up Question Chips */}
                          {msg.structuredData.followUps && (
                            <div className="pt-2 flex flex-wrap gap-1.5 items-center">
                              <span className="text-[11px] font-mono text-[#567C8D] font-bold mr-1">
                                Suggested questions:
                              </span>
                              {msg.structuredData.followUps.map((chip, cIdx) => (
                                <button
                                  key={cIdx}
                                  onClick={() => handleSend(chip)}
                                  className="text-[11.5px] font-sans font-semibold bg-[#EBF1F4] hover:bg-[#567C8D] hover:text-white text-[#567C8D] border border-[#C8D9E6] px-2.5 py-1 rounded-lg transition-colors cursor-pointer flex items-center gap-1"
                                >
                                  <span>{chip}</span>
                                  <ArrowRight className="w-3 h-3 opacity-60" />
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>

                    <div className="text-[10.5px] font-mono text-[#7A92A2] px-1">
                      {msg.timestamp}
                    </div>
                  </div>

                  {!isAssistant && (
                    <div className="w-8 h-8 rounded-xl bg-[#567C8D] text-white flex items-center justify-center flex-shrink-0 shadow-sm border border-[#2F4156] mt-0.5">
                      <User className="w-4.5 h-4.5 text-white" />
                    </div>
                  )}
                </motion.div>
              )
            })}
          </AnimatePresence>

          {/* Typing Animation State */}
          {isTyping && (
            <motion.div
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-start gap-3.5"
            >
              <div className="w-8 h-8 rounded-xl bg-[#2F4156] text-[#C8D9E6] flex items-center justify-center flex-shrink-0 shadow-sm border border-[#567C8D]">
                <Bot className="w-4.5 h-4.5" />
              </div>
              <div className="bg-white border border-[#C8D9E6] rounded-2xl p-3.5 shadow-sm flex items-center gap-2">
                <span className="text-xs font-mono text-[#567C8D] font-medium">
                  BLU is calculating model variance
                </span>
                <span className="flex gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#567C8D] animate-bounce" style={{ animationDelay: "0ms" }} />
                  <span className="w-1.5 h-1.5 rounded-full bg-[#567C8D] animate-bounce" style={{ animationDelay: "150ms" }} />
                  <span className="w-1.5 h-1.5 rounded-full bg-[#567C8D] animate-bounce" style={{ animationDelay: "300ms" }} />
                </span>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* ── INTERACTIVE INPUT BAR ── */}
        <div className="pt-3 border-t border-[#C8D9E6] space-y-2">
          {/* Quick Context Tags */}
          <div className="flex flex-wrap items-center justify-between text-[11px] text-[#7A92A2] font-mono px-1">
            <div className="flex items-center gap-3">
              <span>Press <b className="text-[#2F4156] font-bold">Enter ↵</b> to send</span>
              <span>•</span>
              <span><b className="text-[#2F4156] font-bold">Shift + Enter</b> for new line</span>
            </div>
            <div className="flex items-center gap-1.5 text-[#567C8D] font-semibold">
              <Compass className="w-3.5 h-3.5" />
              <span>BLU Deterministic Forecasting Model</span>
            </div>
          </div>

          <div className="relative flex items-end gap-2 bg-[#FAF7F5] border border-[#C8D9E6] rounded-2xl p-2 focus-within:border-[#567C8D] focus-within:ring-2 focus-within:ring-[#567C8D]/20 transition-all shadow-inner">
            <textarea
              ref={inputRef}
              rows={1}
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault()
                  handleSend()
                }
              }}
              placeholder="Ask BLU about DrugX forecast, analog curve matching, Bass parameters, or scenario risks..."
              className="flex-1 max-h-32 bg-transparent text-[13.5px] text-[#2F4156] placeholder-[#7A92A2] resize-none outline-none px-2.5 py-1.5 font-sans"
            />

            <button
              onClick={() => handleSend()}
              disabled={!inputQuery.trim() || isTyping}
              className={`p-2.5 rounded-xl font-bold transition-all flex items-center justify-center flex-shrink-0 cursor-pointer shadow-md ${
                inputQuery.trim() && !isTyping
                  ? "bg-[#2F4156] hover:bg-[#1D2A37] text-white active:scale-95 border border-[#567C8D]/40"
                  : "bg-[#C8D9E6] text-[#7A92A2] cursor-not-allowed border border-transparent"
              }`}
              title="Send message to BLU"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
