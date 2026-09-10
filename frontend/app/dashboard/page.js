'use client';

import { useState } from 'react';
import Link from 'next/link';
import { 
  Bot, 
  CheckCircle2, 
  Search, 
  FileText, 
  Sparkles, 
  ArrowRight,
  Clock,
  Bell,
  X,
  AlertCircle,
  CheckCircle
} from 'lucide-react';

export default function DashboardPage() {
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [notifications, setNotifications] = useState([
    {
      id: 1,
      title: 'IS 2347 Audit Update',
      desc: 'Pressure cooker safety testing protocols updated.',
      type: 'alert',
      time: '10m ago'
    },
    {
      id: 2,
      title: 'Document Verified',
      desc: 'Steel Reinforcement PDF analysis complete.',
      type: 'success',
      time: '1h ago'
    }
  ]);

  const recentSearches = [
    'IS 2347 Domestic Pressure Cooker Safety',
    'Gold Hallmarking 6-digit HUID Rules',
    'IS 14543 Packaged Drinking Water Limits',
  ];

  const dismissNotification = (id) => {
    setNotifications(notifications.filter(n => n.id !== id));
  };

  return (
    <div className="min-h-screen bg-[#F4EBDD] text-[#3B2A20] p-6 md:p-10 font-sans">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header Bar */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#E1D1BC] pb-6">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-3xl font-black text-[#3A261C]">Welcome Back 👋</h1>
              <span className="bg-[#D6B98C] text-[#3A261C] text-[10px] font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider">
                Pro
              </span>
            </div>
            <p className="text-sm text-[#705543] mt-1 font-medium">
              Bureau of Indian Standards — Intelligent Desk
            </p>
          </div>

          <div className="flex items-center gap-3 relative">
            {/* Bell Button with Dynamic Badge Count */}
            <button 
              onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
              className="p-2.5 rounded-xl bg-[#FFF9F1] border border-[#E1D1BC] text-[#5A3D2E] hover:bg-[#EFE1CF] transition shadow-xs relative focus:outline-hidden"
              aria-label="Notifications"
            >
              <Bell className="w-4 h-4" />
              {notifications.length > 0 && (
                <span className="absolute -top-1.5 -right-1.5 px-1.5 py-0.5 bg-amber-600 text-white text-[9px] font-bold rounded-full min-w-[18px] text-center shadow-xs">
                  {notifications.length}
                </span>
              )}
            </button>

            {/* Notification Dropdown Menu */}
            {isNotificationsOpen && (
              <div className="absolute right-0 top-12 w-80 bg-[#FFF9F1] border border-[#E1D1BC] rounded-2xl shadow-xl z-50 p-4 space-y-3">
                <div className="flex items-center justify-between border-b border-[#E3D5C3] pb-2">
                  <h4 className="font-bold text-xs text-[#3A261C]">Notifications ({notifications.length})</h4>
                  <button 
                    onClick={() => setIsNotificationsOpen(false)}
                    className="text-[#806044] hover:text-[#3A261C]"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>

                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {notifications.length === 0 ? (
                    <p className="text-xs text-[#806044] text-center py-4">No new notifications</p>
                  ) : (
                    notifications.map((item) => (
                      <div 
                        key={item.id}
                        className="p-3 bg-[#FBF5EC] border border-[#E3D5C3] rounded-xl flex items-start justify-between gap-2 text-xs"
                      >
                        <div className="flex gap-2">
                          {item.type === 'alert' ? (
                            <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                          ) : (
                            <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                          )}
                          <div>
                            <span className="font-bold text-[#3A261C] block">{item.title}</span>
                            <p className="text-[#6B5242] text-[11px]">{item.desc}</p>
                            <span className="text-[9px] text-[#9A7652] block mt-1">{item.time}</span>
                          </div>
                        </div>
                        <button 
                          onClick={() => dismissNotification(item.id)}
                          className="text-[#9A7652] hover:text-[#3A261C]"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}

            <Link
              href="/chat"
              className="flex items-center gap-2 bg-[#5A3D2E] hover:bg-[#704C38] text-[#FFF8EE] px-4 py-2.5 rounded-xl font-bold text-xs transition shadow-sm"
            >
              <Sparkles className="w-3.5 h-3.5 text-[#D6B98C]" />
              <span>Ask BIS AI</span>
            </Link>
          </div>
        </div>

        {/* Hero Quick Action Section */}
        <div className="bg-[#FFF9F1] rounded-3xl p-6 md:p-8 border border-[#E1D1BC] shadow-sm space-y-4">
          <h2 className="text-lg font-black text-[#3A261C]">What is on your mind?</h2>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            
            {/* 1. Ask BIS AI */}
            <Link
              href="/chat"
              className="p-5 bg-[#F9EFE3] hover:bg-[#F2E4D2] border border-[#E0D0BB] hover:border-[#9A7652] rounded-2xl transition shadow-xs flex flex-col justify-between h-36 group"
            >
              <div className="w-10 h-10 rounded-xl bg-[#5A3D2E] text-[#FFF8EE] flex items-center justify-center shadow-xs">
                <Bot className="w-5 h-5" />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-bold text-sm text-[#3A261C] block">Ask BIS AI</span>
                  <span className="text-xs text-[#806044]">Instant standard answers</span>
                </div>
                <ArrowRight className="w-4 h-4 text-[#8A6447] group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>

            {/* 2. Check Compliance */}
            <Link
              href="/compliance"
              className="p-5 bg-[#F9EFE3] hover:bg-[#F2E4D2] border border-[#E0D0BB] hover:border-[#9A7652] rounded-2xl transition shadow-xs flex flex-col justify-between h-36 group"
            >
              <div className="w-10 h-10 rounded-xl bg-[#5A3D2E] text-[#FFF8EE] flex items-center justify-center shadow-xs">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-bold text-sm text-[#3A261C] block">Check Compliance</span>
                  <span className="text-xs text-[#806044]">Track active audits</span>
                </div>
                <ArrowRight className="w-4 h-4 text-[#8A6447] group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>

            {/* 3. Search Standards */}
            <Link
              href="/standards"
              className="p-5 bg-[#F9EFE3] hover:bg-[#F2E4D2] border border-[#E0D0BB] hover:border-[#9A7652] rounded-2xl transition shadow-xs flex flex-col justify-between h-36 group"
            >
              <div className="w-10 h-10 rounded-xl bg-[#5A3D2E] text-[#FFF8EE] flex items-center justify-center shadow-xs">
                <Search className="w-5 h-5" />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-bold text-sm text-[#3A261C] block">Search Standards</span>
                  <span className="text-xs text-[#806044]">IS Index Database</span>
                </div>
                <ArrowRight className="w-4 h-4 text-[#8A6447] group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>

            {/* 4. Analyze Document */}
            <Link
              href="/documents"
              className="p-5 bg-[#F9EFE3] hover:bg-[#F2E4D2] border border-[#E0D0BB] hover:border-[#9A7652] rounded-2xl transition shadow-xs flex flex-col justify-between h-36 group"
            >
              <div className="w-10 h-10 rounded-xl bg-[#5A3D2E] text-[#FFF8EE] flex items-center justify-center shadow-xs">
                <FileText className="w-5 h-5" />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-bold text-sm text-[#3A261C] block">Analyze Document</span>
                  <span className="text-xs text-[#806044]">PDF Audit Verification</span>
                </div>
                <ArrowRight className="w-4 h-4 text-[#8A6447] group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>

          </div>
        </div>

        {/* Dashboard Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Active Compliance Overview */}
          <div className="lg:col-span-2 bg-[#FFF9F1] rounded-3xl p-6 border border-[#E1D1BC] shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-[#E3D5C3] pb-3">
              <h3 className="font-bold text-sm text-[#3A261C]">Active Compliance Overview</h3>
              <Link href="/compliance" className="text-xs font-bold text-[#8A6447] hover:underline">
                View Plan
              </Link>
            </div>

            <div className="p-4 bg-[#F2E4D2] rounded-2xl border border-[#DCC5A8] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <span className="text-[10px] uppercase font-bold text-[#806044] tracking-wider">
                  IS 2347 Certification
                </span>
                <h4 className="font-black text-lg text-[#3A261C]">PRESSURE COOKER</h4>
                <p className="text-xs text-[#6B5242] mt-0.5">Status: Testing Protocols Stage</p>
              </div>

              <div className="flex items-center gap-3">
                <div className="text-right">
                  <span className="text-xl font-black text-[#5A3D2E]">65%</span>
                  <p className="text-[10px] text-[#806044]">Completed</p>
                </div>
                <Link
                  href="/compliance"
                  className="bg-[#5A3D2E] hover:bg-[#704C38] text-[#FFF8EE] px-3.5 py-2 rounded-xl text-xs font-bold transition shrink-0"
                >
                  Resume
                </Link>
              </div>
            </div>
          </div>

          {/* Recent Activity Panel */}
          <div className="bg-[#FFF9F1] rounded-3xl p-6 border border-[#E1D1BC] shadow-sm space-y-4">
            <div className="flex items-center gap-2 border-b border-[#E3D5C3] pb-3">
              <Clock className="w-4 h-4 text-[#8A6447]" />
              <h3 className="font-bold text-sm text-[#3A261C]">Recent Queries</h3>
            </div>

            <div className="space-y-2">
              {recentSearches.map((item, idx) => (
                <Link
                  key={idx}
                  href={`/chat?q=${encodeURIComponent(item)}`}
                  className="p-3 bg-[#FBF5EC] hover:bg-[#F2E4D2] border border-[#E3D5C3] rounded-xl text-xs font-medium text-[#4A3427] transition block truncate"
                >
                  {item}
                </Link>
              ))}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}