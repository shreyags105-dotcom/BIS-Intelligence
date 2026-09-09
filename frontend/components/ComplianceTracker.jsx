'use client';

import { useState } from 'react';
import { 
  CheckCircle2, 
  Circle, 
  ArrowRight, 
  FlaskConical 
} from 'lucide-react';

export default function ComplianceTracker() {
  const [product] = useState({
    name: 'PRESSURE COOKER',
    standard: 'IS 2347',
    progress: 65,
    nextAction: 'Review testing requirements for safety valve pressure testing.',
  });

  const steps = [
    { title: 'Product Selection', completed: true },
    { title: 'Standard Identified (IS 2347)', completed: true },
    { title: 'Requirements Mapping', completed: true },
    { title: 'Testing Protocols', completed: false, current: true },
    { title: 'Document Verification', completed: false },
    { title: 'Certification Audit', completed: false },
    { title: 'Compliance Granted', completed: false },
  ];

  return (
    <div className="max-w-4xl mx-auto p-6 bg-[#FFF9F1] rounded-3xl border border-[#E1D1BC] shadow-sm space-y-6">
      <div className="flex justify-between items-start border-b border-[#E3D5C3] pb-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-[#8A6447]">
            Active Compliance Plan
          </span>
          <h2 className="text-2xl font-black text-[#3A261C] mt-1">{product.name}</h2>
          <p className="text-sm font-semibold text-[#705543]">Standard: {product.standard}</p>
        </div>
        <div className="text-right">
          <span className="text-2xl font-black text-[#5A3D2E]">{product.progress}%</span>
          <p className="text-xs text-[#806044]">Overall Completion</p>
        </div>
      </div>

      <div className="space-y-2">
        <div className="w-full bg-[#EADBC8] h-4 rounded-full overflow-hidden border border-[#D5BEA3]">
          <div 
            className="bg-[#5A3D2E] h-full transition-all duration-500 rounded-full"
            style={{ width: `${product.progress}%` }}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
        {steps.map((step, idx) => (
          <div 
            key={idx}
            className={`flex items-center gap-3 p-3.5 rounded-xl border transition ${
              step.completed 
                ? 'bg-[#F2E4D2] border-[#DCC5A8] text-[#3A261C]' 
                : step.current 
                ? 'bg-[#FFFDF9] border-[#9A7652] ring-1 ring-[#9A7652]' 
                : 'bg-[#FBF5EC] border-[#E3D5C3] text-[#8C7565]'
            }`}
          >
            {step.completed ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-700 shrink-0" />
            ) : (
              <Circle className="w-5 h-5 text-[#A18A75] shrink-0" />
            )}
            <span className="text-xs font-bold">{step.title}</span>
          </div>
        ))}
      </div>

      <div className="p-4 bg-[#5A3D2E] text-[#FFF8EE] rounded-2xl flex items-center justify-between gap-4 shadow-md">
        <div className="flex items-center gap-3">
          <FlaskConical className="w-6 h-6 text-[#D6B98C] shrink-0" />
          <div>
            <span className="text-[10px] uppercase font-bold tracking-wider text-[#D6B98C]">
              Next Recommended Action
            </span>
            <p className="text-xs font-medium text-[#F7E9D4]">{product.nextAction}</p>
          </div>
        </div>
        <button className="bg-[#D6B98C] hover:bg-[#EADBC8] text-[#3A261C] px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-1.5 shrink-0">
          <span>Start Review</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}