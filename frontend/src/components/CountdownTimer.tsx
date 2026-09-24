import React, { useState, useEffect } from 'react';
import { Clock, AlertCircle } from 'lucide-react';

interface Props {
  targetTime: string; // ISO string of current_close_time
  forcedCloseTime?: string; // ISO string of forced_bid_close_time
  triggerWindowMinutes?: number; // X minutes
  onExpire?: () => void;
}

export const CountdownTimer: React.FC<Props> = ({
  targetTime,
  forcedCloseTime,
  triggerWindowMinutes = 10,
  onExpire,
}) => {
  const [timeLeft, setTimeLeft] = useState<{
    hours: number;
    minutes: number;
    seconds: number;
    totalSeconds: number;
    isExpired: boolean;
    isInTriggerWindow: boolean;
  }>({
    hours: 0,
    minutes: 0,
    seconds: 0,
    totalSeconds: 0,
    isExpired: false,
    isInTriggerWindow: false,
  });

  useEffect(() => {
    function calculate() {
      const targetDate = new Date(targetTime).getTime();
      const now = new Date().getTime();
      const difference = targetDate - now;

      if (difference <= 0) {
        setTimeLeft({
          hours: 0,
          minutes: 0,
          seconds: 0,
          totalSeconds: 0,
          isExpired: true,
          isInTriggerWindow: false,
        });
        if (onExpire) onExpire();
        return;
      }

      const totalSecs = Math.floor(difference / 1000);
      const hours = Math.floor(totalSecs / 3600);
      const minutes = Math.floor((totalSecs % 3600) / 60);
      const seconds = totalSecs % 60;

      const triggerWindowSeconds = triggerWindowMinutes * 60;
      const inWindow = totalSecs <= triggerWindowSeconds;

      setTimeLeft({
        hours,
        minutes,
        seconds,
        totalSeconds: totalSecs,
        isExpired: false,
        isInTriggerWindow: inWindow,
      });
    }

    calculate();
    const interval = setInterval(calculate, 1000);
    return () => clearInterval(interval);
  }, [targetTime, triggerWindowMinutes, onExpire]);

  if (timeLeft.isExpired) {
    return (
      <div className="flex items-center gap-1.5 text-slate-500 font-medium text-sm">
        <Clock className="w-4 h-4 text-slate-400" />
        <span>Bidding Ended</span>
      </div>
    );
  }

  const pad = (n: number) => n.toString().padStart(2, '0');

  return (
    <div className="flex items-center gap-2">
      <div
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border font-mono font-bold text-sm transition-colors ${
          timeLeft.isInTriggerWindow
            ? 'bg-amber-50 text-amber-900 border-amber-300 animate-pulse'
            : 'bg-slate-50 text-slate-800 border-slate-200'
        }`}
      >
        <Clock
          className={`w-4 h-4 ${
            timeLeft.isInTriggerWindow ? 'text-amber-600' : 'text-slate-500'
          }`}
        />
        <span>
          {timeLeft.hours > 0 && `${pad(timeLeft.hours)}:`}
          {pad(timeLeft.minutes)}:{pad(timeLeft.seconds)}
        </span>
      </div>

      {timeLeft.isInTriggerWindow && (
        <span className="flex items-center gap-1 text-xs font-semibold text-amber-700 bg-amber-100/70 border border-amber-200 px-2 py-1 rounded">
          <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
          Extension Window Active (X={triggerWindowMinutes}m)
        </span>
      )}
    </div>
  );
};
