import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { motion, AnimatePresence } from "framer-motion"
import {
  Plus,
  Copy,
  Check,
  X,
  ExternalLink,
  Layers,
  Sparkles,
  ArrowBigUp,
  ArrowBigDown,
  Table as TableIcon,
  LineChart as LineChartIcon,
} from "lucide-react"
import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  ReferenceArea,
  ReferenceLine,
} from "recharts"
import logoImg from "../assets/logo.png"
import bullMarketIcon from "../assets/icons/bull-market.png"
import bearMarketIcon from "../assets/icons/bear-market.png"
import scaleIcon from "../assets/icons/scale.png"
import { loadForecastRun, type ForecastRun } from "../api"

// ── Number Counter Component with Smooth Ease-Out ──
function AnimatedCounter({
  end,
  duration = 1.2,
  decimals = 0,
  prefix = "",
  suffix = "",
}: {
  end: number
  duration?: number
  decimals?: number
  prefix?: string
  suffix?: string
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

  const formatted =
    decimals > 0 ? count.toFixed(decimals) : Math.round(count).toLocaleString()

  return (
    <span>
      {prefix}
      {formatted}
      {suffix}
    </span>
  )
}

type Scenario = "bull" | "base" | "bear"

interface AnalogItem {
  id: string
  name: string
  meta: string
  sim: string
  peakShare: string
  launchYear: string
  curveType: string
  description: string
}

const analogsData: AnalogItem[] = [
  {
    id: "ANL_014",
    name: "GLP-1 agonist · Oral",
    meta: "GLP-1 agonist · Oral",
    sim: "0.91",
    peakShare: "24.5%",
    launchYear: "2021",
    curveType: "Exponential Adoption",
    description: "Oral formulation with rapid uptake across primary care and endocrinology.",
  },
  {
    id: "ANL_028",
    name: "GLP-1 agonist · Injectable",
    meta: "GLP-1 agonist · Injectable",
    sim: "0.87",
    peakShare: "31.2%",
    launchYear: "2019",
    curveType: "High Imitation Bass",
    description: "Weekly injectable bassline with strong market expansion dynamics.",
  },
  {
    id: "ANL_016",
    name: "SGLT2 inhibitor · Oral",
    meta: "SGLT2 inhibitor · Oral",
    sim: "0.82",
    peakShare: "18.9%",
    launchYear: "2018",
    curveType: "Steady Linear Peak",
    description: "Established oral therapy with broad formulary coverage and moderate access friction.",
  },
  {
    id: "ANL_022",
    name: "GLP-1 agonist · Oral",
    meta: "GLP-1 agonist · Oral",
    sim: "0.79",
    peakShare: "21.0%",
    launchYear: "2022",
    curveType: "S-Curve Diffusion",
    description: "Secondary analog showing constrained early payer tiering followed by expansion.",
  },
  {
    id: "ANL_030",
    name: "JAK inhibitor · Oral",
    meta: "JAK inhibitor · Oral",
    sim: "0.74",
    peakShare: "14.8%",
    launchYear: "2020",
    curveType: "Targeted Niche Fit",
    description: "Specialty oral launch with stringent prior-authorization requirements.",
  },
]

const chartData = [
  { month: "M1", bear: 98000, base: 98000, bull: 98000 },
  { month: "M2", bear: 210000, base: 210000, bull: 210000 },
  { month: "M3", bear: 420000, base: 420000, bull: 420000 },
  { month: "M4", bear: 680000, base: 680000, bull: 680000 },
  { month: "M5", bear: 880000, base: 880000, bull: 880000 },
  { month: "M6", bear: 720000, base: 920000, bull: 1100000 },
  { month: "M7", bear: 810000, base: 1100000, bull: 1380000 },
  { month: "M8", bear: 870000, base: 980741, bull: 1220000 },
  { month: "M9", bear: 840000, base: 940000, bull: 1290000 },
  { month: "M10", bear: 855000, base: 934000, bull: 1320000 },
  { month: "M11", bear: 862000, base: 933000, bull: 1340000 },
  { month: "M12", bear: 870442, base: 932967, bull: 1353266 },
]

const tableData = [
  {
    scenario: "Bull" as Scenario,
    tagClass: "bull",
    peakMonth: 12,
    peakRx: 1353266,
    month12Rx: 1353266,
    cumulative: 12507866,
    avgGrowth: 2.89,
  },
  {
    scenario: "Base" as Scenario,
    tagClass: "base",
    peakMonth: 8,
    peakRx: 980741,
    month12Rx: 932967,
    cumulative: 10978279,
    avgGrowth: 3.41,
  },
  {
    scenario: "Bear" as Scenario,
    tagClass: "bear",
    peakMonth: 5,
    peakRx: 988627,
    month12Rx: 870442,
    cumulative: 9530110,
    avgGrowth: 2.10,
  },
]

const formulaParameters = [
  { key: "calib", label: "Calibration Factor", value: "13.57" },
  { key: "p", label: "p (innovation)", value: "0.0276" },
  { key: "q", label: "q (imitation)", value: "0.1204" },
  { key: "m", label: "m (ceiling)", value: "23.2M" },
  { key: "blend", label: "Blend (analog/bass)", value: "50 / 50" },
]

const scenarioContext = [
  {
    key: "bull" as Scenario,
    title: "Bull",
    color: "#2E7D5B",
    items: [
      { label: "Competitive entry", value: "Low" },
      { label: "Payer access", value: "Improving" },
      { label: "Promo spend", value: "Increasing" },
    ],
    note: "Market +15%, adoption speed ×1.10",
  },
  {
    key: "base" as Scenario,
    title: "Base",
    color: "#567C8D",
    items: [
      { label: "Competitive entry", value: "Moderate" },
      { label: "Payer access", value: "Stable" },
      { label: "Promo spend", value: "Stable" },
    ],
    note: "Fitted values, no adjustment",
  },
  {
    key: "bear" as Scenario,
    title: "Bear",
    color: "#C25450",
    items: [
      { label: "Competitive entry", value: "High" },
      { label: "Payer access", value: "Tightening" },
      { label: "Promo spend", value: "Decreasing" },
    ],
    note: "Market −15%, adoption speed ×0.90",
  },
]

function getScenarioIcon(key: Scenario) {
  switch (key) {
    case "bull":
      return bullMarketIcon
    case "base":
      return scaleIcon
    case "bear":
      return bearMarketIcon
  }
}

function formatY(v: number) {
  if (v >= 1000000) return `${(v / 1000000).toFixed(1)}M`
  if (v >= 1000) return `${(v / 1000).toFixed(0)}k`
  return `${v}`
}

export default function Dashboard() {
  const navigate = useNavigate()
  const [run] = useState<ForecastRun | null>(() => loadForecastRun())
  const [view, setView] = useState<"Graph" | "Table">("Graph")
  const [copied, setCopied] = useState(false)
  const [selectedAnalog, setSelectedAnalog] = useState<AnalogItem | null>(null)
  const [visibleScenarios, setVisibleScenarios] = useState<Record<Scenario, boolean>>({
    bull: true,
    base: true,
    bear: true,
  })

  // State to track hover for KPI cards 1-3
  const [hoveredCard, setHoveredCard] = useState<number | null>(null)
  // State to track hover for KPI card 4
  const [hoveredCard4, setHoveredCard4] = useState(false)

  // State to track hover for the 5 formula parameter cards
  const [hoveredParam, setHoveredParam] = useState<string | null>(null)

  // State to track hover for the 3 scenario assumption cards
  const [hoveredScenarioCard, setHoveredScenarioCard] = useState<Scenario | null>(null)

  const knownMonths = run?.known_monthly_rx ?? []
  const scenarioResult = (key: Scenario) => run?.scenario_results?.[key]
  const seriesFor = (key: Scenario) => [...knownMonths, ...(scenarioResult(key)?.forecast ?? [])]
  const chartData = Array.from({ length: run?.forecast_horizon_months ?? 0 }, (_, index) => ({
    month: `M${index + 1}`,
    bull: seriesFor("bull")[index] ?? null,
    base: seriesFor("base")[index] ?? null,
    bear: seriesFor("bear")[index] ?? null,
  }))
  const analogsData = (run?.selected_analogs ?? []).map((analog) => ({
    id: analog.drug_id,
    name: analog.drug_name || analog.drug_id,
    meta: `Rank ${analog.rank} analog`,
    sim: analog.similarity_score.toFixed(2),
    peakShare: "",
    launchYear: "",
    curveType: "Analog curve",
    description: `Similarity weight ${(analog.weight * 100).toFixed(1)}%`,
  }))
  const tableData = (Object.keys({ bull: true, base: true, bear: true }) as Scenario[]).map((key) => {
    const series = seriesFor(key)
    const peakRx = series.length ? Math.max(...series) : 0
    const peakMonth = series.length ? series.indexOf(peakRx) + 1 : 0
    const month12Rx = series.at(-1) ?? 0
    const growthValues = series.slice(1).map((value, index) => {
      const previous = series[index]
      return previous ? ((value - previous) / previous) * 100 : 0
    })
    return {
      scenario: key[0].toUpperCase() + key.slice(1) as Scenario,
      tagClass: key,
      peakMonth,
      peakRx,
      month12Rx,
      cumulative: series.reduce((sum, value) => sum + value, 0),
      avgGrowth: growthValues.length ? growthValues.reduce((sum, value) => sum + value, 0) / growthValues.length : 0,
    }
  })
  const baseSeries = seriesFor("base")
  const basePeak = baseSeries.length ? Math.max(...baseSeries) : 0
  const basePeakMonth = baseSeries.length ? baseSeries.indexOf(basePeak) + 1 : 0
  const baseCumulative = baseSeries.reduce((sum, value) => sum + value, 0)
  const month12 = baseSeries.at(-1) ?? 0
  const bullMonth12 = seriesFor("bull").at(-1) ?? 0
  const bearMonth12 = seriesFor("bear").at(-1) ?? 0
  const spread = (value: number) => month12 ? ((value / month12) - 1) * 100 : 0
  const baseParams = run?.base_bass_params
  const formulaParameters = run ? [
    { key: "calib", label: "Calibration Factor", value: baseParams?.calibration_factor.toFixed(2) ?? "" },
    { key: "p", label: "p (innovation)", value: baseParams?.bass_p.toFixed(4) ?? "" },
    { key: "q", label: "q (imitation)", value: baseParams?.bass_q.toFixed(4) ?? "" },
    { key: "m", label: "m (ceiling)", value: `${((baseParams?.bass_m ?? 0) / 1000000).toFixed(2)}M` },
    { key: "blend", label: "Blend (analog/bass)", value: `${((baseParams?.blend_weight_analog ?? 0) * 100).toFixed(0)} / ${((baseParams?.blend_weight_bass ?? 0) * 100).toFixed(0)}` },
  ] : []
  const scenarioContext = (Object.keys({ bull: true, base: true, bear: true }) as Scenario[]).map((key) => {
    const assumptions = run?.scenario_assumptions_used?.[key] ?? {}
    const title = key[0].toUpperCase() + key.slice(1)
    return {
      key,
      title,
      color: key === "bull" ? "#2E7D5B" : key === "bear" ? "#C25450" : "#567C8D",
      items: [
        { label: "Competitive entry", value: String(assumptions.competition_factor ?? "") },
        { label: "Payer access", value: String(assumptions.payer_access_factor ?? "") },
        { label: "Promo spend", value: String(assumptions.promotion_factor ?? "") },
      ],
      note: run ? `Market ×${Number(assumptions.market_size_multiplier ?? 0).toFixed(2)}, speed ×${Number(assumptions.adoption_speed_multiplier ?? 0).toFixed(2)}` : "",
    }
  })

  const toggleScenario = (s: Scenario) => {
    setVisibleScenarios((prev) => {
      const activeCount = Object.values(prev).filter(Boolean).length
      if (prev[s] && activeCount <= 1) return prev
      return { ...prev, [s]: !prev[s] }
    })
  }

  const handleCopyFormula = () => {
    navigator.clipboard.writeText("forecast = 0.50 * analog_curve + 0.50 * bass_curve")
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  // Filtered scenario comparison table rows based on graph selection
  const filteredTableData = tableData.filter(
    (row) => visibleScenarios[row.scenario.toLowerCase() as Scenario]
  )

  return (
    <div className="space-y-8 pb-16 text-[#2F4156]">
      {/* ---------- TOP HEADER BAR ---------- */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-[#C8D9E6]">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16 flex-shrink-0 flex items-center justify-center">
            <img src={logoImg} alt="Baseline Logo" className="w-full h-full object-contain" />
          </div>
          <div className="border-l border-[#C8D9E6] pl-4">
            <h1 className="font-serif text-[26px] sm:text-[32px] font-medium leading-tight tracking-[-0.01em] text-[#2F4156]">
              {run ? `${run.new_drug_name} — Launch Forecast` : "Launch Forecast"}
            </h1>
            <div className="mt-1 flex flex-wrap gap-4 sm:gap-6 text-[13px] text-[#567C8D]">
              <span>
                Model: <b className="font-semibold text-[#2F4156]">{run?.selected_model || "Awaiting forecast"}</b>
              </span>
              <span>
                Known months: <b className="font-semibold text-[#2F4156]">{run ? knownMonths.length : "—"}</b>
              </span>
              <span>
                Run: <b className="font-semibold text-[#2F4156]">{run ? new Date(run.uploaded_at).toLocaleString() : "—"}</b>
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate("/upload")}
            className="flex items-center gap-2 bg-[#2F4156] hover:bg-[#1D2A37] active:scale-95 text-white text-xs font-semibold px-4.5 py-2.5 rounded-xl transition-all shadow-md border border-[#567C8D]/40 cursor-pointer"
          >
            <Plus className="w-4 h-4 text-[#C8D9E6]" />
            <span>New Forecast</span>
          </button>
        </div>
      </div>

      {/* ---------- SECTION 1: STATS SUMMARY CARDS (Dynamic Left-to-Right Hover Transition) ---------- */}
      <div>
        <span className="font-mono text-[11px] tracking-[.08em] uppercase text-[#567C8D] mb-3 block font-bold">
          Stats
        </span>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Card 1: Peak Month */}
          <motion.div
            whileHover={{ y: -3 }}
            onMouseEnter={() => setHoveredCard(1)}
            onMouseLeave={() => setHoveredCard(null)}
            className="clean-tile-interactive rounded-[14px] p-5.5 relative overflow-hidden cursor-pointer"
          >
            {/* Smooth Left-to-Right Blue Fill Layer */}
            <motion.div
              initial={false}
              animate={{
                clipPath:
                  hoveredCard === 1
                    ? "inset(0% 0% 0% 0%)"
                    : "inset(0% 100% 0% 0%)",
              }}
              transition={{ duration: 0.42, ease: [0.25, 1, 0.5, 1] }}
              className="absolute inset-0 bg-[#567C8D] p-5.5 z-10 flex flex-col justify-between"
              style={{
                boxShadow: "inset 0 1px 0 rgba(255, 255, 255, 0.25)",
              }}
            >
              <div>
                <div className="text-[12.5px] text-[#E2ECF4] mb-2 font-medium">Peak Month</div>
                <div className="font-mono font-bold text-[30px] text-white">
                  {basePeakMonth ? <>Month <AnimatedCounter end={basePeakMonth} duration={1.1} /></> : "—"}
                </div>
              </div>
              <div className="text-[11.5px] text-[#C8D9E6] mt-1 font-mono font-semibold">
                Base scenario
              </div>
            </motion.div>

            {/* Base Card Content */}
            <div className="relative z-0">
              <div className="text-[12.5px] text-[#567C8D] mb-2 font-medium">Peak Month</div>
              <div className="font-mono font-semibold text-[30px] text-[#2F4156]">
                {basePeakMonth ? <>Month <AnimatedCounter end={basePeakMonth} duration={1.1} /></> : "—"}
              </div>
              <div className="text-[11.5px] text-[#7A92A2] mt-1 font-mono">Base scenario</div>
            </div>
          </motion.div>

          {/* Card 2: Peak Rx */}
          <motion.div
            whileHover={{ y: -3 }}
            onMouseEnter={() => setHoveredCard(2)}
            onMouseLeave={() => setHoveredCard(null)}
            className="clean-tile-interactive rounded-[14px] p-5.5 relative overflow-hidden cursor-pointer"
          >
            {/* Smooth Left-to-Right Blue Fill Layer */}
            <motion.div
              initial={false}
              animate={{
                clipPath:
                  hoveredCard === 2
                    ? "inset(0% 0% 0% 0%)"
                    : "inset(0% 100% 0% 0%)",
              }}
              transition={{ duration: 0.42, ease: [0.25, 1, 0.5, 1] }}
              className="absolute inset-0 bg-[#567C8D] p-5.5 z-10 flex flex-col justify-between"
              style={{
                boxShadow: "inset 0 1px 0 rgba(255, 255, 255, 0.25)",
              }}
            >
              <div>
                <div className="text-[12.5px] text-[#E2ECF4] mb-2 font-medium">Peak Rx</div>
                <div className="font-mono font-bold text-[30px] text-white">
                  {basePeak ? <AnimatedCounter end={basePeak} duration={1.3} /> : "—"}
                </div>
              </div>
              <div className="text-[11.5px] text-[#C8D9E6] mt-1 font-mono font-semibold">
                at peak month, Base
              </div>
            </motion.div>

            {/* Base Card Content */}
            <div className="relative z-0">
              <div className="text-[12.5px] text-[#567C8D] mb-2 font-medium">Peak Rx</div>
              <div className="font-mono font-semibold text-[30px] text-[#2F4156]">
                {basePeak ? <AnimatedCounter end={basePeak} duration={1.3} /> : "—"}
              </div>
              <div className="text-[11.5px] text-[#7A92A2] mt-1 font-mono">at peak month, Base</div>
            </div>
          </motion.div>

          {/* Card 3: 12-Month Cumulative Rx */}
          <motion.div
            whileHover={{ y: -3 }}
            onMouseEnter={() => setHoveredCard(3)}
            onMouseLeave={() => setHoveredCard(null)}
            className="clean-tile-interactive rounded-[14px] p-5.5 relative overflow-hidden cursor-pointer"
          >
            {/* Smooth Left-to-Right Blue Fill Layer */}
            <motion.div
              initial={false}
              animate={{
                clipPath:
                  hoveredCard === 3
                    ? "inset(0% 0% 0% 0%)"
                    : "inset(0% 100% 0% 0%)",
              }}
              transition={{ duration: 0.42, ease: [0.25, 1, 0.5, 1] }}
              className="absolute inset-0 bg-[#567C8D] p-5.5 z-10 flex flex-col justify-between"
              style={{
                boxShadow: "inset 0 1px 0 rgba(255, 255, 255, 0.25)",
              }}
            >
              <div>
                <div className="text-[12.5px] text-[#E2ECF4] mb-2 font-medium">12-Month Cumulative Rx</div>
                <div className="font-mono font-bold text-[30px] text-white">
                  {baseCumulative ? <AnimatedCounter end={baseCumulative / 1000000} decimals={2} duration={1.2} suffix="M" /> : "—"}
                </div>
              </div>
              <div className="text-[11.5px] text-[#C8D9E6] mt-1 font-mono font-semibold">
                Base scenario total
              </div>
            </motion.div>

            {/* Base Card Content */}
            <div className="relative z-0">
              <div className="text-[12.5px] text-[#567C8D] mb-2 font-medium">12-Month Cumulative Rx</div>
              <div className="font-mono font-semibold text-[30px] text-[#2F4156]">
                {baseCumulative ? <AnimatedCounter end={baseCumulative / 1000000} decimals={2} duration={1.2} suffix="M" /> : "—"}
              </div>
              <div className="text-[11.5px] text-[#7A92A2] mt-1 font-mono">Base scenario total</div>
            </div>
          </motion.div>

          {/* Card 4: Scenario Spread (Navy -> Teal dark glass with Sky Blue reflection) */}
          <motion.div
            whileHover={{ y: -3 }}
            onMouseEnter={() => setHoveredCard4(true)}
            onMouseLeave={() => setHoveredCard4(false)}
            animate={{
              background: hoveredCard4
                ? "linear-gradient(135deg, #1D2A37 0%, #2F4156 100%)"
                : "#567C8D",
            }}
            transition={{ duration: 0.35, ease: "easeInOut" }}
            className="rounded-[14px] p-5.5 flex flex-col justify-center text-white border border-[#C8D9E6]/30 cursor-pointer backdrop-blur-md"
            style={{
              boxShadow: "0 10px 25px -4px rgba(47, 65, 86, 0.35), 0 4px 10px -2px rgba(47, 65, 86, 0.20), inset 0 1px 0 rgba(200, 217, 230, 0.35)",
            }}
          >
            <div className="text-[12.5px] text-[#E2ECF4] mb-2 leading-snug font-medium">
              Scenario Spread vs. Base (Month 12)
            </div>
            <div className="flex justify-between items-center font-mono text-[14px] mt-1">
              <span className="text-[#A3D9BE] font-bold flex items-center gap-1">
                <ArrowBigUp className="w-4 h-4 fill-current" /> Bull {month12 ? <AnimatedCounter end={spread(bullMonth12)} decimals={1} duration={1.2} /> : "—"}%
              </span>
              <span className="text-[#F2B8B6] font-bold flex items-center gap-1">
                <ArrowBigDown className="w-4 h-4 fill-current" /> Bear {month12 ? <AnimatedCounter end={spread(bearMonth12)} decimals={1} duration={1.2} /> : "—"}%
              </span>
            </div>
          </motion.div>
        </div>
      </div>

      {/* ---------- SECTION 2: MAIN DATA GRID (1.7fr / 1fr) ---------- */}
      <div className="grid grid-cols-1 lg:grid-cols-[1.7fr_1fr] gap-6">
        {/* Left Panel: 12-Month Interactive Chart with dynamic shadows for all 3 scenarios */}
        <div className="clean-tile rounded-[16px] p-6.5">
          <div className="flex flex-wrap justify-between items-center gap-3 mb-4">
            <div className="font-serif text-[21px] font-medium text-[#2F4156]">
              12-Month Forecast
            </div>

            <div className="flex items-center gap-4">
              {/* Legend Toggles */}
              <div className="flex items-center gap-3 text-xs font-medium text-[#567C8D]">
                <button
                  onClick={() => toggleScenario("bull")}
                  className={`inline-flex items-center gap-1.5 transition-all cursor-pointer ${visibleScenarios.bull ? "opacity-100 font-bold text-[#2E7D5B]" : "opacity-40"
                    }`}
                >
                  <img src={bullMarketIcon} alt="Bull" className="w-3.5 h-3.5 object-contain inline-block" />
                  Bull
                </button>
                <button
                  onClick={() => toggleScenario("base")}
                  className={`inline-flex items-center gap-1.5 transition-all cursor-pointer ${visibleScenarios.base ? "opacity-100 font-bold text-[#567C8D]" : "opacity-40"
                    }`}
                >
                  <img src={scaleIcon} alt="Base" className="w-3.5 h-3.5 object-contain inline-block" />
                  Base
                </button>
                <button
                  onClick={() => toggleScenario("bear")}
                  className={`inline-flex items-center gap-1.5 transition-all cursor-pointer ${visibleScenarios.bear ? "opacity-100 font-bold text-[#C25450]" : "opacity-40"
                    }`}
                >
                  <img src={bearMarketIcon} alt="Bear" className="w-3.5 h-3.5 object-contain inline-block" />
                  Bear
                </button>
              </div>

              {/* View Switcher */}
              <div className="flex bg-[#EBF1F4] p-0.5 rounded-lg border border-[#C8D9E6]">
                <button
                  onClick={() => setView("Graph")}
                  className={`flex items-center gap-1 px-2.5 py-1 text-[11px] font-mono rounded-md transition-colors ${view === "Graph"
                      ? "bg-white text-[#567C8D] font-bold shadow-xs border border-[#AFC5D6]"
                      : "text-[#567C8D] hover:text-[#2F4156]"
                    }`}
                >
                  <LineChartIcon className="w-3.5 h-3.5" />
                  Graph
                </button>
                <button
                  onClick={() => setView("Table")}
                  className={`flex items-center gap-1 px-2.5 py-1 text-[11px] font-mono rounded-md transition-colors ${view === "Table"
                      ? "bg-white text-[#567C8D] font-bold shadow-xs border border-[#AFC5D6]"
                      : "text-[#567C8D] hover:text-[#2F4156]"
                    }`}
                >
                  <TableIcon className="w-3.5 h-3.5" />
                  Table
                </button>
              </div>
            </div>
          </div>

          {view === "Graph" ? (
            <div className="w-full relative" style={{ height: 280 }}>
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={chartData} margin={{ top: 15, right: 20, left: 0, bottom: 5 }}>
                  <defs>
                    {/* Green gradient shadow for Bull */}
                    <linearGradient id="bullGradClean" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#2E7D5B" stopOpacity={0.28} />
                      <stop offset="95%" stopColor="#2E7D5B" stopOpacity={0.01} />
                    </linearGradient>

                    {/* Blue gradient shadow for Base */}
                    <linearGradient id="baseGradClean" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#567C8D" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#567C8D" stopOpacity={0.01} />
                    </linearGradient>

                    {/* Red gradient shadow for Bear */}
                    <linearGradient id="bearGradClean" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#C25450" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#C25450" stopOpacity={0.01} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="2 4" stroke="#C8D9E6" vertical={false} />
                  <ReferenceArea x1="M1" x2="M5" fill="#EBF1F4" fillOpacity={0.75} />
                  <ReferenceLine x="M5" stroke="#AFC5D6" strokeDasharray="3 3" />
                  <XAxis
                    dataKey="month"
                    axisLine={{ stroke: "#C8D9E6" }}
                    tickLine={false}
                    tick={{ fontFamily: "IBM Plex Mono", fontSize: 11, fill: "#567C8D" }}
                  />
                  <YAxis
                    tickFormatter={formatY}
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontFamily: "IBM Plex Mono", fontSize: 11, fill: "#567C8D" }}
                    width={48}
                  />
                  <Tooltip
                    content={({ active, payload, label }: any) => {
                      if (active && payload && payload.length) {
                        const isActual = ["M1", "M2", "M3", "M4", "M5"].includes(label)
                        return (
                          <div
                            className="bg-white/95 border border-[#C8D9E6] rounded-xl p-3.5 shadow-2xl font-mono text-xs space-y-2 min-w-[170px] backdrop-blur-md"
                            style={{
                              boxShadow: "0 12px 30px -4px rgba(47, 65, 86, 0.20), 0 4px 10px -2px rgba(47, 65, 86, 0.10)",
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
                                {isActual ? "Actual" : "Forecast"}
                              </span>
                            </div>
                            <div className="space-y-1.5 pt-0.5">
                              {payload.map((entry: any, index: number) => {
                                const color =
                                  entry.dataKey === "bull"
                                    ? "#2E7D5B"
                                    : entry.dataKey === "base"
                                    ? "#567C8D"
                                    : "#C25450"
                                return (
                                  <div
                                    key={index}
                                    className="flex items-center justify-between gap-3 text-[11.5px]"
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

                  {/* Bear scenario line + red under-shadow */}
                  {visibleScenarios.bear && (
                    <Area
                      type="monotone"
                      dataKey="bear"
                      name="Bear"
                      stroke="#C25450"
                      strokeWidth={2.5}
                      fill="url(#bearGradClean)"
                      dot={false}
                      activeDot={{ r: 4 }}
                      isAnimationActive={true}
                      animationDuration={1300}
                      animationEasing="ease-out"
                    />
                  )}

                  {/* Base scenario line + blue under-shadow */}
                  {visibleScenarios.base && (
                    <Area
                      type="monotone"
                      dataKey="base"
                      name="Base"
                      stroke="#567C8D"
                      strokeWidth={2.8}
                      fill="url(#baseGradClean)"
                      dot={false}
                      activeDot={{ r: 4 }}
                      isAnimationActive={true}
                      animationDuration={1300}
                      animationEasing="ease-out"
                    />
                  )}

                  {/* Bull scenario line + green under-shadow */}
                  {visibleScenarios.bull && (
                    <Area
                      type="monotone"
                      dataKey="bull"
                      name="Bull"
                      stroke="#2E7D5B"
                      strokeWidth={2.5}
                      fill="url(#bullGradClean)"
                      dot={false}
                      activeDot={{ r: 4 }}
                      isAnimationActive={true}
                      animationDuration={1300}
                      animationEasing="ease-out"
                    />
                  )}
                </ComposedChart>
              </ResponsiveContainer>
              <div className="absolute top-3 left-[65px] text-[10px] font-mono text-[#567C8D] pointer-events-none uppercase tracking-wider font-bold">
                known actuals {knownMonths.length ? `(M1-M${knownMonths.length})` : ""}
              </div>
              <div className="absolute top-3 left-[300px] text-[10px] font-mono text-[#567C8D] pointer-events-none uppercase tracking-wider font-bold">
                forecast →
              </div>
            </div>
          ) : (
            <div className="overflow-x-auto py-2">
              <table className="w-full text-[13px] border-collapse">
                <thead>
                  <tr className="border-b border-[#C8D9E6]">
                    <th className="text-left font-mono text-[10.5px] uppercase text-[#567C8D] tracking-[.04em] pb-2.5 font-bold">
                      Month
                    </th>
                    {visibleScenarios.bull && (
                      <th className="text-left font-mono text-[10.5px] uppercase text-[#2E7D5B] tracking-[.04em] pb-2.5 font-bold">
                        Bull Rx
                      </th>
                    )}
                    {visibleScenarios.base && (
                      <th className="text-left font-mono text-[10.5px] uppercase text-[#567C8D] tracking-[.04em] pb-2.5 font-bold">
                        Base Rx
                      </th>
                    )}
                    {visibleScenarios.bear && (
                      <th className="text-left font-mono text-[10.5px] uppercase text-[#C25450] tracking-[.04em] pb-2.5 font-bold">
                        Bear Rx
                      </th>
                    )}
                  </tr>
                </thead>
                <tbody>
                  {chartData.map((row) => (
                    <tr key={row.month} className="border-b border-[#C8D9E6]/60 hover:bg-[#EBF1F4] transition-colors">
                      <td className="py-2.5 font-mono font-bold text-[#2F4156]">{row.month}</td>
                      {visibleScenarios.bull && (
                        <td className="py-2.5 font-mono text-[#2E7D5B] font-bold">
                          <AnimatedCounter end={row.bull} duration={1.2} />
                        </td>
                      )}
                      {visibleScenarios.base && (
                        <td className="py-2.5 font-mono text-[#567C8D] font-semibold">
                          <AnimatedCounter end={row.base} duration={1.2} />
                        </td>
                      )}
                      {visibleScenarios.bear && (
                        <td className="py-2.5 font-mono text-[#C25450] font-semibold">
                          <AnimatedCounter end={row.bear} duration={1.2} />
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Right Panel: Top-5 Analogs */}
        <div className="clean-tile rounded-[16px] p-6.5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="font-mono text-[11px] tracking-[.08em] uppercase text-[#567C8D] font-bold">
                Top-5 Analogs Used
              </span>
            </div>

            <div className="divide-y divide-[#C8D9E6]/60">
              {analogsData.map((a) => (
                <motion.div
                  key={a.id}
                  whileHover={{ x: 4 }}
                  onClick={() => setSelectedAnalog(a)}
                  className="flex justify-between items-center py-3 cursor-pointer group rounded-lg px-2 -mx-2 hover:bg-[#EBF1F4] transition-colors"
                >
                  <div>
                    <div className="font-bold text-[13.5px] text-[#2F4156] group-hover:text-[#567C8D] transition-colors flex items-center gap-1.5">
                      <span>{a.id}</span>
                      <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                    <div className="text-[11.5px] text-[#567C8D] mt-0.5">{a.meta}</div>
                  </div>
                  <span className="font-mono text-[12px] font-bold bg-[#EBF1F4] text-[#567C8D] border border-[#C8D9E6] group-hover:bg-[#567C8D] group-hover:text-white px-2.5 py-1 rounded-[6px] transition-all">
                    {a.sim}
                  </span>
                </motion.div>
              ))}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-[#C8D9E6]/60 text-[11.5px] text-[#7A92A2] italic">
            Click any analog to view curve matching details.
          </div>
        </div>
      </div>

      {/* ---------- SECTION 3: SCENARIO COMPARISON TABLE (Filters by Active Scenarios) ---------- */}
      <div className="clean-tile rounded-[16px] p-6.5">
        <div className="flex items-center justify-between mb-4">
          <span className="font-mono text-[11px] tracking-[.08em] uppercase text-[#567C8D] font-bold">
            Scenario Comparison
          </span>
          <span className="text-[11px] text-[#7A92A2] font-mono">
            Showing {filteredTableData.length} of {tableData.length} Scenarios
          </span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-[13px] border-collapse">
            <thead>
              <tr className="border-b border-[#C8D9E6]">
                <th className="text-left font-mono text-[10.5px] uppercase text-[#567C8D] tracking-[.04em] pb-3 px-3 font-bold">
                  Scenario
                </th>
                <th className="text-left font-mono text-[10.5px] uppercase text-[#567C8D] tracking-[.04em] pb-3 px-3 font-bold">
                  Peak Month
                </th>
                <th className="text-left font-mono text-[10.5px] uppercase text-[#567C8D] tracking-[.04em] pb-3 px-3 font-bold">
                  Peak Rx
                </th>
                <th className="text-left font-mono text-[10.5px] uppercase text-[#567C8D] tracking-[.04em] pb-3 px-3 font-bold">
                  Month-12 Rx
                </th>
                <th className="text-left font-mono text-[10.5px] uppercase text-[#567C8D] tracking-[.04em] pb-3 px-3 font-bold">
                  12mo Cumulative
                </th>
                <th className="text-left font-mono text-[10.5px] uppercase text-[#567C8D] tracking-[.04em] pb-3 px-3 font-bold">
                  Avg MoM Growth
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredTableData.map((row) => (
                <tr key={row.scenario} className="border-b border-[#C8D9E6]/60 last:border-b-0 hover:bg-[#EBF1F4] transition-colors">
                  <td className="py-3 px-3">
                    <span
                      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold border ${row.tagClass === "bull"
                          ? "bg-[#E8F5EE] text-[#2E7D5B] border-[#A3D9BE]"
                          : row.tagClass === "base"
                            ? "bg-[#EBF1F4] text-[#567C8D] border-[#C8D9E6]"
                            : "bg-[#FCEEED] text-[#C25450] border-[#F2B8B6]"
                        }`}
                    >
                      {row.tagClass === "bull" && (
                        <img src={bullMarketIcon} alt="" className="w-3.5 h-3.5 object-contain flex-shrink-0" />
                      )}
                      {row.tagClass === "base" && (
                        <img src={scaleIcon} alt="" className="w-3.5 h-3.5 object-contain flex-shrink-0" />
                      )}
                      {row.tagClass === "bear" && (
                        <img src={bearMarketIcon} alt="" className="w-3.5 h-3.5 object-contain flex-shrink-0" />
                      )}
                      <span>{row.scenario}</span>
                    </span>
                  </td>
                  <td className="py-3 px-3 font-mono font-semibold text-[#2F4156]">
                    Month <AnimatedCounter end={row.peakMonth} duration={1.1} />
                  </td>
                  <td className="py-3 px-3 font-mono font-semibold text-[#2F4156]">
                    <AnimatedCounter end={row.peakRx} duration={1.3} />
                  </td>
                  <td className="py-3 px-3 font-mono font-semibold text-[#2F4156]">
                    <AnimatedCounter end={row.month12Rx} duration={1.3} />
                  </td>
                  <td className="py-3 px-3 font-mono font-semibold text-[#2F4156]">
                    <AnimatedCounter end={row.cumulative} duration={1.4} />
                  </td>
                  <td className="py-3 px-3 font-mono font-semibold text-[#2F4156]">
                    <AnimatedCounter end={row.avgGrowth} decimals={2} duration={1.1} suffix="%" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      

      {/* ---------- SECTION 5: SCENARIO ASSUMPTIONS CONTEXT (Smooth Left-to-Right Teal Fill Hover) ---------- */}
      <div>
        <span className="font-mono text-[11px] tracking-[.08em] uppercase text-[#567C8D] mb-3 block font-bold">
          Scenario Assumptions — Business Context
        </span>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {scenarioContext.map((sc) => (
            <motion.div
              key={sc.key}
              whileHover={{ y: -3 }}
              onMouseEnter={() => setHoveredScenarioCard(sc.key)}
              onMouseLeave={() => setHoveredScenarioCard(null)}
              className="clean-tile-interactive rounded-[16px] p-5.5 relative overflow-hidden cursor-pointer"
            >
              {/* Smooth Left-to-Right Teal Fill Layer */}
              <motion.div
                initial={false}
                animate={{
                  clipPath:
                    hoveredScenarioCard === sc.key
                      ? "inset(0% 0% 0% 0%)"
                      : "inset(0% 100% 0% 0%)",
                }}
                transition={{ duration: 0.42, ease: [0.25, 1, 0.5, 1] }}
                className="absolute inset-0 bg-[#567C8D] p-5.5 z-10 flex flex-col justify-between text-white"
                style={{
                  boxShadow: "inset 0 1px 0 rgba(255, 255, 255, 0.25)",
                }}
              >
                <div>
                  <div className="flex items-center gap-2.5 font-bold text-[15px] text-white mb-3">
                    <img src={getScenarioIcon(sc.key)} alt={sc.title} className="w-5 h-5 object-contain" />
                    <span>{sc.title}</span>
                  </div>
                  <div className="divide-y divide-white/20">
                    {sc.items.map((item) => (
                      <div key={item.label} className="flex justify-between text-[12.5px] py-2 text-[#E2ECF4]">
                        <span>{item.label}</span>
                        <b className="text-white font-bold">{item.value}</b>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="text-[11.5px] text-[#C8D9E6] mt-3 italic">
                  {sc.note}
                </div>
              </motion.div>

              {/* Base Content */}
              <div className="relative z-0 flex flex-col justify-between h-full">
                <div>
                  <div className="flex items-center gap-2.5 font-bold text-[15px] text-[#2F4156] mb-3">
                    <img src={getScenarioIcon(sc.key)} alt={sc.title} className="w-5 h-5 object-contain" />
                    <span>{sc.title}</span>
                  </div>
                  <div className="divide-y divide-[#C8D9E6]/60">
                    {sc.items.map((item) => (
                      <div key={item.label} className="flex justify-between text-[12.5px] py-2 text-[#567C8D]">
                        <span>{item.label}</span>
                        <b className="text-[#2F4156] font-semibold">{item.value}</b>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="text-[11.5px] text-[#7A92A2] mt-3 italic">{sc.note}</div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* ---------- SECTION 4: TRANSPARENCY STRIP ---------- */}
      <div className="clean-tile rounded-[16px] p-6.5 space-y-4">
        <div>
          <span className="font-mono text-[11px] tracking-[.08em] uppercase text-[#567C8D] mb-1.5 block font-bold">
            How This Forecast Was Calculated — Not a Black Box
          </span>
          <div className="text-[13px] text-[#567C8D] max-w-[680px]">
            Combines a blended curve from the selected historical launches with a Bass adoption-curve
            fit to this drug's own early data — weighted by whichever signal fits better.
          </div>
        </div>

        {/* Dark Terminal Formula Block */}
        <div
          className="font-mono text-[14px] text-[#C8D9E6] p-4 rounded-xl flex items-center justify-between flex-wrap gap-3 border border-[#C8D9E6]/20"
          style={{
            backgroundColor: "#1D2A37",
            boxShadow: "0 4px 14px rgba(29, 42, 55, 0.35), inset 0 1px 0 rgba(200, 217, 230, 0.15)",
          }}
        >
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-[#7A92A2]">formula:</span>
            <span className="font-semibold text-white">forecast</span>
            <span>=</span>
            <span className="text-[#A3D9BE] font-semibold">0.50</span>
            <span>× analog_curve +</span>
            <span className="text-[#F2B8B6] font-semibold">0.50</span>
            <span>× bass_curve</span>
          </div>

          <button
            onClick={handleCopyFormula}
            className="flex items-center gap-1.5 bg-[#567C8D] hover:bg-[#436371] text-xs font-mono text-white px-3 py-1.5 rounded-lg border border-white/20 transition-colors cursor-pointer"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-[#A3D9BE]" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? "Copied!" : "Copy Formula"}</span>
          </button>
        </div>

        {/* 5 Parameter Cards with Smooth Left-to-Right Teal Fill on Hover */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
          {formulaParameters.map((param) => (
            <motion.div
              key={param.key}
              whileHover={{ y: -2 }}
              onMouseEnter={() => setHoveredParam(param.key)}
              onMouseLeave={() => setHoveredParam(null)}
              className="text-center p-3.5 bg-[#EBF1F4] rounded-xl border border-[#C8D9E6] shadow-2xs relative overflow-hidden cursor-pointer"
            >
              {/* Smooth Left-to-Right Teal Fill Layer */}
              <motion.div
                initial={false}
                animate={{
                  clipPath:
                    hoveredParam === param.key
                      ? "inset(0% 0% 0% 0%)"
                      : "inset(0% 100% 0% 0%)",
                }}
                transition={{ duration: 0.38, ease: [0.25, 1, 0.5, 1] }}
                className="absolute inset-0 bg-[#567C8D] p-3.5 z-10 flex flex-col justify-center items-center text-white"
                style={{
                  boxShadow: "inset 0 1px 0 rgba(255, 255, 255, 0.25)",
                }}
              >
                <div className="text-[11px] text-[#E2ECF4] mb-1 font-medium truncate w-full">
                  {param.label}
                </div>
                <div className="font-mono font-bold text-[16px] text-white">
                  {param.value}
                </div>
              </motion.div>

              {/* Base Content */}
              <div className="relative z-0">
                <div className="text-[11px] text-[#567C8D] mb-1 font-medium truncate">
                  {param.label}
                </div>
                <div className="font-mono font-bold text-[16px] text-[#2F4156]">
                  {param.value}
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        <div className="flex items-center gap-2 text-[12.5px] text-[#567C8D] pt-1">
          <Layers className="w-4 h-4 text-[#2E7D5B]" />
          <span>✓ Validated across <b className="text-[#2F4156]">{run ? run.selected_analogs.length : 0} historical launches</b> — backend pipeline output</span>
        </div>
      </div>

      {/* ---------- ANALOG DETAILS MODAL ---------- */}
      <AnimatePresence>
        {selectedAnalog && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#2F4156]/60 backdrop-blur-xs">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="rounded-2xl p-6.5 max-w-md w-full shadow-2xl space-y-4 border border-[#C8D9E6] bg-white"
              style={{
                boxShadow: "0 25px 50px -12px rgba(47, 65, 86, 0.40)",
              }}
            >
              <div className="flex justify-between items-start">
                <div>
                  <span className="font-mono text-xs text-[#567C8D] font-bold uppercase tracking-wider bg-[#EBF1F4] border border-[#C8D9E6] px-2 py-0.5 rounded-md">
                    Analog Details
                  </span>
                  <h3 className="font-serif text-2xl font-bold text-[#2F4156] mt-1.5">
                    {selectedAnalog.id}
                  </h3>
                  <p className="text-xs text-[#567C8D]">{selectedAnalog.meta}</p>
                </div>
                <button
                  onClick={() => setSelectedAnalog(null)}
                  className="text-[#7A92A2] hover:text-[#2F4156] p-1.5 rounded-lg hover:bg-[#EBF1F4] cursor-pointer transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="bg-[#FAF7F5] p-4 rounded-xl space-y-2.5 font-mono text-xs border border-[#C8D9E6]">
                <div className="flex justify-between">
                  <span className="text-[#567C8D]">Similarity Score:</span>
                  <span className="font-bold text-[#567C8D]">{selectedAnalog.sim}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#567C8D]">Peak Market Share:</span>
                  <span className="font-bold text-[#2F4156]">{selectedAnalog.peakShare}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#567C8D]">Launch Year:</span>
                  <span className="font-bold text-[#2F4156]">{selectedAnalog.launchYear}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#567C8D]">Curve Model Fit:</span>
                  <span className="font-bold text-[#2E7D5B]">{selectedAnalog.curveType}</span>
                </div>
              </div>

              <p className="text-xs text-[#567C8D] leading-relaxed">
                {selectedAnalog.description}
              </p>

              <div className="pt-2 flex justify-end">
                <button
                  onClick={() => setSelectedAnalog(null)}
                  className="bg-[#2F4156] text-white text-xs font-semibold px-4 py-2 rounded-xl hover:bg-[#1D2A37] border border-[#567C8D]/30 cursor-pointer shadow-xs transition-colors"
                >
                  Close Window
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ---------- FOOTER NOTE ---------- */}
      <div className="text-center text-[11.5px] text-[#7A92A2] font-mono mt-10">
      </div>
    </div>
  )
}
