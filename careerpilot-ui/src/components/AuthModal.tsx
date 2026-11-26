import { useState, type FormEvent } from 'react';
import { X, Sparkles, AlertCircle, LogIn, UserPlus } from 'lucide-react';
import { authService } from '../services/api.ts';

interface AuthModalProps {
  onClose: () => void;
  onSuccess: (username: string) => void;
  initialMode?: 'signin' | 'register';
}

export default function AuthModal({ onClose, onSuccess, initialMode = 'signin' }: AuthModalProps) {
  const [isLogin, setIsLogin] = useState(initialMode === 'signin');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [usernameOrEmail, setUsernameOrEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');
    try {
      if (isLogin) {
        const res = await authService.login({ usernameOrEmail, password });
        localStorage.setItem('careerpilot_user', res.username);
        onSuccess(res.username);
      } else {
        const res = await authService.register({ username, email, password });
        localStorage.setItem('careerpilot_user', res.username);
        onSuccess(res.username);
      }
    } catch (err: any) {
      const serverMsg = err.response?.data?.message;
      if (serverMsg) {
        setErrorMsg(serverMsg);
      } else if (isLogin) {
        setErrorMsg('Invalid username/email or password. Please try again.');
      } else {
        setErrorMsg('Registration failed. Check if username or email is already taken.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="relative w-full max-w-md p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl space-y-5">
        <button onClick={onClose} className="absolute right-4 top-4 text-slate-400 hover:text-white transition-colors">
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="space-y-1">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-blue-400" />
            {isLogin ? 'Welcome Back to CareerPilot AI' : 'Join CareerPilot AI'}
          </h2>
          <p className="text-xs text-slate-400">
            {isLogin ? 'Sign in to access your matched jobs and ATS resumes.' : 'Create your account to save matched jobs and track applications.'}
          </p>
        </div>

        {/* Mode Tabs */}
        <div className="grid grid-cols-2 p-1 bg-slate-950 rounded-xl border border-slate-800">
          <button
            type="button"
            onClick={() => { setIsLogin(true); setErrorMsg(''); }}
            className={`flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-semibold transition-all ${
              isLogin ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20' : 'text-slate-400 hover:text-white'
            }`}
          >
            <LogIn className="w-3.5 h-3.5" />
            Sign In
          </button>
          <button
            type="button"
            onClick={() => { setIsLogin(false); setErrorMsg(''); }}
            className={`flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-semibold transition-all ${
              !isLogin ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20' : 'text-slate-400 hover:text-white'
            }`}
          >
            <UserPlus className="w-3.5 h-3.5" />
            Create Account
          </button>
        </div>

        {errorMsg && (
          <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3.5">
          {isLogin ? (
            /* Sign In Fields */
            <>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Username or Email</label>
                <input
                  type="text"
                  required
                  value={usernameOrEmail}
                  onChange={(e) => setUsernameOrEmail(e.target.value)}
                  placeholder="laxman or laxman@example.com"
                  className="w-full px-3.5 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-sm focus:outline-none focus:border-blue-500 transition-colors"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Password</label>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="w-full px-3.5 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-sm focus:outline-none focus:border-blue-500 transition-colors"
                />
              </div>
            </>
          ) : (
            /* Register Fields */
            <>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Username</label>
                <input
                  type="text"
                  required
                  minLength={3}
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="e.g. laxman235"
                  className="w-full px-3.5 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-sm focus:outline-none focus:border-blue-500 transition-colors"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="e.g. laxman@example.com"
                  className="w-full px-3.5 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-sm focus:outline-none focus:border-blue-500 transition-colors"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Password</label>
                <input
                  type="password"
                  required
                  minLength={8}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Minimum 8 characters"
                  className="w-full px-3.5 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-sm focus:outline-none focus:border-blue-500 transition-colors"
                />
              </div>
            </>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-lg text-sm font-semibold bg-blue-600 hover:bg-blue-500 text-white transition-all shadow-md shadow-blue-500/20 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? (
              <span>Authenticating with Spring Boot...</span>
            ) : isLogin ? (
              <>
                <LogIn className="w-4 h-4" />
                <span>Sign In</span>
              </>
            ) : (
              <>
                <UserPlus className="w-4 h-4" />
                <span>Create Account</span>
              </>
            )}
          </button>
        </form>

        <div className="text-center pt-2 border-t border-slate-800">
          {isLogin ? (
            <p className="text-xs text-slate-400">
              Don't have an account?{' '}
              <button
                type="button"
                onClick={() => { setIsLogin(false); setErrorMsg(''); }}
                className="text-blue-400 hover:underline font-medium"
              >
                Create Account
              </button>
            </p>
          ) : (
            <p className="text-xs text-slate-400">
              Already have an account?{' '}
              <button
                type="button"
                onClick={() => { setIsLogin(true); setErrorMsg(''); }}
                className="text-blue-400 hover:underline font-medium"
              >
                Sign In
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
