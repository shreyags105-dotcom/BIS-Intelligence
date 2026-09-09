'use client';

import { useState } from 'react';
import { Search, Filter, BookOpen, ExternalLink, ShieldCheck, Tag } from 'lucide-react';

export default function StandardsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');

  const categories = ['All', 'Electronics & IT', 'Steel & Metals', 'Food & Agriculture', 'Chemicals'];

  const standardsData = [
    {
      code: 'IS 2347 : 2017',
      title: 'Domestic Pressure Cookers — Specification',
      category: 'Electronics & IT',
      status: 'Mandatory ISI',
      scope: 'Covers safety, material quality, burst pressure limits, and release valve requirements.',
    },
    {
      code: 'IS 1786 : 2008',
      title: 'High Strength Deformed Steel Bars and Wires for Concrete Reinforcement',
      category: 'Steel & Metals',
      status: 'Mandatory ISI',
      scope: 'Specifies physical properties, chemical composition, and mechanical testing protocols for Fe 500D bars.',
    },
    {
      code: 'IS 14543 : 2024',
      title: 'Packaged Drinking Water (Other than Packaged Natural Mineral Water)',
      category: 'Food & Agriculture',
      status: 'Mandatory ISI',
      scope: 'Defines microbiological standards, heavy metal limits, and mandatory packaging hygiene criteria.',
    },
    {
      code: 'IS 13252 (Part 1) : 2010',
      title: 'Information Technology Equipment — Safety (General Requirements)',
      category: 'Electronics & IT',
      status: 'CRS Scheme',
      scope: 'Mandatory registration scheme requirements for adapters, power supplies, and consumer electronics.',
    },
  ];

  const filteredStandards = standardsData.filter((item) => {
    const matchesQuery = item.code.toLowerCase().includes(searchQuery.toLowerCase()) || 
                         item.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'All' || item.category === selectedCategory;
    return matchesQuery && matchesCategory;
  });

  return (
    <div className="min-h-screen bg-[#F4EBDD] text-[#3B2A20] p-6 md:p-10 font-sans">
      <div className="max-w-5xl mx-auto space-y-6">
        
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-black text-[#3A261C]">Standards Search Index</h1>
          <p className="text-sm text-[#705543] mt-1">
            Search active Bureau of Indian Standards (IS), mandatory certification schemes, and testing scopes.
          </p>
        </div>

        {/* Search Bar & Filter Bar */}
        <div className="bg-[#FFF9F1] p-4 rounded-2xl border border-[#E1D1BC] shadow-xs space-y-3">
          <div className="relative">
            <Search className="w-5 h-5 absolute left-3.5 top-3.5 text-[#8A6447]" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by Standard Number (e.g., IS 2347) or Keyword (e.g., Steel)..."
              className="w-full bg-[#FBF5EC] border border-[#E3D5C3] rounded-xl pl-11 pr-4 py-3 text-xs font-semibold text-[#3A261C] placeholder-[#9A816E] focus:outline-none focus:ring-1 focus:ring-[#8A6447]"
            />
          </div>

          {/* Category Filter Tags */}
          <div className="flex flex-wrap items-center gap-2 pt-1">
            <Filter className="w-3.5 h-3.5 text-[#8A6447] mr-1" />
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                  selectedCategory === cat
                    ? 'bg-[#5A3D2E] text-[#FFF8EE]'
                    : 'bg-[#F2E4D2] text-[#6B5242] hover:bg-[#EADBC8]'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Results List */}
        <div className="space-y-4">
          {filteredStandards.map((item, idx) => (
            <div
              key={idx}
              className="bg-[#FFF9F1] rounded-2xl p-6 border border-[#E1D1BC] shadow-xs hover:border-[#A18063] transition space-y-3"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#E3D5C3] pb-3">
                <div className="flex items-center gap-2.5">
                  <BookOpen className="w-5 h-5 text-[#8A6447]" />
                  <span className="font-black text-base text-[#3A261C]">{item.code}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="bg-[#F2E4D2] text-[#5A3D2E] text-[11px] font-bold px-2.5 py-1 rounded-md flex items-center gap-1">
                    <Tag className="w-3 h-3" />
                    {item.category}
                  </span>
                  <span className="bg-[#D6B98C] text-[#3A261C] text-[11px] font-bold px-2.5 py-1 rounded-md flex items-center gap-1">
                    <ShieldCheck className="w-3 h-3" />
                    {item.status}
                  </span>
                </div>
              </div>

              <h3 className="font-bold text-sm text-[#3A261C]">{item.title}</h3>
              <p className="text-xs text-[#705543] leading-relaxed">{item.scope}</p>

              <div className="pt-2 flex justify-end">
                <button className="text-xs font-bold text-[#8A6447] hover:text-[#3A261C] flex items-center gap-1 transition">
                  <span>View Technical Clause Details</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}

          {filteredStandards.length === 0 && (
            <div className="text-center p-8 text-[#806044] text-xs font-medium bg-[#FFF9F1] rounded-2xl border border-[#E1D1BC]">
              No standard found matching your query.
            </div>
          )}
        </div>

      </div>
    </div>
  );
}