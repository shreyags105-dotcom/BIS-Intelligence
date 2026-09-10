'use client';

import { useState, useRef } from 'react';
import { UploadCloud, CheckCircle2, FileText, AlertCircle, Loader2 } from 'lucide-react';

export default function DocumentAnalysisPage() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [hasResults, setHasResults] = useState(false);
  const [fileName, setFileName] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setFileName(file.name);
      startAnalysis(file);
    }
  };

  const startAnalysis = async (file) => {
    setIsAnalyzing(true);
    setHasResults(false);
    setAnalysisResult(null);
    setError('');
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await fetch(`${API_URL}/documents/analyze`, { method: 'POST', body: formData });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail || 'Document analysis failed');
      setAnalysisResult(result);
      setHasResults(true);
    } catch (analysisError) {
      setError(analysisError.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F4EBDD] text-[#3B2A20] p-6 md:p-10 font-sans">
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-black text-[#3A261C]">Document Analysis</h1>
          <p className="text-sm text-[#705543] mt-1 font-medium">
            Upload factory test reports, ISI license applications, or lab test sheets for AI verification.
          </p>
        </div>

        {/* Upload Box Dropzone */}
        <div className="border-2 border-dashed border-[#CBB8A1] bg-[#FFF9F1] rounded-3xl p-10 text-center space-y-4 shadow-sm">
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileChange} 
            accept=".pdf,.xls,.xlsx,.doc,.docx" 
            className="hidden" 
          />

          <div className="w-16 h-16 bg-[#EADBC8] text-[#5A3D2E] rounded-2xl flex items-center justify-center mx-auto shadow-xs">
            {isAnalyzing ? (
              <Loader2 className="w-8 h-8 animate-spin" />
            ) : (
              <UploadCloud className="w-8 h-8" />
            )}
          </div>

          <div>
            <h3 className="font-bold text-lg text-[#3A261C]">
              {isAnalyzing 
                ? 'Extracting Compliance Data...' 
                : 'Upload a compliance document'}
            </h3>
            <p className="text-xs text-[#806044] mt-1">
              Supports PDF, Excel, and Word files
            </p>
          </div>

          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isAnalyzing}
            className="bg-[#5A3D2E] hover:bg-[#704C38] text-[#FFF8EE] font-bold text-sm px-6 py-3 rounded-xl transition shadow-xs disabled:opacity-50"
          >
            {isAnalyzing ? 'Analyzing...' : 'Select File to Analyze'}
          </button>
        </div>

        {error && <div className="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800"><AlertCircle className="h-4 w-4" />{error}</div>}

        {/* Dynamic Analysis Results Card */}
        {hasResults && (
          <div className="bg-[#FFF9F1] border border-[#E1D1BC] rounded-3xl p-6 space-y-6 shadow-sm animate-fade-in">
            <div className="flex items-center justify-between border-b border-[#E3D5C3] pb-4">
              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-emerald-100 text-emerald-800 rounded-xl">
                  <CheckCircle2 className="w-6 h-6" />
                </div>
                <div>
                  <h4 className="font-bold text-base text-[#3A261C]">Document Verification Complete</h4>
                  <p className="text-xs text-[#705543]">{analysisResult?.filename || fileName}</p>
                </div>
              </div>
              <span className="bg-emerald-100 text-emerald-800 font-bold text-xs px-3 py-1 rounded-full border border-emerald-300">
                PASSED
              </span>
            </div>

            {/* Extracted Details Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-[#F2E4D2] border border-[#DCC5A8] rounded-2xl">
                <span className="text-[10px] uppercase font-bold text-[#806044] tracking-wider block">
                  Matched Standard
                </span>
                <span className="font-black text-base text-[#3A261C] block mt-1">
                  {analysisResult?.matched_standard || 'Not identified'}
                </span>
                <p className="text-xs text-[#6B5242] mt-0.5">Domestic Pressure Cookers — Specifications</p>
              </div>

              <div className="p-4 bg-[#F2E4D2] border border-[#DCC5A8] rounded-2xl">
                <span className="text-[10px] uppercase font-bold text-[#806044] tracking-wider block">
                  Safety Valve Pressure Test
                </span>
                <span className="font-black text-base text-[#3A261C] block mt-1">
                  {analysisResult?.issues?.length ? `${analysisResult.issues.length} issue(s) identified` : 'No issues identified'}
                </span>
                <p className="text-xs text-[#6B5242] mt-0.5">{analysisResult?.results}</p>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}