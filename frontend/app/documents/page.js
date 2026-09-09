'use client';

import { useState } from 'react';
import { UploadCloud, FileCheck, AlertCircle, ArrowRight } from 'lucide-react';

export default function DocumentsPage() {
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzed, setAnalyzed] = useState(false);

  const handleUpload = () => {
    setAnalyzing(true);
    setTimeout(() => {
      setAnalyzing(false);
      setAnalyzed(true);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-[#F4EBDD] p-6 md:p-10 text-[#3B2A20]">
      <div className="max-w-4xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-black text-[#3A261C]">Document Analysis</h1>
          <p className="text-sm text-[#705543] mt-1">
            Upload factory test reports, ISI license applications, or lab test sheets for AI verification.
          </p>
        </div>

        {/* Dropzone Box */}
        <div className="bg-[#FFF9F1] border-2 border-dashed border-[#CBB396] rounded-3xl p-8 text-center space-y-4">
          <div className="w-14 h-14 bg-[#EADBC8] text-[#5A3D2E] rounded-2xl flex items-center justify-center mx-auto">
            <UploadCloud className="w-7 h-7" />
          </div>
          <div>
            <h3 className="font-bold text-base text-[#3A261C]">Drag and drop your compliance PDF</h3>
            <p className="text-xs text-[#806044] mt-1">Supports IS Audit Certificates, Test Sheets, and Specification Reports</p>
          </div>
          <button
            onClick={handleUpload}
            disabled={analyzing}
            className="bg-[#5A3D2E] hover:bg-[#704C38] text-[#FFF8EE] px-6 py-2.5 rounded-xl font-bold text-xs transition shadow-sm"
          >
            {analyzing ? 'Extracting Compliance Data...' : 'Select File to Analyze'}
          </button>
        </div>

        {/* Extraction Preview */}
        {analyzed && (
          <div className="bg-[#FFF9F1] rounded-3xl p-6 border border-[#E1D1BC] shadow-sm space-y-4">
            <div className="flex items-center gap-2 border-b border-[#E3D5C3] pb-3 text-emerald-800">
              <FileCheck className="w-5 h-5" />
              <h3 className="font-bold text-sm">Document Verification Complete</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="p-3 bg-[#FBF5EC] rounded-xl border border-[#E3D5C3]">
                <span className="text-[#806044] block font-semibold">Matched Standard</span>
                <span className="font-black text-[#3A261C] text-sm">IS 2347 : 2017</span>
              </div>
              <div className="p-3 bg-[#FBF5EC] rounded-xl border border-[#E3D5C3]">
                <span className="text-[#806044] block font-semibold">Verification Result</span>
                <span className="font-black text-emerald-700 text-sm">Safety Pressure Valve Passed</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}