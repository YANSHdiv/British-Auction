import React from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle, ArrowLeft } from 'lucide-react';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center text-center px-4">
      <AlertTriangle className="w-16 h-16 text-amber-500 mb-4" />
      <h1 className="text-3xl font-black text-slate-900 tracking-tight">404 - Page Not Found</h1>
      <p className="text-sm text-slate-500 mt-2 max-w-sm">
        The requested page does not exist or you do not have permission to view it.
      </p>
      <Link
        to="/"
        className="mt-6 inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-blue-600 text-white font-bold text-sm hover:bg-blue-700 transition"
      >
        <ArrowLeft className="w-4 h-4" />
        Return to Auctions Dashboard
      </Link>
    </div>
  );
};
