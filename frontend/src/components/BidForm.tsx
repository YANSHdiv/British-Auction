import React, { useState, useMemo } from 'react';
import { SupplierRankingItem, CreateBidPayload, RFQStatus } from '../types';
import { api } from '../services/api';
import { Send, DollarSign, AlertCircle, CheckCircle2, TrendingDown } from 'lucide-react';

interface Props {
  rfqId: string;
  myCurrentBid: SupplierRankingItem | null;
  auctionStatus: RFQStatus;
  onBidSuccess: () => void;
}

export const BidForm: React.FC<Props> = ({
  rfqId,
  myCurrentBid,
  auctionStatus,
  onBidSuccess,
}) => {
  const [carrierName, setCarrierName] = useState('');
  const [freightCharges, setFreightCharges] = useState<string>('');
  const [originCharges, setOriginCharges] = useState<string>('');
  const [destinationCharges, setDestinationCharges] = useState<string>('');
  const [transitTimeDays, setTransitTimeDays] = useState<number>(2);
  const [validityDate, setValidityDate] = useState<string>(
    new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  );

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Live total calculation
  const totalAmount = useMemo(() => {
    const f = parseFloat(freightCharges) || 0;
    const o = parseFloat(originCharges) || 0;
    const d = parseFloat(destinationCharges) || 0;
    return f + o + d;
  }, [freightCharges, originCharges, destinationCharges]);

  // Validation against previous bid
  const previousBestAmount = myCurrentBid ? parseFloat(myCurrentBid.total_amount.toString()) : null;
  const isLowerThanPrevious = previousBestAmount === null || (totalAmount > 0 && totalAmount < previousBestAmount);

  const isAuctionActive = auctionStatus === 'ACTIVE';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setSuccessMessage(null);

    if (!isAuctionActive) {
      setErrorMessage(`Cannot place bid. Auction status is ${auctionStatus}.`);
      return;
    }

    if (!carrierName.trim()) {
      setErrorMessage('Carrier Name is required.');
      return;
    }

    if (totalAmount <= 0) {
      setErrorMessage('Total bid amount must be greater than $0.00.');
      return;
    }

    if (previousBestAmount !== null && totalAmount >= previousBestAmount) {
      setErrorMessage(
        `British Auction Rule Violation: Your new bid ($${totalAmount.toLocaleString()}) must be strictly lower than your previous best bid ($${previousBestAmount.toLocaleString()}).`
      );
      return;
    }

    setIsSubmitting(true);
    try {
      const payload: CreateBidPayload = {
        carrier_name: carrierName.trim(),
        freight_charges: parseFloat(freightCharges) || 0,
        origin_charges: parseFloat(originCharges) || 0,
        destination_charges: parseFloat(destinationCharges) || 0,
        transit_time_days: transitTimeDays,
        validity_date: new Date(validityDate).toISOString(),
      };

      await api.submitBid(rfqId, payload);
      setSuccessMessage(`Bid of $${totalAmount.toLocaleString(undefined, { minimumFractionDigits: 2 })} submitted successfully!`);
      // Clear charges to encourage next lower bid if desired
      setFreightCharges('');
      setOriginCharges('');
      setDestinationCharges('');
      onBidSuccess();
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to submit bid.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <div className="bg-slate-50/80 px-6 py-4 border-b border-slate-200 flex items-center justify-between">
        <div>
          <h3 className="font-bold text-slate-800 text-base">Submit Competitive Quote</h3>
          <p className="text-xs text-slate-500 mt-0.5">
            British Auction Rules: Each new quote must beat your previous best price.
          </p>
        </div>
        {myCurrentBid && (
          <div className="text-right">
            <span className="text-xs text-slate-500 block">Your Current Status:</span>
            <div className="inline-flex items-center gap-1.5 font-bold text-sm">
              <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded text-xs">
                {myCurrentBid.rank_label}
              </span>
              <span className="font-mono text-slate-900">
                ${parseFloat(myCurrentBid.total_amount.toString()).toLocaleString(undefined, { minimumFractionDigits: 2 })}
              </span>
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="p-6 space-y-5">
        {errorMessage && (
          <div className="p-3.5 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-start gap-2.5">
            <AlertCircle className="w-5 h-5 text-rose-500 flex-shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold block">Bid Submission Rejected</span>
              <span>{errorMessage}</span>
            </div>
          </div>
        )}

        {successMessage && (
          <div className="p-3.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm flex items-center gap-2.5">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
            <span className="font-medium">{successMessage}</span>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Carrier Name */}
          <div className="sm:col-span-2">
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              Carrier Name *
            </label>
            <input
              type="text"
              required
              disabled={!isAuctionActive || isSubmitting}
              placeholder="e.g. Apex Premier Logistics Fleet"
              value={carrierName}
              onChange={(e) => setCarrierName(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            />
          </div>

          {/* Freight Charges */}
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              Freight Charges ($) *
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-400 font-bold">$</span>
              <input
                type="number"
                step="0.01"
                min="0"
                required
                disabled={!isAuctionActive || isSubmitting}
                placeholder="0.00"
                value={freightCharges}
                onChange={(e) => setFreightCharges(e.target.value)}
                className="w-full pl-8 pr-3.5 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm font-mono"
              />
            </div>
          </div>

          {/* Origin Charges */}
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              Origin Charges ($)
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-400 font-bold">$</span>
              <input
                type="number"
                step="0.01"
                min="0"
                disabled={!isAuctionActive || isSubmitting}
                placeholder="0.00"
                value={originCharges}
                onChange={(e) => setOriginCharges(e.target.value)}
                className="w-full pl-8 pr-3.5 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm font-mono"
              />
            </div>
          </div>

          {/* Destination Charges */}
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              Destination Charges ($)
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-400 font-bold">$</span>
              <input
                type="number"
                step="0.01"
                min="0"
                disabled={!isAuctionActive || isSubmitting}
                placeholder="0.00"
                value={destinationCharges}
                onChange={(e) => setDestinationCharges(e.target.value)}
                className="w-full pl-8 pr-3.5 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm font-mono"
              />
            </div>
          </div>

          {/* Transit Time */}
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              Transit Time (Days) *
            </label>
            <input
              type="number"
              min="1"
              required
              disabled={!isAuctionActive || isSubmitting}
              value={transitTimeDays}
              onChange={(e) => setTransitTimeDays(parseInt(e.target.value) || 1)}
              className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm font-mono"
            />
          </div>

          {/* Validity of Quote */}
          <div className="sm:col-span-2">
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              Validity of Quote *
            </label>
            <input
              type="date"
              required
              disabled={!isAuctionActive || isSubmitting}
              value={validityDate}
              onChange={(e) => setValidityDate(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            />
          </div>
        </div>

        {/* Total Calculation & Rule Status Summary */}
        <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex flex-wrap items-center justify-between gap-4">
          <div>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">
              Total Calculated Quote Price
            </span>
            <div className="flex items-baseline gap-1 mt-0.5">
              <span className="text-2xl font-black font-mono text-slate-900">
                ${totalAmount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
              <span className="text-xs text-slate-500 font-medium">(Freight + Origin + Dest)</span>
            </div>
          </div>

          {previousBestAmount !== null && (
            <div className="text-right">
              <span className="text-xs font-semibold text-slate-500 block">British Rule Check</span>
              {totalAmount > 0 && !isLowerThanPrevious ? (
                <span className="inline-flex items-center gap-1 text-xs font-bold text-rose-600 bg-rose-50 px-2.5 py-1 rounded border border-rose-200">
                  <AlertCircle className="w-3.5 h-3.5" />
                  Must be &lt; ${previousBestAmount.toLocaleString()}
                </span>
              ) : totalAmount > 0 ? (
                <span className="inline-flex items-center gap-1 text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded border border-emerald-200">
                  <TrendingDown className="w-3.5 h-3.5" />
                  ${(previousBestAmount - totalAmount).toLocaleString(undefined, { minimumFractionDigits: 2 })} lower than prior bid!
                </span>
              ) : null}
            </div>
          )}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={!isAuctionActive || isSubmitting || totalAmount <= 0 || !isLowerThanPrevious}
          className="w-full py-3 px-4 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm shadow transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {isSubmitting ? (
            <span>Processing Transaction & Rankings...</span>
          ) : (
            <>
              <Send className="w-4 h-4" />
              <span>Submit Competitive Bid</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
};
