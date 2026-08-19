export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

export interface ForecastScenario {
  forecast: number[]
  params: {
    p: number
    q: number
    m: number
    calibration_factor: number
  }
  raw_assumptions: Record<string, number | string | boolean>
}

export interface ForecastRun {
  run_id: string
  new_drug_id: string
  new_drug_name: string
  selected_model: string
  uploaded_at: string
  forecast_horizon_months: number
  top_k: number
  known_monthly_rx: number[]
  selected_analogs: Array<{
    drug_id: string
    drug_name?: string | null
    rank: number
    similarity_score: number
    weight: number
  }>
  base_bass_params: {
    calibration_factor: number
    bass_p: number
    bass_q: number
    bass_m: number
    blend_weight_analog: number
    blend_weight_bass: number
  }
  scenario_results: Record<string, ForecastScenario>
  scenario_assumptions_used: Record<string, Record<string, number | string | boolean>>
  output_files: Record<string, string>
  warnings: string[]
}

export async function runForecast(
  newDrugDataset: File,
  analogDataset: File,
  assumptions: Record<string, Record<string, number | string | boolean>>,
): Promise<ForecastRun> {
  const formData = new FormData()
  formData.append("new_drug_dataset", newDrugDataset)
  formData.append("analog_dataset", analogDataset)
  formData.append(
    "model_market_assumptions",
    new File([JSON.stringify(assumptions)], "model_market_assumptions.json", {
      type: "application/json",
    }),
  )

  const response = await fetch(`${API_BASE_URL}/api/v1/forecast/run`, {
    method: "POST",
    body: formData,
  })

  if (!response.ok) {
    const body = await response.json().catch(() => null)
    const detail = body?.detail
    const message =
      typeof detail === "string"
        ? detail
        : detail?.issues?.join(" ") || "The forecast could not be generated."
    throw new Error(message)
  }

  return response.json() as Promise<ForecastRun>
}

export function saveForecastRun(run: ForecastRun) {
  window.sessionStorage.setItem("baseline.forecast.run", JSON.stringify(run))
}

export function loadForecastRun(): ForecastRun | null {
  const stored = window.sessionStorage.getItem("baseline.forecast.run")
  if (!stored) return null
  try {
    return JSON.parse(stored) as ForecastRun
  } catch {
    window.sessionStorage.removeItem("baseline.forecast.run")
    return null
  }
}
