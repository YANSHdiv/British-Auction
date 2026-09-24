import React from 'react';
import { Bid } from '../types';
import { format } from 'date-fns';
import { ListOrdered, Truck, Calendar } from 'lucide-react';

interface Props {
  bids: Bid[];
  currentUserId?: string;
}

export const BidTable: React.FC<Props> = ({ bids, currentUserId }) => {
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
      return format(new Date(dateStr), 'MMM d, yyyy HH:mm:ss');
    } catch {
      return dateStr;
    }
  };

  if (!bids || bids.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <div className="bg-slate-50/80 px-6 py-4 border-b border-slate-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ListOrdered className="w-5 h-5 text-slate-600" />
          <h3 className="font-bold text-slate-800 text-base">Complete Bidding History</h3>
        </div>
        <span className="text-xs text-slate-500 font-medium">
          Total Quotes Submitted: {bids.length}
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50/50 text-slate-500 text-xs uppercase font-semibold border-b border-slate-200">
            <tr>
              <th className="px-6 py-3.5">Supplier / Carrier</th>
              <th className="px-6 py-3.5 text-right">Total Price</th>
              <th className="px-6 py-3.5 text-right">Freight Charges</th>
              <th className="px-6 py-3.5 text-right">Origin / Dest</th>
              <th className="px-6 py-3.5 text-center">Transit</th>
              <th className="px-6 py-3.5">Quote Validity</th>
              <th className="px-6 py-3.5">Timestamp</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {bids.map((bid) => {
              const isMe = currentUserId === bid.supplier_id;
              return (
                <tr
                  key={bid.id}
                  className={`hover:bg-slate-50/60 transition-colors ${
                    isMe ? 'bg-blue-50/20' : ''
                  }`}
                >
                  <td className="px-6 py-3.5 whitespace-nowrap">
                    <div>
                      <span className="font-semibold text-slate-900 block flex items-center gap-1.5">
                        <Truck className="w-3.5 h-3.5 text-slate-400" />
                        {bid.supplier?.company_name || 'Supplier'}
                        {isMe && (
                          <span className="text-[10px] uppercase font-bold bg-blue-100 text-blue-800 px-1 py-0.2 rounded">
                            You
                          </span>
                        )}
                      </span>
                      <span className="text-xs text-slate-500">Carrier: {bid.carrier_name}</span>
                    </div>
                  </td>
                  <td className="px-6 py-3.5 text-right whitespace-nowrap">
                    <span className="font-mono font-bold text-slate-900">
                      {formatCurrency(bid.total_amount)}
                    </span>
                  </td>
                  <td className="px-6 py-3.5 text-right whitespace-nowrap font-mono text-slate-600">
                    {formatCurrency(bid.freight_charges)}
                  </td>
                  <td className="px-6 py-3.5 text-right whitespace-nowrap font-mono text-xs text-slate-500">
                    <div>O: {formatCurrency(bid.origin_charges)}</div>
                    <div>D: {formatCurrency(bid.destination_charges)}</div>
                  </td>
                  <td className="px-6 py-3.5 text-center whitespace-nowrap text-xs text-slate-600">
                    {bid.transit_time_days} days
                  </td>
                  <td className="px-6 py-3.5 whitespace-nowrap text-xs text-slate-500">
                    {formatDate(bid.validity_date)}
                  </td>
                  <td className="px-6 py-3.5 whitespace-nowrap text-xs font-mono text-slate-400">
                    {formatDate(bid.created_at)}
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
