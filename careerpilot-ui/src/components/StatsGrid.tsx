import { Target, Search, Clock, Award } from 'lucide-react';

export default function StatsGrid() {
  const stats = [
    { label: 'Discovered Jobs', value: '142', change: '+18 today', icon: Search, color: 'text-blue-400', bg: 'bg-blue-500/10' },
    { label: 'Top ATS Match', value: '96%', change: 'Senior Java Dev', icon: Target, color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
    { label: 'Active Applications', value: '8', change: '2 in interview', icon: Clock, color: 'text-indigo-400', bg: 'bg-indigo-500/10' },
    { label: 'Skill Optimization', value: '94%', change: '3 keywords added', icon: Award, color: 'text-purple-400', bg: 'bg-purple-500/10' },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((s, idx) => (
        <div key={idx} className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-all flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">{s.label}</p>
            <p className="text-2xl font-bold text-white mt-1">{s.value}</p>
            <span className="text-xs text-slate-500 mt-0.5 inline-block">{s.change}</span>
          </div>
          <div className={`p-3 rounded-xl ${s.bg}`}>
            <s.icon className={`w-6 h-6 ${s.color}`} />
          </div>
        </div>
      ))}
    </div>
  );
}
