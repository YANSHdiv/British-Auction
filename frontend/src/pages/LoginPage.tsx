import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Gavel, ShieldCheck, Truck, Building2, AlertCircle } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('password123');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (loginEmail?: string) => {
    setError(null);
    setLoading(true);
    try {
      await login(loginEmail || email, password);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (demoEmail: string) => {
    setEmail(demoEmail);
    handleLogin(demoEmail);
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-12">
      <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-2xl border border-slate-200 shadow-xl">
        <div className="text-center">
          <div className="w-12 h-12 rounded-xl bg-blue-700 text-white flex items-center justify-center mx-auto shadow-md">
            <Gavel className="w-6 h-6" />
          </div>
          <h2 className="mt-4 text-2xl font-black text-slate-900 tracking-tight">
            British Auction RFQ Console
          </h2>
          <p className="mt-1 text-xs text-slate-500 font-medium">
            Sign in to access your procurement auctions and bidding cockpit
          </p>
        </div>

        {error && (
          <div className="p-3.5 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0 text-rose-600" />
            <span>{error}</span>
          </div>
        )}

        <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); handleLogin(); }}>
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              Email Address
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="e.g. buyer@example.com"
              className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 px-4 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm shadow transition disabled:opacity-50"
          >
            {loading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>

        {/* Quick Demo Credentials Switcher */}
        <div className="pt-4 border-t border-slate-200">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-3 text-center">
            One-Click Demo Profiles
          </span>
          <div className="space-y-2">
            {/* Buyer */}
            <button
              type="button"
              onClick={() => handleQuickLogin('buyer@example.com')}
              className="w-full text-left p-2.5 rounded-lg border border-blue-200 bg-blue-50/60 hover:bg-blue-100/70 transition flex items-center justify-between"
            >
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-blue-700" />
                <div>
                  <span className="text-xs font-bold text-blue-900 block leading-tight">Alex Buyer (Buyer)</span>
                  <span className="text-[11px] text-blue-700">Global Freight Procurement</span>
                </div>
              </div>
              <span className="text-[11px] font-semibold text-blue-800 bg-blue-200/70 px-2 py-0.5 rounded">
                buyer@example.com
              </span>
            </button>

            {/* Supplier 1 */}
            <button
              type="button"
              onClick={() => handleQuickLogin('supplier1@example.com')}
              className="w-full text-left p-2.5 rounded-lg border border-emerald-200 bg-emerald-50/60 hover:bg-emerald-100/70 transition flex items-center justify-between"
            >
              <div className="flex items-center gap-2">
                <Truck className="w-4 h-4 text-emerald-700" />
                <div>
                  <span className="text-xs font-bold text-emerald-900 block leading-tight">John Swift (Supplier 1)</span>
                  <span className="text-[11px] text-emerald-700">Apex Freight Solutions</span>
                </div>
              </div>
              <span className="text-[11px] font-semibold text-emerald-800 bg-emerald-200/70 px-2 py-0.5 rounded">
                supplier1@example.com
              </span>
            </button>

            {/* Supplier 2 */}
            <button
              type="button"
              onClick={() => handleQuickLogin('supplier2@example.com')}
              className="w-full text-left p-2.5 rounded-lg border border-slate-200 bg-slate-50 hover:bg-slate-100 transition flex items-center justify-between"
            >
              <div className="flex items-center gap-2">
                <Truck className="w-4 h-4 text-slate-700" />
                <div>
                  <span className="text-xs font-bold text-slate-900 block leading-tight">Sarah Miller (Supplier 2)</span>
                  <span className="text-[11px] text-slate-600">BlueDart Express Cargo</span>
                </div>
              </div>
              <span className="text-[11px] font-semibold text-slate-700 bg-slate-200 px-2 py-0.5 rounded">
                supplier2@example.com
              </span>
            </button>

            {/* Supplier 3 */}
            <button
              type="button"
              onClick={() => handleQuickLogin('supplier3@example.com')}
              className="w-full text-left p-2.5 rounded-lg border border-slate-200 bg-slate-50 hover:bg-slate-100 transition flex items-center justify-between"
            >
              <div className="flex items-center gap-2">
                <Truck className="w-4 h-4 text-slate-700" />
                <div>
                  <span className="text-xs font-bold text-slate-900 block leading-tight">Michael Chang (Supplier 3)</span>
                  <span className="text-[11px] text-slate-600">Continental Shipping & Transit</span>
                </div>
              </div>
              <span className="text-[11px] font-semibold text-slate-700 bg-slate-200 px-2 py-0.5 rounded">
                supplier3@example.com
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
