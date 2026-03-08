import os

base = 'workspace/pitwall-ai/frontend'

os.makedirs(f'{base}/src/components', exist_ok=True)
os.makedirs(f'{base}/src/pages', exist_ok=True)

files = {}

files[f'{base}/src/components/Navbar.tsx'] = '''import { Link, useLocation } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard" },
  { to: "/drivers/2026", label: "Drivers" },
  { to: "/compare", label: "Compare" },
];

export default function Navbar() {
  const location = useLocation();
  return (
    <nav className="sticky top-0 z-50 bg-f1-gray/95 backdrop-blur border-b border-f1-border">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <span className="text-f1-red font-black text-xl tracking-tight">PITWALL</span>
          <span className="text-f1-white font-light text-xl">.ai</span>
        </Link>
        <div className="flex items-center gap-6">
          {links.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              className={`text-sm font-medium transition-colors hover:text-f1-red ${
                location.pathname === l.to ? "text-f1-red" : "text-f1-muted"
              }`}
            >
              {l.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}
'''

files[f'{base}/src/components/RaceCard.tsx'] = '''import { Link } from "react-router-dom";

interface RaceCardProps {
  year: number;
  round: number;
  name: string;
  circuit: string;
  date: string;
  country: string;
  winner?: string;
  completed: boolean;
}

export default function RaceCard({ year, round, name, circuit, date, country, winner, completed }: RaceCardProps) {
  return (
    <Link
      to={`/race/${year}/${round}`}
      className="block bg-f1-card border border-f1-border rounded-lg p-4 hover:border-f1-red transition-all duration-200 group"
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-f1-muted text-xs font-mono">R{String(round).padStart(2, "0")}</span>
        <span className="text-xs text-f1-muted">{date}</span>
      </div>
      <h3 className="text-f1-white font-semibold text-sm group-hover:text-f1-red transition-colors">
        {country} {name}
      </h3>
      <p className="text-f1-muted text-xs mt-1">{circuit}</p>
      {completed && winner && (
        <div className="mt-3 pt-2 border-t border-f1-border">
          <span className="text-xs text-f1-muted">Winner: </span>
          <span className="text-xs text-f1-white font-medium">{winner}</span>
        </div>
      )}
      {!completed && (
        <div className="mt-3 pt-2 border-t border-f1-border">
          <span className="text-xs text-f1-red font-medium">UPCOMING</span>
        </div>
      )}
    </Link>
  );
}
'''

files[f'{base}/src/pages/Dashboard.tsx'] = '''import { useState, useEffect } from "react";
import RaceCard from "../components/RaceCard";
import { getRaces } from "../api";

interface Race {
  round: number;
  name: string;
  circuit: string;
  date: string;
  country: string;
  winner?: string;
  completed: boolean;
}

export default function Dashboard() {
  const [races, setRaces] = useState<Race[]>([]);
  const [loading, setLoading] = useState(true);
  const year = 2026;

  useEffect(() => {
    getRaces(year)
      .then((res) => setRaces(res.data))
      .catch(() => {
        setRaces([
          { round: 1, name: "Australian Grand Prix", circuit: "Albert Park", date: "2026-03-08", country: "\ud83c\udde6\ud83c\uddfa", winner: "George Russell", completed: true },
          { round: 2, name: "Chinese Grand Prix", circuit: "Shanghai International", date: "2026-03-15", country: "\ud83c\udde8\ud83c\uddf3", completed: false },
          { round: 3, name: "Japanese Grand Prix", circuit: "Suzuka", date: "2026-03-29", country: "\ud83c\uddef\ud83c\uddf5", completed: false },
          { round: 4, name: "Bahrain Grand Prix", circuit: "Sakhir", date: "2026-04-12", country: "\ud83c\udde7\ud83c\udded", completed: false },
          { round: 5, name: "Saudi Arabian Grand Prix", circuit: "Jeddah", date: "2026-04-19", country: "\ud83c\uddf8\ud83c\udde6", completed: false },
          { round: 6, name: "Miami Grand Prix", circuit: "Miami International", date: "2026-05-03", country: "\ud83c\uddfa\ud83c\uddf8", completed: false },
        ]);
      })
      .finally(() => setLoading(false));
  }, []);

  const completed = races.filter((r) => r.completed);
  const upcoming = races.filter((r) => !r.completed);

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-black text-f1-white">
          {year} <span className="text-f1-red">F1</span> Season
        </h1>
        <p className="text-f1-muted mt-1">Race analytics, driver stats & predictions</p>
      </div>

      {loading ? (
        <div className="text-f1-muted text-center py-20">Loading races...</div>
      ) : (
        <>
          {completed.length > 0 && (
            <section className="mb-10">
              <h2 className="text-lg font-semibold text-f1-white mb-4 flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span> Completed
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {completed.map((r) => (
                  <RaceCard key={r.round} year={year} {...r} />
                ))}
              </div>
            </section>
          )}

          {upcoming.length > 0 && (
            <section>
              <h2 className="text-lg font-semibold text-f1-white mb-4 flex items-center gap-2">
                <span className="w-2 h-2 bg-f1-red rounded-full animate-pulse"></span> Upcoming
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {upcoming.map((r) => (
                  <RaceCard key={r.round} year={year} {...r} />
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
}
'''

files[f'{base}/src/pages/RaceDetail.tsx'] = '''import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { getRaceResults, getStrategy } from "../api";

interface Result {
  position: number;
  driver: string;
  team: string;
  time: string;
  points: number;
}

interface Stint {
  driver: string;
  compound: string;
  laps: number;
  start_lap: number;
}

const COMPOUND_COLORS: Record<string, string> = {
  SOFT: "bg-red-500",
  MEDIUM: "bg-yellow-500",
  HARD: "bg-gray-300",
  INTERMEDIATE: "bg-green-500",
  WET: "bg-blue-500",
};

export default function RaceDetail() {
  const { year, round } = useParams<{ year: string; round: string }>();
  const [tab, setTab] = useState<"results" | "strategy" | "telemetry">("results");
  const [results, setResults] = useState<Result[]>([]);
  const [strategy, setStrategy] = useState<Stint[]>([]);
  const [loading, setLoading] = useState(true);

  const y = Number(year);
  const r = Number(round);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      getRaceResults(y, r).catch(() => ({ data: [] })),
      getStrategy(y, r).catch(() => ({ data: [] })),
    ]).then(([resRes, stratRes]) => {
      setResults(resRes.data.length ? resRes.data : [
        { position: 1, driver: "George Russell", team: "Mercedes", time: "1:32:46.123", points: 25 },
        { position: 2, driver: "Kimi Antonelli", team: "Mercedes", time: "+2.974s", points: 18 },
        { position: 3, driver: "Charles Leclerc", team: "Ferrari", time: "+15.519s", points: 15 },
        { position: 4, driver: "Lewis Hamilton", team: "Ferrari", time: "+22.341s", points: 12 },
        { position: 5, driver: "Lando Norris", team: "McLaren", time: "+28.876s", points: 10 },
      ]);
      setStrategy(stratRes.data);
      setLoading(false);
    });
  }, [y, r]);

  const tabs = [
    { key: "results" as const, label: "Results" },
    { key: "strategy" as const, label: "Strategy" },
    { key: "telemetry" as const, label: "Telemetry" },
  ];

  return (
    <div>
      <h1 className="text-2xl font-black text-f1-white mb-1">Round {round}</h1>
      <p className="text-f1-muted mb-6">{year} Season</p>

      <div className="flex gap-4 mb-6 border-b border-f1-border">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`pb-2 text-sm font-medium transition-colors border-b-2 ${
              tab === t.key
                ? "border-f1-red text-f1-red"
                : "border-transparent text-f1-muted hover:text-f1-white"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-f1-muted text-center py-20">Loading...</div>
      ) : (
        <>
          {tab === "results" && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-f1-border text-f1-muted text-left">
                    <th className="py-3 px-2 w-12">POS</th>
                    <th className="py-3 px-2">DRIVER</th>
                    <th className="py-3 px-2">TEAM</th>
                    <th className="py-3 px-2">TIME</th>
                    <th className="py-3 px-2 w-16">PTS</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((res) => (
                    <tr key={res.position} className="border-b border-f1-border/50 hover:bg-f1-card transition-colors">
                      <td className="py-3 px-2 font-mono font-bold text-f1-white">{res.position}</td>
                      <td className="py-3 px-2 font-medium text-f1-white">{res.driver}</td>
                      <td className="py-3 px-2 text-f1-muted">{res.team}</td>
                      <td className="py-3 px-2 font-mono text-f1-muted">{res.time}</td>
                      <td className="py-3 px-2 font-mono text-f1-red">{res.points}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {tab === "strategy" && (
            <div>
              {strategy.length === 0 ? (
                <p className="text-f1-muted text-center py-10">Strategy data not available yet.</p>
              ) : (
                <div className="space-y-2">
                  {strategy.map((s, i) => (
                    <div key={i} className="flex items-center gap-3">
                      <span className="text-xs font-mono text-f1-muted w-16">{s.driver}</span>
                      <div
                        className={`h-6 rounded ${COMPOUND_COLORS[s.compound] || "bg-gray-500"}`}
                        style={{ width: `${s.laps * 3}px` }}
                        title={`${s.compound} - ${s.laps} laps`}
                      />
                      <span className="text-xs text-f1-muted">{s.compound} ({s.laps}L)</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {tab === "telemetry" && (
            <div className="text-center py-20">
              <p className="text-f1-muted">Telemetry visualization coming soon.</p>
              <p className="text-f1-muted text-xs mt-2">Speed, throttle, brake & gear traces</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
'''

files[f'{base}/src/pages/Drivers.tsx'] = '''import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { getDrivers } from "../api";

interface Driver {
  code: string;
  name: string;
  team: string;
  number: number;
  points: number;
  wins: number;
  podiums: number;
}

const TEAM_COLORS: Record<string, string> = {
  Mercedes: "border-l-[#00D2BE]",
  Ferrari: "border-l-[#DC0000]",
  "Red Bull": "border-l-[#3671C6]",
  McLaren: "border-l-[#FF8700]",
  Alpine: "border-l-[#0090FF]",
  "Aston Martin": "border-l-[#006F62]",
  Williams: "border-l-[#005AFF]",
  Haas: "border-l-[#B6BABD]",
  Sauber: "border-l-[#52E252]",
  "Racing Bulls": "border-l-[#6692FF]",
};

export default function Drivers() {
  const { year } = useParams<{ year: string }>();
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDrivers(Number(year))
      .then((res) => setDrivers(res.data))
      .catch(() => {
        setDrivers([
          { code: "RUS", name: "George Russell", team: "Mercedes", number: 63, points: 25, wins: 1, podiums: 1 },
          { code: "ANT", name: "Kimi Antonelli", team: "Mercedes", number: 12, points: 18, wins: 0, podiums: 1 },
          { code: "LEC", name: "Charles Leclerc", team: "Ferrari", number: 16, points: 15, wins: 0, podiums: 1 },
          { code: "HAM", name: "Lewis Hamilton", team: "Ferrari", number: 44, points: 12, wins: 0, podiums: 0 },
          { code: "NOR", name: "Lando Norris", team: "McLaren", number: 4, points: 10, wins: 0, podiums: 0 },
          { code: "VER", name: "Max Verstappen", team: "Red Bull", number: 1, points: 8, wins: 0, podiums: 0 },
        ]);
      })
      .finally(() => setLoading(false));
  }, [year]);

  return (
    <div>
      <h1 className="text-2xl font-black text-f1-white mb-1">{year} Drivers</h1>
      <p className="text-f1-muted mb-6">Championship standings after Round 1</p>

      {loading ? (
        <div className="text-f1-muted text-center py-20">Loading drivers...</div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {drivers.map((d, i) => (
            <div
              key={d.code}
              className={`bg-f1-card border border-f1-border rounded-lg p-4 border-l-4 ${TEAM_COLORS[d.team] || "border-l-f1-muted"}`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-f1-muted text-xs font-mono">P{i + 1}</span>
                <span className="text-f1-muted text-xs font-mono">#{d.number}</span>
              </div>
              <h3 className="text-f1-white font-bold text-lg">{d.name}</h3>
              <p className="text-f1-muted text-sm">{d.team}</p>
              <div className="mt-3 pt-2 border-t border-f1-border flex justify-between text-xs">
                <span className="text-f1-muted">Points: <span className="text-f1-white font-bold">{d.points}</span></span>
                <span className="text-f1-muted">Wins: <span className="text-f1-white font-bold">{d.wins}</span></span>
                <span className="text-f1-muted">Podiums: <span className="text-f1-white font-bold">{d.podiums}</span></span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
'''

files[f'{base}/src/pages/Compare.tsx'] = '''import { useState } from "react";
import { compareDrivers } from "../api";

const AVAILABLE_DRIVERS = [
  { code: "RUS", name: "George Russell" },
  { code: "ANT", name: "Kimi Antonelli" },
  { code: "LEC", name: "Charles Leclerc" },
  { code: "HAM", name: "Lewis Hamilton" },
  { code: "NOR", name: "Lando Norris" },
  { code: "VER", name: "Max Verstappen" },
  { code: "PIA", name: "Oscar Piastri" },
  { code: "SAI", name: "Carlos Sainz" },
];

interface CompareResult {
  driver: string;
  points: number;
  wins: number;
  podiums: number;
  avg_finish: number;
  avg_quali: number;
  dnfs: number;
}

export default function Compare() {
  const [d1, setD1] = useState("RUS");
  const [d2, setD2] = useState("LEC");
  const [results, setResults] = useState<CompareResult[]>([]);
  const [loading, setLoading] = useState(false);

  const handleCompare = () => {
    setLoading(true);
    compareDrivers(2026, [d1, d2])
      .then((res) => setResults(res.data))
      .catch(() => {
        setResults([
          { driver: d1, points: 25, wins: 1, podiums: 1, avg_finish: 1.0, avg_quali: 1.0, dnfs: 0 },
          { driver: d2, points: 15, wins: 0, podiums: 1, avg_finish: 3.0, avg_quali: 4.0, dnfs: 0 },
        ]);
      })
      .finally(() => setLoading(false));
  };

  const stats = ["points", "wins", "podiums", "avg_finish", "avg_quali", "dnfs"] as const;
  const labels: Record<string, string> = {
    points: "Points",
    wins: "Wins",
    podiums: "Podiums",
    avg_finish: "Avg Finish",
    avg_quali: "Avg Quali",
    dnfs: "DNFs",
  };

  return (
    <div>
      <h1 className="text-2xl font-black text-f1-white mb-1">Driver Comparison</h1>
      <p className="text-f1-muted mb-6">Head-to-head stats for the 2026 season</p>

      <div className="flex flex-wrap items-end gap-4 mb-8">
        <div>
          <label className="block text-xs text-f1-muted mb-1">Driver 1</label>
          <select
            value={d1}
            onChange={(e) => setD1(e.target.value)}
            className="bg-f1-card border border-f1-border rounded px-3 py-2 text-f1-white text-sm"
          >
            {AVAILABLE_DRIVERS.map((d) => (
              <option key={d.code} value={d.code}>{d.name}</option>
            ))}
          </select>
        </div>
        <span className="text-f1-muted text-xl font-bold pb-1">vs</span>
        <div>
          <label className="block text-xs text-f1-muted mb-1">Driver 2</label>
          <select
            value={d2}
            onChange={(e) => setD2(e.target.value)}
            className="bg-f1-card border border-f1-border rounded px-3 py-2 text-f1-white text-sm"
          >
            {AVAILABLE_DRIVERS.map((d) => (
              <option key={d.code} value={d.code}>{d.name}</option>
            ))}
          </select>
        </div>
        <button
          onClick={handleCompare}
          className="bg-f1-red hover:bg-red-700 text-white font-semibold px-6 py-2 rounded text-sm transition-colors"
        >
          Compare
        </button>
      </div>

      {loading && <div className="text-f1-muted text-center py-10">Loading...</div>}

      {results.length === 2 && !loading && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-f1-border text-f1-muted text-left">
                <th className="py-3 px-2">STAT</th>
                <th className="py-3 px-2 text-center">{results[0].driver}</th>
                <th className="py-3 px-2 text-center">{results[1].driver}</th>
              </tr>
            </thead>
            <tbody>
              {stats.map((s) => {
                const v1 = results[0][s];
                const v2 = results[1][s];
                const better1 = s === "avg_finish" || s === "avg_quali" || s === "dnfs" ? v1 <= v2 : v1 >= v2;
                const better2 = !better1;
                return (
                  <tr key={s} className="border-b border-f1-border/50">
                    <td className="py-3 px-2 text-f1-muted">{labels[s]}</td>
                    <td className={`py-3 px-2 text-center font-mono font-bold ${better1 ? "text-green-400" : "text-f1-muted"}`}>
                      {typeof v1 === "number" && v1 % 1 !== 0 ? v1.toFixed(1) : v1}
                    </td>
                    <td className={`py-3 px-2 text-center font-mono font-bold ${better2 ? "text-green-400" : "text-f1-muted"}`}>
                      {typeof v2 === "number" && v2 % 1 !== 0 ? v2.toFixed(1) : v2}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
'''

for path, content in files.items():
    with open(path, 'w') as f:
        f.write(content)
    print(f'  OK {path}')

print(f'\nPhase 2 complete. {len(files)} component/page files written.')
