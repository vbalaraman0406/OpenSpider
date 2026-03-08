import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

def write(path, content):
    full = os.path.join(base, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Created: {path}')

# RaceDashboard.jsx
write('frontend/src/pages/RaceDashboard.jsx', r'''import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from "recharts";

const TEAM_COLORS = {
  "Red Bull Racing": "#3671C6",
  "McLaren": "#FF8000",
  "Ferrari": "#E8002D",
  "Mercedes": "#27F4D2",
  "Aston Martin": "#229971",
  "Alpine": "#FF87BC",
  "Williams": "#64C4FF",
  "RB": "#6692FF",
  "Sauber": "#52E252",
  "Haas F1 Team": "#B6BABD",
};

const COMPOUND_COLORS = {
  SOFT: "bg-red-500",
  MEDIUM: "bg-yellow-500",
  HARD: "bg-white",
  INTERMEDIATE: "bg-green-500",
  WET: "bg-blue-500",
};

const COMPOUND_TEXT = {
  SOFT: "text-white",
  MEDIUM: "text-black",
  HARD: "text-black",
  INTERMEDIATE: "text-white",
  WET: "text-white",
};

export default function RaceDashboard() {
  const { year, round } = useParams();
  const [results, setResults] = useState(null);
  const [laps, setLaps] = useState(null);
  const [strategy, setStrategy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("results");
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [resResults, resLaps, resStrategy] = await Promise.allSettled([
          axios.get(`/api/race/${year}/${round}/results`),
          axios.get(`/api/race/${year}/${round}/laps`),
          axios.get(`/api/race/${year}/${round}/strategy`),
        ]);
        if (resResults.status === "fulfilled") setResults(resResults.value.data);
        if (resLaps.status === "fulfilled") setLaps(resLaps.value.data);
        if (resStrategy.status === "fulfilled") setStrategy(resStrategy.value.data);
      } catch (err) {
        setError("Failed to load race data. Make sure the backend is running.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [year, round]);

  // Process lap data for chart
  const getChartData = () => {
    if (!laps || !laps.laps) return [];
    const drivers = [...new Set(laps.laps.map((l) => l.driver))].slice(0, 5);
    const maxLap = Math.max(...laps.laps.map((l) => l.lap_number));
    const chartData = [];
    for (let lap = 1; lap <= maxLap; lap++) {
      const point = { lap };
      drivers.forEach((drv) => {
        const lapData = laps.laps.find(
          (l) => l.driver === drv && l.lap_number === lap
        );
        if (lapData && lapData.lap_time) {
          point[drv] = parseFloat(lapData.lap_time.toFixed(3));
        }
      });
      chartData.push(point);
    }
    return { chartData, drivers };
  };

  const getTeamColor = (team) => {
    for (const [key, color] of Object.entries(TEAM_COLORS)) {
      if (team && team.includes(key)) return color;
    }
    return "#888888";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-pitwall-red border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-pitwall-gray">Loading race data...</p>
          <p className="text-xs text-pitwall-gray mt-1">First load may take 30-60s to fetch from F1 servers</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card border-red-500/50 text-center py-12">
        <p className="text-red-400 text-lg mb-2">{error}</p>
        <p className="text-pitwall-gray text-sm">Run: uvicorn app.main:app --reload --port 8000</p>
      </div>
    );
  }

  const { chartData, drivers: chartDrivers } = getChartData();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="text-xs font-mono text-pitwall-red mb-1">
            ROUND {round} / {year}
          </div>
          <h1 className="text-3xl font-black">Race Dashboard</h1>
        </div>
        <div className="flex space-x-2">
          {["results", "laptimes", "strategy"].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === tab
                  ? "bg-pitwall-red text-white"
                  : "bg-pitwall-surface text-pitwall-gray hover:text-white border border-pitwall-border"
              }`}
            >
              {tab === "results" ? "Classification" : tab === "laptimes" ? "Lap Times" : "Strategy"}
            </button>
          ))}
        </div>
      </div>

      {/* Results Table */}
      {activeTab === "results" && results && (
        <div className="card overflow-x-auto">
          <h2 className="text-lg font-bold mb-4">Race Classification</h2>
          <table className="data-table">
            <thead>
              <tr>
                <th>POS</th>
                <th>DRIVER</th>
                <th>TEAM</th>
                <th>GRID</th>
                <th>STATUS</th>
                <th>POINTS</th>
              </tr>
            </thead>
            <tbody>
              {results.results &&
                results.results.map((r, i) => (
                  <tr key={i}>
                    <td>
                      <span
                        className={`inline-flex items-center justify-center w-8 h-8 rounded-full font-bold text-sm ${
                          r.position === 1
                            ? "bg-yellow-500 text-black"
                            : r.position === 2
                            ? "bg-gray-400 text-black"
                            : r.position === 3
                            ? "bg-amber-700 text-white"
                            : "bg-pitwall-surface text-white"
                        }`}
                      >
                        {r.position || "--"}
                      </span>
                    </td>
                    <td>
                      <div className="flex items-center space-x-3">
                        <div
                          className="w-1 h-8 rounded-full"
                          style={{ backgroundColor: getTeamColor(r.team) }}
                        />
                        <div>
                          <div className="font-bold">{r.driver}</div>
                          <div className="text-xs text-pitwall-gray">{r.full_name}</div>
                        </div>
                      </div>
                    </td>
                    <td className="text-sm">{r.team}</td>
                    <td className="font-mono text-sm">{r.grid_position || "--"}</td>
                    <td>
                      <span
                        className={`text-xs px-2 py-1 rounded ${
                          r.status === "Finished"
                            ? "bg-green-500/20 text-green-400"
                            : "bg-red-500/20 text-red-400"
                        }`}
                      >
                        {r.status}
                      </span>
                    </td>
                    <td className="font-mono font-bold">{r.points}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Lap Times Chart */}
      {activeTab === "laptimes" && chartData && chartData.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-bold mb-4">Lap Time Comparison (Top 5)</h2>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a4a" />
              <XAxis
                dataKey="lap"
                stroke="#8892a4"
                fontSize={12}
                label={{ value: "Lap", position: "insideBottom", offset: -5, fill: "#8892a4" }}
              />
              <YAxis
                stroke="#8892a4"
                fontSize={12}
                domain={["auto", "auto"]}
                label={{ value: "Time (s)", angle: -90, position: "insideLeft", fill: "#8892a4" }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1a1a2e",
                  border: "1px solid #2a2a4a",
                  borderRadius: "8px",
                  color: "#fff",
                }}
              />
              <Legend />
              {chartDrivers &&
                chartDrivers.map((drv, i) => (
                  <Line
                    key={drv}
                    type="monotone"
                    dataKey={drv}
                    stroke={["#e10600", "#3671C6", "#FF8000", "#27F4D2", "#FF87BC"][i]}
                    dot={false}
                    strokeWidth={2}
                  />
                ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Tire Strategy */}
      {activeTab === "strategy" && strategy && (
        <div className="card">
          <h2 className="text-lg font-bold mb-4">Tire Strategy</h2>
          <div className="space-y-3">
            {strategy.strategies &&
              strategy.strategies.map((s, i) => (
                <div key={i} className="flex items-center space-x-4">
                  <div className="w-12 font-bold text-sm">{s.driver}</div>
                  <div className="flex-1 flex items-center space-x-1">
                    {s.stints.map((stint, j) => {
                      const totalLaps = strategy.strategies[0]
                        ? Math.max(...strategy.strategies.flatMap((st) => st.stints.map((sn) => sn.end_lap)))
                        : 58;
                      const widthPct = (stint.laps / totalLaps) * 100;
                      return (
                        <div
                          key={j}
                          className={`h-8 rounded flex items-center justify-center text-xs font-bold ${COMPOUND_COLORS[stint.compound] || "bg-gray-500"} ${COMPOUND_TEXT[stint.compound] || "text-white"}`}
                          style={{ width: `${widthPct}%`, minWidth: "30px" }}
                          title={`${stint.compound} - Laps ${stint.start_lap}-${stint.end_lap} (${stint.laps} laps)`}
                        >
                          {stint.compound ? stint.compound[0] : "?"}
                        </div>
                      );
                    })}
                  </div>
                  <div className="text-xs text-pitwall-gray w-24 text-right">
                    {s.stints.map((st) => st.compound ? st.compound[0] : "?").join(" > ")}
                  </div>
                </div>
              ))}
          </div>
          {/* Legend */}
          <div className="flex items-center space-x-4 mt-6 pt-4 border-t border-pitwall-border">
            {Object.entries(COMPOUND_COLORS).map(([compound, color]) => (
              <div key={compound} className="flex items-center space-x-1">
                <div className={`w-4 h-4 rounded ${color}`} />
                <span className="text-xs text-pitwall-gray">{compound}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
''')

print('RaceDashboard.jsx created')
