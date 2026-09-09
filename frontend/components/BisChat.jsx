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
  WifiOff,
  Search,
  CheckCircle2,
  Copy,
  Check,
  Download,
  Plus,
  MessageSquare,
  HelpCircle,
  ExternalLink,
} from 'lucide-react';

const SUGGESTED_QUESTIONS = [
  'What is IS 1786 for steel reinforcement bars?',
  'What are the mandatory Gold Hallmarking regulations in India?',
  'What are the permissible limits under IS 14543 Drinking Water Standards?',
  'How to apply for a new BIS Product Certification (ISI Mark)?',
];

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export default function BisChat() {
  const [messages, setMessages] = useState([
    {
      role: 'ai',
      text: 'Namaste! I am your **BIS AI Assistant**. Ask me anything about Indian Standards (IS), product certification schemes, hallmarking regulations, or testing compliance.',
    },
  ]);

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState(null);

  const [chatHistory, setChatHistory] = useState([
    { id: '1', title: 'IS 1786 Steel Specifications' },
    { id: '2', title: 'Gold Hallmarking Audit Rules' },
    { id: '3', title: 'Packaged Water IS 14543 Limits' },
  ]);

  const [activeCitation, setActiveCitation] = useState({
    standard: 'Select / Ask Query',
    references:
      'Ask a query to view clause-level citation metadata and official BIS standard references.',
    source: 'BIS Official Registry',
    mode: 'Awaiting Query',
  });

  const [isOffline, setIsOffline] = useState(false);

  const chatEndRef = useRef(null);

  useEffect(() => {
    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleNewChat = () => {
    setMessages([
      {
        role: 'ai',
        text: 'Namaste! I am your **BIS AI Assistant**. Ask me anything about Indian Standards (IS), product certification schemes, hallmarking regulations, or testing compliance.',
      },
    ]);

    setActiveCitation({
      standard: 'Select / Ask Query',
      references:
        'Ask a query to view clause-level citation metadata and official BIS standard references.',
      source: 'BIS Official Registry',
      mode: 'Awaiting Query',
    });
  };

  const executeSearch = async (queryText) => {
    if (!queryText.trim() || loading) return;

    const userMessage = queryText.trim();
    setInput('');

    setMessages((prev) => [
      ...prev,
      { role: 'user', text: userMessage },
    ]);

    if (!chatHistory.some((item) => item.title === userMessage)) {
      setChatHistory((prev) => [
        { id: Date.now().toString(), title: userMessage },
        ...prev,
      ]);
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userMessage, mode: 'consumer' }),
      });

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`);
      }

      const chatResponse = await response.json();

      setMessages((prev) => [
        ...prev,
        { role: 'ai', text: chatResponse.direct_answer },
      ]);

      setActiveCitation({
        standard: chatResponse.standard || 'IS Standard Identified',
        references: chatResponse.references || 'Standard compliance guidelines applied.',
        source: chatResponse.source || 'BIS Official Portal Data',
        mode: chatResponse.mode || 'Live Citation',
      });
    } catch (error) {
      console.error('Chat error:', error);

      setMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          text: 'I could not connect to the BIS backend server. Please verify your FastAPI backend is running at `http://127.0.0.1:8000`.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    executeSearch(input);
  };

  const handleCopy = (text, index) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const handleDownloadPDF = (text, index) => {
    const printWindow = window.open('', '_blank');
    if (!printWindow) return;

    printWindow.document.write(`
      <html>
        <head>
          <title>BIS AI Assistant - Compliance Response</title>
          <style>
            body { font-family: sans-serif; padding: 40px; color: #3A261C; line-height: 1.6; }
            h1 { color: #3A261C; border-bottom: 2px solid #D6B98C; padding-bottom: 10px; }
            .meta { font-size: 12px; color: #806044; margin-bottom: 20px; }
            .content { background: #FAF5EE; padding: 20px; border-radius: 8px; border: 1px solid #E1D1BC; }
          </style>
        </head>
        <body>
          <h1>Bureau of Indian Standards - AI Compliance Record</h1>
          <div class="meta">Generated by BIS AI Assistant • Date: ${new Date().toLocaleDateString()}</div>
          <div class="content">${text.replace(/\n/g, '<br/>')}</div>
        </body>
      </html>
    `);
    printWindow.document.close();
    printWindow.focus();
    printWindow.print();
  };

  return (
    <div className="flex h-screen bg-[#F4EBDD] text-[#3B2A20] font-sans overflow-hidden">
      <aside className="w-64 bg-[#3A261C] text-[#FFF8EE] flex flex-col justify-between p-4 border-r border-[#51372A] shrink-0">
        <div className="space-y-4">
          <div className="flex items-center gap-3 px-2 py-1">
            <div className="w-9 h-9 bg-[#D6B98C] text-[#3A261C] rounded-xl flex items-center justify-center font-black text-sm tracking-wider shadow">
              BIS
            </div>
            <div>
              <h2 className="font-bold text-sm leading-tight flex items-center gap-1.5">
                BIS AI Portal
                <Sparkles className="w-3.5 h-3.5 text-[#D6B98C]" />
              </h2>
              <p className="text-[10px] text-[#D6B98C]">Standards Intelligence</p>
            </div>
          </div>

          <button
            type="button"
            onClick={handleNewChat}
            className="w-full flex items-center gap-2 bg-[#51372A] hover:bg-[#634534] border border-[#755744] text-[#EADBC8] hover:text-white px-3.5 py-2.5 rounded-xl text-xs font-semibold transition shadow-sm"
          >
            <Plus className="w-4 h-4" />
            New Conversation
          </button>

          <div className="space-y-2 pt-2">
            <span className="text-[10px] font-bold uppercase tracking-wider text-[#D6B98C]/70 px-2 flex items-center gap-1.5">
              <MessageSquare className="w-3 h-3" />
              Chat History
            </span>
            <div className="space-y-1 max-h-[calc(100vh-320px)] overflow-y-auto pr-1">
              {chatHistory.map((chat) => (
                <button
                  key={chat.id}
                  type="button"
                  onClick={() => executeSearch(chat.title)}
                  className="w-full text-left text-xs px-3 py-2 rounded-lg text-[#EADBC8] hover:bg-[#51372A] hover:text-white truncate transition block"
                >
                  {chat.title}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="pt-4 border-t border-[#51372A] space-y-2">
          <div className="flex items-center justify-between text-xs text-[#D6B98C] px-2">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              Engine Online
            </span>
            <span className="text-[10px] bg-[#51372A] px-2 py-0.5 rounded border border-[#755744]">
              v2.4
            </span>
          </div>
        </div>
      </aside>

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-[#FFF9F1] border-b border-[#E1D1BC] px-6 py-3.5 flex justify-between items-center shadow-sm">
          <div>
            <h1 className="text-base font-bold text-[#3A261C] flex items-center gap-2">
              Ask Anything About BIS Standards, Certification & Compliance
            </h1>
            <p className="text-xs text-[#806044]">
              Bureau of Indian Standards Intelligent Verification System
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleNewChat}
              className="flex items-center gap-1.5 text-xs font-medium text-[#5A3D2E] hover:bg-[#EFE1CF] border border-[#D5BEA3] px-3 py-1.5 rounded-lg transition"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Reset
            </button>
          </div>
        </header>

        {isOffline && (
          <div className="bg-[#F4DFC0] border-b border-[#C9A66B] text-[#79552F] px-4 py-1.5 text-xs flex items-center justify-center gap-2">
            <WifiOff className="w-3.5 h-3.5" />
            <span>Network disconnected. Operating in offline mode.</span>
          </div>
        )}

        <main className="flex-1 flex overflow-hidden p-4 gap-4 max-w-7xl w-full mx-auto">
          <section className="flex-1 bg-[#FFF9F1] rounded-2xl shadow-sm border border-[#E1D1BC] flex flex-col overflow-hidden">
            <div className="flex-1 p-6 overflow-y-auto space-y-6">
              {messages.length === 1 && (
                <div className="bg-[#F9EFE3] border border-[#E3D4C1] rounded-2xl p-5 space-y-4">
                  <div className="flex items-center gap-2 text-[#3A261C]">
                    <HelpCircle className="w-5 h-5 text-[#8A6447]" />
                    <h3 className="font-bold text-sm">Suggested Questions</h3>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                    {SUGGESTED_QUESTIONS.map((q, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => executeSearch(q)}
                        className="p-3 bg-[#FFF9F1] hover:bg-[#FAF2E6] border border-[#E0D0BB] hover:border-[#9A7652] rounded-xl text-left text-xs font-medium text-[#4A3427] transition shadow-xs flex items-start gap-2 group"
                      >
                        <Search className="w-3.5 h-3.5 text-[#8A6447] group-hover:text-[#3A261C] shrink-0 mt-0.5" />
                        <span>{q}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex gap-3.5 ${
                    msg.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {msg.role === 'ai' && (
                    <div className="w-9 h-9 rounded-xl bg-[#5A3D2E] text-[#F7E9D4] flex items-center justify-center shrink-0 shadow-sm">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}

                  <div className="max-w-[82%] space-y-2">
                    <div
                      className={`rounded-2xl px-5 py-4 text-sm leading-relaxed shadow-xs ${
                        msg.role === 'user'
                          ? 'bg-[#C9A77A] text-[#332218] font-medium rounded-tr-xs'
                          : 'bg-[#F1E5D5] text-[#49352A] rounded-tl-xs border border-[#E2D1BA] prose prose-sm max-w-none'
                      }`}
                    >
                      {msg.role === 'ai' ? (
                        <ReactMarkdown>{msg.text}</ReactMarkdown>
                      ) : (
                        msg.text
                      )}
                    </div>

                    {msg.role === 'ai' && index > 0 && (
                      <div className="flex items-center gap-2 pt-0.5 px-1">
                        <button
                          type="button"
                          onClick={() => handleCopy(msg.text, index)}
                          className="flex items-center gap-1 text-[11px] font-medium text-[#7A6453] hover:text-[#3A261C] bg-[#EFE1CF] hover:bg-[#EADBC8] border border-[#D8C0A0] px-2.5 py-1 rounded-md transition"
                        >
                          {copiedIndex === index ? (
                            <>
                              <Check className="w-3 h-3 text-emerald-700" />
                              <span className="text-emerald-700">Copied!</span>
                            </>
                          ) : (
                            <>
                              <Copy className="w-3 h-3" />
                              <span>Copy Answer</span>
                            </>
                          )}
                        </button>

                        <button
                          type="button"
                          onClick={() => handleDownloadPDF(msg.text, index)}
                          className="flex items-center gap-1 text-[11px] font-medium text-[#7A6453] hover:text-[#3A261C] bg-[#EFE1CF] hover:bg-[#EADBC8] border border-[#D8C0A0] px-2.5 py-1 rounded-md transition"
                        >
                          <Download className="w-3 h-3" />
                          <span>Download PDF</span>
                        </button>
                      </div>
                    )}
                  </div>

                  {msg.role === 'user' && (
                    <div className="w-9 h-9 rounded-xl bg-[#E7D7C2] text-[#5A3D2E] border border-[#D2BFA7] flex items-center justify-center shrink-0">
                      <User className="w-4 h-4" />
                    </div>
                  )}
                </div>
              ))}

              {loading && (
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-[#5A3D2E] text-[#F7E9D4] flex items-center justify-center shrink-0 shadow-sm">
                    <Bot className="w-4 h-4" />
                  </div>
                  <div className="bg-[#F1E5D5] border border-[#DCC8AE] rounded-2xl rounded-tl-xs px-4 py-3 flex items-center gap-2.5 text-[#70503B]">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-xs font-medium">
                      Fetching verified response from BIS records...
                    </span>
                  </div>
                </div>
              )}

              <div ref={chatEndRef} />
            </div>

            <div className="p-4 bg-[#F8EFE3] border-t border-[#E1D1BC]">
              <form onSubmit={handleSubmit} className="flex gap-2.5">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask anything about BIS standards, certification, or compliance..."
                  className="flex-1 px-4 py-3 bg-[#FFFDF9] border border-[#D8C5AD] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#B18A61]/30 focus:border-[#9A7652] text-sm text-[#3F2C21] placeholder-[#A18A75] shadow-inner"
                />
                <button
                  type="submit"
                  disabled={loading || !input.trim()}
                  className="bg-[#5A3D2E] hover:bg-[#704C38] disabled:bg-[#D8CABB] disabled:text-[#9F9184] text-[#FFF8EE] px-5 py-3 rounded-xl font-semibold text-xs transition flex items-center gap-2 shadow-sm"
                >
                  <span>Send</span>
                  <Send className="w-3.5 h-3.5" />
                </button>
              </form>
            </div>
          </section>

          <section className="w-80 bg-[#FFF9F1] rounded-2xl shadow-sm border border-[#E1D1BC] p-4 flex flex-col justify-between overflow-y-auto">
            <div className="space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-[#E3D5C3]">
                <div className="flex items-center gap-1.5 font-bold text-[#4A3427] text-xs">
                  <ShieldCheck className="w-4 h-4 text-[#8A6447]" />
                  <span>Sources & References</span>
                </div>
                <span className="text-[9px] uppercase font-bold tracking-wider px-2 py-1 rounded bg-[#EADBC8] text-[#6C4B37] border border-[#D7C2A7]">
                  {activeCitation.mode}
                </span>
              </div>

              <div className="bg-[#F2E4D2] border border-[#DCC5A8] rounded-xl p-3.5 shadow-xs">
                <div className="flex items-center gap-1.5 text-[10px] font-semibold text-[#806044] uppercase tracking-wider mb-1">
                  <BookOpen className="w-3 h-3" />
                  <span>Primary Standard</span>
                </div>
                <span className="text-lg font-black text-[#432D21] block">
                  {activeCitation.standard}
                </span>
              </div>

              <div className="space-y-3">
                <div>
                  <label className="text-[10px] font-bold text-[#806F61] uppercase tracking-wider flex items-center gap-1 mb-1">
                    <FileText className="w-3 h-3" />
                    Clause Reference
                  </label>
                  <div className="bg-[#FBF5EC] p-3 rounded-xl border border-[#E3D5C3] text-xs text-[#665145] leading-relaxed min-h-[50px]">
                    {activeCitation.references}
                  </div>
                </div>

                <div>
                  <label className="text-[10px] font-bold text-[#806F61] uppercase tracking-wider flex items-center gap-1 mb-1">
                    <Database className="w-3 h-3" />
                    Authority Provider
                  </label>
                  <div className="bg-[#FBF5EC] p-3 rounded-xl border border-[#E3D5C3] text-xs font-medium text-[#665145] flex items-center justify-between">
                    <span>{activeCitation.source}</span>
                    <ExternalLink className="w-3 h-3 text-[#8A6447]" />
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-4 p-3 bg-[#EFE1CF] rounded-xl border border-[#D8C0A0] text-[#654735] text-[11px] flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-[#805C40] shrink-0 mt-0.5" />
              <p className="leading-tight">
                <strong>Official Audit Trace:</strong> Grounded responses mapped directly to Indian Standard documentation.
              </p>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}