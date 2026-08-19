import { useState, DragEvent, useRef, useCallback, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { motion, AnimatePresence } from "framer-motion"
import {
  UploadCloud,
  CheckCircle2,
  FileSpreadsheet,
  Play,
  Loader2,
  Check,
  ShieldCheck,
} from "lucide-react"
import logoImg from "../assets/logo.png"
import scaleIcon from "../assets/icons/scale.png"
import { runForecast, saveForecastRun } from "../api"

// ─────────────────────────────────────────────
// Custom Wave Slider Component
// The filled track IS the wave — the line itself
// undulates like water while the thumb is held,
// and flattens smoothly on release.
// ─────────────────────────────────────────────
interface WaveSliderProps {
  min: number
  max: number
  step: number
  value: number
  onChange: (v: number) => void
}

function WaveSlider({ min, max, step, value, onChange }: WaveSliderProps) {
  const [dragging, setDragging] = useState(false)
  // wavePhase scrolls the sine wave forward in time (rAF-driven)
  const [wavePhase, setWavePhase] = useState(0)
  // amplitude smoothly transitions 0 → 3 on drag start, 3 → 0 on release
  const [amplitude, setAmplitude] = useState(0)

  const animFrameRef  = useRef<number | null>(null)
  const ampFrameRef   = useRef<number | null>(null)
  const containerRef  = useRef<HTMLDivElement>(null)
  const [trackWidth, setTrackWidth] = useState(300)

  // Measure actual track pixel width after mount / resize
  useEffect(() => {
    const measure = () => {
      if (containerRef.current) setTrackWidth(containerRef.current.clientWidth)
    }
    measure()
    window.addEventListener("resize", measure)
    return () => window.removeEventListener("resize", measure)
  }, [])

  // Drive wavePhase forward continuously while dragging
  useEffect(() => {
    if (dragging) {
      let last: number | null = null
      const tick = (ts: number) => {
        if (last !== null) {
          // ~1.4 full wavelengths per second
          setWavePhase((p) => (p + (ts - last!) * 0.008) % (2 * Math.PI))
        }
        last = ts
        animFrameRef.current = requestAnimationFrame(tick)
      }
      animFrameRef.current = requestAnimationFrame(tick)
    } else {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current)
    }
    return () => { if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current) }
  }, [dragging])

  // Smoothly ease amplitude toward target (0 when idle, 3 when dragging)
  useEffect(() => {
    const target = dragging ? 3.2 : 0
    let last: number | null = null
    const easeAmp = (ts: number) => {
      if (last !== null) {
        const dt = ts - last
        setAmplitude((a) => {
          const delta = target - a
          if (Math.abs(delta) < 0.01) return target
          return a + delta * Math.min(1, dt * 0.006) // smooth exponential ease
        })
      }
      last = ts
      ampFrameRef.current = requestAnimationFrame(easeAmp)
    }
    ampFrameRef.current = requestAnimationFrame(easeAmp)
    return () => { if (ampFrameRef.current) cancelAnimationFrame(ampFrameRef.current) }
  }, [dragging])

  const pct = ((value - min) / (max - min)) * 100
  // pixel width of the filled (left) portion
  const filledPx = Math.max(0, (pct / 100) * trackWidth)

  // Build SVG path for the wavy filled line.
  // The line runs from x=0 to x=filledPx at y=mid ± amplitude*sin(...)
  const SVG_H = 14       // SVG viewBox height — gives vertical room for the wave
  const MID   = SVG_H / 2
  const STEP  = 1.8      // x step for smoothness
  const WAVELENGTH = 32  // pixels per full wave cycle

  const buildPath = (): string => {
    if (filledPx <= 0) return ""
    const pts: string[] = []
    for (let x = 0; x <= filledPx; x += STEP) {
      const y = MID + amplitude * Math.sin((x / WAVELENGTH) * 2 * Math.PI + wavePhase)
      pts.push(`${x.toFixed(1)},${y.toFixed(2)}`)
    }
    // Ensure we always end exactly at filledPx
    const yEnd = MID + amplitude * Math.sin((filledPx / WAVELENGTH) * 2 * Math.PI + wavePhase)
    pts.push(`${filledPx.toFixed(1)},${yEnd.toFixed(2)}`)
    return "M" + pts.join(" L")
  }

  const handlePointerDown = useCallback((e: React.PointerEvent) => {
    setDragging(true)
    ;(e.target as HTMLElement).setPointerCapture(e.pointerId)
  }, [])
  const handlePointerUp = useCallback(() => setDragging(false), [])

  return (
    <div ref={containerRef} className="relative w-full select-none py-2">
      {/* SVG track — Sky Blue background line + Teal wave filled line */}
      <svg
        width="100%"
        height={SVG_H}
        viewBox={`0 0 ${trackWidth} ${SVG_H}`}
        style={{ display: "block", overflow: "visible" }}
      >
        {/* Sky Blue background track line */}
        <line
          x1={0} y1={MID}
          x2={trackWidth} y2={MID}
          stroke="#C8D9E6"
          strokeWidth={4}
          strokeLinecap="round"
        />

        {/* Teal filled portion — THE line itself is the wave */}
        {filledPx > 0 && (
          <path
            d={buildPath()}
            fill="none"
            stroke="#567C8D"
            strokeWidth={dragging ? 3.5 : 3}
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{ transition: "stroke-width 0.2s ease" }}
          />
        )}

        {/* Thumb circle drawn in SVG for pixel-perfect alignment */}
        <circle
          cx={filledPx}
          cy={MID}
          r={dragging ? 8 : 6.5}
          fill={dragging ? "#567C8D" : "#FFFFFF"}
          stroke="#567C8D"
          strokeWidth={2}
          style={{
            transition: "r 0.18s ease, fill 0.18s ease",
            filter: dragging
              ? "drop-shadow(0 0 5px rgba(86,124,141,0.40))"
              : "drop-shadow(0 1px 3px rgba(47,65,86,0.20))",
          }}
        />
      </svg>

      {/* Invisible native range input for interaction — covers the same area */}
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        onPointerDown={handlePointerDown}
        onPointerUp={handlePointerUp}
        onPointerLeave={handlePointerUp}
        className="absolute inset-0 w-full opacity-0 cursor-pointer"
        style={{ height: "100%", zIndex: 10 }}
      />
    </div>
  )
}

// ─────────────────────────────────────────────
// Smooth Segmented Control Component
// ─────────────────────────────────────────────
interface SegmentedControlProps {
  options: string[]
  value: string
  onChange: (v: string) => void
  id: string
}

function SegmentedControl({ options, value, onChange, id }: SegmentedControlProps) {
  return (
    <div className="flex bg-[#EBF1F4] p-1.5 rounded-xl border border-[#C8D9E6] w-full relative">
      {options.map((o) => (
        <button
          key={o}
          type="button"
          id={`${id}-${o}`}
          onClick={() => onChange(o)}
          className="flex-1 py-2 text-xs font-bold rounded-lg z-10 relative transition-colors duration-200 cursor-pointer"
          style={{
            color: value === o ? "#2F4156" : "#567C8D",
          }}
        >
          {/* Animated pill highlight using layoutId */}
          {value === o && (
            <motion.div
              layoutId={id}
              className="absolute inset-0 bg-white rounded-[8px] shadow-xs border border-[#AFC5D6]"
              transition={{ type: "spring", stiffness: 380, damping: 34 }}
              style={{ zIndex: -1 }}
            />
          )}
          {o}
        </button>
      ))}
    </div>
  )
}

// ─────────────────────────────────────────────
// Main Upload Page
// ─────────────────────────────────────────────
export default function NewForecast() {
  const navigate = useNavigate()
  const [file1, setFile1] = useState<File | null>(null)
  const [file2, setFile2] = useState<File | null>(null)
  const [dragActive1, setDragActive1] = useState(false)
  const [dragActive2, setDragActive2] = useState(false)

  // Model parameters
  const [marketSize, setMarketSize] = useState(0)
  const [adoptionSpeed, setAdoptionSpeed] = useState(1.0)
  const [penetrationCeiling, setPenetrationCeiling] = useState(1.0)
  const [competitiveEntry, setCompetitiveEntry] = useState(false)
  const [payerTrend, setPayerTrend] = useState("Stable")
  const [promoTrend, setPromoTrend] = useState("Steady")

  // Multi-stage submission state
  const [isProcessing, setIsProcessing] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)

  const steps = [
    "Parsing Data Source & Historic Series...",
    "Aligning Top-5 Analog Curves...",
    "Calibrating Bass Model Parameters (p, q, m)...",
    "Generating Multi-Scenario Forecasts (Bull, Base, Bear)...",
  ]

  const handleDragOver = (e: DragEvent<HTMLDivElement>, step: 1 | 2) => {
    e.preventDefault()
    e.stopPropagation()
    if (step === 1) setDragActive1(true)
    if (step === 2) setDragActive2(true)
  }

  const handleDragLeave = (e: DragEvent<HTMLDivElement>, step: 1 | 2) => {
    e.preventDefault()
    e.stopPropagation()
    if (step === 1) setDragActive1(false)
    if (step === 2) setDragActive2(false)
  }

  const handleDrop = (e: DragEvent<HTMLDivElement>, step: 1 | 2) => {
    e.preventDefault()
    e.stopPropagation()
    if (step === 1) {
      setDragActive1(false)
      setFile1(e.dataTransfer.files?.[0] || null)
    }
    if (step === 2) {
      setDragActive2(false)
      setFile2(e.dataTransfer.files?.[0] || null)
    }
  }

  const buildAssumptions = () => {
    const payerFactor = payerTrend === "Improving" ? 1.1 : payerTrend === "Worsening" ? 0.9 : 1
    const promoFactor = promoTrend === "Ramping" ? 1.15 : promoTrend === "Cutting" ? 0.85 : 1
    const competitionFactor = competitiveEntry ? 0.9 : 1
    const baseMarket = 1 + marketSize / 100
    const basePenetration = Math.min(0.95, 0.25 * penetrationCeiling)

    return {
      bull: {
        market_size_multiplier: baseMarket * 1.15,
        peak_penetration: Math.min(0.99, basePenetration * 1.15),
        adoption_speed_multiplier: adoptionSpeed * 1.1,
        competition_factor: competitionFactor,
        payer_access_factor: payerFactor * 1.05,
        promotion_factor: promoFactor * 1.05,
      },
      base: {
        market_size_multiplier: baseMarket,
        peak_penetration: basePenetration,
        adoption_speed_multiplier: adoptionSpeed,
        competition_factor: competitionFactor,
        payer_access_factor: payerFactor,
        promotion_factor: promoFactor,
      },
      bear: {
        market_size_multiplier: baseMarket * 0.85,
        peak_penetration: basePenetration * 0.85,
        adoption_speed_multiplier: adoptionSpeed * 0.9,
        competition_factor: competitionFactor * 0.9,
        payer_access_factor: payerFactor * 0.95,
        promotion_factor: promoFactor * 0.95,
      },
    }
  }

  const handleGenerate = async () => {
    if (!file1 || !file2) return
    setIsProcessing(true)
    setCurrentStep(0)
    try {
      const run = await runForecast(file1, file2, buildAssumptions())
      saveForecastRun(run)
      setCurrentStep(steps.length - 1)
      navigate("/dashboard")
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "The forecast could not be generated.")
      setIsProcessing(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-8 pb-20 text-[#2F4156]">
      <div>
        <div className="w-14 h-14 sm:w-16 sm:h-16 mb-3 flex items-center justify-center">
          <img src={logoImg} alt="Baseline Logo" className="w-full h-full object-contain" />
        </div>
        <h1 className="font-serif text-[30px] sm:text-[36px] font-bold text-[#2F4156]">
          New Forecast Setup
        </h1>
        <p className="text-[13px] text-[#567C8D] mt-1">
          Upload primary launch history, configure comparative analog datasets, and adjust Bass model parameters.
        </p>
      </div>

      <div className="space-y-6">
        {/* Step 1: Primary Data Source */}
        <div className="clean-tile rounded-[18px] p-6.5">
          <div className="flex items-center justify-between mb-2">
            <h2 className="font-serif text-[19px] font-bold text-[#2F4156] flex items-center gap-2.5">
              <span className="w-6.5 h-6.5 rounded-full bg-[#567C8D] text-white text-xs font-mono flex items-center justify-center font-bold">
                1
              </span>
              Primary Data Source
            </h2>
            {file1 && (
              <span className="font-mono text-xs text-[#2E7D5B] flex items-center gap-1 font-bold">
                <Check className="w-3.5 h-3.5" /> Parsed 5 Months
              </span>
            )}
          </div>
          <p className="text-[12px] text-[#567C8D] mb-4">
            Upload actual Rx history or monthly launch series (.json)
          </p>

          <div
            onDragOver={(e) => handleDragOver(e, 1)}
            onDragLeave={(e) => handleDragLeave(e, 1)}
            onDrop={(e) => handleDrop(e, 1)}
            className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center transition-all cursor-pointer ${
              dragActive1
                ? "border-[#567C8D] bg-[#EBF1F4]"
                : "border-[#AFC5D6] bg-[#FAF7F5] hover:bg-[#EBF1F4] hover:border-[#567C8D]"
            }`}
          >
            <input
              type="file"
              id="file1-input"
              className="hidden"
              onChange={(e) => setFile1(e.target.files?.[0] || null)}
            />
            <label htmlFor="file1-input" className="flex flex-col items-center cursor-pointer">
              {file1 ? (
                <div className="flex items-center gap-3 text-[#2E7D5B] font-bold text-sm bg-[#E8F5EE] border border-[#A3D9BE] px-4 py-2.5 rounded-xl shadow-2xs">
                  <FileSpreadsheet className="w-5 h-5 text-[#2E7D5B]" />
                  <span>{file1.name}</span>
                  <CheckCircle2 className="w-4 h-4 ml-2 text-[#2E7D5B]" />
                </div>
              ) : (
                <>
                  <UploadCloud className="text-[#567C8D] w-10 h-10 mb-2" />
                  <span className="text-sm text-[#2F4156] font-bold">
                    Click or drag primary data file to upload
                  </span>
                  <span className="text-xs text-[#7A92A2] mt-1 font-medium">
                    Supports JSON up to 25MB
                  </span>
                </>
              )}
            </label>
          </div>
        </div>

        {/* Step 2: Analog Dataset */}
        <div className="clean-tile rounded-[18px] p-6.5">
          <div className="flex items-center justify-between mb-2">
            <h2 className="font-serif text-[19px] font-bold text-[#2F4156] flex items-center gap-2.5">
              <span className="w-6.5 h-6.5 rounded-full bg-[#567C8D] text-white text-xs font-mono flex items-center justify-center font-bold">
                2
              </span>
              Analog Benchmark Data
            </h2>
            {file2 && (
              <span className="font-mono text-xs text-[#2E7D5B] flex items-center gap-1 font-bold">
                <Check className="w-3.5 h-3.5" /> 35 Analogs Active
              </span>
            )}
          </div>
          <p className="text-[12px] text-[#567C8D] mb-4">
            Comparable past product launch curves for similarity indexing
          </p>

          <div
            onDragOver={(e) => handleDragOver(e, 2)}
            onDragLeave={(e) => handleDragLeave(e, 2)}
            onDrop={(e) => handleDrop(e, 2)}
            className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center transition-all cursor-pointer ${
              dragActive2
                ? "border-[#567C8D] bg-[#EBF1F4]"
                : "border-[#AFC5D6] bg-[#FAF7F5] hover:bg-[#EBF1F4] hover:border-[#567C8D]"
            }`}
          >
            <input
              type="file"
              id="file2-input"
              className="hidden"
              onChange={(e) => setFile2(e.target.files?.[0] || null)}
            />
            <label htmlFor="file2-input" className="flex flex-col items-center cursor-pointer">
              {file2 ? (
                <div className="flex items-center gap-3 text-[#2E7D5B] font-bold text-sm bg-[#E8F5EE] border border-[#A3D9BE] px-4 py-2.5 rounded-xl shadow-2xs">
                  <FileSpreadsheet className="w-5 h-5 text-[#2E7D5B]" />
                  <span>{file2.name}</span>
                  <CheckCircle2 className="w-4 h-4 ml-2 text-[#2E7D5B]" />
                </div>
              ) : (
                <>
                  <UploadCloud className="text-[#567C8D] w-10 h-10 mb-2" />
                  <span className="text-sm text-[#2F4156] font-bold">
                    Click or drag analog benchmark dataset
                  </span>
                  <span className="text-xs text-[#7A92A2] mt-1 font-medium">
                    Supports JSON up to 25MB
                  </span>
                </>
              )}
            </label>
          </div>
        </div>

        {/* Step 3: Model Assumptions */}
        <div className="clean-tile rounded-[18px] p-6.5 space-y-6">
          <div className="flex items-center gap-2 border-b border-[#C8D9E6] pb-4">
            <img src={scaleIcon} alt="Model Assumptions" className="w-5 h-5 object-contain" />
            <h2 className="font-serif text-[19px] font-bold text-[#2F4156]">
              Step 3: Model Assumptions &amp; Parameters
            </h2>
          </div>

          {/* Market Size Slider */}
          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="text-[13.5px] text-[#2F4156] font-bold">
                Market Size Adjustment (%)
              </label>
              <motion.span
                key={marketSize}
                initial={{ scale: 0.85, opacity: 0.6 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ type: "spring", stiffness: 400, damping: 20 }}
                className="text-[13px] text-[#567C8D] font-mono font-bold bg-[#EBF1F4] border border-[#C8D9E6] px-2 py-0.5 rounded min-w-[52px] text-center"
              >
                {marketSize > 0 ? `+${marketSize}%` : `${marketSize}%`}
              </motion.span>
            </div>
            <p className="text-[12px] text-[#567C8D] mb-3">
              Adjust total addressable market base estimate
            </p>
            <WaveSlider
              min={-30}
              max={30}
              step={1}
              value={marketSize}
              onChange={setMarketSize}
            />
          </div>

          {/* Adoption Speed Slider */}
          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="text-[13.5px] text-[#2F4156] font-bold">
                Adoption Speed Multiplier
              </label>
              <motion.span
                key={adoptionSpeed}
                initial={{ scale: 0.85, opacity: 0.6 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ type: "spring", stiffness: 400, damping: 20 }}
                className="text-[13px] text-[#567C8D] font-mono font-bold bg-[#EBF1F4] border border-[#C8D9E6] px-2 py-0.5 rounded min-w-[52px] text-center"
              >
                {adoptionSpeed.toFixed(2)}x
              </motion.span>
            </div>
            <p className="text-[12px] text-[#567C8D] mb-3">
              Slower (0.85x) ← → Faster (1.15x)
            </p>
            <WaveSlider
              min={0.85}
              max={1.15}
              step={0.01}
              value={adoptionSpeed}
              onChange={setAdoptionSpeed}
            />
          </div>

          {/* Penetration Ceiling Slider */}
          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="text-[13.5px] text-[#2F4156] font-bold">
                Peak Penetration Ceiling
              </label>
              <motion.span
                key={penetrationCeiling}
                initial={{ scale: 0.85, opacity: 0.6 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ type: "spring", stiffness: 400, damping: 20 }}
                className="text-[13px] text-[#567C8D] font-mono font-bold bg-[#EBF1F4] border border-[#C8D9E6] px-2 py-0.5 rounded min-w-[52px] text-center"
              >
                {penetrationCeiling.toFixed(2)}x
              </motion.span>
            </div>
            <p className="text-[12px] text-[#567C8D] mb-3">
              Lower ceiling ← → Higher ceiling
            </p>
            <WaveSlider
              min={0.85}
              max={1.20}
              step={0.01}
              value={penetrationCeiling}
              onChange={setPenetrationCeiling}
            />
          </div>

          {/* Competitive Entry Flag Toggle */}
          <div className="flex items-center justify-between pt-3 border-t border-[#C8D9E6]">
            <div>
              <label className="text-[13.5px] text-[#2F4156] font-bold block">
                Competitive Entry Flag
              </label>
              <span className="text-[12px] text-[#567C8D]">
                Account for anticipated biosimilar/generic entrants
              </span>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={competitiveEntry}
                onChange={(e) => setCompetitiveEntry(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-[#C8D9E6] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#567C8D] border border-[#AFC5D6]" />
            </label>
          </div>

          {/* Payer Access Segmented Control */}
          <div className="pt-2">
            <label className="text-[13.5px] text-[#2F4156] font-bold block mb-1">
              Payer Access Trend
            </label>
            <p className="text-[12px] text-[#567C8D] mb-3">
              Formulary status &amp; prior authorization tiering
            </p>
            <SegmentedControl
              id="payer-trend"
              options={["Worsening", "Stable", "Improving"]}
              value={payerTrend}
              onChange={setPayerTrend}
            />
          </div>

          {/* Promotional Spend Segmented Control */}
          <div className="pt-2">
            <label className="text-[13.5px] text-[#2F4156] font-bold block mb-1">
              Promotional Spend Trend
            </label>
            <p className="text-[12px] text-[#567C8D] mb-3">
              Sales force scaling &amp; marketing push
            </p>
            <SegmentedControl
              id="promo-trend"
              options={["Cutting", "Steady", "Ramping"]}
              value={promoTrend}
              onChange={setPromoTrend}
            />
          </div>

          {/* Submit Action Button */}
          <div className="pt-4">
            <button
              onClick={handleGenerate}
              disabled={!file1 || !file2 || isProcessing}
              className="w-full bg-[#2F4156] hover:bg-[#1D2A37] active:scale-[0.99] text-white font-sans text-sm font-bold py-3.5 rounded-xl transition-all shadow-md flex items-center justify-center gap-2 cursor-pointer border border-[#567C8D]/40"
            >
              <Play className="w-4 h-4 fill-white" />
              <span>Generate Forecast Model</span>
            </button>
          </div>
        </div>
      </div>

      {/* Processing Pipeline Modal */}
      <AnimatePresence>
        {isProcessing && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#2F4156]/60 backdrop-blur-xs">
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="rounded-2xl p-8 max-w-md w-full shadow-2xl space-y-6 text-center border border-[#C8D9E6] bg-white"
              style={{
                boxShadow: "0 25px 50px -12px rgba(47, 65, 86, 0.40)",
              }}
            >
              <div className="w-16 h-16 rounded-full bg-[#2F4156] text-white flex items-center justify-center mx-auto shadow-sm border border-[#C8D9E6]/30">
                <Loader2 className="w-8 h-8 animate-spin text-[#C8D9E6]" />
              </div>

              <div>
                <h3 className="font-serif text-2xl font-bold text-[#2F4156]">
                  Processing Forecast Model
                </h3>
                <p className="text-xs text-[#567C8D] mt-1 font-mono">
                  Synthesizing Bass curves and historical launch analogs...
                </p>
              </div>

              <div className="space-y-3 text-left bg-[#FAF7F5] p-4.5 rounded-xl border border-[#C8D9E6] font-mono text-xs">
                {steps.map((stepText, idx) => (
                  <div key={stepText} className="flex items-center gap-3">
                    {idx < currentStep ? (
                      <CheckCircle2 className="w-4 h-4 text-[#2E7D5B] flex-shrink-0" />
                    ) : idx === currentStep ? (
                      <Loader2 className="w-4 h-4 text-[#567C8D] animate-spin flex-shrink-0" />
                    ) : (
                      <div className="w-4 h-4 rounded-full border border-[#AFC5D6] flex-shrink-0" />
                    )}
                    <span
                      className={
                        idx <= currentStep
                          ? "text-[#2F4156] font-bold"
                          : "text-[#7A92A2]"
                      }
                    >
                      {stepText}
                    </span>
                  </div>
                ))}
              </div>

              <div className="flex items-center justify-center gap-1.5 text-[11px] text-[#567C8D] font-mono">
                <ShieldCheck className="w-3.5 h-3.5 text-[#2E7D5B]" />
                <span>Deterministic LOO-CV Engine</span>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  )
}
