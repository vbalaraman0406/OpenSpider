import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

def write(path, content):
    full = os.path.join(base, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Created: {path}')

# DriverStats.jsx
write('frontend/src/pages/DriverStats.jsx', r'''import React, { useState, useEffect } from "react";
import axios from "axios";

const TEAM_COLORS = {
  "Red Bull Racing": { bg: "bg-[#3671C6]/20", border: "border-[#3671C6]", text: "text-[#3671C6]" },
  "McLaren": { bg: "bg-[#FF8000]/20", border: "border-[#FF8000]", text: "text-[#FF8000]" },
  "Ferrari": { bg: "bg-[#E8002D]/20", border: "border-[#E8002D]", text: "text-[#E8002D]" },
  "Mercedes": { bg: "bg-[#27F4D2]/20", border: "border-[#27F4D2]", text: "text-[#27F4D2]" },
  "Aston Martin": { bg: "bg-[#229971]/20", border: "border-[#229971]", text: "text-[#229971]" },
  "Alpine": { bg: "bg-[#FF87BC]/20", border: "border-[#FF87BC]", text: "text-[#FF87BC]" },
  "Williams": { bg: "bg-[#64C4FF]/20", border: "border-[#64C4FF]", text: "text-[#64C4FF]" },
  "RB": { bg: "bg-[#6692FF]/20", border: "border-[#6692FF]", text: "text-[#6692FF]" },
  "Sauber": { bg: "bg-[#52E252]/20", border: "border-[#52E252]", text: "text-[#52E252]" },
  "Haas": { bg: "bg-[#B6BABD]/20", border: "border-[#B6BABD]", text: "text-[#B6BABD]" },
};

const getTeamStyle = (team) => {
  for (const [key, style] of Object.entries(TEAM_COLORS)) {
    if (team && team.includes(key)) return style;
  }
  return { bg: "bg-gray-500/20", border: "border-gray-500", text: "text-gray-400" };
};

export default function DriverStats() {
  const [drivers, setDrivers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [driver1, setDriver1] = useState(null);
  const [driver2, setDriver2] = useState(null);
  const [compareMode, setCompareMode] = useState(false);

  useEffect(() => {
    const fetchDrivers = async () => {
      try {
        const res = await axios.get("/api/drivers");
        setDrivers(res.data.drivers || []);
      } catch (err) {
        // Use fallback data if API is not running
        setDrivers([
          { code: "VER", name: "Max Verstappen", number: 1, team: "Red Bull Racing", country: "NED" },
          { code: "NOR", name: "Lando Norris", number: 4, team: "McLaren", country: "GBR" },
          { code: "LEC", name: "Charles Leclerc", number: 16, team: "Ferrari", country: "MON" },
          { code: "HAM", name: "Lewis Hamilton", number: 44, team: "Ferrari", country: "GBR" },
          { code: "RUS", name: "George Russell", number: 63, team: "Mercedes", country: "GBR" },
          { code: "PIA", name: "Oscar Piastri", number: 81, team: "McLaren", country: "AUS" },
          { code: "ANT", name: "Andrea Kimi Antonelli", number: 12, team: "Mercedes", country: "ITA" },
          { code: "SAI", name: "Carlos Sainz Jr.", number: 55, team: "Williams", country: "ESP" },
          { code: "ALO", name: "Fernando Alonso", number: 14, team: "Aston Martin", country: "ESP" },
          { code: "STR", name: "Lance Stroll", number: 18, team: "Aston Martin", country: "CAN" },
          { code: "GAS", name: "Pierre Gasly", number: 10, team: "Alpine", country: "FRA" },
          { code: "TSU", name: "Yuki Tsunoda", number: 22, team: "RB", country: "JPN" },
          { code: "ALB", name: "Alexander Albon", number: 23, team: "Williams", country: "THA" },
          { code: "HUL", name: "Nico Hulkenberg", number: 27, team: "Sauber", country: "GER" },
          { code: "BEA", name: "Oliver Bearman", number: 87, team: "Haas", country: "GBR" },
          { code: "OCO", name: "Esteban Ocon", number: 31, team: "Haas", country: "FRA" },
          { code: "LAW", name: "Liam Lawson", number: 30, team: "Red Bull Racing", country: "NZL" },
          { code: "HAD", name: "Isack Hadjar", number: 6, team: "RB", country: "FRA" },
          { code: "BOR", name: "Gabriel Bortoleto", number: 5, team: "Sauber", country: "BRA" },
          { code: "DOO", name: "Jack Doohan", number: 7, team: "Alpine", country: "AUS" },
        ]);
      } finally {
        setLoading(false);
      }
    };
    fetchDrivers();
  }, []);

  const handleDriverSelect = (driver) => {
    if (!compareMode) return;
    if (!driver1) {
      setDriver1(driver);
    } else if (!driver2) {
      setDriver2(driver);
    } else {
      setDriver1(driver);
      setDriver2(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-12 h-12 border-4 border-pitwall-red border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="text-xs font-mono text-pitwall-red mb-1">2025 SEASON</div>
          <h1 className="text-3xl font-black">Driver Lineup</h1>
        </div>
        <button
          onClick={() => {
            setCompareMode(!compareMode);
            setDriver1(null);
            setDriver2(null);
          }}
          className={compareMode ? "btn-primary" : "btn-secondary"}
        >
          {compareMode ? "Exit Compare" : "Compare Drivers"}
        </button>
      </div>

      {compareMode && (
        <div className="card border-pitwall-red/30">
          <p className="text-sm text-pitwall-gray mb-2">Select two drivers to compare:</p>
          <div className="flex items-center space-x-4">
            <div className={`flex-1 p-4 rounded-lg border ${driver1 ? "border-pitwall-red bg-pitwall-red/10" : "border-dashed border-pitwall-border"}`}>
              {driver1 ? (
                <div className="text-center">
                  <div className="text-2xl font-black">{driver1.code}</div>
                  <div className="text-sm text-pitwall-gray">{driver1.name}</div>
                </div>
              ) : (
                <div className="text-center text-pitwall-gray">Select Driver 1</div>
              )}
            </div>
            <div className="text-2xl font-bold text-pitwall-red">VS</div>
            <div className={`flex-1 p-4 rounded-lg border ${driver2 ? "border-pitwall-red bg-pitwall-red/10" : "border-dashed border-pitwall-border"}`}>
              {driver2 ? (
                <div className="text-center">
                  <div className="text-2xl font-black">{driver2.code}</div>
                  <div className="text-sm text-pitwall-gray">{driver2.name}</div>
                </div>
              ) : (
                <div className="text-center text-pitwall-gray">Select Driver 2</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Driver Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {drivers.map((driver) => {
          const style = getTeamStyle(driver.team);
          const isSelected = driver1?.code === driver.code || driver2?.code === driver.code;
          return (
            <div
              key={driver.code}
              onClick={() => handleDriverSelect(driver)}
              className={`card ${compareMode ? "cursor-pointer hover:scale-105" : ""} transition-all duration-200 ${
                isSelected ? "ring-2 ring-pitwall-red" : ""
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className={`text-4xl font-black font-mono ${style.text}`}>
                  {driver.number}
                </div>
                <span className={`text-xs px-2 py-1 rounded ${style.bg} ${style.text} border ${style.border}`}>
                  {driver.team}
                </span>
              </div>
              <div className="text-lg font-bold">{driver.name}</div>
              <div className="flex items-center justify-between mt-2">
                <span className="text-sm font-mono text-pitwall-gray">{driver.code}</span>
                <span className="text-xs text-pitwall-gray">{driver.country}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Teams Summary */}
      <div className="card">
        <h2 className="text-lg font-bold mb-4">2025 Team Lineup</h2>
        <table className="data-table">
          <thead>
            <tr>
              <th>TEAM</th>
              <th>DRIVER 1</th>
              <th>DRIVER 2</th>
            </tr>
          </thead>
          <tbody>
            {[
              ["Red Bull Racing", "Max Verstappen (#1)", "Liam Lawson (#30)"],
              ["McLaren", "Lando Norris (#4)", "Oscar Piastri (#81)"],
              ["Ferrari", "Lewis Hamilton (#44)", "Charles Leclerc (#16)"],
              ["Mercedes", "George Russell (#63)", "Andrea Kimi Antonelli (#12)"],
              ["Aston Martin", "Fernando Alonso (#14)", "Lance Stroll (#18)"],
              ["Alpine", "Pierre Gasly (#10)", "Jack Doohan (#7)"],
              ["Williams", "Alexander Albon (#23)", "Carlos Sainz Jr. (#55)"],
              ["RB", "Yuki Tsunoda (#22)", "Isack Hadjar (#6)"],
              ["Sauber", "Nico Hulkenberg (#27)", "Gabriel Bortoleto (#5)"],
              ["Haas", "Oliver Bearman (#87)", "Esteban Ocon (#31)"],
            ].map(([team, d1, d2], i) => {
              const style = getTeamStyle(team);
              return (
                <tr key={i}>
                  <td>
                    <div className="flex items-center space-x-2">
                      <div className={`w-3 h-3 rounded-full ${style.bg} border ${style.border}`} />
                      <span className="font-medium">{team}</span>
                    </div>
                  </td>
                  <td>{d1}</td>
                  <td>{d2}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
''')

print('DriverStats.jsx created')
