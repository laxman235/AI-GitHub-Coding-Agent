import { useState } from 'react';
import { Search, MapPin, DollarSign, Sparkles, Building2 } from 'lucide-react';

interface Job {
  id: number;
  title: string;
  company: string;
  location: string;
  salary: string;
  matchScore: number;
  tags: string[];
  posted: string;
}

const mockJobs: Job[] = [
  {
    id: 1,
    title: 'Senior Java Backend Engineer (Spring Boot & Microservices)',
    company: 'Fintech Nexus',
    location: 'Bangalore, India (Hybrid)',
    salary: '₹28,00,000 - ₹38,00,000',
    matchScore: 96,
    tags: ['Java 21', 'Spring Boot 3', 'Kafka', 'Docker', 'PostgreSQL'],
    posted: '2h ago',
  },
  {
    id: 2,
    title: 'Lead Full Stack Developer (React & Java)',
    company: 'CloudScale Systems',
    location: 'Hyderabad, India (Remote)',
    salary: '₹32,00,000 - ₹45,00,000',
    matchScore: 91,
    tags: ['React', 'TypeScript', 'Java', 'AWS', 'REST APIs'],
    posted: '5h ago',
  },
  {
    id: 3,
    title: 'Staff Software Architect',
    company: 'EnterpriseAI Labs',
    location: 'Pune, India (Office)',
    salary: '₹40,00,000 - ₹55,00,000',
    matchScore: 88,
    tags: ['System Design', 'Microservices', 'Kubernetes', 'Redis'],
    posted: '1d ago',
  },
];

export default function JobFeed() {
  const [searchTerm, setSearchTerm] = useState('');
  const [appliedJobs, setAppliedJobs] = useState<number[]>([]);

  const filtered = mockJobs.filter(
    (j) =>
      j.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      j.tags.some((t) => t.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const handleApply = (id: number) => {
    setAppliedJobs((prev) => [...prev, id]);
  };

  return (
    <div className="space-y-6">
      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-5 h-5 absolute left-3 top-3 text-slate-500" />
          <input
            type="text"
            placeholder="Search by title, skill (e.g. Java 21, Spring Boot, React)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors text-sm"
          />
        </div>
      </div>

      {/* Job Cards */}
      <div className="space-y-4">
        {filtered.map((job) => {
          const isApplied = appliedJobs.includes(job.id);
          return (
            <div
              key={job.id}
              className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 hover:border-slate-700 transition-all flex flex-col md:flex-row items-start md:items-center justify-between gap-6"
            >
              <div className="space-y-3 flex-1">
                <div className="flex items-center gap-3 flex-wrap">
                  <h3 className="text-lg font-bold text-white hover:text-blue-400 cursor-pointer transition-colors">
                    {job.title}
                  </h3>
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    <Sparkles className="w-3 h-3" />
                    {job.matchScore}% Match
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400">
                  <span className="flex items-center gap-1 text-slate-300 font-medium">
                    <Building2 className="w-4 h-4 text-slate-500" />
                    {job.company}
                  </span>
                  <span className="flex items-center gap-1">
                    <MapPin className="w-4 h-4 text-slate-500" />
                    {job.location}
                  </span>
                  <span className="flex items-center gap-1 text-emerald-400 font-medium">
                    <DollarSign className="w-4 h-4" />
                    {job.salary}
                  </span>
                  <span className="text-slate-500">{job.posted}</span>
                </div>

                <div className="flex flex-wrap gap-1.5 pt-1">
                  {job.tags.map((tag, i) => (
                    <span
                      key={i}
                      className="px-2.5 py-1 rounded-md text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700/50"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex items-center gap-3 self-stretch md:self-auto justify-end">
                <button
                  onClick={() => handleApply(job.id)}
                  disabled={isApplied}
                  className={`px-5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                    isApplied
                      ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                      : 'bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-500/20'
                  }`}
                >
                  {isApplied ? 'Application Submitted' : 'Quick Apply'}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
