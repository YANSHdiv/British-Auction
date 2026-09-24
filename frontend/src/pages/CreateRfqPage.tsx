import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../services/api';
import { CreateRFQPayload, ExtensionTriggerType } from '../types';
import {
  PlusCircle,
  ChevronLeft,
  Calendar,
  Clock,
  Zap,
  ShieldAlert,
  AlertCircle,
  CheckCircle2,
} from 'lucide-react';

export const CreateRfqPage: React.FC = () => {
  const navigate = useNavigate();

  // Generate sensible default datetime strings in local format for datetime-local inputs
  const now = new Date();
  const formatInputDateTime = (date: Date) => {
    const pad = (n: number) => n.toString().padStart(2, '0');
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(
      date.getHours()
    )}:${pad(date.getMinutes())}`;
  };

  const defaultStart = new Date(now.getTime() - 5 * 60 * 1000); // 5 mins ago
  const defaultClose = new Date(now.getTime() + 25 * 60 * 1000); // 25 mins from now
  const defaultForcedClose = new Date(now.getTime() + 60 * 60 * 1000); // 60 mins from now
  const defaultPickup = new Date(now.getTime() + 5 * 24 * 60 * 60 * 1000); // 5 days from now

  const [name, setName] = useState('');
  const [referenceId, setReferenceId] = useState(`RFQ-${Date.now().toString().slice(-6)}`);
  const [pickupDate, setPickupDate] = useState(formatInputDateTime(defaultPickup));
  const [bidStartTime, setBidStartTime] = useState(formatInputDateTime(defaultStart));
  const [bidCloseTime, setBidCloseTime] = useState(formatInputDateTime(defaultClose));
  const [forcedBidCloseTime, setForcedBidCloseTime] = useState(formatInputDateTime(defaultForcedClose));

  // British Auction Configuration
  const [britishEnabled, setBritishEnabled] = useState(true);
  const [triggerWindowX, setTriggerWindowX] = useState<number>(10);
  const [extensionDurationY, setExtensionDurationY] = useState<number>(5);
  const [triggerType, setTriggerType] = useState<ExtensionTriggerType>('BID_RECEIVED');

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    const start = new Date(bidStartTime).getTime();
    const close = new Date(bidCloseTime).getTime();
    const forced = new Date(forcedBidCloseTime).getTime();

    // Validation rules
    if (close <= start) {
      setErrorMessage('Bid Close Date & Time must be strictly later than Bid Start Date & Time.');
      return;
    }

    if (forced <= close) {
      setErrorMessage('Rule Violation: Forced Bid Close Date & Time must always be greater than Bid Close Time.');
      return;
    }

    if (triggerWindowX < 0) {
      setErrorMessage('Trigger Window (X) must be non-negative.');
      return;
    }

    if (extensionDurationY <= 0) {
      setErrorMessage('Extension Duration (Y) must be greater than 0 minutes.');
      return;
    }

    setIsSubmitting(true);
    try {
      const payload: CreateRFQPayload = {
        name: name.trim(),
        reference_id: referenceId.trim(),
        pickup_service_date: new Date(pickupDate).toISOString(),
        bid_start_time: new Date(bidStartTime).toISOString(),
        bid_close_time: new Date(bidCloseTime).toISOString(),
        forced_bid_close_time: new Date(forcedBidCloseTime).toISOString(),
        auction_config: {
          british_auction_enabled: britishEnabled,
          trigger_window_minutes: triggerWindowX,
          extension_duration_minutes: extensionDurationY,
          extension_trigger_type: triggerType,
        },
      };

      const created = await api.createRfq(payload);
      navigate(`/auctions/${created.id}`);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to create RFQ.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div>
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-blue-600 uppercase tracking-wider mb-3 transition"
        >
          <ChevronLeft className="w-4 h-4" />
          Back to Auctions
        </Link>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
          Create New British Auction RFQ
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Configure service details, bidding timeline, and British Auction extension triggers.
        </p>
      </div>

      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-bold block">Validation Rule Failure</span>
            <span>{errorMessage}</span>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-8 bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 shadow-sm">
        {/* Section 1: RFQ Core Details */}
        <div>
          <h2 className="text-base font-bold text-slate-900 border-b border-slate-100 pb-2 mb-4">
            1. Procurement Service & Identification
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                RFQ Name *
              </label>
              <input
                type="text"
                required
                placeholder="e.g. Cross-Country Freight Chicago to Dallas"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Reference ID *
              </label>
              <input
                type="text"
                required
                placeholder="e.g. RFQ-2026-CHI-DAL"
                value={referenceId}
                onChange={(e) => setReferenceId(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="sm:col-span-2">
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Pickup / Service Date *
              </label>
              <input
                type="datetime-local"
                required
                value={pickupDate}
                onChange={(e) => setPickupDate(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Section 2: Bidding Timeline Governance */}
        <div>
          <h2 className="text-base font-bold text-slate-900 border-b border-slate-100 pb-2 mb-4">
            2. Auction Timeline & Boundary Governance
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Bid Start Date & Time *
              </label>
              <input
                type="datetime-local"
                required
                value={bidStartTime}
                onChange={(e) => setBidStartTime(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-[11px] text-slate-400 mt-1 block">Bidding opens to suppliers</span>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Bid Close Date & Time *
              </label>
              <input
                type="datetime-local"
                required
                value={bidCloseTime}
                onChange={(e) => setBidCloseTime(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-[11px] text-slate-400 mt-1 block">Scheduled close before extensions</span>
            </div>

            <div className="bg-rose-50/50 p-3 rounded-xl border border-rose-200">
              <label className="block text-xs font-bold text-rose-800 uppercase tracking-wider mb-1.5 flex items-center gap-1">
                <ShieldAlert className="w-3.5 h-3.5 text-rose-600" />
                Forced Bid Close Time *
              </label>
              <input
                type="datetime-local"
                required
                value={forcedBidCloseTime}
                onChange={(e) => setForcedBidCloseTime(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg border border-rose-300 text-sm focus:outline-none focus:ring-2 focus:ring-rose-500 bg-white"
              />
              <span className="text-[11px] text-rose-600 font-semibold mt-1 block">
                Rule: Must be &gt; Bid Close Time. Hard stop!
              </span>
            </div>
          </div>
        </div>

        {/* Section 3: British Auction Configuration */}
        <div>
          <div className="flex items-center justify-between border-b border-slate-100 pb-2 mb-4">
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Zap className="w-4 h-4 text-blue-600" />
              3. British Auction Configuration Options
            </h2>
            <label className="flex items-center gap-2 cursor-pointer text-xs font-bold text-slate-700">
              <input
                type="checkbox"
                checked={britishEnabled}
                onChange={(e) => setBritishEnabled(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500"
              />
              British Auction Enabled
            </label>
          </div>

          {britishEnabled && (
            <div className="space-y-6 bg-slate-50/70 p-6 rounded-xl border border-slate-200">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                {/* Trigger Window X */}
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                    Trigger Window (X Minutes) *
                  </label>
                  <input
                    type="number"
                    min="0"
                    required
                    value={triggerWindowX}
                    onChange={(e) => setTriggerWindowX(parseInt(e.target.value) || 0)}
                    className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  />
                  <p className="text-xs text-slate-500 mt-1.5">
                    Defines how close to the auction end the system monitors bidding activity.
                  </p>
                </div>

                {/* Extension Duration Y */}
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                    Extension Duration (Y Minutes) *
                  </label>
                  <input
                    type="number"
                    min="1"
                    required
                    value={extensionDurationY}
                    onChange={(e) => setExtensionDurationY(parseInt(e.target.value) || 1)}
                    className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  />
                  <p className="text-xs text-slate-500 mt-1.5">
                    Defines how much extra time is added when a qualifying trigger event occurs.
                  </p>
                </div>
              </div>

              {/* Extension Trigger Types */}
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  Extension Trigger Condition *
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {/* Trigger A */}
                  <div
                    onClick={() => setTriggerType('BID_RECEIVED')}
                    className={`p-4 rounded-xl border-2 cursor-pointer transition ${
                      triggerType === 'BID_RECEIVED'
                        ? 'border-blue-600 bg-blue-50/70 text-blue-900'
                        : 'border-slate-200 bg-white hover:border-slate-300 text-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold text-sm">Bid Received</span>
                      {triggerType === 'BID_RECEIVED' && (
                        <CheckCircle2 className="w-4 h-4 text-blue-600" />
                      )}
                    </div>
                    <p className="text-xs text-slate-500">
                      If any supplier submits a new bid during the trigger window X, auction extends by Y.
                    </p>
                  </div>

                  {/* Trigger B */}
                  <div
                    onClick={() => setTriggerType('ANY_RANK_CHANGE')}
                    className={`p-4 rounded-xl border-2 cursor-pointer transition ${
                      triggerType === 'ANY_RANK_CHANGE'
                        ? 'border-blue-600 bg-blue-50/70 text-blue-900'
                        : 'border-slate-200 bg-white hover:border-slate-300 text-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold text-sm">Any Rank Change</span>
                      {triggerType === 'ANY_RANK_CHANGE' && (
                        <CheckCircle2 className="w-4 h-4 text-blue-600" />
                      )}
                    </div>
                    <p className="text-xs text-slate-500">
                      If any change in supplier ranking occurs during the trigger window X, auction extends by Y.
                    </p>
                  </div>

                  {/* Trigger C */}
                  <div
                    onClick={() => setTriggerType('L1_RANK_CHANGE')}
                    className={`p-4 rounded-xl border-2 cursor-pointer transition ${
                      triggerType === 'L1_RANK_CHANGE'
                        ? 'border-blue-600 bg-blue-50/70 text-blue-900'
                        : 'border-slate-200 bg-white hover:border-slate-300 text-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold text-sm">Lowest Bidder (L1) Change</span>
                      {triggerType === 'L1_RANK_CHANGE' && (
                        <CheckCircle2 className="w-4 h-4 text-blue-600" />
                      )}
                    </div>
                    <p className="text-xs text-slate-500">
                      Auction extends only when the lowest-priced supplier (L1) changes in trigger window X.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Submit Button */}
        <div className="pt-4 border-t border-slate-100 flex items-center justify-end gap-3">
          <Link
            to="/"
            className="px-5 py-2.5 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 font-semibold text-sm transition"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={isSubmitting}
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm shadow transition disabled:opacity-50"
          >
            <PlusCircle className="w-4 h-4" />
            {isSubmitting ? 'Creating RFQ...' : 'Create & Publish RFQ'}
          </button>
        </div>
      </form>
    </div>
  );
};
