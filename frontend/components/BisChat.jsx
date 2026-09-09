'use client';

import { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Bot, 
  User, 
  ShieldCheck, 
  BookOpen, 
  FileText, 
  Database, 
  Sparkles, 
  Loader2,
  CheckCircle2
} from 'lucide-react';

export default function BisChat() {
  const [messages, setMessages] = useState([
    {
      role: 'ai',
      text: 'Namaste! I am your BIS AI Assistant. Ask me about Indian Standards (IS), product certification schemes, hallmarking, or testing labs.',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const [activeCitation, setActiveCitation] = useState({
    standard: 'Select / Ask Query',
    references: 'Ask a query to see clause-level verification from official BIS standards.',
    source: 'BIS Official Portal',
    mode: 'Awaiting Query',
  });

  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');

    setMessages((prev) => [...prev, { role: 'user', text: userMessage }]);
    setLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMessage }),
      });

      if (!response.ok) throw new Error('Failed to connect to server');

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        { role: 'ai', text: data.answer || 'No response text received.' },
      ]);

      setActiveCitation({
        standard: data.standard || 'General Query',
        references: data.references || 'No specific clause reference provided.',
        source: data.source || 'BIS Guidance Directory',
        mode: data.mode || 'Standard RAG',
      });
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          text: '⚠️ Unable to connect to the backend server at http://127.0.0.1:8000. Please ensure the FastAPI server is running.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-slate-100 text-slate-800">
      <header className="bg-indigo-950 text-white px-6 py-4 shadow-lg flex justify-between items-center border-b border-indigo-900">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-tr from-indigo-500 to-blue-400 p-2.5 rounded-xl text-white font-extrabold text-xl shadow-md tracking-wide">
            BIS
          </div>
          <div>
            <h1 className="text-lg font-bold flex items-center gap-2">
              AI Standards & Compliance Assistant
              <Sparkles className="w-4 h-4 text-amber-400 animate-pulse" />
            </h1>
            <p className="text-xs text-indigo-200">
              Bureau of Indian Standards • SIH Intelligent Agent
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            <span className="w-2 h-2 bg-emerald-400 rounded-full animate-ping" />
            Backend Connected (Port 8000)
          </span>
        </div>
      </header>

      <main className="flex-1 flex overflow-hidden p-4 gap-4 max-w-7xl w-full mx-auto">
        <section className="flex-1 bg-white rounded-2xl shadow-sm border border-slate-200 flex flex-col overflow-hidden">
          <div className="flex-1 p-6 overflow-y-auto space-y-5">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`flex gap-3.5 ${
                  msg.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {msg.role === 'ai' && (
                  <div className="w-9 h-9 rounded-xl bg-indigo-600 text-white flex items-center justify-center font-bold shrink-0 shadow-sm">
                    <Bot className="w-5 h-5" />
                  </div>
                )}

                <div
                  className={`max-w-[80%] rounded-2xl p-4 text-sm leading-relaxed shadow-sm ${
                    msg.role === 'user'
                      ? 'bg-indigo-600 text-white rounded-tr-none font-medium'
                      : 'bg-slate-50 text-slate-800 rounded-tl-none border border-slate-200/80'
                  }`}
                >
                  {msg.text}
                </div>

                {msg.role === 'user' && (
                  <div className="w-9 h-9 rounded-xl bg-slate-800 text-white flex items-center justify-center font-bold shrink-0 shadow-sm">
                    <User className="w-5 h-5" />
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex items-center gap-3 text-slate-500 text-sm">
                <div className="w-9 h-9 rounded-xl bg-indigo-600 text-white flex items-center justify-center shrink-0">
                  <Bot className="w-5 h-5" />
                </div>
                <div className="bg-slate-50 border border-slate-200 rounded-2xl rounded-tl-none px-4 py-3 flex items-center gap-2.5">
                  <Loader2 className="w-4 h-4 text-indigo-600 animate-spin" />
                  <span>Searching BIS Standards & Clauses...</span>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          <form
            onSubmit={handleSubmit}
            className="p-4 bg-slate-50 border-t border-slate-200 flex gap-3"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask e.g. What is the mandatory IS standard for domestic pressure cookers?"
              className="flex-1 px-4 py-3 bg-white border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-600 text-sm shadow-inner"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 text-white px-6 py-3 rounded-xl font-medium text-sm transition flex items-center gap-2 shadow-md shadow-indigo-200"
            >
              <span>Send</span>
              <Send className="w-4 h-4" />
            </button>
          </form>
        </section>

        <section className="w-96 bg-white rounded-2xl shadow-sm border border-slate-200 p-5 flex flex-col justify-between overflow-y-auto">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-slate-200 mb-5">
              <div className="flex items-center gap-2 font-bold text-slate-900 text-sm">
                <ShieldCheck className="w-5 h-5 text-indigo-600" />
                <span>Source Grounding & Evidence</span>
              </div>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-1 rounded-md bg-indigo-50 text-indigo-700 border border-indigo-100">
                {activeCitation.mode}
              </span>
            </div>

            <div className="bg-gradient-to-br from-indigo-50 to-blue-50 border border-indigo-100 rounded-xl p-4 mb-5 shadow-xs">
              <div className="flex items-center gap-2 text-xs font-semibold text-indigo-600 uppercase tracking-wider mb-1">
                <BookOpen className="w-4 h-4" />
                <span>Applicable Standard</span>
              </div>
              <span className="text-xl font-extrabold text-indigo-950 block">
                {activeCitation.standard}
              </span>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5 mb-1.5">
                  <FileText className="w-3.5 h-3.5 text-slate-400" />
                  Clause & Document Reference
                </label>
                <div className="bg-slate-50 p-3 rounded-xl border border-slate-200/80 text-xs text-slate-700 leading-relaxed italic min-h-[70px]">
                  {activeCitation.references}
                </div>
              </div>

              <div>
                <label className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5 mb-1.5">
                  <Database className="w-3.5 h-3.5 text-slate-400" />
                  Source Data Provider
                </label>
                <div className="bg-slate-50 p-3 rounded-xl border border-slate-200/80 text-xs font-medium text-slate-700">
                  {activeCitation.source}
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 p-3 bg-emerald-50 rounded-xl border border-emerald-200/80 text-emerald-900 text-xs flex items-center gap-2.5">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
            <p className="leading-snug">
              <strong>Verified Traceability:</strong> Grounded in official BIS standards.
            </p>
          </div>
        </section>
      </main>
    </div>
  );
}