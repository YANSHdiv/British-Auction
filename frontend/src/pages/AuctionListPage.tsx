import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { RFQ } from '../types';
import { AuctionStatusBadge } from '../components/AuctionStatusBadge';
import { CountdownTimer } from '../components/CountdownTimer';
import { useAuth } from '../context/AuthContext';
import { format } from 'date-fns';
import {
  Gavel,
  Search,
  Filter,
  PlusCircle,
  Clock,
  ArrowRight,
  TrendingDown,
  Building,
  RefreshCw,
  Users,
} from 'lucide-react';

export const AuctionListPage: React.FC = () => {
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const { isBuyer } = useAuth();

  // Poll list every 4 seconds for live updates
  const {
    data: rfqs = [],
    isLoading,
    isRefetching,
    refetch,
  } = useQuery({
    queryKey: ['rfqs', selectedStatus],
    queryFn: () => api.listRfqs(selectedStatus),
    refetchInterval: 4000,
  });

  const formatCurrency = (val: string | number | null) => {
    if (val === null || val === undefined) return 'No Bids';
    const num = typeof val === 'string' ? parseFloat(val) : val;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(num);
  };

  const formatDate = (dateStr: string) => {
    try {
      return format(new Date(dateStr), 'MMM d, yyyy HH:mm');
    } catch {
      return dateStr;
    }
  };

  const filteredRfqs = rfqs.filter((r) => {
    const query = searchQuery.toLowerCase();
    return (
      r.name.toLowerCase().includes(query) ||
      r.reference_id.toLowerCase().includes(query)
    );
  });

  const statusTabs = [
    { id: 'ALL', label: 'All Auctions' },
    { id: 'ACTIVE', label: 'Active' },
    { id: 'SCHEDULED', label: 'Scheduled' },
    { id: 'CLOSED', label: 'Closed' },
    { id: 'FORCE_CLOSED', label: 'Force Closed' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Top Banner / Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">
              Procurement Auctions Console
            </h1>
            {isRefetching && (
              <RefreshCw className="w-4 h-4 text-blue-500 animate-spin" />
            )}
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Real-time British Reverse Auctions with automated dynamic extensions and strict forced-close governance.
          </p>
        </div>

        {isBuyer && (
          <Link
            to="/create-rfq"
            className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm shadow transition"
          >
            <PlusCircle className="w-4 h-4" />
            Create British Auction RFQ
          </Link>
        )}
      </div>

      {/* Filter Tabs & Search Bar */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
        {/* Status Tabs */}
        <div className="flex items-center gap-1.5 p-1 bg-slate-200/70 rounded-xl overflow-x-auto text-xs font-bold">
          {statusTabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSelectedStatus(tab.id)}
              className={`px-3 py-2 rounded-lg transition whitespace-nowrap ${
                selectedStatus === tab.id
                  ? 'bg-white text-slate-900 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/50'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <div className="relative min-w-[280px]">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search RFQ name or ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          />
        </div>
      </div>

      {/* Auction List Table / Cards */}
      {isLoading ? (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center text-slate-500">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto text-blue-600 mb-2" />
          <p className="text-sm font-medium">Loading live auctions...</p>
        </div>
      ) : filteredRfqs.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center text-slate-500">
          <Gavel className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-700">No Auctions Found</h3>
          <p className="text-sm text-slate-500 mt-1">
            No British Auctions match your selected filters.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-slate-500 text-xs uppercase font-semibold border-b border-slate-200">
                <tr>
                  <th className="px-6 py-4">RFQ Name & Reference</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 text-right">Current Lowest Bid (L1)</th>
                  <th className="px-6 py-4">Time Remaining / Countdown</th>
                  <th className="px-6 py-4">Current Close Time</th>
                  <th className="px-6 py-4">Forced Close Time</th>
                  <th className="px-6 py-4 text-center">Bids / Suppliers</th>
                  <th className="px-6 py-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredRfqs.map((rfq) => {
                  const isActive = rfq.effective_status === 'ACTIVE';

                  return (
                    <tr
                      key={rfq.id}
                      className="hover:bg-slate-50/80 transition-colors group"
                    >
                      {/* Name & Reference */}
                      <td className="px-6 py-4">
                        <div>
                          <Link
                            to={`/auctions/${rfq.id}`}
                            className="font-bold text-slate-900 group-hover:text-blue-600 text-sm block"
                          >
                            {rfq.name}
                          </Link>
                          <span className="text-xs font-mono font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200 mt-1 inline-block">
                            {rfq.reference_id}
                          </span>
                        </div>
                      </td>

                      {/* Status */}
                      <td className="px-6 py-4 whitespace-nowrap">
                        <AuctionStatusBadge status={rfq.effective_status} />
                      </td>

                      {/* Lowest Bid Amount */}
                      <td className="px-6 py-4 text-right whitespace-nowrap">
                        {rfq.lowest_bid_amount !== null ? (
                          <div>
                            <span className="text-base font-extrabold font-mono text-emerald-700">
                              {formatCurrency(rfq.lowest_bid_amount)}
                            </span>
                            <span className="text-[11px] text-emerald-600 block font-semibold flex items-center justify-end gap-1">
                              <TrendingDown className="w-3 h-3" /> Lowest Price
                            </span>
                          </div>
                        ) : (
                          <span className="text-xs text-slate-400 italic">No Bids Yet</span>
                        )}
                      </td>

                      {/* Countdown */}
                      <td className="px-6 py-4 whitespace-nowrap">
                        {isActive ? (
                          <CountdownTimer
                            targetTime={rfq.current_close_time}
                            forcedCloseTime={rfq.forced_bid_close_time}
                            triggerWindowMinutes={rfq.auction_config?.trigger_window_minutes || 10}
                          />
                        ) : (
                          <span className="text-xs font-medium text-slate-400">
                            {rfq.effective_status === 'SCHEDULED' ? 'Starts soon' : 'Auction Finished'}
                          </span>
                        )}
                      </td>

                      {/* Current Bid Close */}
                      <td className="px-6 py-4 whitespace-nowrap text-xs font-mono text-slate-700">
                        <div>{formatDate(rfq.current_close_time)}</div>
                        {rfq.auction_config && rfq.auction_config.extension_count > 0 && (
                          <span className="text-[10px] font-bold text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200 mt-0.5 inline-block">
                            +{rfq.auction_config.extension_count}x extended
                          </span>
                        )}
                      </td>

                      {/* Forced Close */}
                      <td className="px-6 py-4 whitespace-nowrap text-xs font-mono text-rose-700 font-semibold">
                        {formatDate(rfq.forced_bid_close_time)}
                      </td>

                      {/* Bids & Suppliers Count */}
                      <td className="px-6 py-4 text-center whitespace-nowrap text-xs">
                        <span className="inline-flex items-center gap-1 font-semibold text-slate-700 bg-slate-100 px-2 py-1 rounded">
                          <Users className="w-3 h-3 text-slate-500" />
                          {rfq.bid_count} {rfq.bid_count === 1 ? 'bid' : 'bids'} ({rfq.supplier_count} sup)
                        </span>
                      </td>

                      {/* View Action */}
                      <td className="px-6 py-4 text-right whitespace-nowrap">
                        <Link
                          to={`/auctions/${rfq.id}`}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 group-hover:bg-blue-600 text-slate-700 group-hover:text-white font-bold text-xs transition"
                        >
                          <span>Console</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
