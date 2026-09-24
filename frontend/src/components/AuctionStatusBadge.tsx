import React from 'react';
import { RFQStatus } from '../types';
import { Clock, CheckCircle2, AlertTriangle, Lock, FileText } from 'lucide-react';

interface Props {
  status: RFQStatus;
  size?: 'sm' | 'md' | 'lg';
}

export const AuctionStatusBadge: React.FC<Props> = ({ status, size = 'md' }) => {
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
    lg: 'text-sm px-3 py-1.5',
  };

  switch (status) {
    case 'ACTIVE':
      return (
        <span className={`inline-flex items-center gap-1.5 font-semibold rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 ${sizeClasses[size]}`}>
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
          Active Auction
        </span>
      );
    case 'SCHEDULED':
      return (
        <span className={`inline-flex items-center gap-1.5 font-semibold rounded-full bg-blue-50 text-blue-700 border border-blue-200 ${sizeClasses[size]}`}>
          <Clock className="w-3.5 h-3.5 text-blue-500" />
          Scheduled
        </span>
      );
    case 'CLOSED':
      return (
        <span className={`inline-flex items-center gap-1.5 font-semibold rounded-full bg-slate-100 text-slate-700 border border-slate-200 ${sizeClasses[size]}`}>
          <CheckCircle2 className="w-3.5 h-3.5 text-slate-500" />
          Closed
        </span>
      );
    case 'FORCE_CLOSED':
      return (
        <span className={`inline-flex items-center gap-1.5 font-semibold rounded-full bg-rose-50 text-rose-700 border border-rose-200 ${sizeClasses[size]}`}>
          <Lock className="w-3.5 h-3.5 text-rose-500" />
          Force Closed
        </span>
      );
    case 'DRAFT':
    default:
      return (
        <span className={`inline-flex items-center gap-1.5 font-semibold rounded-full bg-gray-100 text-gray-700 border border-gray-200 ${sizeClasses[size]}`}>
          <FileText className="w-3.5 h-3.5 text-gray-500" />
          Draft
        </span>
      );
  }
};
