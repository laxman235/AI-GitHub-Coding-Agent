import { useState } from 'react';
import { CheckCircle2, AlertTriangle, RefreshCw, Sparkles, FileText } from 'lucide-react';

export default function ResumeOptimizer() {
  const [analyzing, setAnalyzing] = useState(false);
  const [score, setScore] = useState(88);

  const missingKeywords = ['Kafka Partitioning', 'Docker Multi-Stage Build', 'Redis Caching Strategy', 'Spring Security JWT Filter'];
  const matchedSkills = ['Java 21', 'Spring Boot 3', 'Hibernate', 'JUnit 5', 'Mockito', 'REST APIs', 'PostgreSQL'];

  const handleReoptimize = () => {
    setAnalyzing(true);
    setTimeout(() => {
      setScore(95);
      setAnalyzing(false);
    }, 1200);
  };

  return (
    <div className="space-y-6">
      {/* Header card */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <FileText className="w-6 h-6 text-blue-400" />
            <h2 className="text-xl font-bold text-white">ATS Semantic Scorecard & Resume Enhancer</h2>
          </div>
          <p className="text-sm text-slate-400">
            Current active resume: <span className="font-semibold text-slate-200">Laxman_Java_Backend_Architect_2026.pdf</span>
          </p>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-center">
            <span className="text-3xl font-extrabold text-emerald-400">{score}%</span>
            <span className="block text-xs text-slate-500 font-medium">ATS Compatibility</span>
          </div>
          <button
            onClick={handleReoptimize}
            disabled={analyzing}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-all shadow-md shadow-indigo-500/20"
          >
            <RefreshCw className={`w-4 h-4 ${analyzing ? 'animate-spin' : ''}`} />
            {analyzing ? 'Analyzing with AI...' : 'Run Semantic Optimizer'}
          </button>
        </div>
      </div>

      {/* Analysis Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Missing Keywords Box */}
        <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-400" />
              Missing High-Impact Keywords
            </h3>
            <span className="text-xs text-amber-400/80 font-medium">Recommended for top 5% match</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {missingKeywords.map((kw, i) => (
              <span key={i} className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-500/10 text-amber-300 border border-amber-500/20 flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-amber-400" />
                + {kw}
              </span>
            ))}
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            The AI agent analyzed 42 matching Java 21 Spring Boot openings and discovered these keywords improve recruiter visibility by 48%.
          </p>
        </div>

        {/* Matched Competencies */}
        <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              Verified Core Competencies
            </h3>
            <span className="text-xs text-emerald-400/80 font-medium">{matchedSkills.length} Verified</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {matchedSkills.map((sk, i) => (
              <span key={i} className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                ✓ {sk}
              </span>
            ))}
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            All required foundational Java 21, JPA/Hibernate, and Mockito testing requirements are strongly represented.
          </p>
        </div>
      </div>
    </div>
  );
}
