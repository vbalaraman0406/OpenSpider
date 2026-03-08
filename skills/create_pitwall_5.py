import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

def write(path, content):
    full = os.path.join(base, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Created: {path}')

# Home.jsx
write('frontend/src/pages/Home.jsx', r'''import React from "react";
import { Link } from "react-router-dom";

const FEATURES = [
  {
    title: "Race Analytics",
    description: "Deep-dive into race results, lap times, sector analysis, and position changes with interactive visualizations.",
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
  },
  {
    title: "Telemetry Data",
    description: "Compare driver telemetry traces including speed, throttle, brake, and gear data across any lap.",
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
  },
  {
    title: "Tire Strategy",
    description: "Visualize pit stop strategies, compound choices, and tire degradation patterns for every driver.",
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  },
  {
    title: "Predictive Models",
    description: "ML-powered race outcome predictions based on historical data, qualifying pace, and weather conditions.",
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
  },
];

export default function Home() {
  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="text-center py-16">
        <div className="inline-flex items-center space-x-2 bg-pitwall-surface border border-pitwall-border rounded-full px-4 py-1.5 mb-6">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <span className="text-xs font-mono text-pitwall-gray">2025 SEASON LIVE</span>
        </div>

        <h1 className="text-5xl md:text-7xl font-black mb-6 leading-tight">
          <span className="text-white">PITWALL</span>
          <span className="text-pitwall-red">.AI</span>
        </h1>

        <p className="text-xl text-pitwall-gray max-w-2xl mx-auto mb-8 leading-relaxed">
          Formula 1 analytics powered by data. Race results, telemetry traces,
          tire strategies, and predictive insights — all in one dashboard.
        </p>

        <div className="flex items-center justify-center space-x-4">
          <Link to="/race/2025/1" className="btn-primary text-lg px-8 py-3">
            View Australian GP
          </Link>
          <Link to="/drivers" className="btn-secondary text-lg px-8 py-3">
            Driver Stats
          </Link>
        </div>
      </section>

      {/* Stats Bar */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { value: "24", label: "Races" },
          { value: "20", label: "Drivers" },
          { value: "10", label: "Teams" },
          { value: "1000+", label: "Data Points/Lap" },
        ].map((stat, i) => (
          <div key={i} className="card text-center">
            <div className="stat-value text-pitwall-red">{stat.value}</div>
            <div className="stat-label">{stat.label}</div>
          </div>
        ))}
      </section>

      {/* Feature Cards */}
      <section>
        <h2 className="text-2xl font-bold mb-8 text-center">
          Analytics <span className="text-pitwall-red">Suite</span>
        </h2>
        <div className="grid md:grid-cols-2 gap-6">
          {FEATURES.map((feature, i) => (
            <div key={i} className="card hover:border-pitwall-red/50 transition-all duration-300 group">
              <div className="text-pitwall-red mb-4 group-hover:scale-110 transition-transform">
                {feature.icon}
              </div>
              <h3 className="text-lg font-bold mb-2">{feature.title}</h3>
              <p className="text-pitwall-gray text-sm leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Recent Race Quick Link */}
      <section className="card border-pitwall-red/30">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-xs font-mono text-pitwall-red mb-1">LATEST RACE</div>
            <h3 className="text-xl font-bold">2025 Australian Grand Prix</h3>
            <p className="text-pitwall-gray text-sm mt-1">Albert Park, Melbourne - Round 1</p>
          </div>
          <Link to="/race/2025/1" className="btn-primary">
            View Results
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="text-center text-pitwall-gray text-sm py-8 border-t border-pitwall-border">
        <p>Built with FastF1, React, and Tailwind CSS</p>
        <p className="mt-1">Data sourced from official F1 timing feeds</p>
      </footer>
    </div>
  );
}
''')

print('Home.jsx created')
