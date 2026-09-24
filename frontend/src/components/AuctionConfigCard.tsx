import React from 'react';
import { AuctionConfiguration, RFQ } from '../types';
import { Settings, RefreshCw, Zap, ShieldAlert, Calendar } from 'lucide-react';
import { format } from 'date-fns';

interface Props {
  rfq: RFQ;
  config?: AuctionConfiguration;
}

export const AuctionConfigCard: React.FC<Props> = ({ rfq, config }) => {
  if (!config) return null;

  const getTriggerLabel = (type: string) => {
    switch (type) {
      case 'BID_RECEIVED':
        return 'Bid Received in Last X Minutes';
      case 'ANY_RANK_CHANGE':
        return 'Any Supplier Rank Change in Last X Minutes';
      case 'L1_RANK_CHANGE':
        return 'Lowest Bidder (L1) Rank Change in Last X Minutes';
      default:
        return type;
    }
  };

  const getTriggerDescription = (type: string) => {
    switch (type) {
      case 'BID_RECEIVED':
        return 'Extends the auction whenever any supplier submits a valid competitive bid during the trigger window.';
      case 'ANY_RANK_CHANGE':
        return 'Extends the auction whenever a bid changes the relative ranking of any competing supplier.';
      case 'L1_RANK_CHANGE':
        return 'Extends the auction only when the lowest-priced supplier (L1 position) is displaced by a new bidder.';
      default:
        return '';
    }
  };

  const formatDate = (dateStr: string) => {
    try {
      return format(new Date(dateStr), 'MMM d, yyyy HH:mm:ss');
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <div className="bg-slate-50/80 px-6 py-4 border-b border-slate-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Settings className="w-5 h-5 text-blue-600" />
          <h3 className="font-bold text-slate-800 text-base">British Auction Dynamic Extension Rules</h3>
        </div>
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
          <Zap className="w-3.5 h-3.5 text-blue-500" />
          British Auction Active
        </span>
      </div>

      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          {/* X Window */}
          <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
              Trigger Window (X)
            </span>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-black text-slate-900">{config.trigger_window_minutes}</span>
              <span className="text-sm font-medium text-slate-600">Minutes</span>
            </div>
            <p className="text-xs text-slate-500 mt-2">
              Bidding monitored during the final {config.trigger_window_minutes} minutes before bid close.
            </p>
          </div>

          {/* Y Duration */}
          <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
              Extension Duration (Y)
            </span>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-black text-slate-900">{config.extension_duration_minutes}</span>
              <span className="text-sm font-medium text-slate-600">Minutes Added</span>
            </div>
            <p className="text-xs text-slate-500 mt-2">
              Auction time extends by {config.extension_duration_minutes}m per qualifying trigger event.
            </p>
          </div>

          {/* Extension Count */}
          <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
              Extensions Applied
            </span>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-black text-blue-600">{config.extension_count}</span>
              <span className="text-sm font-medium text-slate-600">Times Extended</span>
            </div>
            <p className="text-xs text-slate-500 mt-2">
              Total extensions granted so far during active bidding.
            </p>
          </div>
        </div>

        {/* Selected Trigger Type Banner */}
        <div className="p-4 rounded-lg bg-blue-50/50 border border-blue-100 flex items-start gap-3 mb-6">
          <Zap className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
          <div>
            <span className="text-xs font-bold text-blue-900 uppercase tracking-wider block">
              Configured Trigger Condition
            </span>
            <span className="text-sm font-bold text-slate-900 block mt-0.5">
              {getTriggerLabel(config.extension_trigger_type)}
            </span>
            <p className="text-xs text-slate-600 mt-1">
              {getTriggerDescription(config.extension_trigger_type)}
            </p>
          </div>
        </div>

        {/* Hard Limit / Boundary Times Table */}
        <div className="border-t border-slate-100 pt-4 grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
          <div>
            <span className="text-slate-500 block mb-0.5 font-medium">Initial Bid Close Time:</span>
            <span className="font-semibold text-slate-800 font-mono">{formatDate(rfq.bid_close_time)}</span>
          </div>
          <div>
            <span className="text-slate-500 block mb-0.5 font-medium">Current Extended Close Time:</span>
            <span className="font-bold text-blue-700 font-mono">{formatDate(config.current_close_time)}</span>
          </div>
          <div>
            <span className="text-rose-600 flex items-center gap-1 mb-0.5 font-semibold">
              <ShieldAlert className="w-3.5 h-3.5" />
              Forced Bid Close Time (Hard Limit):
            </span>
            <span className="font-bold text-rose-700 font-mono">{formatDate(rfq.forced_bid_close_time)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
