import React from 'react';
import { SupplierRankingItem } from '../types';
import { Trophy, Award, Clock, DollarSign, Calendar } from 'lucide-react';
import { format } from 'date-fns';

interface Props {
  rankings: SupplierRankingItem[];
  currentUserId?: string;
}

export const RankingTable: React.FC<Props> = ({ rankings, currentUserId }) => {
  const formatCurrency = (val: string | number) => {
    const num = typeof val === 'string' ? parseFloat(val) : val;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(num || 0);
  };

  const formatDate = (dateStr: string) => {
    try {
      return format(new Date(dateStr), 'MMM d, yyyy HH:mm');
    } catch {
      return dateStr;
    }
  };

  if (!rankings || rankings.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-8 text-center">
        <Award className="w-12 h-12 text-slate-300 mx-auto mb-3" />
        <h4 className="text-base font-semibold text-slate-700">No Bids Placed Yet</h4>
        <p className="text-sm text-slate-500 mt-1 max-w-sm mx-auto">
          No supplier quotes have been submitted. Suppliers can place bids below to compete for L1 ranking.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <div className="bg-slate-50/80 px-6 py-4 border-b border-slate-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Trophy className="w-5 h-5 text-amber-500" />
          <h3 className="font-bold text-slate-800 text-base">Live Supplier Rankings</h3>
        </div>
        <span className="text-xs font-semibold text-slate-500">
          Ranked by Lowest Total Price (Tie-break: Earliest Submission)
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50/50 text-slate-500 text-xs uppercase font-semibold border-b border-slate-200">
            <tr>
              <th className="px-6 py-3.5">Rank</th>
              <th className="px-6 py-3.5">Supplier / Company</th>
              <th className="px-6 py-3.5 text-right">Total Price</th>
              <th className="px-6 py-3.5 text-right">Freight Charges</th>
              <th className="px-6 py-3.5 text-right">Origin / Dest</th>
              <th className="px-6 py-3.5 text-center">Transit Time</th>
              <th className="px-6 py-3.5">Quote Validity</th>
              <th className="px-6 py-3.5">Submitted</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {rankings.map((item) => {
              const isL1 = item.rank === 1;
              const isMe = currentUserId === item.supplier_id;

              return (
                <tr
                  key={item.supplier_id}
                  className={`transition-colors ${
                    isL1
                      ? 'bg-amber-50/40 hover:bg-amber-50/70 font-medium'
                      : isMe
                      ? 'bg-blue-50/30 hover:bg-blue-50/60'
                      : 'hover:bg-slate-50/80'
                  }`}
                >
                  {/* Rank Badge */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <span
                        className={`inline-flex items-center justify-center font-bold rounded-md px-2.5 py-1 text-xs shadow-xs ${
                          isL1
                            ? 'bg-amber-500 text-white ring-2 ring-amber-400/50'
                            : item.rank === 2
                            ? 'bg-slate-200 text-slate-700'
                            : item.rank === 3
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-slate-100 text-slate-600'
                        }`}
                      >
                        {item.rank_label}
                      </span>
                      {isL1 && (
                        <span className="inline-flex items-center gap-1 text-[11px] font-bold text-amber-700 bg-amber-100 px-2 py-0.5 rounded-full">
                          <Trophy className="w-3 h-3 text-amber-600" />
                          Lowest Bidder
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Supplier Company */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <span className="font-bold text-slate-900 block flex items-center gap-2">
                        {item.company_name}
                        {isMe && (
                          <span className="text-[10px] uppercase font-bold bg-blue-100 text-blue-800 px-1.5 py-0.2 rounded">
                            You
                          </span>
                        )}
                      </span>
                      <span className="text-xs text-slate-500">Contact: {item.supplier_name}</span>
                    </div>
                  </td>

                  {/* Total Amount */}
                  <td className="px-6 py-4 text-right whitespace-nowrap">
                    <span
                      className={`text-base font-extrabold font-mono ${
                        isL1 ? 'text-amber-700' : 'text-slate-900'
                      }`}
                    >
                      {formatCurrency(item.total_amount)}
                    </span>
                    <span className="text-[11px] text-slate-400 block">
                      {item.bid_count} {item.bid_count === 1 ? 'bid' : 'bids'} placed
                    </span>
                  </td>

                  {/* Freight Charges */}
                  <td className="px-6 py-4 text-right whitespace-nowrap font-mono text-slate-700">
                    {formatCurrency(item.freight_charges)}
                  </td>

                  {/* Origin & Dest */}
                  <td className="px-6 py-4 text-right whitespace-nowrap font-mono text-xs text-slate-600">
                    <div>Origin: {formatCurrency(item.origin_charges)}</div>
                    <div>Dest: {formatCurrency(item.destination_charges)}</div>
                  </td>

                  {/* Transit Time */}
                  <td className="px-6 py-4 text-center whitespace-nowrap">
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-slate-100 text-slate-700 text-xs font-semibold">
                      <Clock className="w-3 h-3 text-slate-500" />
                      {item.transit_time_days} {item.transit_time_days === 1 ? 'day' : 'days'}
                    </span>
                  </td>

                  {/* Quote Validity */}
                  <td className="px-6 py-4 whitespace-nowrap text-xs text-slate-600">
                    {formatDate(item.validity_date)}
                  </td>

                  {/* Submitted */}
                  <td className="px-6 py-4 whitespace-nowrap text-xs text-slate-500 font-mono">
                    {formatDate(item.submitted_at)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
