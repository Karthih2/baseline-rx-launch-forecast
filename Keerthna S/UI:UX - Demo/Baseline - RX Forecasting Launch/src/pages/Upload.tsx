import { UploadCloud } from "lucide-react"

export default function NewForecast() {
  return (
    <div className="max-w-xl mx-auto space-y-8">
      <h1 className="font-serif text-2xl text-[#2F4156]">New Forecast</h1>

      <div className="space-y-10">
        {/* Step 1 */}
        <div>
          <h2 className="font-sans font-medium text-[#2F4156] mb-3">
            Step 1: Upload new data
          </h2>
          <div className="border border-dashed border-[#567C8D] rounded-lg bg-[#2F4156] flex flex-col items-center justify-center py-10 px-4 cursor-pointer hover:bg-[#3a5068] transition-colors">
            <UploadCloud className="text-[#C8D9E6] w-8 h-8 mb-3" />
            <span className="text-sm text-[#F5EFEB] font-medium">
              Click or drag file to this area
            </span>
            <span className="text-xs text-[#C8D9E6] mt-1">
              Upload primary data source
            </span>
          </div>
        </div>

        {/* Step 2 */}
        <div>
          <h2 className="font-sans font-medium text-[#2F4156] mb-3">
            Step 2: Upload analog data
          </h2>
          <div className="border border-dashed border-[#567C8D] rounded-lg bg-[#2F4156] flex flex-col items-center justify-center py-10 px-4 cursor-pointer hover:bg-[#3a5068] transition-colors">
            <UploadCloud className="text-[#C8D9E6] w-8 h-8 mb-3" />
            <span className="text-sm text-[#F5EFEB] font-medium">
              Click or drag file to this area
            </span>
            <span className="text-xs text-[#C8D9E6] mt-1">
              Comparable past product launches
            </span>
          </div>
        </div>

        {/* Step 3 */}
        <div>
          <h2 className="font-sans font-medium text-[#2F4156] mb-4">
            Step 3: Model assumptions
          </h2>
          <div className="bg-[#2F4156] border border-[#567C8D] rounded-[8px] p-6 space-y-6">
            {/* Field 1 */}
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-[13px] text-[#F5EFEB] font-medium">
                  Market size adjustment (%)
                </label>
                <span className="text-[12px] text-[#C8D9E6] font-mono tabular-nums">
                  0%
                </span>
              </div>
              <p className="text-[12px] text-[#C8D9E6] mb-3">
                Adjust the total addressable market base
              </p>
              <input
                type="range"
                min="-30"
                max="30"
                step="1"
                defaultValue="0"
                className="w-full accent-[#C8D9E6]"
              />
            </div>

            {/* Field 2 */}
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-[13px] text-[#F5EFEB] font-medium">
                  Adoption speed
                </label>
                <span className="text-[12px] text-[#C8D9E6] font-mono tabular-nums">
                  1.00x
                </span>
              </div>
              <p className="text-[12px] text-[#C8D9E6] mb-3">
                Slower ← → Faster
              </p>
              <input
                type="range"
                min="0.85"
                max="1.15"
                step="0.01"
                defaultValue="1"
                className="w-full accent-[#C8D9E6]"
              />
            </div>

            {/* Field 3 */}
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-[13px] text-[#F5EFEB] font-medium">
                  Peak penetration ceiling
                </label>
                <span className="text-[12px] text-[#C8D9E6] font-mono tabular-nums">
                  1.00x
                </span>
              </div>
              <p className="text-[12px] text-[#C8D9E6] mb-3">
                Lower ceiling ← → Higher ceiling
              </p>
              <input
                type="range"
                min="0.85"
                max="1.20"
                step="0.01"
                defaultValue="1"
                className="w-full accent-[#C8D9E6]"
              />
            </div>

            {/* Field 4: Toggle */}
            <div className="flex items-center justify-between pt-2">
              <div>
                <label className="text-[13px] text-[#F5EFEB] font-medium block">
                  Competitive entry flag
                </label>
                <span className="text-[12px] text-[#C8D9E6]">
                  Account for anticipated market entrants
                </span>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" />
                <div className="w-9 h-5 bg-[#567C8D] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-[#C8D9E6]"></div>
              </label>
            </div>

            {/* Field 5: Payer access trend */}
            <div className="pt-2">
              <label className="text-[13px] text-[#F5EFEB] font-medium block mb-1">
                Payer access trend
              </label>
              <p className="text-[12px] text-[#C8D9E6] mb-3">
                Expected formulary coverage shifts
              </p>
              <div className="flex bg-[#F5EFEB] p-1 rounded border border-[#C8D9E6] w-full">
                {["Worsening", "Stable", "Improving"].map((o) => (
                  <button
                    key={o}
                    className={`flex-1 py-1.5 text-xs font-medium rounded transition-colors ${
                      o === "Stable"
                        ? "bg-white shadow-sm text-[#2F4156]"
                        : "text-[#567C8D] hover:text-[#2F4156]"
                    }`}
                  >
                    {o}
                  </button>
                ))}
              </div>
            </div>

            {/* Field 6: Promotional spend trend */}
            <div className="pt-2">
              <label className="text-[13px] text-[#F5EFEB] font-medium block mb-1">
                Promotional spend trend
              </label>
              <p className="text-[12px] text-[#C8D9E6] mb-3">
                Marketing investment over time
              </p>
              <div className="flex bg-[#F5EFEB] p-1 rounded border border-[#C8D9E6] w-full">
                {["Cutting", "Steady", "Ramping"].map((o) => (
                  <button
                    key={o}
                    className={`flex-1 py-1.5 text-xs font-medium rounded transition-colors ${
                      o === "Steady"
                        ? "bg-white shadow-sm text-[#2F4156]"
                        : "text-[#567C8D] hover:text-[#2F4156]"
                    }`}
                  >
                    {o}
                  </button>
                ))}
              </div>
            </div>

            {/* Submit */}
            <div className="pt-6">
              <button className="w-full bg-[#F5EFEB] text-[#2F4156] font-sans text-sm font-semibold py-2.5 rounded-[6px] hover:bg-[#C8D9E6] transition-colors">
                Generate forecast
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
