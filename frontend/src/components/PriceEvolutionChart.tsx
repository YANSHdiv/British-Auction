import React from 'react';
import { Bid } from '../types';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { format } from 'date-fns';
import { TrendingDown } from 'lucide-react';

interface Props {
  bids: Bid[];
}

export const PriceEvolutionChart: React.FC<Props> = ({ bids }) => {
  if (!bids || bids.length < 2) {
    return null;
  }

  // Reverse so chronological order (earliest to latest)
  const sortedChronological = [...bids].sort(
    (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
  );

  const data = sortedChronological.map((b, idx) => ({
    index: idx + 1,
    time: format(new Date(b.created_at), 'HH:mm:ss'),
    amount: parseFloat(b.total_amount.toString()),
    supplier: b.supplier?.company_name || 'Supplier',
  }));

  const formatTooltipValue = (value: any) => {
    return [`$${Number(value).toLocaleString()}`, 'Total Price'];
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <TrendingDown className="w-5 h-5 text-emerald-600" />
          <h3 className="font-bold text-slate-800 text-base">Auction Price Evolution</h3>
        </div>
        <span className="text-xs text-slate-500 font-medium">
          Downward competitive bidding trajectory
        </span>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 20, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="time" stroke="#94a3b8" fontSize={11} tickLine={false} />
            <YAxis
              stroke="#94a3b8"
              fontSize={11}
              tickLine={false}
              tickFormatter={(v) => `$${v.toLocaleString()}`}
            />
            <Tooltip
              formatter={formatTooltipValue}
              labelFormatter={(label) => `Submitted At: ${label}`}
              contentStyle={{
                backgroundColor: '#ffffff',
                borderColor: '#e2e8f0',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                fontSize: '12px',
              }}
            />
            <Line
              type="monotone"
              dataKey="amount"
              stroke="#0284c7"
              strokeWidth={2.5}
              dot={{ r: 4, fill: '#0284c7' }}
              activeDot={{ r: 6, fill: '#0369a1' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
