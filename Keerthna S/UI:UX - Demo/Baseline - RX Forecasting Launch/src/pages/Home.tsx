import { useState } from "react"
import { Plus } from "lucide-react"
import {
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  ReferenceArea,
  ReferenceLine,
} from "recharts"
import { useNavigate } from "react-router-dom"

import bullImg from "../imports/Screenshot_2026-08-17_at_2.23.27_PM-removebg-preview.png"
import bearImg from "../imports/Screenshot_2026-08-17_at_2.23.52_PM-removebg-preview.png"
import baseImg from "../imports/Screenshot_2026-08-17_at_12.47.32_PM-removebg-preview.png"

// ── palette ──────────────────────────────────────────────────────────────────
const P = {
  beige: "#F5EFEB",
  navy: "#2F4156",
  teal: "#567C8D",
  sky: "#C8D9E6",
  white: "#FFFFFF",
  darkTeal: "#2B6777",
}

type Scenario = "bull" | "base" | "bear"

const LINE_COLOR: Record<Scenario, string> = {
  bull: "#2E8B57",
  base: "#3b82f6",
  bear: "#B0413E",
}
const SOFT: Record<Scenario, string> = {
  bull: "#E8F5EE",
  base: "#EFF6FF",
  bear: "#FBEAE9",
}

const chartData = [
  { month: "M1", bear: 98, base: 98, bull: 98 },
  { month: "M2", bear: 210, base: 210, bull: 210 },
  { month: "M3", bear: 420, base: 420, bull: 420 },
  { month: "M4", bear: 680, base: 680, bull: 680 },
  { month: "M5", bear: 880, base: 880, bull: 880 },
  { month: "M6", bear: 720, base: 920, bull: 1100 },
  { month: "M7", bear: 810, base: 1100, bull: 1380 },
  { month: "M8", bear: 870, base: 980, bull: 1220 },
  { month: "M9", bear: 840, base: 940, bull: 1290 },
  { month: "M10", bear: 855, base: 934, bull: 1320 },
  { month: "M11", bear: 862, base: 933, bull: 1340 },
  { month: "M12", bear: 870, base: 933, bull: 1353 },
]

const tableData = [
  {
    scenario: "Bull" as Scenario,
    peakMonth: 12,
    peakRx: "1,353,266",
    month12Rx: "1,353,266",
    cumulative: "12,507,866",
    avgGrowth: "2.89%",
  },
  {
    scenario: "Base" as Scenario,
    peakMonth: 8,
    peakRx: "980,741",
    month12Rx: "932,967",
    cumulative: "10,978,279",
    avgGrowth: "3.41%",
  },
  {
    scenario: "Bear" as Scenario,
    peakMonth: 5,
    peakRx: "988,627",
    month12Rx: "870,442",
    cumulative: "9,530,110",
    avgGrowth: "2.10%",
  },
]

const analogs = [
  { id: "ANL_014", meta: "GLP-1 agonist · Oral", sim: "0.91" },
  { id: "ANL_028", meta: "GLP-1 agonist · Injectable", sim: "0.87" },
  { id: "ANL_016", meta: "SGLT2 inhibitor · Oral", sim: "0.82" },
  { id: "ANL_022", meta: "GLP-1 agonist · Oral", sim: "0.79" },
  { id: "ANL_030", meta: "JAK inhibitor · Oral", sim: "0.74" },
]

const scenarioContext: Record<Scenario, {
  items: { label: string value: string }[]
  note: string
}> = {
  bull: {
    items: [
      { label: "Competitive entry", value: "Low" },
      { label: "Payer access", value: "Improving" },
      { label: "Promo spend", value: "Increasing" },
    ],
    note: "Market +15%, adoption speed ×1.10",
  },
  base: {
    items: [
      { label: "Competitive entry", value: "Moderate" },
      { label: "Payer access", value: "Stable" },
      { label: "Promo spend", value: "Stable" },
    ],
    note: "Fitted values, no adjustment",
  },
  bear: {
    items: [
      { label: "Competitive entry", value: "High" },
      { label: "Payer access", value: "Tightening" },
      { label: "Promo spend", value: "Decreasing" },
    ],
    note: "Market −15%, adoption speed ×0.90",
  },
}

const SCENARIOS: { key: Scenario img: string label: string }[] = [
  { key: "bull", img: bullImg, label: "Bull" },
  { key: "base", img: baseImg, label: "Base" },
  { key: "bear", img: bearImg, label: "Bear" },
]

function formatY(v: number) {
  return v >= 1000 ? `${(v / 1000).toFixed(0)}k` : `${v}`
}

export default function Home() {
  const [view, setView] = useState<"Graph" | "Table">("Graph")
  // multi-select set — at least one always active
  const [selected, setSelected] = useState<Set<Scenario>>(new Set(["base"]))
  const navigate = useNavigate()

  const toggle = (s: Scenario) => {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(s)) {
        if (next.size > 1) next.delete(s)
      } else {
        next.add(s)
      }
      return next
    })
  }

  // for assumptions card: show last clicked / first selected
  const contextKey = (["bull", "base", "bear"] as Scenario[]).find((s) =>
    selected.has(s),
  )!

  return (
    <div
      className="space-y-6"
      style={{
        background: P.beige,
        minHeight: "100%",
        borderRadius: "16px",
        padding: "24px",
      }}
    >
      {/* ── HEADER ── */}
      <div
        className="flex flex-wrap gap-4 justify-between items-end pb-5"
        style={{ borderBottom: `1px solid ${P.sky}` }}
      >
        <div>
          <h1
            className="font-serif text-[28px] sm:text-[32px] font-medium tracking-tight"
            style={{ color: P.navy }}
          >
            DrugX — Launch Forecast
          </h1>
          <div
            className="mt-1.5 flex flex-wrap gap-4 text-[13px]"
            style={{ color: P.teal }}
          >
            <span>
              Model:{" "}
              <b style={{ color: P.navy }} className="font-semibold">
                Analog + Bass (Static)
              </b>
            </span>
            <span>
              Known months:{" "}
              <b style={{ color: P.navy }} className="font-semibold">
                5
              </b>
            </span>
          </div>
        </div>
        <button
          onClick={() => navigate("/upload")}
          className="flex items-center gap-2 text-sm font-medium rounded-[6px] px-4 py-2 transition-colors shadow-sm"
          style={{ background: P.navy, color: P.white }}
        >
          <Plus className="w-4 h-4" />
          New Forecast
        </button>
      </div>

      {/* ── STATS ── */}
      <div>
        <span
          className="font-mono text-[11px] tracking-[.08em] uppercase mb-2.5 block"
          style={{ color: P.teal }}
        >
          Stats
        </span>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Peak Month */}
          <div
            className="rounded-[10px] p-5"
            style={{ background: P.white, border: `1px solid ${P.sky}` }}
          >
            <div className="text-[12.5px] mb-2" style={{ color: P.teal }}>
              Peak Month
            </div>
            <div
              className="font-mono font-semibold text-[26px]"
              style={{ color: P.navy }}
            >
              Month 8
            </div>
            <div className="text-[11.5px] mt-1" style={{ color: P.teal }}>
              Base scenario
            </div>
          </div>
          {/* Peak Rx */}
          <div
            className="rounded-[10px] p-5"
            style={{ background: P.white, border: `1px solid ${P.sky}` }}
          >
            <div className="text-[12.5px] mb-2" style={{ color: P.teal }}>
              Peak Rx
            </div>
            <div
              className="font-mono font-semibold text-[26px]"
              style={{ color: P.navy }}
            >
              980,741
            </div>
            <div className="text-[11.5px] mt-1" style={{ color: P.teal }}>
              at peak month, Base
            </div>
          </div>
          {/* 12-Month Cumulative */}
          <div
            className="rounded-[10px] p-5"
            style={{ background: P.white, border: `1px solid ${P.sky}` }}
          >
            <div className="text-[12.5px] mb-2" style={{ color: P.teal }}>
              12-Month Cumulative Rx
            </div>
            <div
              className="font-mono font-semibold text-[26px]"
              style={{ color: P.navy }}
            >
              10.98M
            </div>
            <div className="text-[11.5px] mt-1" style={{ color: P.teal }}>
              Base scenario total
            </div>
          </div>
          {/* Spread card */}
          <div
            className="rounded-[10px] p-5 flex flex-col justify-center"
            style={{
              background: `linear-gradient(135deg, ${P.darkTeal} 0%, #204f5b 100%)`,
            }}
          >
            <div
              className="text-[12px] mb-3 leading-snug"
              style={{ color: "#cfe3e6" }}
            >
              Scenario Spread vs. Base
              <br />
              (Month 12)
            </div>
            <div className="flex flex-col gap-2 font-mono text-[13px]">
              <span
                className="flex items-center gap-1.5"
                style={{ color: "#8fe0b4" }}
              >
                <span className="text-[17px] leading-none flex-shrink-0">
                  ▲
                </span>
                <span>Bull +18.7%</span>
              </span>
              <span
                className="flex items-center gap-1.5"
                style={{ color: "#f2a6a1" }}
              >
                <span className="text-[17px] leading-none flex-shrink-0">
                  ▼
                </span>
                <span>Bear −13.2%</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* ── MAIN GRID ── */}
      <div className="grid grid-cols-1 lg:grid-cols-[1.7fr_1fr] gap-5">
        {/* Left — chart / table */}
        <div
          className="rounded-[10px] p-5"
          style={{ background: P.white, border: `1px solid ${P.sky}` }}
        >
          <div className="flex justify-between items-center mb-5">
            <h2
              className="font-serif text-[18px] font-medium"
              style={{ color: P.navy }}
            >
              12-Month Forecast
            </h2>
            <button
              onClick={() =>
                setView((v) => (v === "Graph" ? "Table" : "Graph"))
              }
              className="text-xs font-medium px-3 py-1.5 rounded-[6px] transition-colors"
              style={{
                border: `1px solid ${P.sky}`,
                background: P.beige,
                color: P.navy,
              }}
            >
              View: {view === "Graph" ? "Table" : "Graph"}
            </button>
          </div>

          {view === "Graph" ? (
            <>
              {/* Multi-select scenario buttons */}
              <div className="flex flex-wrap gap-3 mb-5 items-center">
                {SCENARIOS.map(({ key, img, label }) => {
                  const isOn = selected.has(key)
                  return (
                    <button
                      key={key}
                      onClick={() => toggle(key)}
                      className="flex flex-col items-center gap-1 px-3 py-2 rounded-[8px] border-2 transition-all"
                      style={
                        isOn
                          ? {
                              borderColor: LINE_COLOR[key],
                              background: SOFT[key],
                              transform: "scale(1.05)",
                              boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                            }
                          : { borderColor: P.sky, opacity: 0.45 }
                      }
                    >
                      <img
                        src={img}
                        alt={label}
                        className="w-10 h-10 object-contain"
                      />
                      <span
                        className="text-[10px] font-semibold uppercase tracking-wider"
                        style={{ color: LINE_COLOR[key] }}
                      >
                        {label}
                      </span>
                    </button>
                  )
                })}
                {/* Legend */}
                <div
                  className="ml-auto flex flex-wrap items-center gap-3 text-[12px]"
                  style={{ color: P.teal }}
                >
                  {(["bull", "base", "bear"] as Scenario[])
                    .filter((s) => selected.has(s))
                    .map((s) => (
                      <span key={s} className="flex items-center gap-1.5">
                        <span
                          className="inline-block w-3 h-[2.5px] rounded"
                          style={{ background: LINE_COLOR[s] }}
                        />
                        <span className="capitalize">{s}</span>
                      </span>
                    ))}
                  <span
                    className="flex items-center gap-1.5 pl-3"
                    style={{ borderLeft: `1px solid ${P.sky}` }}
                  >
                    <span
                      className="inline-block w-3 h-0.5 rounded"
                      style={{ background: P.sky }}
                    />
                    known
                  </span>
                </div>
              </div>

              {/* known / forecast labels above chart */}
              <div
                className="flex text-[10px] font-mono mb-1 px-1"
                style={{ color: P.teal }}
              >
                <span style={{ width: "42%" }}>known</span>
                <span>forecast →</span>
              </div>

              {/* Chart */}
              <div style={{ width: "100%", height: 260 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart
                    data={chartData}
                    margin={{ top: 10, right: 20, left: 0, bottom: 10 }}
                  >
                    <defs>
                      {(["bull", "base", "bear"] as Scenario[]).map((s) => (
                        <linearGradient
                          key={s}
                          id={`grad-${s}`}
                          x1="0"
                          y1="0"
                          x2="0"
                          y2="1"
                        >
                          <stop
                            offset="5%"
                            stopColor={LINE_COLOR[s]}
                            stopOpacity={0.18}
                          />
                          <stop
                            offset="95%"
                            stopColor={LINE_COLOR[s]}
                            stopOpacity={0.01}
                          />
                        </linearGradient>
                      ))}
                    </defs>
                    <CartesianGrid
                      strokeDasharray="3 3"
                      vertical={false}
                      stroke="#E8EDF2"
                    />
                    <ReferenceArea
                      x1="M1"
                      x2="M5"
                      fill={P.beige}
                      fillOpacity={0.8}
                    />
                    <ReferenceLine
                      x="M5"
                      stroke={P.sky}
                      strokeDasharray="4 3"
                    />
                    <XAxis
                      dataKey="month"
                      axisLine={{ stroke: P.sky }}
                      tickLine={false}
                      tick={{
                        fontFamily: '"IBM Plex Mono", monospace',
                        fontSize: 11,
                        fill: P.teal,
                      }}
                    />
                    <YAxis
                      tickFormatter={formatY}
                      axisLine={false}
                      tickLine={false}
                      tick={{
                        fontFamily: '"IBM Plex Mono", monospace',
                        fontSize: 11,
                        fill: P.teal,
                      }}
                      width={40}
                    />
                    <Tooltip
                      isAnimationActive={false}
                      contentStyle={{
                        fontFamily: '"IBM Plex Sans", sans-serif',
                        fontSize: "12px",
                        borderRadius: "6px",
                        border: `1px solid ${P.sky}`,
                        background: P.white,
                        color: P.navy,
                      }}
                    />
                    {(["bull", "base", "bear"] as Scenario[]).map((s) =>
                      selected.has(s) ? (
                        <Area
                          key={s}
                          type="monotone"
                          dataKey={s}
                          name={s.charAt(0).toUpperCase() + s.slice(1)}
                          stroke={LINE_COLOR[s]}
                          strokeWidth={2.5}
                          fill={`url(#grad-${s})`}
                          dot={false}
                          isAnimationActive={false}
                        />
                      ) : (
                        <Line
                          key={s}
                          type="monotone"
                          dataKey={s}
                          name={s.charAt(0).toUpperCase() + s.slice(1)}
                          stroke={LINE_COLOR[s]}
                          strokeWidth={1}
                          strokeOpacity={0.2}
                          dot={false}
                          isAnimationActive={false}
                        />
                      ),
                    )}
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            </>
          ) : (
            <div className="overflow-x-auto">
              <span
                className="font-mono text-[11px] tracking-[.08em] uppercase mb-3 block"
                style={{ color: P.teal }}
              >
                Scenario Comparison
              </span>
              <table className="w-full text-[13px] border-collapse">
                <thead>
                  <tr>
                    {[
                      "Scenario",
                      "Peak Month",
                      "Peak Rx",
                      "Month-12 Rx",
                      "12mo Cumulative",
                      "Avg MoM Growth",
                    ].map((h) => (
                      <th
                        key={h}
                        className="text-left font-mono text-[10.5px] uppercase tracking-[.04em] font-medium pb-3 pr-4"
                        style={{
                          color: P.teal,
                          borderBottom: `1px solid ${P.sky}`,
                        }}
                      >
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {tableData.map((row) => {
                    const s = row.scenario.toLowerCase() as Scenario
                    return (
                      <tr
                        key={row.scenario}
                        style={{ borderBottom: `1px solid ${P.sky}` }}
                      >
                        <td className="py-2.5 pr-4">
                          <span
                            className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold"
                            style={{
                              background: SOFT[s],
                              color: LINE_COLOR[s],
                            }}
                          >
                            {row.scenario}
                          </span>
                        </td>
                        <td
                          className="font-mono py-2.5 pr-4"
                          style={{ color: P.navy }}
                        >
                          {row.peakMonth}
                        </td>
                        <td
                          className="font-mono py-2.5 pr-4"
                          style={{ color: P.navy }}
                        >
                          {row.peakRx}
                        </td>
                        <td
                          className="font-mono py-2.5 pr-4"
                          style={{ color: P.navy }}
                        >
                          {row.month12Rx}
                        </td>
                        <td
                          className="font-mono py-2.5 pr-4"
                          style={{ color: P.navy }}
                        >
                          {row.cumulative}
                        </td>
                        <td
                          className="font-mono py-2.5"
                          style={{ color: P.navy }}
                        >
                          {row.avgGrowth}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Right — Top-5 Analogs */}
        <div
          className="rounded-[10px] p-5"
          style={{ background: P.white, border: `1px solid ${P.sky}` }}
        >
          <span
            className="font-mono text-[11px] tracking-[.08em] uppercase mb-4 block"
            style={{ color: P.teal }}
          >
            Top-5 Analogs Used
          </span>
          <div>
            {analogs.map((a, i) => (
              <div
                key={a.id}
                className="flex items-center justify-between py-3"
                style={{
                  borderBottom:
                    i < analogs.length - 1 ? `1px solid ${P.sky}` : "none",
                }}
              >
                <div>
                  <div
                    className="font-semibold text-[13px]"
                    style={{ color: P.navy }}
                  >
                    {a.id}
                  </div>
                  <div
                    className="text-[11.5px] mt-0.5"
                    style={{ color: P.teal }}
                  >
                    {a.meta}
                  </div>
                </div>
                <span
                  className="font-mono text-[12px] font-semibold px-2.5 py-1 rounded-[5px]"
                  style={{ background: P.sky, color: P.darkTeal }}
                >
                  {a.sim}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── SCENARIO ASSUMPTIONS ── */}
      {view === "Graph" && (
        <div
          className="rounded-[10px] p-5"
          style={{ background: P.white, border: `1px solid ${P.sky}` }}
        >
          <span
            className="font-mono text-[11px] tracking-[.08em] uppercase mb-4 block"
            style={{ color: P.teal }}
          >
            Scenario Assumptions — Business Context
          </span>
          <div className="flex items-center gap-2 mb-4">
            {(["bull", "base", "bear"] as Scenario[])
              .filter((s) => selected.has(s))
              .map((s) => (
                <span
                  key={s}
                  className="flex items-center gap-1.5 text-[13px] font-semibold capitalize px-2 py-0.5 rounded-full"
                  style={{ background: SOFT[s], color: LINE_COLOR[s] }}
                >
                  <span
                    className="w-2 h-2 rounded-full inline-block"
                    style={{ background: LINE_COLOR[s] }}
                  />
                  {s}
                </span>
              ))}
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            {(["bull", "base", "bear"] as Scenario[])
              .filter((s) => selected.has(s))
              .map((s) => {
                const ctx = scenarioContext[s]
                return (
                  <div
                    key={s}
                    className="rounded-[8px] p-4"
                    style={{
                      background: P.beige,
                      border: `1px solid ${P.sky}`,
                    }}
                  >
                    <div
                      className="font-semibold text-[13px] mb-3 capitalize flex items-center gap-2"
                      style={{ color: LINE_COLOR[s] }}
                    >
                      <span
                        className="w-2.5 h-2.5 rounded-full inline-block"
                        style={{ background: LINE_COLOR[s] }}
                      />
                      {s}
                    </div>
                    {ctx.items.map((item) => (
                      <div
                        key={item.label}
                        className="flex justify-between text-[12px] py-1.5"
                        style={{ borderBottom: `1px solid ${P.sky}` }}
                      >
                        <span style={{ color: P.teal }}>{item.label}</span>
                        <b style={{ color: P.navy }} className="font-medium">
                          {item.value}
                        </b>
                      </div>
                    ))}
                    <p
                      className="text-[11px] italic mt-3"
                      style={{ color: P.teal }}
                    >
                      {ctx.note}
                    </p>
                  </div>
                )
              })}
          </div>
        </div>
      )}

      {/* ── NOTE ── */}
      <div
        className="p-4 rounded-[8px] border-l-4 text-sm italic"
        style={{
          background: P.white,
          borderColor: P.darkTeal,
          color: P.teal,
          border: `1px solid ${P.sky}`,
          borderLeftColor: P.darkTeal,
          borderLeftWidth: "4px",
        }}
      >
        <span className="font-semibold not-italic" style={{ color: P.navy }}>
          Note:
        </span>{" "}
        This is derived based on mathematical assumptions and formula.
      </div>
    </div>
  )
}
