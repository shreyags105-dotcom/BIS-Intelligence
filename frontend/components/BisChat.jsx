'use client';

import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

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
  RotateCcw,
  Terminal,
  WifiOff,
} from 'lucide-react';

const SAMPLE_QUERIES = [
  'What is IS 1786 for steel reinforcement bars?',
  'Gold Hallmarking Regulations',
  'IS 14543 Drinking Water Standards',
];

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

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
    references:
      'Ask a query to see clause-level verification from official BIS standards.',
    source: 'BIS Official Portal',
    mode: 'Awaiting Query',
  });

  const [isOffline, setIsOffline] = useState(false);

  const chatEndRef = useRef(null);

  /* =========================
     ONLINE / OFFLINE STATUS
  ========================= */

  useEffect(() => {
    const handleOnline = () => {
      setIsOffline(false);
    };

    const handleOffline = () => {
      setIsOffline(true);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  /* =========================
     AUTO SCROLL
  ========================= */

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({
      behavior: 'smooth',
    });
  }, [messages, loading]);

  /* =========================
     CLEAR CHAT
  ========================= */

  const handleClearChat = () => {
    setMessages([
      {
        role: 'ai',
        text: 'Namaste! I am your BIS AI Assistant. Ask me about Indian Standards (IS), product certification schemes, hallmarking, or testing labs.',
      },
    ]);

    setActiveCitation({
      standard: 'Select / Ask Query',
      references:
        'Ask a query to see clause-level verification from official BIS standards.',
      source: 'BIS Official Portal',
      mode: 'Awaiting Query',
    });
  };

  /* =========================
     SEND MESSAGE
  ========================= */

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!input.trim() || loading) {
      return;
    }

    const userMessage = input.trim();

    setInput('');

    setMessages((prev) => [
      ...prev,
      {
        role: 'user',
        text: userMessage,
      },
    ]);

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',

        headers: {
          'Content-Type': 'application/json',
        },

        body: JSON.stringify({
          question: userMessage,
          mode: 'consumer',
        }),
      });

      if (!response.ok) {
        throw new Error(
          `Backend returned ${response.status}`
        );
      }

      const chatResponse = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          text: chatResponse.answer,
        },
      ]);

      setActiveCitation({
        standard:
          chatResponse.standard || 'IS Standard',

        references:
          chatResponse.references ||
          'Standard guidelines',

        source:
          chatResponse.source ||
          'BIS Data',

        mode:
          chatResponse.mode ||
          'Live Query',
      });
    } catch (error) {
      console.error('Chat error:', error);

      setMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          text: 'I could not connect to the BIS backend. Please start the API server and try again.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  /* =========================
     UI
  ========================= */

  return (
    <div className="flex flex-col h-screen bg-[#F4EBDD] text-[#3B2A20] font-sans">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <header className="bg-[#3A261C] text-[#FFF8EE] px-6 py-4 shadow-lg flex justify-between items-center border-b border-[#8B6F55]">

        {/* LEFT SIDE */}

        <div className="flex items-center gap-4">

          {/* BIS LOGO */}

          <div className="w-12 h-12 bg-[#D6B98C] text-[#3A261C] rounded-2xl flex items-center justify-center font-black text-lg shadow-md tracking-wider">
            BIS
          </div>

          {/* TITLE */}

          <div>
            <h1 className="text-lg font-bold flex items-center gap-2">
              AI Standards & Compliance Assistant

              <Sparkles className="w-4 h-4 text-[#D6B98C]" />
            </h1>

            <p className="text-xs text-[#D6B98C] mt-0.5">
              Bureau of Indian Standards • Intelligence Assistant
            </p>
          </div>

        </div>

        {/* RIGHT SIDE */}

        <div className="flex items-center gap-3">

          {/* CLEAR CHAT */}

          <button
            type="button"
            onClick={handleClearChat}
            className="flex items-center gap-2 text-xs font-medium text-[#EADBC8] hover:text-white bg-[#51372A] hover:bg-[#634534] border border-[#755744] px-3 py-2 rounded-xl transition"
          >
            <RotateCcw className="w-3.5 h-3.5" />

            Clear Chat
          </button>

          {/* SYSTEM STATUS */}

          <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold bg-[#D6B98C]/15 text-[#E7CFA7] border border-[#D6B98C]/40">

            <span className="w-2 h-2 bg-[#D6B98C] rounded-full animate-pulse" />

            System Live

          </span>

        </div>

      </header>


      {/* =====================================================
          MAIN CONTAINER
      ===================================================== */}

      <main className="flex-1 flex overflow-hidden p-4 gap-4 max-w-7xl w-full mx-auto">

        {/* ===================================================
            CHAT SECTION
        =================================================== */}

        <section className="flex-1 bg-[#FFF9F1] rounded-3xl shadow-[0_8px_30px_rgba(80,50,30,0.10)] border border-[#E1D1BC] flex flex-col overflow-hidden">

          {/* OFFLINE BANNER */}

          {isOffline && (
            <div className="bg-[#F4DFC0] border-b border-[#C9A66B] text-[#79552F] px-4 py-2 text-xs flex items-center justify-center gap-2">

              <WifiOff className="w-4 h-4" />

              <span>
                Network connection lost. You are currently offline.
              </span>

            </div>
          )}


          {/* =================================================
              MESSAGE AREA
          ================================================= */}

          <div className="flex-1 p-6 overflow-y-auto space-y-6">

            {messages.map((msg, index) => (

              <div
                key={index}
                className={`flex gap-3.5 ${
                  msg.role === 'user'
                    ? 'justify-end'
                    : 'justify-start'
                }`}
              >

                {/* AI ICON */}

                {msg.role === 'ai' && (
                  <div className="w-10 h-10 rounded-2xl bg-[#5A3D2E] text-[#F7E9D4] flex items-center justify-center shrink-0 shadow-md">

                    <Bot className="w-5 h-5" />

                  </div>
                )}


                {/* MESSAGE BUBBLE */}

                <div
                  className={`max-w-[80%] rounded-2xl px-5 py-4 text-sm leading-relaxed shadow-sm ${
                    msg.role === 'user'
                      ? 'bg-[#C9A77A] text-[#332218] font-medium rounded-tr-sm'
                      : 'bg-[#F1E5D5] text-[#49352A] rounded-tl-sm border border-[#E2D1BA] prose prose-sm max-w-none'
                  }`}
                >

                  {msg.role === 'ai' ? (
                    <ReactMarkdown>
                      {msg.text}
                    </ReactMarkdown>
                  ) : (
                    msg.text
                  )}

                </div>


                {/* USER ICON */}

                {msg.role === 'user' && (
                  <div className="w-10 h-10 rounded-2xl bg-[#E7D7C2] text-[#5A3D2E] border border-[#D2BFA7] flex items-center justify-center shrink-0">

                    <User className="w-5 h-5" />

                  </div>
                )}

              </div>

            ))}


            {/* =================================================
                LOADING MESSAGE
            ================================================= */}

            {loading && (
              <div className="flex items-center gap-3">

                {/* AI ICON */}

                <div className="w-10 h-10 rounded-2xl bg-[#5A3D2E] text-[#F7E9D4] flex items-center justify-center shrink-0 shadow-md">

                  <Bot className="w-5 h-5" />

                </div>


                {/* LOADING BUBBLE */}

                <div className="bg-[#F1E5D5] border border-[#DCC8AE] rounded-2xl rounded-tl-sm px-5 py-3 flex items-center gap-2.5 text-[#70503B]">

                  <Loader2 className="w-4 h-4 animate-spin" />

                  <span className="text-xs">
                    Checking BIS standards database...
                  </span>

                </div>

              </div>
            )}

            {/* SCROLL TARGET */}

            <div ref={chatEndRef} />

          </div>


          {/* =================================================
              INPUT AREA
          ================================================= */}

          <div className="px-5 pt-4 pb-4 bg-[#F8EFE3] border-t border-[#E1D1BC]">

            {/* QUICK PROMPTS */}

            <div className="flex gap-2 overflow-x-auto pb-3">

              {SAMPLE_QUERIES.map((query, idx) => (

                <button
                  key={idx}
                  type="button"
                  onClick={() => setInput(query)}
                  className="text-xs bg-[#FFF9F1] text-[#654635] hover:bg-[#6A4936] hover:text-[#FFF8EE] border border-[#D5BEA3] px-4 py-2 rounded-full transition shrink-0 shadow-sm"
                >

                  {query}

                </button>

              ))}

            </div>


            {/* INPUT FORM */}

            <form
              onSubmit={handleSubmit}
              className="flex gap-3"
            >

              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about Indian Standards..."
                className="flex-1 px-5 py-3.5 bg-[#FFFDF9] border border-[#D8C5AD] rounded-2xl focus:outline-none focus:ring-2 focus:ring-[#B18A61]/30 focus:border-[#9A7652] text-sm text-[#3F2C21] placeholder-[#A18A75] shadow-inner"
              />

              {/* SEND BUTTON */}

              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="bg-[#5A3D2E] hover:bg-[#704C38] disabled:bg-[#D8CABB] disabled:text-[#9F9184] text-[#FFF8EE] px-6 py-3 rounded-2xl font-semibold text-sm transition flex items-center gap-2 shadow-md"
              >

                <span>
                  Send
                </span>

                <Send className="w-4 h-4" />

              </button>

            </form>

          </div>

        </section>


        {/* ===================================================
            SOURCE GROUNDING PANEL
        =================================================== */}

        <section className="w-96 bg-[#FFF9F1] rounded-3xl shadow-[0_8px_30px_rgba(80,50,30,0.10)] border border-[#E1D1BC] p-5 flex flex-col justify-between overflow-y-auto">

          <div>

            {/* PANEL HEADER */}

            <div className="flex items-center justify-between pb-4 border-b border-[#E3D5C3] mb-5">

              <div className="flex items-center gap-2 font-bold text-[#4A3427] text-sm">

                <ShieldCheck className="w-5 h-5 text-[#8A6447]" />

                <span>
                  Source Grounding
                </span>

              </div>


              {/* MODE */}

              <span className="text-[10px] uppercase font-bold tracking-wider px-2.5 py-1.5 rounded-lg bg-[#EADBC8] text-[#6C4B37] border border-[#D7C2A7]">

                {activeCitation.mode}

              </span>

            </div>


            {/* =================================================
                APPLICABLE STANDARD
            ================================================= */}

            <div className="bg-[#F2E4D2] border border-[#DCC5A8] rounded-2xl p-5 mb-5 shadow-sm">

              <div className="flex items-center gap-2 text-xs font-semibold text-[#806044] uppercase tracking-wider mb-2">

                <BookOpen className="w-4 h-4" />

                <span>
                  Applicable Standard
                </span>

              </div>


              <span className="text-2xl font-black text-[#432D21] block">

                {activeCitation.standard}

              </span>

            </div>


            {/* =================================================
                DETAILS
            ================================================= */}

            <div className="space-y-5">

              {/* CLAUSE & DOCUMENT */}

              <div>

                <label className="text-xs font-bold text-[#806F61] uppercase tracking-wider flex items-center gap-1.5 mb-2">

                  <FileText className="w-3.5 h-3.5" />

                  Clause & Document Reference

                </label>


                <div className="bg-[#FBF5EC] p-4 rounded-2xl border border-[#E3D5C3] text-xs text-[#665145] leading-relaxed min-h-[80px]">

                  {activeCitation.references}

                </div>

              </div>


              {/* SOURCE */}

              <div>

                <label className="text-xs font-bold text-[#806F61] uppercase tracking-wider flex items-center gap-1.5 mb-2">

                  <Database className="w-3.5 h-3.5" />

                  Source Data Provider

                </label>


                <div className="bg-[#FBF5EC] p-4 rounded-2xl border border-[#E3D5C3] text-xs font-medium text-[#665145]">

                  {activeCitation.source}

                </div>

              </div>

            </div>

          </div>


          <div className="mt-6 p-4 bg-[#EFE1CF] rounded-2xl border border-[#D8C0A0] text-[#654735] text-xs flex items-start gap-3">

            <Terminal className="w-5 h-5 text-[#805C40] shrink-0" />

            <p className="leading-relaxed">

              <strong>
                Verified Traceability:
              </strong>{' '}

              Direct clause mapping from official BIS datasets.

            </p>

          </div>

        </section>

      </main>

    </div>
  );
}