import React from 'react';
import { ShieldCheck, ShieldAlert, AlertTriangle } from 'lucide-react';
import { Badge } from './Badge.jsx';

export function ConfidenceBadge({ score, rating, showPercent = true }) {
  let variant = 'green';
  let Icon = ShieldCheck;
  let label = rating || 'HIGH';

  if (score >= 85 || rating === 'HIGH') {
    variant = 'green';
    Icon = ShieldCheck;
    label = 'High Confidence';
  } else if (score >= 60 || rating === 'MEDIUM') {
    variant = 'amber';
    Icon = AlertTriangle;
    label = 'Medium Confidence';
  } else {
    variant = 'rose';
    Icon = ShieldAlert;
    label = 'Low Confidence';
  }

  return (
    <Badge variant={variant} icon={Icon}>
      <span>{label}</span>
      {showPercent && score !== undefined && (
        <span className="font-mono font-semibold ml-0.5">({score}%)</span>
      )}
    </Badge>
  );
}
