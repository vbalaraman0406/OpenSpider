import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

def write(path, content):
    full = os.path.join(base, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Created: {path}')

# Navbar.jsx - using text flags instead of emoji
navbar = r'''import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

const RACES_2025 = [
  { round: 1, name: "Australian GP", flag: "AUS" },
  { round: 2, name: "Chinese GP", flag: "CHN" },
  { round: 3, name: "Japanese GP", flag: "JPN" },
  { round: 4, name: "Bahrain GP", flag: "BHR" },
  { round: 5, name: "Saudi Arabian GP", flag: "KSA" },
  { round: 6, name: "Miami GP", flag: "USA" },
  { round: 7, name: "Emilia Romagna GP", flag: "ITA" },
  { round: 8, name: "Monaco GP", flag: "MON" },
  { round: 9, name: "Spanish GP", flag: "ESP" },
  { round: 10, name: "Canadian GP", flag: "CAN" },
  { round: 11, name: "Austrian GP", flag: "AUT" },
  { round: 12, name: "British GP", flag: "GBR" },
  { round: 13, name: "Belgian GP", flag: "BEL" },
  { round: 14, name: "Hungarian GP", flag: "HUN" },
  { round: 15, name: "Dutch GP", flag: "NED" },
  { round: 16, name: "Italian GP", flag: "ITA" },
  { round: 17, name: "Azerbaijan GP", flag: "AZE" },
  { round: 18, name: "Singapore GP", flag: "SGP" },
  { round: 19, name: "United States GP", flag: "USA" },
  { round: 20, name: "Mexico City GP", flag: "MEX" },
  { round: 21, name: "Brazilian GP", flag: "BRA" },
  { round: 22, name: "Las Vegas GP", flag: "USA" },
  { round: 23, name: "Qatar GP", flag: "QAT" },
  { round: 24, name: "Abu Dhabi GP", flag: "UAE" },
];

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const [raceDropdown, setRaceDropdown] = useState(false);
  const navigate = useNavigate();

  return (
    <nav className="bg-pitwall-card border-b border-pitwall-border sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-pitwall-red rounded-lg flex items-center justify-center">
              <span className="text-white font-black text-sm">P</span>
            </div>
            <span className="text-xl font-bold">
              Pitwall<span className="text-pitwall-red">.ai</span>
            </span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center space-x-6">
            <Link to="/" className="text-pitwall-gray hover:text-white transition-colors font-medium">
              Home
            </Link>

            {/* Race Selector Dropdown */}
            <div className="relative">
              <button
                onClick={() => setRaceDropdown(!raceDropdown)}
                className="text-pitwall-gray hover:text-white transition-colors font-medium flex items-center space-x-1"
              >
                <span>Races</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              {raceDropdown && (
                <div className="absolute top-full mt-2 w-64 bg-pitwall-surface border border-pitwall-border rounded-lg shadow-xl py-2 max-h-80 overflow-y-auto">
                  {RACES_2025.map((race) => (
                    <button
                      key={race.round}
                      onClick={() => {
                        navigate(`/race/2025/${race.round}`);
                        setRaceDropdown(false);
                      }}
                      className="w-full text-left px-4 py-2 hover:bg-pitwall-card text-sm flex items-center space-x-2"
                    >
                      <span className="text-xs font-mono text-pitwall-gray w-8">{race.flag}</span>
                      <span>R{race.round} - {race.name}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>

            <Link to="/drivers" className="text-pitwall-gray hover:text-white transition-colors font-medium">
              Drivers
            </Link>

            <div className="h-6 w-px bg-pitwall-border" />

            <span className="text-xs text-pitwall-gray font-mono bg-pitwall-surface px-3 py-1 rounded-full">
              2025 SEASON
            </span>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden text-pitwall-gray hover:text-white"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {isOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {isOpen && (
        <div className="md:hidden border-t border-pitwall-border">
          <div className="px-4 py-3 space-y-2">
            <Link to="/" className="block text-pitwall-gray hover:text-white py-2" onClick={() => setIsOpen(false)}>Home</Link>
            <Link to="/race/2025/1" className="block text-pitwall-gray hover:text-white py-2" onClick={() => setIsOpen(false)}>Australian GP</Link>
            <Link to="/drivers" className="block text-pitwall-gray hover:text-white py-2" onClick={() => setIsOpen(false)}>Drivers</Link>
          </div>
        </div>
      )}
    </nav>
  );
}
'''

write('frontend/src/components/Navbar.jsx', navbar)
print('Navbar created successfully')
