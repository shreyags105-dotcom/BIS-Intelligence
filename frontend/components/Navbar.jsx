'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Bot, CheckCircle2, LayoutDashboard, FileText, Search } from 'lucide-react';

export default function Navbar() {
  const pathname = usePathname();

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Ask BIS AI', path: '/chat', icon: Bot },
    { name: 'Compliance Tracker', path: '/compliance', icon: CheckCircle2 },
    { name: 'Standards Search', path: '/standards', icon: Search },
    { name: 'Document Analysis', path: '/documents', icon: FileText },
  ];

  return (
    <nav className="bg-[#3A261C] text-[#FFF8EE] px-6 py-3 border-b border-[#5A3D2E] flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-[#D6B98C] text-[#3A261C] rounded-xl flex items-center justify-center font-black text-sm">
          BIS
        </div>
        <span className="font-black text-base tracking-wide text-[#F4EBDD]">BIS Intelligence</span>
      </div>

      <div className="flex items-center gap-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.path;
          return (
            <Link
              key={item.path}
              href={item.path}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold transition ${
                isActive
                  ? 'bg-[#5A3D2E] text-[#D6B98C]'
                  : 'text-[#E0D0BB] hover:bg-[#4A3225] hover:text-[#FFF8EE]'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span className="hidden md:inline">{item.name}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
  