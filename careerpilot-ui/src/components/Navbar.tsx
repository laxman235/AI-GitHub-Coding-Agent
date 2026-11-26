import { Briefcase, FileText, CheckCircle2, User, Sparkles, LogOut } from 'lucide-react';
import { TabType } from '../App.tsx';

interface NavbarProps {
  activeTab: TabType;
  setActiveTab: (tab: TabType) => void;
  onOpenAuth: () => void;
  onLogout: () => void;
  currentUser: string | null;
}

export default function Navbar({ activeTab, setActiveTab, onOpenAuth, onLogout, currentUser }: NavbarProps) {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-800 bg-slate-950/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab('jobs')}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="text-xl font-bold tracking-tight text-white">CareerPilot</span>
            <span className="text-xl font-bold text-blue-500 ml-1">AI</span>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="hidden md:flex items-center gap-1 bg-slate-900/60 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('jobs')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'jobs'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Briefcase className="w-4 h-4" />
            Job Discovery
          </button>
          <button
            onClick={() => setActiveTab('resume')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'resume'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <FileText className="w-4 h-4" />
            Resume ATS Optimizer
          </button>
          <button
            onClick={() => setActiveTab('applications')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'applications'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <CheckCircle2 className="w-4 h-4" />
            Application Tracker
          </button>
        </nav>

        {/* User Auth Pill */}
        <div className="flex items-center gap-3">
          {currentUser ? (
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-700 text-sm">
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                <span className="font-medium text-slate-200">{currentUser}</span>
              </div>
              <button
                onClick={onLogout}
                title="Sign Out"
                className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-900 rounded-lg transition-colors border border-transparent hover:border-slate-800"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold bg-blue-600 hover:bg-blue-500 text-white transition-all shadow-md shadow-blue-500/20"
            >
              <User className="w-4 h-4" />
              Sign In / Register
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
