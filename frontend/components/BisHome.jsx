'use client';

import { useEffect, useMemo, useState } from 'react';
import {
  ArrowLeft,
  ArrowRight,
  Award,
  Beaker,
  BookOpen,
  Bot,
  CheckCircle2,
  ChevronRight,
  ExternalLink,
  Factory,
  FlaskConical,
  Loader2,
  MessageSquare,
  Search,
  Send,
  ShieldCheck,
  Star,
  UserRound,
} from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

const SERVICES = [
  { key: 'certification', label: 'Certification', description: 'ISI marks, licensing and compliance', icon: Award },
  { key: 'hallmarking', label: 'Hallmarking', description: 'Gold, silver and HUID guidance', icon: ShieldCheck },
  { key: 'labs', label: 'Laboratories', description: 'BIS-recognized testing facilities', icon: FlaskConical },
  { key: 'standards', label: 'Standards', description: 'Browse the Indian Standards index', icon: BookOpen },
  { key: 'consumer', label: 'Consumer Services', description: 'Understand marks and complaints', icon: UserRound },
];

const STARTER_PROMPTS = {
  industry: 'I manufacture pressure cookers. Which BIS standard applies?',
  consumer: 'What does the BIS mark mean?',
};

function displayStandard(value) {
  if (!value || value === 'N/A') return 'Not identified';
  return value.replace(/^IS(?=\d)/i, 'IS ');
}

export default function BisHome() {
  const [view, setView] = useState('home');
  const [mode, setMode] = useState('consumer');
  const [query, setQuery] = useState('');
  const [standards, setStandards] = useState([]);
  const [selectedStandard, setSelectedStandard] = useState(null);
  const [service, setService] = useState(null);
  const [loading, setLoading] = useState(false);
  const [notice, setNotice] = useState('');

  useEffect(() => {
    const fetchStandards = async () => {
      try {
        const response = await fetch(`${API_URL}/standards`);
        if (!response.ok) throw new Error('Could not load standards');
        const data = await response.json();
        setStandards(data.standards || []);
      } catch (error) {
        setNotice('The standards index is unavailable. Start the backend and try again.');
      }
    };

    fetchStandards();
  }, []);

  const searchResults = useMemo(() => {
    const term = query.trim().toLowerCase();
    if (!term) return standards.slice(0, 6);
    return standards.filter((item) =>
      `${item.id} ${item.product} ${item.purpose}`.toLowerCase().includes(term),
    ).slice(0, 8);
  }, [query, standards]);

  const openStandard = async (standardId) => {
    setLoading(true);
    setNotice('');
    try {
      const response = await fetch(`${API_URL}/standard/${encodeURIComponent(standardId)}`);
      if (!response.ok) throw new Error('Standard not found');
      setSelectedStandard(await response.json());
      setView('standard');
    } catch (error) {
      setNotice('This standard could not be loaded from the backend.');
    } finally {
      setLoading(false);
    }
  };

  const openService = async (serviceKey) => {
    if (serviceKey === 'standards') {
      setView('search');
      return;
    }
    if (serviceKey === 'consumer') {
      setMode('consumer');
      setView('chat');
      return;
    }

    setLoading(true);
    setNotice('');
    try {
      const response = await fetch(`${API_URL}/${serviceKey}`);
      if (!response.ok) throw new Error('Service unavailable');
      setService({ ...await response.json(), label: SERVICES.find((item) => item.key === serviceKey)?.label });
      setView('service');
    } catch (error) {
      setNotice('This BIS service is currently unavailable.');
    } finally {
      setLoading(false);
    }
  };

  const startChat = (nextMode, prompt = '') => {
    setMode(nextMode);
    setQuery(prompt);
    setView('chat');
  };

  return (
    <div className="min-h-screen bg-[#f4ebdd] text-[#3b2a20]">
      <header className="border-b border-[#6e4d39] bg-[#3a261c] text-[#fff8ee]">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-5 py-4 lg:px-8">
          <button type="button" onClick={() => setView('home')} className="flex items-center gap-3 text-left">
            <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-[#d6b98c] font-black tracking-wide text-[#3a261c]">BIS</span>
            <span>
              <span className="block text-sm font-black uppercase tracking-[0.18em] text-[#eadbc8]">BIS Intelligence</span>
              <span className="block text-xs text-[#d6b98c]">Indian Standards and BIS Services</span>
            </span>
          </button>
          <nav className="hidden items-center gap-2 text-sm md:flex">
            <button type="button" onClick={() => setView('home')} className="rounded-lg px-3 py-2 text-[#eadbc8] hover:bg-[#51372a]">Home</button>
            <button type="button" onClick={() => setView('search')} className="rounded-lg px-3 py-2 text-[#eadbc8] hover:bg-[#51372a]">Find a Standard</button>
            <button type="button" onClick={() => startChat('consumer')} className="rounded-lg px-3 py-2 text-[#eadbc8] hover:bg-[#51372a]">Ask BIS AI</button>
          </nav>
        </div>
      </header>

      {notice && (
        <div className="mx-auto mt-4 flex max-w-7xl items-center gap-2 px-5 text-sm text-[#895c36] lg:px-8">
          <span className="rounded-lg border border-[#d3ab78] bg-[#f8e6c8] px-3 py-2">{notice}</span>
        </div>
      )}

      <main className="mx-auto max-w-7xl px-5 py-8 lg:px-8 lg:py-12">
        {view === 'home' && <HomeView onChat={startChat} onSearch={() => setView('search')} onService={openService} />}
        {view === 'chat' && <ChatView mode={mode} initialPrompt={query} onBack={() => setView('home')} />}
        {view === 'search' && (
          <SearchView
            query={query}
            setQuery={setQuery}
            results={searchResults}
            loading={loading}
            onBack={() => setView('home')}
            onOpen={openStandard}
            onAsk={(item) => startChat('industry', `Tell me about ${item.product} and ${item.id}.`)}
          />
        )}
        {view === 'standard' && <StandardView standard={selectedStandard} onBack={() => setView('search')} onAsk={() => startChat('industry', `Tell me about ${selectedStandard?.product} and ${selectedStandard?.id}.`)} />}
        {view === 'service' && <ServiceView service={service} onBack={() => setView('home')} />}
      </main>
    </div>
  );
}

function HomeView({ onChat, onSearch, onService }) {
  return (
    <div className="space-y-10">
      <section className="grid items-end gap-8 lg:grid-cols-[1.15fr_0.85fr]">
        <div>
          <p className="mb-4 text-xs font-bold uppercase tracking-[0.24em] text-[#946b48]">Your standards desk</p>
          <h1 className="max-w-3xl text-4xl font-black leading-tight tracking-tight text-[#3a261c] sm:text-6xl">BIS Intelligence</h1>
          <p className="mt-4 max-w-xl text-xl leading-relaxed text-[#72533e]">AI-powered assistance for Indian Standards, certification, testing and everyday BIS questions.</p>
          <div className="mt-8 flex flex-wrap gap-3">
            <button type="button" onClick={() => onChat('industry', STARTER_PROMPTS.industry)} className="inline-flex items-center gap-2 rounded-xl bg-[#5a3d2e] px-5 py-3 text-sm font-bold text-[#fff8ee] shadow-md hover:bg-[#704c38]"><Factory className="h-4 w-4" /> Industry Assistant</button>
            <button type="button" onClick={() => onChat('consumer', STARTER_PROMPTS.consumer)} className="inline-flex items-center gap-2 rounded-xl border border-[#c9a77a] bg-[#fff9f1] px-5 py-3 text-sm font-bold text-[#5a3d2e] hover:bg-[#f1e5d5]"><UserRound className="h-4 w-4" /> Consumer Assistant</button>
          </div>
        </div>
        <div className="border-l-4 border-[#c9a77a] bg-[#fff9f1] p-6 shadow-sm">
          <p className="text-sm font-bold uppercase tracking-[0.18em] text-[#946b48]">How can we help?</p>
          <p className="mt-3 text-2xl font-semibold leading-snug text-[#4b3427]">Find a standard, understand a mark, or get your next compliance question answered.</p>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        <ActionCard icon={Factory} title="Industry" description="Find standards, requirements and certification pathways." onClick={() => onChat('industry', STARTER_PROMPTS.industry)} />
        <ActionCard icon={UserRound} title="Consumer" description="Understand BIS marks, products and consumer guidance." onClick={() => onChat('consumer', STARTER_PROMPTS.consumer)} />
        <ActionCard icon={Search} title="Find Indian Standard" description="Search the standards index by product or IS number." onClick={onSearch} />
        <ActionCard icon={ShieldCheck} title="Hallmarking" description="Learn how BIS hallmarking and HUID verification work." onClick={() => onService('hallmarking')} />
      </section>

      <section>
        <div className="mb-4 flex items-end justify-between gap-4"><div><p className="text-xs font-bold uppercase tracking-[0.2em] text-[#946b48]">BIS services</p><h2 className="mt-1 text-2xl font-black text-[#3a261c]">Verified starting points</h2></div><button type="button" onClick={onSearch} className="hidden items-center gap-1 text-sm font-bold text-[#704c38] sm:flex">Browse standards <ArrowRight className="h-4 w-4" /></button></div>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">{SERVICES.map((item) => <ActionCard key={item.key} compact icon={item.icon} title={item.label} description={item.description} onClick={() => onService(item.key)} />)}</div>
      </section>
    </div>
  );
}

function ActionCard({ icon: Icon, title, description, onClick, compact = false }) {
  return <button type="button" onClick={onClick} className={`group flex w-full items-start gap-4 border border-[#e1d1bc] bg-[#fff9f1] text-left shadow-sm transition hover:-translate-y-0.5 hover:border-[#b18a61] hover:shadow-md ${compact ? 'p-4' : 'p-5'}`}><span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#f1e5d5] text-[#6a4936] group-hover:bg-[#e7d7c2]"><Icon className="h-5 w-5" /></span><span className="min-w-0"><span className="block font-bold text-[#4a3427]">{title}</span><span className="mt-1 block text-sm leading-relaxed text-[#806f61]">{description}</span></span><ChevronRight className="ml-auto mt-1 h-4 w-4 shrink-0 text-[#b18a61]" /></button>;
}

function ChatView({ mode, initialPrompt, onBack }) {
  const [input, setInput] = useState(initialPrompt || '');
  const [messages, setMessages] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [rating, setRating] = useState(null);

  const submit = async (event) => {
    event.preventDefault();
    const question = input.trim();
    if (!question || loading) return;
    setMessages((current) => [...current, { role: 'user', text: question }]);
    setInput('');
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/chat`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question, mode }) });
      if (!response.ok) throw new Error('Chat unavailable');
      const data = await response.json();
      setResult(data);
      setMessages((current) => [...current, { role: 'ai', text: data.direct_answer }]);
    } catch (error) {
      setMessages((current) => [...current, { role: 'ai', text: 'The BIS backend could not be reached. Start the API server and try again.' }]);
    } finally {
      setLoading(false);
    }
  };

  const sendFeedback = async (value) => {
    setRating(value);
    const question = messages.find((message) => message.role === 'user')?.text;
    if (!question) return;
    await fetch(`${API_URL}/feedback`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question, rating: value }) }).catch(() => {});
  };

  return <div className="space-y-6">
    <PageHeading eyebrow={mode === 'industry' ? 'Industry Assistant' : 'Consumer Assistant'} title="What do you want help with?" onBack={onBack} />
    <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
      <section className="border border-[#e1d1bc] bg-[#fff9f1] p-5 shadow-sm sm:p-7">
        <div className="mb-6 flex items-center gap-3"><span className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#f1e5d5] text-[#6a4936]">{mode === 'industry' ? <Factory className="h-5 w-5" /> : <UserRound className="h-5 w-5" />}</span><div><p className="text-xs font-bold uppercase tracking-[0.18em] text-[#946b48]">{mode} mode</p><p className="font-bold text-[#4a3427]">Ask a BIS question in plain language</p></div></div>
        <div className="min-h-[220px] space-y-4">{messages.length === 0 && <p className="max-w-lg text-2xl font-semibold leading-relaxed text-[#5a3d2e]">{initialPrompt || (mode === 'industry' ? 'I manufacture pressure cookers. Which BIS standard applies?' : 'What does the BIS mark mean?')}</p>}{messages.map((message, index) => <div key={`${message.role}-${index}`} className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : ''}`}><span className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[#f1e5d5] text-[#6a4936]">{message.role === 'user' ? <UserRound className="h-4 w-4" /> : <Bot className="h-4 w-4" />}</span><p className={`max-w-[85%] whitespace-pre-wrap rounded-xl px-4 py-3 text-sm leading-relaxed ${message.role === 'user' ? 'bg-[#c9a77a] text-[#332218]' : 'bg-[#f1e5d5] text-[#49352a]'}`}>{message.text}</p></div>)}{loading && <div className="flex items-center gap-2 text-sm text-[#806f61]"><Loader2 className="h-4 w-4 animate-spin" /> Checking verified BIS information...</div>}</div>
        <form onSubmit={submit} className="mt-6 flex gap-2 border-t border-[#e3d5c3] pt-5"><input value={input} onChange={(event) => setInput(event.target.value)} placeholder="Ask about a product, mark or standard..." className="min-w-0 flex-1 rounded-xl border border-[#d8c5ad] bg-[#fffdf9] px-4 py-3 text-sm outline-none focus:border-[#9a7652]" /><button disabled={loading || !input.trim()} className="inline-flex items-center gap-2 rounded-xl bg-[#5a3d2e] px-4 py-3 text-sm font-bold text-[#fff8ee] disabled:opacity-40"><Send className="h-4 w-4" /> Ask AI</button></form>
      </section>
      <EvidencePanel result={result} rating={rating} onRate={sendFeedback} />
    </div>
  </div>;
}

function EvidencePanel({ result, rating, onRate }) {
  return <aside className="border border-[#e1d1bc] bg-[#fff9f1] p-5 shadow-sm"><div className="flex items-center gap-2 border-b border-[#e3d5c3] pb-4 font-bold text-[#4a3427]"><ShieldCheck className="h-5 w-5 text-[#8a6447]" /> BIS Source</div>{result ? <div className="space-y-4 pt-5"><div><p className="text-xs font-bold uppercase tracking-wider text-[#806044]">Applicable Standard</p><p className="mt-1 text-2xl font-black text-[#432d21]">{displayStandard(result.standard)}</p></div><Info label="Requirements & answer" value={result.answer} /><Info label="Reference" value={result.references} /><Info label="Source" value={result.source} /><SourceLink value={result.references} /><Feedback rating={rating} onRate={onRate} /></div> : <p className="pt-5 text-sm leading-relaxed text-[#806f61]">Your answer will appear here with the applicable standard, evidence and official source.</p>}</aside>;
}

function Info({ label, value }) { return <div><p className="text-xs font-bold uppercase tracking-wider text-[#806f61]">{label}</p><p className="mt-2 rounded-xl border border-[#e3d5c3] bg-[#fbf5ec] p-3 text-sm leading-relaxed text-[#665145]">{value || 'Not available'}</p></div>; }
function SourceLink({ value }) { return value?.startsWith('http') ? <a href={value} target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 text-sm font-bold text-[#704c38] hover:underline">View Reference <ExternalLink className="h-4 w-4" /></a> : null; }
function Feedback({ rating, onRate }) { return <div className="border-t border-[#e3d5c3] pt-4"><p className="text-xs font-bold uppercase tracking-wider text-[#806f61]">Was this useful?</p><div className="mt-2 flex gap-2">{[1, 2, 3, 4, 5].map((value) => <button key={value} type="button" onClick={() => onRate(value)} aria-label={`Rate ${value} out of 5`} className={`rounded-lg p-1 ${rating >= value ? 'text-[#b17832]' : 'text-[#c9b8a4]'}`}><Star className="h-5 w-5 fill-current" /></button>)}</div></div>; }

function SearchView({ query, setQuery, results, loading, onBack, onOpen, onAsk }) {
  return <div className="space-y-6"><PageHeading eyebrow="Standards index" title="Find a Standard" onBack={onBack} /><section className="border border-[#e1d1bc] bg-[#fff9f1] p-5 shadow-sm sm:p-7"><form onSubmit={(event) => event.preventDefault()} className="flex flex-col gap-3 sm:flex-row"><div className="relative flex-1"><Search className="pointer-events-none absolute left-4 top-3.5 h-5 w-5 text-[#a18a75]" /><input autoFocus value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search product or IS number" className="w-full rounded-xl border border-[#d8c5ad] bg-[#fffdf9] py-3 pl-12 pr-4 text-sm outline-none focus:border-[#9a7652]" /></div><button className="rounded-xl bg-[#5a3d2e] px-6 py-3 text-sm font-bold text-[#fff8ee]">Search</button></form>{loading && <p className="mt-5 flex items-center gap-2 text-sm text-[#806f61]"><Loader2 className="h-4 w-4 animate-spin" /> Loading standard...</p>}<div className="mt-6 divide-y divide-[#e3d5c3]">{results.map((item) => <div key={item.id} className="flex flex-col gap-4 py-5 sm:flex-row sm:items-center sm:justify-between"><div><p className="text-xl font-black text-[#4a3427]">{displayStandard(item.id)}</p><p className="font-semibold text-[#6a4936]">{item.product}</p><p className="mt-1 text-sm text-[#806f61]">{item.purpose}</p></div><div className="flex shrink-0 gap-2"><button type="button" onClick={() => onAsk(item)} className="rounded-lg border border-[#c9a77a] px-3 py-2 text-xs font-bold text-[#6a4936]">Ask AI</button><button type="button" onClick={() => onOpen(item.id)} className="inline-flex items-center gap-1 rounded-lg bg-[#5a3d2e] px-3 py-2 text-xs font-bold text-[#fff8ee]">View Source <ChevronRight className="h-3.5 w-3.5" /></button></div></div>)}{!results.length && <p className="py-8 text-center text-sm text-[#806f61]">No matching standards found.</p>}</div></section></div>;
}

function StandardView({ standard, onBack, onAsk }) {
  if (!standard) return null;
  return <div className="space-y-6"><PageHeading eyebrow="Verified standard record" title={`${displayStandard(standard.id)} · ${standard.product}`} onBack={onBack} /><div className="grid gap-5 lg:grid-cols-2"><Info label="Purpose" value={standard.purpose} /><Info label="Requirements" value={standard.requirements} /><Info label="Testing" value={standard.testing} /><Info label="Certification" value={`${standard.certification} (${standard.scheme})`} /></div><div className="flex flex-wrap gap-3"><button type="button" onClick={onAsk} className="inline-flex items-center gap-2 rounded-xl bg-[#5a3d2e] px-5 py-3 text-sm font-bold text-[#fff8ee]"><MessageSquare className="h-4 w-4" /> Ask AI</button><SourceLink value={standard.url} /></div></div>;
}

function ServiceView({ service, onBack }) {
  return <div className="space-y-6"><PageHeading eyebrow="BIS service" title={service?.label || 'Service'} onBack={onBack} /><section className="max-w-3xl border border-[#e1d1bc] bg-[#fff9f1] p-6 shadow-sm"><div className="space-y-5"><Info label="Overview" value={service?.what_is_it || service?.guidance} />{service?.process && <Info label="Process" value={service.process} />}{service?.consumer_guidance && <Info label="Consumer guidance" value={service.consumer_guidance} />}<SourceLink value={service?.source} /></div></section></div>;
}

function PageHeading({ eyebrow, title, onBack }) { return <div className="flex items-start gap-4"><button type="button" onClick={onBack} aria-label="Go back" className="mt-1 rounded-lg border border-[#d8c5ad] bg-[#fff9f1] p-2 text-[#6a4936] hover:bg-[#f1e5d5]"><ArrowLeft className="h-5 w-5" /></button><div><p className="text-xs font-bold uppercase tracking-[0.2em] text-[#946b48]">{eyebrow}</p><h1 className="mt-1 text-3xl font-black text-[#3a261c] sm:text-4xl">{title}</h1></div></div>; }
