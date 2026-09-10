'use client';

import { useState } from 'react';
import Link from 'next/link';
import { CheckCircle2, Circle, ArrowRight, Beaker, RefreshCw } from 'lucide-react';

export default function CompliancePage() {
  const [steps, setSteps] = useState([
    { id: 1, title: 'Product Selection', completed: true },
    { id: 2, title: 'Standard Identified (IS 2347)', completed: true },
    { id: 3, title: 'Requirements Mapping', completed: true },
    { id: 4, title: 'Testing Protocols', completed: false, current: true },
    { id: 5, title: 'Document Verification', completed: false },
    { id: 6, title: 'Certification Audit', completed: false },
    { id: 7, title: 'Compliance Granted', completed: false },
  ]);

  const toggleStep = (id) => {
    setSteps(prev =>
      prev.map(step =>
        step.id === id ? { ...step, completed: !step.completed } : step
      )
    );
  };

  const completedCount = steps.filter(s => s.completed).length;
  const progressPercent = Math.round((completedCount / steps.length) * 100);

  return (
    <div className="min-h-screen bg-[#F4EBDD] text-[#3B2A20] p-6 md:p-10 font-sans">
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* Main Compliance Card */}
        <div className="bg-[#FFF9F1] border border-[#E1D1BC] rounded-3xl p-6 md:p-8 shadow-xs space-y-6">
          
          {/* Header & Progress Stats */}
          <div className="flex items-start justify-between border-b border-[#E3D5C3] pb-6">
            <div>
              <span className="text-[10px] uppercase font-bold text-[#806044] tracking-wider">
                Active Compliance Plan
              </span>
              <h1 className="text-3xl font-black text-[#3A261C] mt-1">PRESSURE COOKER</h1>
              <p className="text-xs text-[#705543] font-medium mt-0.5">Standard: IS 2347</p>
            </div>
            <div className="text-right">
              <span className="text-3xl font-black text-[#5A3D2E]">{progressPercent}%</span>
              <p className="text-xs text-[#806044]">Overall Completion</p>
            </div>
          </div>

          {/* Dynamic Progress Bar */}
          <div className="w-full bg-[#EADBC8] h-3.5 rounded-full overflow-hidden p-0.5">
            <div 
              className="bg-[#5A3D2E] h-full rounded-full transition-all duration-300"
              style={{ width: `${progressPercent}%` }}
            />
          </div>

          {/* Interactive Checklist Steps Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 pt-2">
            {steps.map((step) => (
              <button
                key={step.id}
                onClick={() => toggleStep(step.id)}
                className={`p-4 rounded-2xl border text-left flex items-center gap-3 transition group ${
                  step.completed 
                    ? 'bg-[#F2E4D2] border-[#DCC5A8] text-[#3A261C]' 
                    : step.current 
                      ? 'bg-[#FFF9F1] border-[#5A3D2E] ring-2 ring-[#5A3D2E]/20' 
                      : 'bg-[#FBF5EC] border-[#E3D5C3] text-[#806044] hover:bg-[#F2E4D2]'
                }`}
              >
                {step.completed ? (
                  <CheckCircle2 className="w-5 h-5 text-[#5A3D2E] shrink-0" />
                ) : (
                  <Circle className="w-5 h-5 text-[#A58E77] shrink-0 group-hover:text-[#5A3D2E]" />
                )}
                <span className={`text-xs font-bold ${step.completed ? 'text-[#3A261C]' : 'text-[#6B5242]'}`}>
                  {step.title}
                </span>
              </button>
            ))}
          </div>

          {/* Next Action Action Bar */}
          <div className="bg-[#5A3D2E] text-[#FFF8EE] rounded-2xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-xs">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-[#704C38] rounded-xl text-[#D6B98C]">
                <Beaker className="w-5 h-5" />
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-[#D6B98C] tracking-wider block">
                  Next Recommended Action
                </span>
                <p className="text-xs text-[#EADBC8] font-medium mt-0.5">
                  Review testing requirements for safety valve pressure testing.
                </p>
              </div>
            </div>

            <Link
              href="/documents"
              className="bg-[#D6B98C] hover:bg-[#C9AA7B] text-[#3A261C] px-5 py-2.5 rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 shrink-0 shadow-xs"
            >
              <span>Start Review</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

        </div>
      </div>
    </div>
  );
}