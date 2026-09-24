import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Gavel, PlusCircle, LogOut, User as UserIcon, Building2 } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout, isBuyer } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Brand Logo & Name */}
          <div className="flex items-center gap-6">
            <Link to="/" className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-lg bg-blue-700 flex items-center justify-center text-white shadow">
                <Gavel className="w-5 h-5" />
              </div>
              <div>
                <span className="font-bold text-lg text-slate-900 tracking-tight block leading-tight">
                  British Auction
                </span>
                <span className="text-xs text-slate-500 font-medium tracking-wide uppercase">
                  RFQ Procurement Platform
                </span>
              </div>
            </Link>

            <nav className="hidden md:flex items-center gap-4 pl-4 border-l border-slate-200">
              <Link
                to="/"
                className="text-sm font-semibold text-slate-700 hover:text-blue-600 transition-colors"
              >
                Auctions Listing
              </Link>
              {isBuyer && (
                <Link
                  to="/create-rfq"
                  className="inline-flex items-center gap-1.5 text-sm font-semibold text-blue-600 hover:text-blue-700 transition-colors"
                >
                  <PlusCircle className="w-4 h-4" />
                  Create RFQ
                </Link>
              )}
            </nav>
          </div>

          {/* Right Header: User profile & Actions */}
          <div className="flex items-center gap-4">
            {user ? (
              <div className="flex items-center gap-3">
                <div className="hidden sm:flex flex-col text-right">
                  <span className="text-sm font-semibold text-slate-800 flex items-center justify-end gap-1.5">
                    <UserIcon className="w-3.5 h-3.5 text-slate-400" />
                    {user.full_name}
                  </span>
                  <span className="text-xs text-slate-500 flex items-center justify-end gap-1">
                    <Building2 className="w-3 h-3 text-slate-400" />
                    {user.company_name}
                  </span>
                </div>

                {/* Role Pill */}
                <span
                  className={`text-xs font-bold uppercase px-2.5 py-1 rounded-md border ${
                    user.role === 'BUYER'
                      ? 'bg-blue-50 text-blue-700 border-blue-200'
                      : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  }`}
                >
                  {user.role}
                </span>

                <button
                  onClick={handleLogout}
                  title="Sign out"
                  className="p-2 text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-lg border border-slate-200 transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <Link
                to="/login"
                className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 shadow-sm transition"
              >
                Sign In
              </Link>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
