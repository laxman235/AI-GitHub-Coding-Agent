import { Clock, CheckCircle2, Award, Bookmark } from 'lucide-react';

interface Application {
  id: number;
  company: string;
  role: string;
  date: string;
  stage: 'Saved' | 'Applied' | 'Interview' | 'Offer';
}

const mockApps: Application[] = [
  { id: 1, company: 'Stripe', role: 'Staff Backend Engineer', date: 'Applied 2d ago', stage: 'Interview' },
  { id: 2, company: 'Netflix', role: 'Senior Java Systems Dev', date: 'Applied 4d ago', stage: 'Applied' },
  { id: 3, company: 'Atlassian', role: 'Full Stack Java / React', date: 'Applied 1w ago', stage: 'Interview' },
  { id: 4, company: 'Google Cloud', role: 'Cloud Platform Architect', date: 'Saved yesterday', stage: 'Saved' },
  { id: 5, company: 'Databricks', role: 'Distributed Systems Engineer', date: 'Offered 3d ago', stage: 'Offer' },
];

export default function ApplicationTracker() {
  const columns = [
    { title: 'Saved Jobs', stage: 'Saved', icon: Bookmark, color: 'text-slate-400', border: 'border-slate-800' },
    { title: 'Applied', stage: 'Applied', icon: Clock, color: 'text-blue-400', border: 'border-blue-900/50' },
    { title: 'Interviews Scheduled', stage: 'Interview', icon: CheckCircle2, color: 'text-indigo-400', border: 'border-indigo-900/50' },
    { title: 'Offers Received', stage: 'Offer', icon: Award, color: 'text-emerald-400', border: 'border-emerald-900/50' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Application Pipeline & Kanban Tracker</h2>
          <p className="text-xs text-slate-400 mt-1">Autonomous status tracking and interview reminders</p>
        </div>
        <span className="text-xs font-semibold px-3 py-1 rounded-full bg-slate-900 border border-slate-700 text-slate-300">
          5 Total Tracked
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {columns.map((col) => {
          const colApps = mockApps.filter((a) => a.stage === col.stage);
          return (
            <div key={col.stage} className={`p-4 rounded-xl bg-slate-900/50 border ${col.border} space-y-3`}>
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <span className={`flex items-center gap-2 text-xs font-bold uppercase tracking-wider ${col.color}`}>
                  <col.icon className="w-4 h-4" />
                  {col.title}
                </span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">
                  {colApps.length}
                </span>
              </div>

              <div className="space-y-2">
                {colApps.map((app) => (
                  <div key={app.id} className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 transition-all space-y-1.5 shadow-sm">
                    <p className="text-sm font-semibold text-white">{app.company}</p>
                    <p className="text-xs text-slate-400">{app.role}</p>
                    <span className="text-[10px] text-slate-500 font-medium block pt-1">{app.date}</span>
                  </div>
                ))}
                {colApps.length === 0 && (
                  <p className="text-xs text-slate-600 text-center py-6">No applications in this stage</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
