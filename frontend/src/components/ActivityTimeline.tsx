import React from 'react';
import { ActivityLog } from '../types';
import { format } from 'date-fns';
import { History, Zap, CheckCircle2, Lock, ArrowRight, Clock, PlusCircle } from 'lucide-react';

interface Props {
  activities: ActivityLog[];
}

export const ActivityTimeline: React.FC<Props> = ({ activities }) => {
  const formatDate = (dateStr: string) => {
    try {
      return format(new Date(dateStr), 'MMM d, yyyy HH:mm:ss');
    } catch {
      return dateStr;
    }
  };

  const formatShortTime = (dateStr: string) => {
    try {
      return format(new Date(dateStr), 'HH:mm:ss');
    } catch {
      return dateStr;
    }
  };

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'AUCTION_EXTENDED':
        return (
          <div className="w-8 h-8 rounded-full bg-amber-500 text-white flex items-center justify-center shadow-sm">
            <Zap className="w-4 h-4" />
          </div>
        );
      case 'BID_SUBMITTED':
        return (
          <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center shadow-sm">
            <Clock className="w-4 h-4" />
          </div>
        );
      case 'AUCTION_FORCE_CLOSED':
        return (
          <div className="w-8 h-8 rounded-full bg-rose-600 text-white flex items-center justify-center shadow-sm">
            <Lock className="w-4 h-4" />
          </div>
        );
      case 'AUCTION_CLOSED':
        return (
          <div className="w-8 h-8 rounded-full bg-slate-600 text-white flex items-center justify-center shadow-sm">
            <CheckCircle2 className="w-4 h-4" />
          </div>
        );
      case 'RFQ_CREATED':
      default:
        return (
          <div className="w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center shadow-sm">
            <PlusCircle className="w-4 h-4" />
          </div>
        );
    }
  };

  if (!activities || activities.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-8 text-center text-slate-500">
        <History className="w-8 h-8 mx-auto text-slate-300 mb-2" />
        <p className="text-sm">No activity recorded for this auction yet.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <div className="bg-slate-50/80 px-6 py-4 border-b border-slate-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <History className="w-5 h-5 text-blue-600" />
          <h3 className="font-bold text-slate-800 text-base">Auction Activity & Extension Log</h3>
        </div>
        <span className="text-xs text-slate-500 font-medium">
          {activities.length} Recorded Events
        </span>
      </div>

      <div className="p-6">
        <div className="relative border-l-2 border-slate-200 ml-4 pl-6 space-y-6">
          {activities.map((act) => {
            const isExtension = act.event_type === 'AUCTION_EXTENDED';
            const isBid = act.event_type === 'BID_SUBMITTED';

            return (
              <div key={act.id} className="relative group">
                {/* Timeline node icon */}
                <div className="absolute -left-[39px] top-0">
                  {getEventIcon(act.event_type)}
                </div>

                <div className={`p-4 rounded-lg border transition-all ${
                  isExtension
                    ? 'bg-amber-50/60 border-amber-200'
                    : 'bg-white border-slate-200 hover:border-slate-300'
                }`}>
                  <div className="flex flex-wrap items-center justify-between gap-2 mb-1.5">
                    <span className={`text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded ${
                      isExtension
                        ? 'bg-amber-200 text-amber-900'
                        : isBid
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-slate-100 text-slate-800'
                    }`}>
                      {act.event_type.replace('_', ' ')}
                    </span>
                    <span className="text-xs text-slate-400 font-mono">
                      {formatDate(act.created_at)}
                    </span>
                  </div>

                  {/* Extension Reason & Time Shift */}
                  {isExtension && (
                    <div className="mt-2 space-y-2">
                      <p className="text-sm font-semibold text-amber-950 leading-snug">
                        {act.extension_reason}
                      </p>

                      {act.old_close_time && act.new_close_time && (
                        <div className="inline-flex items-center gap-2 bg-amber-100/70 border border-amber-300 text-amber-900 px-3 py-1.5 rounded font-mono text-xs">
                          <span>Old Close: {formatShortTime(act.old_close_time)}</span>
                          <ArrowRight className="w-3.5 h-3.5 text-amber-600" />
                          <span className="font-bold">New Close: {formatShortTime(act.new_close_time)}</span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Bid Submission Details */}
                  {isBid && (
                    <div className="mt-1">
                      <p className="text-sm text-slate-800">
                        <span className="font-semibold text-slate-900">{act.supplier_name || 'Supplier'}</span>{' '}
                        submitted quote of{' '}
                        <span className="font-mono font-bold text-blue-700">
                          ${parseFloat(act.metadata_json?.total_amount || '0').toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </span>
                        {act.metadata_json?.rank_label && (
                          <span className="ml-2 font-bold text-xs bg-slate-100 border border-slate-300 px-1.5 py-0.5 rounded">
                            Assigned Rank: {act.metadata_json.rank_label}
                          </span>
                        )}
                      </p>
                    </div>
                  )}

                  {/* General / System Details */}
                  {!isExtension && !isBid && (
                    <p className="text-sm text-slate-600 mt-1">
                      {act.extension_reason || act.metadata_json?.details || 'System event recorded.'}
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
