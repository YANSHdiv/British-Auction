import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { AuctionStatusBadge } from '../components/AuctionStatusBadge';
import { CountdownTimer } from '../components/CountdownTimer';
import { AuctionConfigCard } from '../components/AuctionConfigCard';
import { RankingTable } from '../components/RankingTable';
import { BidTable } from '../components/BidTable';
import { ActivityTimeline } from '../components/ActivityTimeline';
import { BidForm } from '../components/BidForm';
import { PriceEvolutionChart } from '../components/PriceEvolutionChart';
import { format } from 'date-fns';
import {
  ChevronLeft,
  Calendar,
  Building,
  RefreshCw,
  Trophy,
  ShieldAlert,
  Clock,
  Send,
} from 'lucide-react';

export const AuctionDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user, isSupplier } = useAuth();
  const queryClient = useQueryClient();

  if (!id) return <div>Invalid auction ID</div>;

  // 1. Fetch RFQ details (polls every 3s)
  const {
    data: rfq,
    isLoading: isRfqLoading,
    isRefetching: isRfqRefetching,
    refetch: refetchRfq,
  } = useQuery({
    queryKey: ['rfq', id],
    queryFn: () => api.getRfq(id),
    refetchInterval: 3000,
  });

  // 2. Fetch Supplier Rankings (polls every 3s)
  const {
    data: rankingsData,
    refetch: refetchRankings,
  } = useQuery({
    queryKey: ['rankings', id],
    queryFn: () => api.getAuctionRankings(id),
    refetchInterval: 3000,
  });

  // 3. Fetch All Bids (polls every 3s)
  const {
    data: bids = [],
    refetch: refetchBids,
  } = useQuery({
    queryKey: ['bids', id],
    queryFn: () => api.getAuctionBids(id),
    refetchInterval: 3000,
  });

  // 4. Fetch Activity Logs (polls every 3s)
  const {
    data: activities = [],
    refetch: refetchActivities,
  } = useQuery({
    queryKey: ['activities', id],
    queryFn: () => api.getAuctionActivity(id),
    refetchInterval: 3000,
  });

  // 5. Fetch Supplier's own current bid
  const {
    data: myCurrentBid = null,
    refetch: refetchMyBid,
  } = useQuery({
    queryKey: ['myBid', id, user?.id],
    queryFn: () => api.getMyBid(id),
    enabled: !!user && isSupplier,
    refetchInterval: 3000,
  });

  const handleBidSuccess = () => {
    // Invalidate and immediately refetch all queries
    queryClient.invalidateQueries({ queryKey: ['rfq', id] });
    queryClient.invalidateQueries({ queryKey: ['rankings', id] });
    queryClient.invalidateQueries({ queryKey: ['bids', id] });
    queryClient.invalidateQueries({ queryKey: ['activities', id] });
    queryClient.invalidateQueries({ queryKey: ['myBid', id, user?.id] });
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '';
    try {
      return format(new Date(dateStr), 'MMM d, yyyy HH:mm:ss');
    } catch {
      return dateStr;
    }
  };

  if (isRfqLoading || !rfq) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-slate-500">
        <RefreshCw className="w-8 h-8 animate-spin mx-auto text-blue-600 mb-2" />
        <p className="text-base font-semibold">Loading Auction Console...</p>
      </div>
    );
  }

  const isAuctionActive = rfq.effective_status === 'ACTIVE';

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Back button & Title Header */}
      <div>
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-blue-600 uppercase tracking-wider mb-3 transition"
        >
          <ChevronLeft className="w-4 h-4" />
          Back to Auctions Dashboard
        </Link>

        <div className="bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 shadow-sm space-y-6">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-100 pb-6">
            <div>
              <div className="flex items-center gap-3">
                <span className="font-mono text-xs font-bold text-blue-800 bg-blue-100/70 border border-blue-200 px-2.5 py-1 rounded">
                  {rfq.reference_id}
                </span>
                <AuctionStatusBadge status={rfq.effective_status} size="lg" />
                {isRfqRefetching && (
                  <RefreshCw className="w-4 h-4 text-blue-500 animate-spin" />
                )}
              </div>
              <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight mt-2">
                {rfq.name}
              </h1>
            </div>

            {/* Countdown Box */}
            {isAuctionActive && (
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 flex flex-col items-start lg:items-end">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">
                  Bidding Close Countdown
                </span>
                <CountdownTimer
                  targetTime={rfq.current_close_time}
                  forcedCloseTime={rfq.forced_bid_close_time}
                  triggerWindowMinutes={rfq.auction_config?.trigger_window_minutes || 10}
                />
              </div>
            )}
          </div>

          {/* Key Dates Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-slate-500 block font-medium mb-1">Pickup / Service Date:</span>
              <span className="font-bold text-slate-800 flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-slate-400" />
                {formatDate(rfq.pickup_service_date)}
              </span>
            </div>

            <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-slate-500 block font-medium mb-1">Bid Start Time:</span>
              <span className="font-bold text-slate-800 flex items-center gap-1.5 font-mono">
                <Clock className="w-3.5 h-3.5 text-slate-400" />
                {formatDate(rfq.bid_start_time)}
              </span>
            </div>

            <div className="p-3 rounded-lg bg-blue-50/60 border border-blue-100">
              <span className="text-blue-700 block font-bold mb-1">Current Bid Close Time:</span>
              <span className="font-bold text-blue-900 flex items-center gap-1.5 font-mono">
                <Clock className="w-3.5 h-3.5 text-blue-600" />
                {formatDate(rfq.current_close_time)}
              </span>
            </div>

            <div className="p-3 rounded-lg bg-rose-50/60 border border-rose-100">
              <span className="text-rose-700 block font-bold mb-1 flex items-center gap-1">
                <ShieldAlert className="w-3 h-3 text-rose-600" />
                Forced Close (Hard Limit):
              </span>
              <span className="font-bold text-rose-900 flex items-center gap-1.5 font-mono">
                <Clock className="w-3.5 h-3.5 text-rose-600" />
                {formatDate(rfq.forced_bid_close_time)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* British Auction Config Card */}
      <AuctionConfigCard rfq={rfq} config={rfq.auction_config} />

      {/* Main Content Layout: Rankings & Bid Form */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          {/* Supplier Rankings Table (Primary) */}
          <RankingTable
            rankings={rankingsData?.rankings || []}
            currentUserId={user?.id}
          />

          {/* Price Evolution Chart */}
          <PriceEvolutionChart bids={bids} />

          {/* Full Bids History Table */}
          <BidTable bids={bids} currentUserId={user?.id} />
        </div>

        {/* Sidebar: Bidding Cockpit & Activity */}
        <div className="space-y-8">
          {/* Supplier Bid Submission Form */}
          {isSupplier ? (
            <BidForm
              rfqId={rfq.id}
              myCurrentBid={myCurrentBid}
              auctionStatus={rfq.effective_status}
              onBidSuccess={handleBidSuccess}
            />
          ) : (
            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
              <div className="flex items-center gap-2 mb-2 text-slate-800">
                <Building className="w-5 h-5 text-blue-600" />
                <h4 className="font-bold text-sm">Buyer Observation Mode</h4>
              </div>
              <p className="text-xs text-slate-500 leading-relaxed">
                You are viewing this auction as the procuring buyer. Suppliers can submit competitive lower bids below. You can monitor live ranking changes, trigger events, and automatic extensions in real time.
              </p>
            </div>
          )}

          {/* Activity & Extension Timeline */}
          <ActivityTimeline activities={activities} />
        </div>
      </div>
    </div>
  );
};
