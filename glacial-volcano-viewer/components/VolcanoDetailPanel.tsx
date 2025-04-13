import React from 'react';
import { Volcano } from '../types/Volcano';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

interface VolcanoDetailPanelProps {
  volcano: Volcano;
  onClose: () => void;
}

const VolcanoDetailPanel: React.FC<VolcanoDetailPanelProps> = ({ volcano, onClose }) => {
  // Format data for the risk/glacial coverage chart
  const doughnutData = {
    labels: ['Risk Factor', 'Glacial Coverage'],
    datasets: [
      {
        data: [volcano.risk_factor, volcano.glacial_coverage || 0],
        backgroundColor: ['rgba(255, 99, 132, 0.6)', 'rgba(54, 162, 235, 0.6)'],
        borderColor: ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)'],
        borderWidth: 1,
      },
    ],
  };
  
  // Create bar chart data if glacier retreat rate is available
  const barData = {
    labels: ['Glacial Retreat Rate (m/year)'],
    datasets: [
      {
        label: 'Current Rate',
        data: [volcano.glacial_retreat_rate || 0],
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
      },
      {
        label: 'Critical Threshold',
        data: [30], // Example threshold
        backgroundColor: 'rgba(255, 99, 132, 0.6)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 1,
      },
    ],
  };
  
  // Options for the bar chart
  const barOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Glacial Retreat Comparison',
      },
    },
  };

  return (
    <div className="bg-white rounded-lg shadow-xl p-6 overflow-y-auto max-h-[80vh]">
      <div className="flex justify-between items-start mb-4">
        <h2 className="text-2xl font-bold text-gray-800">{volcano.name}</h2>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-gray-700"
          aria-label="Close"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <div className="text-sm text-gray-600">Region</div>
          <div className="font-medium">{volcano.region}, {volcano.country}</div>
        </div>
        <div>
          <div className="text-sm text-gray-600">Coordinates</div>
          <div className="font-medium">{volcano.latitude.toFixed(4)}, {volcano.longitude.toFixed(4)}</div>
        </div>
        <div>
          <div className="text-sm text-gray-600">Elevation</div>
          <div className="font-medium">{volcano.elevation}m</div>
        </div>
        <div>
          <div className="text-sm text-gray-600">Volcano Type</div>
          <div className="font-medium">{volcano.type}</div>
        </div>
        <div>
          <div className="text-sm text-gray-600">Last Eruption</div>
          <div className="font-medium">{volcano.last_eruption || 'Unknown'}</div>
        </div>
        <div>
          <div className="text-sm text-gray-600">Risk Level</div>
          <div className="font-medium">{volcano.risk_level} ({volcano.risk_factor}%)</div>
        </div>
        {volcano.glacial_coverage && (
          <div>
            <div className="text-sm text-gray-600">Glacial Coverage</div>
            <div className="font-medium">{volcano.glacial_coverage}%</div>
          </div>
        )}
        {volcano.glacier_name && (
          <div>
            <div className="text-sm text-gray-600">Glacier Name</div>
            <div className="font-medium">{volcano.glacier_name}</div>
          </div>
        )}
        {volcano.population_within_100km && (
          <div>
            <div className="text-sm text-gray-600">Population (100km radius)</div>
            <div className="font-medium">{volcano.population_within_100km.toLocaleString()}</div>
          </div>
        )}
        {volcano.monitoring_level && (
          <div>
            <div className="text-sm text-gray-600">Monitoring Level</div>
            <div className="font-medium">{volcano.monitoring_level}</div>
          </div>
        )}
      </div>
      
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">Climate Impact</h3>
        <p className="text-gray-700">{volcano.climate_impact}</p>
      </div>
      
      {volcano.description && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">Description</h3>
          <p className="text-gray-700">{volcano.description}</p>
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-2">Risk & Glacial Data</h3>
          <div className="h-[200px]">
            <Doughnut 
              data={doughnutData} 
              options={{
                responsive: true,
                maintainAspectRatio: false,
              }}
            />
          </div>
        </div>
        
        {volcano.glacial_retreat_rate && (
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Glacial Retreat Rate</h3>
            <div className="h-[200px]">
              <Bar 
                data={barData} 
                options={{
                  ...barOptions,
                  maintainAspectRatio: false,
                }}
              />
            </div>
          </div>
        )}
      </div>
      
      {volcano.image_url && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">Satellite Image</h3>
          <img 
            src={volcano.image_url} 
            alt={`${volcano.name} satellite view`} 
            className="w-full h-auto rounded-lg shadow-md"
          />
        </div>
      )}
      
      {volcano.references && volcano.references.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-2">References</h3>
          <ul className="list-disc pl-5 text-gray-700">
            {volcano.references.map((ref, index) => (
              <li key={index} className="mb-1">{ref}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default VolcanoDetailPanel;