import React, { useState } from 'react';
import Navbar from './components/Navbar.tsx';
import StatsGrid from './components/StatsGrid.tsx';
import JobFeed from './components/JobFeed.tsx';
import ResumeOptimizer from './components/ResumeOptimizer.tsx';
import ApplicationTracker from './components/ApplicationTracker.tsx';
import AuthModal from './components/AuthModal.tsx';

export type TabType = 'jobs' | 'resume' | 'applications';

export default function App() {
  const [activeTab, setActiveTab] = useState<TabType>('jobs');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [currentUser, setCurrentUser] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Navbar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        onOpenAuth={() => setShowAuthModal(true)} 
        currentUser={currentUser}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Hero Banner */}
        <div className="relative rounded-2xl bg-gradient-to-r from-blue-900/40 via-indigo-900/30 to-purple-900/40 border border-slate-800 p-8 shadow-2xl backdrop-blur-sm overflow-hidden">
          <div className="max-w-3xl space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse"></span>
              Autonomous Agent Active
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
              Accelerate Your Career with <span className="bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">Agentic AI</span>
            </h1>
            <p className="text-slate-400 text-sm sm:text-base leading-relaxed">
              CareerPilot AI autonomously crawls top job boards daily, matches your resume against real job requirements with semantic ATS scoring, and manages your full application lifecycle.
            </p>
          </div>
        </div>

        {/* Real-time Stats Grid */}
        <StatsGrid />

        {/* Tab Content */}
        <div className="transition-all duration-300">
          {activeTab === 'jobs' && <JobFeed />}
          {activeTab === 'resume' && <ResumeOptimizer />}
          {activeTab === 'applications' && <ApplicationTracker />}
        </div>
      </main>

      <footer className="border-t border-slate-900 bg-slate-950/80 py-6 text-center text-xs text-slate-500">
        © 2026 CareerPilot AI. Autonomous Career Management Engine powered by Spring Boot 3 & Agentic LLMs.
      </footer>

      {showAuthModal && (
        <AuthModal 
          onClose={() => setShowAuthModal(false)} 
          onSuccess={(username) => {
            setCurrentUser(username);
            setShowAuthModal(false);
          }} 
        />
      )}
    </div>
  );
}
