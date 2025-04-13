import React from 'react';
import { Volcano } from '../types/Volcano';

interface VolcanoRiskCardProps {
  volcano: Volcano;
  onClick?: () => void;
}

const VolcanoRiskCard: React.FC<VolcanoRiskCardProps> = ({ volcano, onClick }) => {
  // Determine risk level color
  const getRiskColor = (risk: string): string => {
    switch (risk.toLowerCase()) {
      case 'low':
        return 'bg-green-100 border-green-500 text-green-800';
      case 'medium':
        return 'bg-yellow-100 border-yellow-500 text-yellow-800';
      case 'high':
        return 'bg-orange-100 border-orange-500 text-orange-800';
      case 'extreme':
        return 'bg-red-100 border-red-500 text-red-800';
      default:
        return 'bg-gray-100 border-gray-500 text-gray-800';
    }
  };

  // Format risk factor as a percentage
  const riskPercentage = `${Math.round(volcano.risk_factor)}%`;

  return (
    <div 
      className={`border-l-4 rounded-lg shadow-md p-4 mb-4 cursor-pointer transition-all duration-200 hover:shadow-lg ${getRiskColor(volcano.risk_level)}`}
      onClick={onClick}
    >
      <div className="flex justify-between items-start">
        <h3 className="text-lg font-bold">{volcano.name}</h3>
        <div className="text-sm font-semibold px-2 py-1 rounded bg-white bg-opacity-50">
          {volcano.region}, {volcano.country}
        </div>
      </div>
      
      <div className="mt-2 text-sm">
        <div className="grid grid-cols-2 gap-2">
          <div>Type: {volcano.type}</div>
          <div>Elevation: {volcano.elevation}m</div>
          <div>Last Eruption: {volcano.last_eruption || 'Unknown'}</div>
          <div>Risk: {volcano.risk_level}</div>
        </div>
      </div>
      
      <div className="mt-3">
        <div className="text-xs font-medium mb-1">Risk Factor: {riskPercentage}</div>
        <div className="w-full bg-gray-200 rounded-full h-2.5">
          <div 
            className="h-2.5 rounded-full bg-current" 
            style={{ width: riskPercentage }}
          ></div>
        </div>
      </div>
      
      {volcano.glacial_coverage && (
        <div className="mt-3">
          <div className="text-xs font-medium mb-1">Glacial Coverage: {volcano.glacial_coverage}%</div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div 
              className="h-2.5 rounded-full bg-blue-500" 
              style={{ width: `${volcano.glacial_coverage}%` }}
            ></div>
          </div>
        </div>
      )}
      
      {volcano.climate_impact && (
        <div className="mt-2 text-sm">
          <span className="font-semibold">Climate Impact:</span> {volcano.climate_impact}
        </div>
      )}
    </div>
  );
};

export default VolcanoRiskCard;