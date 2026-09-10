'use client';

import { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  RotateCcw, 
  Copy, 
  Download, 
  ExternalLink, 
  CheckCircle2, 
  BookOpen, 
  FileText, 
  Database,
  Bot,
  User,
  Loader2
} from 'lucide-react';

export default function ChatPage() {
  const [inputMessage, setInputMessage] = useState('');
  const [messages, setMessages] = useState([
    {
      sender: 'ai',
      text: 'Namaste! I am your BIS AI Assistant. Ask me anything about Indian Standards (IS), product certification schemes, hallmarking regulations, or testing compliance.'
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeMetadata, setActiveMetadata] = useState({
    standard: 'Select / Ask Query',
    clause: 'Ask a query to view clause-level citation metadata and official BIS standard references.',
    authority: 'BIS Official Registry'
  });

  const messagesEndRef = useRef(null);

  // Get backend base URL from env variable with a local fallback
  const API_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userQuery = inputMessage.trim();
    
    // 1. Append user message locally & set loading state
    setMessages(prev => [...prev, { sender: 'user', text: userQuery }]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // 2. Request to FastAPI Backend
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: userQuery }),
      });

      if (!response.ok) {
        throw new Error(`Server returned status ${response.status}`);
      }

      const data = await response.json();
      console.log('FastAPI Raw Response Payload:', data);

      // 3. Robust key extraction (handles strings, dicts, or nested objects)
      let aiText = '';
      if (typeof data === 'string') {
        aiText = data;
      } else if (data && typeof data === 'object') {
        aiText = 
          data.response || 
          data.answer || 
          data.message || 
          data.text || 
          data.result || 
          data.bot_response ||
          (data.data && data.data.text) ||
          JSON.stringify(data);
      }

      // Update active citation sidebar metadata if provided by RAG response
      if (data.standard || data.primary_standard) {
        setActiveMetadata({
          standard: data.standard || data.primary_standard,
          clause: data.clause || data.clause_reference || 'Clause parameters verified against official registry.',
          authority: data.authority || 'BIS Official Registry'
        });
      }

      setMessages(prev => [
        ...prev, 
        { 
          sender: 'ai', 
          text: aiText || 'No response text returned from server.',
          sources: data.sources || data.references || [] 
        }
      ]);
    } catch (error) {
      console.warn('Backend unavailable, falling back to local handler:', error);
      
      // Fallback response if FastAPI server is offline during frontend testing
      setTimeout(() => {
        setMessages(prev => [
          ...prev, 
          { 
            sender: 'ai', 
            text: `(Offline Simulation) Processed response for query: "${userQuery}".\n\nFor verified standards compliance (e.g., IS 14543 or IS 1786), please ensure your Uvicorn FastAPI server is running on port 8000.`,
            sources: ['IS Standard Documentation']
          }
        ]);
        setIsLoading(false);
      }, 800);
      return;
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setMessages([
      {
        sender: 'ai',
        text: 'Namaste! I am your BIS AI Assistant. Ask me anything about Indian Standards (IS), product certification schemes, hallmarking regulations, or testing compliance.'
      }
    ]);
    setActiveMetadata({
      standard: 'Select / Ask Query',
      clause: 'Ask a query to view clause-level citation metadata and official BIS standard references.',
      authority: 'BIS Official Registry'
    });
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-80px)] bg-[#F4EBDD] text-[#3B2A20] p-4 md:p-6 font-sans">
      
      {/* Header Bar */}
      <div className="flex items-center justify-between pb-4 border-b border-[#E3D5C3] mb-4">
        <div>
          <h1 className="text-xl md:text-2xl font-black text-[#3A261C]">
            Ask Anything About BIS Standards, Certification & Compliance
          </h1>
          <p className="text-xs text-[#705543] font-medium mt-0.5">
            Bureau of Indian Standards Intelligent Verification System
          </p>
        </div>
        <button
          onClick={handleReset}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[#E3D5C3] bg-[#FFF9F1] hover:bg-[#F2E4D2] text-xs font-bold text-[#5A3D2E] transition"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset</span>
        </button>
      </div>

      {/* Main Content Layout */}
      <div className="flex flex-1 gap-6 overflow-hidden min-h-0">
        
        {/* Middle Panel - Main Chat Window */}
        <div className="flex-1 min-w-0 bg-[#FFF9F1] rounded-3xl border border-[#E1D1BC] flex flex-col h-full shadow-xs">
          
          {/* Messages Scroll Area */}
          <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4">
            {messages.map((msg, idx) => (
              <div 
                key={idx} 
                className={`flex gap-3 max-w-[85%] ${msg.sender === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
              >
                {/* Avatar Icon */}
                <div className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${
                  msg.sender === 'user' ? 'bg-[#A8886A] text-[#FFF9F1]' : 'bg-[#5A3D2E] text-[#FFF9F1]'
                }`}>
                  {msg.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </div>

                {/* Message Bubble */}
                <div className="space-y-2">
                  <div className={`p-4 rounded-2xl text-xs md:text-sm leading-relaxed whitespace-pre-wrap ${
                    msg.sender === 'user' 
                      ? 'bg-[#A8886A] text-[#FFF9F1] rounded-tr-none' 
                      : 'bg-[#F2E4D2] text-[#3A261C] rounded-tl-none border border-[#E3D5C3]'
                  }`}>
                    {msg.text}
                  </div>

                  {/* Actions Bar for AI Messages */}
                  {msg.sender === 'ai' && idx !== 0 && (
                    <div className="flex items-center gap-2 pt-1">
                      <button 
                        onClick={() => copyToClipboard(msg.text)}
                        className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[#EADBC8] hover:bg-[#DCC5A8] text-[10px] font-bold text-[#5A3D2E] transition"
                      >
                        <Copy className="w-3 h-3" />
                        <span>Copy Answer</span>
                      </button>
                      <button 
                        className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[#EADBC8] hover:bg-[#DCC5A8] text-[10px] font-bold text-[#5A3D2E] transition"
                      >
                        <Download className="w-3 h-3" />
                        <span>Download PDF</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* Loading Indicator */}
            {isLoading && (
              <div className="flex gap-3 max-w-[85%]">
                <div className="w-8 h-8 rounded-xl bg-[#5A3D2E] text-[#FFF9F1] flex items-center justify-center shrink-0">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="p-4 rounded-2xl bg-[#F2E4D2] text-[#3A261C] rounded-tl-none border border-[#E3D5C3] text-xs font-medium flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin text-[#5A3D2E]" />
                  <span>Fetching verified response from BIS records...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Chat Input Box */}
          <form onSubmit={handleSendMessage} className="p-4 border-t border-[#E3D5C3] bg-[#FFF9F1] rounded-b-3xl">
            <div className="flex items-center gap-2 bg-[#FBF5EC] border border-[#E3D5C3] rounded-2xl p-2 focus-within:ring-2 focus-within:ring-[#5A3D2E]/20">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask anything about BIS standards, certification, or compliance..."
                className="flex-1 bg-transparent px-3 py-1 text-xs md:text-sm text-[#3A261C] focus:outline-hidden placeholder-[#A58E77]"
              />
              <button
                type="submit"
                disabled={!inputMessage.trim() || isLoading}
                className="bg-[#A8886A] hover:bg-[#5A3D2E] disabled:opacity-50 text-[#FFF9F1] px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-1.5 shrink-0"
              >
                <span>Send</span>
                <Send className="w-3.5 h-3.5" />
              </button>
            </div>
          </form>

        </div>

        {/* Right Sidebar - Sources & References Panel (Fixed Width) */}
        <div className="w-80 shrink-0 hidden lg:flex flex-col gap-4">
          <div className="bg-[#FFF9F1] border border-[#E1D1BC] rounded-3xl p-5 flex-1 space-y-5 shadow-xs overflow-y-auto">
            
            <div className="flex items-center justify-between border-b border-[#E3D5C3] pb-3">
              <div className="flex items-center gap-2 text-[#5A3D2E]">
                <CheckCircle2 className="w-4 h-4" />
                <span className="text-xs font-bold uppercase tracking-wider">Sources & References</span>
              </div>
              <span className="text-[10px] bg-[#EADBC8] text-[#5A3D2E] px-2 py-0.5 rounded-full font-bold">
                CONSUMER
              </span>
            </div>

            {/* Primary Standard Box */}
            <div className="bg-[#F2E4D2] border border-[#E3D5C3] rounded-2xl p-4 space-y-1">
              <div className="flex items-center gap-1.5 text-[10px] font-bold text-[#806044] uppercase tracking-wider">
                <BookOpen className="w-3.5 h-3.5" />
                <span>Primary Standard</span>
              </div>
              <p className="text-lg font-black text-[#3A261C]">
                {activeMetadata.standard}
              </p>
            </div>

            {/* Clause Reference Box */}
            <div className="bg-[#FBF5EC] border border-[#E3D5C3] rounded-2xl p-4 space-y-1">
              <div className="flex items-center gap-1.5 text-[10px] font-bold text-[#806044] uppercase tracking-wider">
                <FileText className="w-3.5 h-3.5" />
                <span>Clause Reference</span>
              </div>
              <p className="text-xs text-[#6B5242] leading-relaxed break-words">
                {activeMetadata.clause}
              </p>
            </div>

            {/* Authority Provider Box */}
            <div className="bg-[#FBF5EC] border border-[#E3D5C3] rounded-2xl p-4 space-y-1">
              <div className="flex items-center gap-1.5 text-[10px] font-bold text-[#806044] uppercase tracking-wider">
                <Database className="w-3.5 h-3.5" />
                <span>Authority Provider</span>
              </div>
              <div className="flex items-center justify-between pt-1">
                <span className="text-xs font-bold text-[#3A261C]">{activeMetadata.authority}</span>
                <a 
                  href="https://www.manakonline.in" 
                  target="_blank" 
                  rel="noreferrer"
                  className="text-[#806044] hover:text-[#5A3D2E]"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>
            </div>

          </div>

          {/* Audit Trace Note Footer */}
          <div className="bg-[#F2E4D2] border border-[#E3D5C3] rounded-2xl p-4 flex items-start gap-3">
            <CheckCircle2 className="w-4 h-4 text-[#5A3D2E] shrink-0 mt-0.5" />
            <div className="text-[11px] leading-tight text-[#6B5242]">
              <strong className="text-[#3A261C] block mb-0.5">Official Audit Trace:</strong>
              Grounded responses mapped directly to Indian Standard documentation.
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}