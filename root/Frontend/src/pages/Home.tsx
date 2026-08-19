import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { motion, AnimatePresence } from "framer-motion"
import {
  Database,
  Award,
  Cpu,
  Layers,
  Sparkles,
  ChevronDown,
  LineChart as LineChartIcon,
  ArrowRight,
} from "lucide-react"
import {
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  CartesianGrid,
  ReferenceArea,
  ReferenceLine,
} from "recharts"
import logoImg from "../assets/logo.png"
import scaleIcon from "../assets/icons/scale.png"

// ── Number Counter Component with Smooth Ease-Out ──
function AnimatedCounter({
  end,
  duration = 1.2,
  decimals = 0,
}: {
  end: number
  duration?: number
  decimals?: number
}) {
  const [count, setCount] = useState(0)

  useEffect(() => {
    let startTimestamp: number | null = null
    const step = (timestamp: number) => {
      if (!startTimestamp) startTimestamp = timestamp
      const progress = Math.min((timestamp - startTimestamp) / (duration * 1000), 1)
      const easeProgress = 1 - Math.pow(1 - progress, 3)
      setCount(easeProgress * end)
      if (progress < 1) {
        requestAnimationFrame(step)
      }
    }
    requestAnimationFrame(step)
  }, [end, duration])

  return <span>{count.toFixed(decimals)}</span>
}

// ── Interactive Chart Data: 3 Blended Curves ──
const simulationChartData = [
  { month: "M1", analog: 110000, bass: 85000, hybrid: 98000, actual: 98000 },
  { month: "M2", analog: 235000, bass: 185000, hybrid: 210000, actual: 210000 },
  { month: "M3", analog: 460000, bass: 380000, hybrid: 420000, actual: 420000 },
  { month: "M4", analog: 710000, bass: 650000, hybrid: 680000, actual: 680000 },
  { month: "M5", analog: 910000, bass: 850000, hybrid: 880000, actual: 880000 },
  { month: "M6", analog: 960000, bass: 880000, hybrid: 920000 },
  { month: "M7", analog: 1140000, bass: 1060000, hybrid: 1100000 },
  { month: "M8", analog: 1010000, bass: 950000, hybrid: 980741 },
  { month: "M9", analog: 960000, bass: 920000, hybrid: 940000 },
  { month: "M10", analog: 945000, bass: 923000, hybrid: 934000 },
  { month: "M11", analog: 940000, bass: 926000, hybrid: 933000 },
  { month: "M12", analog: 938000, bass: 927934, hybrid: 932967 },
]

export default function Home() {
  const navigate = useNavigate()

  // Hover states for top metric cards
  const [hoveredMetric, setHoveredMetric] = useState<number | null>(null)

  // Interactive link between Architecture Cards and Mathematical Formula Box
  const [activeSignal, setActiveSignal] = useState<"w1" | "w2" | null>(null)
  const [hoveredVariable, setHoveredVariable] = useState<string | null>(null)

  // FAQ open index
  const [openFaq, setOpenFaq] = useState<number | null>(0)

  // FAQ Items
  const faqItems = [
    {
      q: "Why combine Analog Matching with Bass Diffusion?",
      a: "Early pharmaceutical launches suffer from extreme data scarcity (often only 1–5 months of TRx). Historical analog curves provide the macro trajectory shape, while calibrated Bass diffusion captures the drug's own specific early prescriber trial and imitation dynamics. Harmonizing both signals produces statistically superior forecasts compared to either method alone.",
    },
    {
      q: "How many months of actual launch data are required?",
      a: "Baseline can generate pre-launch projections using 100% Analog Matching (0 known months), and dynamically transitions to the dual-signal blend as Month 1 through Month 5 actuals become available. The model continuously optimizes signal weights as additional data arrives.",
    },
    {
      q: "Can custom analog curves or proprietary assets be added?",
      a: "Yes. In the New Forecast workspace, analytics teams can upload custom TRx/NRx spreadsheets or analog CSV files with customizable therapeutic tags, formulary friction weights, and competitive entry assumptions.",
    },
  ]

  return (
    <div className="space-y-6 pb-16 text-[#2F4156]">
      {/* ── TOP HEADER BAR ── */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-5 border-b border-[#C8D9E6]">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16 flex-shrink-0 flex items-center justify-center">
            <img src={logoImg} alt="Baseline Logo" className="w-full h-full object-contain" />
          </div>
          <div className="border-l border-[#C8D9E6] pl-4">
            <h1 className="font-serif text-[28px] sm:text-[34px] font-medium leading-tight tracking-[-0.01em] text-[#2F4156]">
              About — Baseline Platform Architecture
            </h1>
            <p className="text-[13px] text-[#567C8D] mt-1 max-w-2xl">
              Deterministic pharmaceutical launch analytics combining 35 historical biopharma analogies
              with dynamically calibrated Bass adoption modeling.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => navigate("/dashboard")}
            className="flex items-center gap-2 bg-[#2F4156] hover:bg-[#1D2A37] active:scale-95 text-white text-xs font-semibold px-4.5 py-2.5 rounded-xl transition-all shadow-md border border-[#567C8D]/40 cursor-pointer"
          >
            <LineChartIcon className="w-4 h-4 text-[#C8D9E6]" />
            <span>Explore Forecast</span>
          </button>
        </div>
      </div>

      {/* ── SECTION 1: TOP 3 STAT CARDS (Animated Counters, Tooltips & Left-to-Right Teal Sweep) ── */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Card 1: Historical Launches */}
        <motion.div
          whileHover={{ y: -3 }}
          onMouseEnter={() => setHoveredMetric(1)}
          onMouseLeave={() => setHoveredMetric(null)}
          className="clean-tile-interactive rounded-[14px] p-5.5 relative overflow-hidden cursor-pointer group"
          title="35 curated benchmark biopharma launch curves across oncology, immunology, & rare disease"
        >
          {/* Teal fill overlay on hover */}
          <motion.div
            initial={false}
            animate={{
              clipPath:
                hoveredMetric === 1 ? "inset(0% 0% 0% 0%)" : "inset(0% 100% 0% 0%)",
            }}
            transition={{ duration: 0.42, ease: [0.25, 1, 0.5, 1] }}
            className="absolute inset-0 bg-[#567C8D] z-10 flex items-center justify-between p-5.5"
            style={{ boxShadow: "inset 0 1px 0 rgba(255, 255, 255, 0.25)" }}
          >
            <div className="flex items-center gap-3.5">
              <div className="w-11 h-11 rounded-xl bg-white/20 text-white border border-white/30 flex items-center justify-center flex-shrink-0">
                <Database className="w-5 h-5" />
              </div>
              <div>
                <div className="font-mono font-bold text-[28px] text-white leading-none">
                  <AnimatedCounter end={35} />
                </div>
                <div className="text-[12px] text-[#E2ECF4] font-medium mt-1">
                  Historical Launches
                </div>
              </div>
            </div>
            <div className="text-[10.5px] font-mono text-[#A3D9BE] font-semibold bg-white/10 px-2 py-1 rounded border border-white/20">
              Curated Library
            </div>
          </motion.div>

          {/* Base content */}
          <div className="relative z-0 flex items-center justify-between w-full">
            <div className="flex items-center gap-3.5">
              <div className="w-11 h-11 rounded-xl bg-[#EBF1F4] text-[#567C8D] border border-[#C8D9E6] flex items-center justify-center flex-shrink-0">
                <Database className="w-5 h-5" />
              </div>
              <div>
                <div className="font-mono font-bold text-[28px] text-[#2F4156] leading-none">
                  <AnimatedCounter end={35} />
                </div>
                <div className="text-[12px] text-[#567C8D] font-medium mt-1">
                  Historical Launches
                </div>
              </div>
            </div>
            <span className="text-[10.5px] font-mono text-[#567C8D] font-bold bg-[#EBF1F4] px-2 py-1 rounded border border-[#C8D9E6]">
              Library Active
            </span>
          </div>
        </motion.div>

        {/* Card 2: Mean MASE Score */}
        <motion.div
          whileHover={{ y: -3 }}
          onMouseEnter={() => setHoveredMetric(2)}
          onMouseLeave={() => setHoveredMetric(null)}
          className="clean-tile-interactive rounded-[14px] p-5.5 relative overflow-hidden cursor-pointer group"
          title="Mean Absolute Scaled Error (<1.0 is superior benchmark accuracy)"
        >
          {/* Teal fill overlay on hover */}
          <motion.div
            initial={false}
            animate={{
              clipPath:
                hoveredMetric === 2 ? "inset(0% 0% 0% 0%)" : "inset(0% 100% 0% 0%)",
            }}
            transition={{ duration: 0.42, ease: [0.25, 1, 0.5, 1] }}
            className="absolute inset-0 bg-[#567C8D] z-10 flex items-center justify-between p-5.5"
            style={{ boxShadow: "inset 0 1px 0 rgba(255, 255, 255, 0.25)" }}
          >
            <div className="flex items-center gap-3.5">
              <div className="w-11 h-11 rounded-xl bg-white/20 text-white border border-white/30 flex items-center justify-center flex-shrink-0">
                <Award className="w-5 h-5" />
              </div>
              <div>
                <div className="font-mono font-bold text-[28px] text-[#A3D9BE] leading-none">
                  <AnimatedCounter end={0.497} decimals={3} />
                </div>
                <div className="text-[12px] text-[#E2ECF4] font-medium mt-1">
                  Mean MASE Score
                </div>
              </div>
            </div>
            <div className="text-[10.5px] font-mono text-[#A3D9BE] font-semibold bg-white/10 px-2 py-1 rounded border border-white/20">
              &lt; 1.0 Superior
            </div>
          </motion.div>

          {/* Base content */}
          <div className="relative z-0 flex items-center justify-between w-full">
            <div className="flex items-center gap-3.5">
              <div className="w-11 h-11 rounded-xl bg-[#E8F5EE] text-[#2E7D5B] border border-[#A3D9BE] flex items-center justify-center flex-shrink-0">
                <Award className="w-5 h-5" />
              </div>
              <div>
                <div className="font-mono font-bold text-[28px] text-[#2E7D5B] leading-none">
                  <AnimatedCounter end={0.497} decimals={3} />
                </div>
                <div className="text-[12px] text-[#567C8D] font-medium mt-1">
                  Mean MASE Score
                </div>
              </div>
            </div>
            <span className="text-[10.5px] font-mono text-[#2E7D5B] font-bold bg-[#E8F5EE] px-2 py-1 rounded border border-[#A3D9BE]">
              50.3% Error Reduction
            </span>
          </div>
        </motion.div>

        {/* Card 3: LOO-CV Engine */}
        <motion.div
          whileHover={{ y: -3 }}
          onMouseEnter={() => setHoveredMetric(3)}
          onMouseLeave={() => setHoveredMetric(null)}
          className="clean-tile-interactive rounded-[14px] p-5.5 relative overflow-hidden cursor-pointer group"
          title="Leave-One-Out Cross-Validation Engine prevents overfitting and data leakage"
        >
          {/* Teal fill overlay on hover */}
          <motion.div
            initial={false}
            animate={{
              clipPath:
                hoveredMetric === 3 ? "inset(0% 0% 0% 0%)" : "inset(0% 100% 0% 0%)",
            }}
            transition={{ duration: 0.42, ease: [0.25, 1, 0.5, 1] }}
            className="absolute inset-0 bg-[#567C8D] z-10 flex items-center justify-between p-5.5"
            style={{ boxShadow: "inset 0 1px 0 rgba(255, 255, 255, 0.25)" }}
          >
            <div className="flex items-center gap-3.5">
              <div className="w-11 h-11 rounded-xl bg-white/20 text-white border border-white/30 flex items-center justify-center flex-shrink-0">
                <Cpu className="w-5 h-5" />
              </div>
              <div>
                <div className="font-mono font-bold text-[26px] text-white leading-none">
                  LOO-CV
                </div>
                <div className="text-[12px] text-[#E2ECF4] font-medium mt-1">
                  Validation Engine
                </div>
              </div>
            </div>
            <div className="text-[10.5px] font-mono text-[#A3D9BE] font-semibold bg-white/10 px-2 py-1 rounded border border-white/20">
              Cross-Validated
            </div>
          </motion.div>

          {/* Base content */}
          <div className="relative z-0 flex items-center justify-between w-full">
            <div className="flex items-center gap-3.5">
              <div className="w-11 h-11 rounded-xl bg-[#EBF1F4] text-[#567C8D] border border-[#C8D9E6] flex items-center justify-center flex-shrink-0">
                <Cpu className="w-5 h-5" />
              </div>
              <div>
                <div className="font-mono font-bold text-[26px] text-[#2F4156] leading-none">
                  LOO-CV
                </div>
                <div className="text-[12px] text-[#567C8D] font-medium mt-1">
                  Validation Engine
                </div>
              </div>
            </div>
            <span className="text-[10.5px] font-mono text-[#567C8D] font-bold bg-[#EBF1F4] px-2 py-1 rounded border border-[#C8D9E6]">
              Zero Data Leakage
            </span>
          </div>
        </motion.div>
      </div>

      {/* ── SECTION 2: DUAL SIGNAL INTEGRATION & VISUAL CURVE SIMULATION (2-Column Grid) ── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left Column (7 cols): Dual Signal Cards + Interactive Objective Function */}
        <div className="lg:col-span-7 space-y-4">
          <div className="clean-tile rounded-[18px] p-5 sm:p-6 space-y-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-[11px] uppercase tracking-wider text-[#567C8D] font-bold bg-[#EBF1F4] px-2 py-0.5 rounded border border-[#C8D9E6]">
                  Core Architecture
                </span>
                <span className="text-xs text-[#567C8D] font-mono">Dual-Signal Harmonization</span>
              </div>
              <h2 className="font-serif text-[22px] font-bold text-[#2F4156] mt-1.5">
                Deterministic Predictive Signals
              </h2>
              <p className="text-xs text-[#567C8D] leading-relaxed mt-1">
                Hover over either signal below to dynamically highlight its mathematical weight in the objective equation:
              </p>
            </div>

            {/* 2 Architecture Interactive Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              {/* Card 1: Analog Curve Matching (w1) */}
              <motion.div
                onMouseEnter={() => setActiveSignal("w1")}
                onMouseLeave={() => setActiveSignal(null)}
                className={`rounded-xl border transition-all cursor-pointer p-4 space-y-2 relative overflow-hidden ${
                  activeSignal === "w1"
                    ? "border-[#567C8D] bg-[#EBF1F4] shadow-md ring-2 ring-[#567C8D]/30"
                    : "border-[#C8D9E6] bg-[#FAF7F5] hover:bg-[#EBF1F4]"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="font-bold text-[#2F4156] text-[13.5px] flex items-center gap-1.5">
                    <Layers className="w-4 h-4 text-[#567C8D]" />
                    <span>1. Analog Curve (w₁)</span>
                  </div>
                  <span className="font-mono text-[11px] font-bold text-[#567C8D] bg-[#EBF1F4] px-2 py-0.5 rounded border border-[#C8D9E6]">
                    w₁ = 0.50
                  </span>
                </div>
                <p className="text-[11.5px] text-[#567C8D] leading-relaxed">
                  Evaluates historical trajectories from 35 pharmaceutical launches, computing Euclidean similarity across adoption velocity.
                </p>
              </motion.div>

              {/* Card 2: Calibrated Bass Diffusion (w2) */}
              <motion.div
                onMouseEnter={() => setActiveSignal("w2")}
                onMouseLeave={() => setActiveSignal(null)}
                className={`rounded-xl border transition-all cursor-pointer p-4 space-y-2 relative overflow-hidden ${
                  activeSignal === "w2"
                    ? "border-[#567C8D] bg-[#EBF1F4] shadow-md ring-2 ring-[#567C8D]/30"
                    : "border-[#C8D9E6] bg-[#FAF7F5] hover:bg-[#EBF1F4]"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="font-bold text-[#2F4156] text-[13.5px] flex items-center gap-1.5">
                    <img src={scaleIcon} alt="Calibration" className="w-4 h-4 object-contain" />
                    <span>2. Bass Diffusion (w₂)</span>
                  </div>
                  <span className="font-mono text-[11px] font-bold text-[#567C8D] bg-[#EBF1F4] px-2 py-0.5 rounded border border-[#C8D9E6]">
                    w₂ = 0.50
                  </span>
                </div>
                <p className="text-[11.5px] text-[#567C8D] leading-relaxed">
                  Fits non-linear adoption parameters (<b className="text-[#2F4156]">p</b>, <b className="text-[#2F4156]">q</b>, <b className="text-[#2F4156]">m</b>) directly to Month 1–5 early prescription actuals.
                </p>
              </motion.div>
            </div>

            {/* Mathematical Objective Formula Box with Dynamic Highlights & Hover Tooltips */}
            <div
              className="font-mono p-4.5 rounded-xl border border-[#C8D9E6]/20 text-[#C8D9E6] space-y-2.5"
              style={{
                backgroundColor: "#1D2A37",
                boxShadow:
                  "0 4px 14px rgba(29, 42, 55, 0.35), inset 0 1px 0 rgba(200, 217, 230, 0.15)",
              }}
            >
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-[#C8D9E6] uppercase tracking-wider font-bold">
                  Mathematical Objective Function
                </span>
                <span className="text-[#A3D9BE] font-semibold text-[10px]">
                  Interactive Variable Inspector
                </span>
              </div>

              {/* Formula String with Hoverable Tokens */}
              <div className="text-[14px] sm:text-[15px] font-bold text-white flex flex-wrap items-center gap-2 pt-1 pb-1">
                <span className="text-[#C8D9E6]">forecast(t)</span>
                <span>=</span>

                {/* w1 Variable Token */}
                <motion.span
                  animate={{
                    scale: activeSignal === "w1" || hoveredVariable === "w1" ? 1.1 : 1,
                    color:
                      activeSignal === "w1" || hoveredVariable === "w1"
                        ? "#A3D9BE"
                        : "#C8D9E6",
                    backgroundColor:
                      activeSignal === "w1" || hoveredVariable === "w1"
                        ? "rgba(163, 217, 190, 0.2)"
                        : "transparent",
                  }}
                  onMouseEnter={() => setHoveredVariable("w1")}
                  onMouseLeave={() => setHoveredVariable(null)}
                  className="px-2 py-0.5 rounded cursor-pointer border border-transparent hover:border-[#A3D9BE]/40"
                  title="Weight w₁: Dynamically calibrated analog weighting factor (0.50)"
                >
                  w₁
                </motion.span>
                <span>·</span>
                <span className="text-[#C8D9E6]">AnalogCurve(t)</span>
                <span>+</span>

                {/* w2 Variable Token */}
                <motion.span
                  animate={{
                    scale: activeSignal === "w2" || hoveredVariable === "w2" ? 1.1 : 1,
                    color:
                      activeSignal === "w2" || hoveredVariable === "w2"
                        ? "#F2B8B6"
                        : "#C8D9E6",
                    backgroundColor:
                      activeSignal === "w2" || hoveredVariable === "w2"
                        ? "rgba(242, 184, 182, 0.2)"
                        : "transparent",
                  }}
                  onMouseEnter={() => setHoveredVariable("w2")}
                  onMouseLeave={() => setHoveredVariable(null)}
                  className="px-2 py-0.5 rounded cursor-pointer border border-transparent hover:border-[#F2B8B6]/40"
                  title="Weight w₂: Fitted Bass diffusion coefficient (0.50)"
                >
                  w₂
                </motion.span>
                <span>·</span>
                <span className="text-[#F2B8B6]">BassDiffusion(t; p, q, m)</span>
              </div>

              {/* Interactive Tooltip Status Note */}
              <div className="text-[11px] text-[#C8D9E6] pt-1 border-t border-white/10 flex items-center justify-between">
                <span>
                  {activeSignal === "w1" || hoveredVariable === "w1"
                    ? "✦ Highlighting w₁: Analog curve weight dynamically optimized to Euclidean fit."
                    : activeSignal === "w2" || hoveredVariable === "w2"
                    ? "✦ Highlighting w₂: Bass diffusion weight fitted via non-linear residual optimization."
                    : "Hover over variables above or architecture cards to inspect signal dynamics."}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column (5 cols): Visual Graphic 3-Curve Overlay Simulation Chart */}
        <div className="lg:col-span-5 clean-tile rounded-[18px] p-5 sm:p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="font-mono text-[11px] uppercase tracking-wider text-[#567C8D] font-bold bg-[#EBF1F4] px-2 py-0.5 rounded border border-[#C8D9E6]">
                Visual Simulation
              </span>
              <span className="text-[11px] font-mono text-[#2E7D5B] font-bold flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-[#2E7D5B] animate-pulse" />
                M1–M5 Locked Actuals
              </span>
            </div>
            <h3 className="font-serif text-[18px] font-bold text-[#2F4156]">
              Tri-Signal Trajectory Convergence
            </h3>
            <p className="text-[11.5px] text-[#567C8D] mt-0.5">
              Overlay of Analog Curve, Calibrated Bass Model, and the Hybrid Forecast:
            </p>
          </div>

          {/* Recharts 3-Curve Graph with Light Glass Tooltip */}
          <div className="w-full h-44 sm:h-48 my-2">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart
                data={simulationChartData}
                margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="2 4" stroke="#C8D9E6" vertical={false} />
                <ReferenceArea x1="M1" x2="M5" fill="#EBF1F4" fillOpacity={0.75} />
                <ReferenceLine x="M5" stroke="#AFC5D6" strokeDasharray="3 3" />
                <XAxis
                  dataKey="month"
                  axisLine={{ stroke: "#C8D9E6" }}
                  tickLine={false}
                  tick={{ fontFamily: "IBM Plex Mono", fontSize: 10, fill: "#567C8D" }}
                />
                <YAxis
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
                  tick={{ fontFamily: "IBM Plex Mono", fontSize: 10, fill: "#567C8D" }}
                />
                <RechartsTooltip
                  content={({ active, payload, label }: any) => {
                    if (active && payload && payload.length) {
                      const isActual = ["M1", "M2", "M3", "M4", "M5"].includes(label)
                      return (
                        <div
                          className="bg-white/95 border border-[#C8D9E6] rounded-xl p-3.5 shadow-2xl font-mono text-xs space-y-2 min-w-[180px] backdrop-blur-md"
                          style={{
                            boxShadow:
                              "0 12px 30px -4px rgba(47, 65, 86, 0.20), 0 4px 10px -2px rgba(47, 65, 86, 0.10)",
                          }}
                        >
                          <div className="flex items-center justify-between pb-1.5 border-b border-[#C8D9E6]">
                            <span className="font-bold text-[#2F4156] text-[13px]">{label}</span>
                            <span
                              className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${
                                isActual
                                  ? "bg-[#E8F5EE] text-[#2E7D5B] border border-[#A3D9BE]"
                                  : "bg-[#EBF1F4] text-[#567C8D] border border-[#C8D9E6]"
                              }`}
                            >
                              {isActual ? "Actuals" : "Forecast"}
                            </span>
                          </div>
                          <div className="space-y-1.5 pt-0.5">
                            {payload.map((entry: any, index: number) => {
                              const color =
                                entry.dataKey === "analog"
                                  ? "#567C8D"
                                  : entry.dataKey === "bass"
                                  ? "#C25450"
                                  : "#2F4156"
                              return (
                                <div
                                  key={index}
                                  className="flex items-center justify-between gap-3 text-[11px]"
                                >
                                  <span className="flex items-center gap-1.5 font-semibold text-[#567C8D]">
                                    <span
                                      className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                                      style={{ backgroundColor: color }}
                                    />
                                    <span>{entry.name}:</span>
                                  </span>
                                  <span className="font-bold text-[#2F4156]">
                                    {Number(entry.value).toLocaleString()}{" "}
                                    <span className="text-[10px] font-normal text-[#7A92A2]">Rx</span>
                                  </span>
                                </div>
                              )
                            })}
                          </div>
                        </div>
                      )
                    }
                    return null
                  }}
                />
                {/* Curve 1: Analog Dashed (Teal) */}
                <Line
                  type="monotone"
                  dataKey="analog"
                  name="Analog Curve"
                  stroke="#567C8D"
                  strokeWidth={1.8}
                  strokeDasharray="4 4"
                  dot={false}
                  isAnimationActive={true}
                  animationDuration={1300}
                  animationEasing="ease-out"
                />
                {/* Curve 2: Bass Dashed (Bear Red Harmonized) */}
                <Line
                  type="monotone"
                  dataKey="bass"
                  name="Bass Model"
                  stroke="#C25450"
                  strokeWidth={1.8}
                  strokeDasharray="3 3"
                  dot={false}
                  isAnimationActive={true}
                  animationDuration={1300}
                  animationEasing="ease-out"
                />
                {/* Curve 3: Combined Hybrid Solid Bold (Navy) */}
                <Line
                  type="monotone"
                  dataKey="hybrid"
                  name="Baseline Hybrid"
                  stroke="#2F4156"
                  strokeWidth={3}
                  dot={{ r: 2.5, fill: "#2F4156" }}
                  activeDot={{ r: 4.5, fill: "#567C8D" }}
                  isAnimationActive={true}
                  animationDuration={1300}
                  animationEasing="ease-out"
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* Graph Legend */}
          <div className="grid grid-cols-3 gap-1.5 pt-2 border-t border-[#C8D9E6]/60 text-[10.5px] font-mono">
            <div className="flex items-center gap-1.5 text-[#567C8D]">
              <span className="w-2.5 h-0.5 bg-[#567C8D] border border-[#567C8D] border-dashed" />
              <span>Analog Curve</span>
            </div>
            <div className="flex items-center gap-1.5 text-[#C25450]">
              <span className="w-2.5 h-0.5 bg-[#C25450] border border-[#C25450] border-dashed" />
              <span>Bass Diffusion</span>
            </div>
            <div className="flex items-center gap-1.5 text-[#2F4156] font-bold">
              <span className="w-2.5 h-1 bg-[#2F4156] rounded-full" />
              <span>Baseline Hybrid</span>
            </div>
          </div>
        </div>
      </div>

      {/* ── SECTION 3: FAQ ACCORDION COMPONENT ── */}
      <div className="clean-tile rounded-[18px] p-5 sm:p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <span className="font-mono text-[11px] uppercase tracking-wider text-[#567C8D] font-bold bg-[#EBF1F4] px-2 py-0.5 rounded border border-[#C8D9E6]">
              Frequently Asked Questions
            </span>
            <h3 className="font-serif text-[20px] font-bold text-[#2F4156] mt-1">
              Methodology & Data FAQs
            </h3>
          </div>
          <span className="text-xs text-[#567C8D] font-mono hidden sm:inline">
            Deterministic Commercial Intelligence
          </span>
        </div>

        <div className="space-y-2.5">
          {faqItems.map((faq, idx) => {
            const isOpen = openFaq === idx
            return (
              <div
                key={idx}
                className="rounded-xl border border-[#C8D9E6] bg-[#FAF7F5] overflow-hidden transition-colors"
              >
                <button
                  onClick={() => setOpenFaq(isOpen ? null : idx)}
                  className="w-full p-4 text-left flex items-center justify-between gap-3 cursor-pointer font-bold text-[13px] text-[#2F4156] hover:bg-[#EBF1F4] transition-colors"
                >
                  <span>{faq.q}</span>
                  <ChevronDown
                    className={`w-4 h-4 text-[#567C8D] flex-shrink-0 transition-transform duration-200 ${
                      isOpen ? "rotate-180 text-[#2F4156]" : ""
                    }`}
                  />
                </button>

                <AnimatePresence>
                  {isOpen && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.25 }}
                      className="px-4 pb-4 text-[12.5px] text-[#567C8D] leading-relaxed border-t border-[#C8D9E6]/60 pt-2.5 bg-white/70"
                    >
                      {faq.a}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )
          })}
        </div>
      </div>

      {/* ── SECTION 4: HIGH-IMPACT CTA FOOTER BANNER ── */}
      <div
        className="rounded-[22px] p-6 sm:p-8 text-white border border-[#C8D9E6]/30 flex flex-wrap items-center justify-between gap-6 shadow-2xl relative overflow-hidden"
        style={{
          backgroundColor: "#1D2A37",
          backgroundImage:
            "radial-gradient(ellipse 100% 120% at 0% 0%, #2F4156 0%, #1D2A37 70%)",
        }}
      >
        <div className="space-y-1.5 max-w-xl relative z-10">
          <div className="flex items-center gap-2">
            <span className="text-xs text-[#C8D9E6] font-mono">LOO-CV Validated</span>
          </div>
          <h2 className="font-serif text-2xl sm:text-3xl font-bold tracking-tight text-white">
            Ready to project your next asset launch?
          </h2>
          <p className="text-xs text-[#E2ECF4] leading-relaxed">
            Run a deterministic launch forecast with calibrated analog matching and Bass curve fitting in under 5 minutes.
          </p>
        </div>

        {/* Action Button */}
        <div className="relative z-10">
          <button
            onClick={() => navigate("/upload")}
            className="flex items-center gap-2.5 bg-[#567C8D] hover:bg-[#436371] active:scale-95 text-white px-6 py-3.5 rounded-xl font-bold text-xs shadow-xl border border-white/20 cursor-pointer transition-all"
            style={{
              boxShadow:
                "0 10px 30px rgba(47, 65, 86, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.25)",
            }}
          >
            <span>Run New Forecast</span>
            <ArrowRight className="w-4 h-4 text-white" />
          </button>
        </div>

        {/* Subtle Background Glow */}
        <div
          className="absolute -bottom-10 -right-10 w-44 h-44 rounded-full bg-[#567C8D]/25 pointer-events-none blur-2xl"
        />
      </div>
    </div>
  )
}
