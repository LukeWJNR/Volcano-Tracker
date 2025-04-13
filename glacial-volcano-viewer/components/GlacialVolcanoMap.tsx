import React, { useRef, useEffect } from 'react';
import { Volcano } from '../types/Volcano';
import 'leaflet/dist/leaflet.css';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';

// Fix for Leaflet marker icons in Next.js
const fixLeafletIcon = () => {
  delete (L.Icon.Default.prototype as any)._getIconUrl;
  
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: '/leaflet/marker-icon-2x.png',
    iconUrl: '/leaflet/marker-icon.png',
    shadowUrl: '/leaflet/marker-shadow.png',
  });
};

interface GlacialVolcanoMapProps {
  volcanoes: Volcano[];
  selectedVolcano?: Volcano | null;
  onVolcanoSelect: (volcano: Volcano) => void;
}

// Create marker icons based on risk level
const createRiskIcon = (riskLevel: string) => {
  // Define colors based on risk level
  const colors = {
    'Low': '#00c853',
    'Medium': '#ffd600',
    'High': '#ff9100',
    'Extreme': '#d50000',
  };
  
  const color = colors[riskLevel as keyof typeof colors] || '#757575';
  
  return new L.DivIcon({
    className: 'custom-div-icon',
    html: `<div style="
      background-color: ${color};
      width: 12px;
      height: 12px;
      border-radius: 50%;
      border: 2px solid white;
      box-shadow: 0 0 4px rgba(0,0,0,0.5);"
    ></div>`,
    iconSize: [12, 12],
    iconAnchor: [6, 6],
  });
};

// Map center helper component
const MapCenterSetter = ({ volcano }: { volcano?: Volcano | null }) => {
  const map = useMap();
  
  useEffect(() => {
    if (volcano) {
      map.setView([volcano.latitude, volcano.longitude], 10);
    }
  }, [map, volcano]);
  
  return null;
};

const GlacialVolcanoMap: React.FC<GlacialVolcanoMapProps> = ({
  volcanoes,
  selectedVolcano,
  onVolcanoSelect,
}) => {
  const leafletContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Fix Leaflet icon issue with Next.js
    fixLeafletIcon();
  }, []);

  if (typeof window === 'undefined') {
    return <div>Loading map...</div>;
  }

  return (
    <div 
      ref={leafletContainerRef}
      className="w-full h-[500px] rounded-lg overflow-hidden shadow-md"
    >
      <MapContainer
        center={[20, 0]} // Default center
        zoom={2}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {/* Dynamically set center if a volcano is selected */}
        <MapCenterSetter volcano={selectedVolcano} />
        
        {volcanoes.map((volcano) => (
          <Marker
            key={volcano.id}
            position={[volcano.latitude, volcano.longitude]}
            icon={createRiskIcon(volcano.risk_level)}
            eventHandlers={{
              click: () => onVolcanoSelect(volcano),
            }}
          >
            <Popup>
              <div>
                <h3 className="font-bold">{volcano.name}</h3>
                <p>Type: {volcano.type}</p>
                <p>Risk Level: {volcano.risk_level}</p>
                {volcano.glacial_coverage && (
                  <p>Glacial Coverage: {volcano.glacial_coverage}%</p>
                )}
                {volcano.last_eruption && (
                  <p>Last Eruption: {volcano.last_eruption}</p>
                )}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};

export default GlacialVolcanoMap;