import React, { useEffect, useState } from 'react';
import VolcanoRiskCard from '../components/VolcanoRiskCard';
import { Volcano } from '../types/Volcano';

export default function Embed() {
  const [volcanoData, setVolcanoData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchGlacialVolcanoes() {
      try {
        // Fetch the GeoJSON data
        const response = await fetch('/data/glacialVolcanoes.geojson');
        if (!response.ok) {
          throw new Error(`Error fetching data: ${response.statusText}`);
        }
        const data = await response.json();
        setVolcanoData(data);
      } catch (err) {
        console.error('Error loading volcanoes:', err);
        setError(err instanceof Error ? err.message : 'Unknown error loading volcano data');
      } finally {
        setLoading(false);
      }
    }

    fetchGlacialVolcanoes();
  }, []);

  if (loading) {
    return <div className="loading">Loading volcano data...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="embed-container">
      <div className="volcano-grid">
        {volcanoData && volcanoData.features && volcanoData.features.map((feature: any, i: number) => (
          <VolcanoRiskCard key={i} volcano={{
            name: feature.properties.name,
            country: feature.properties.country,
            alertLevel: feature.properties.alertLevel || "Low",
            lastEruption: feature.properties.lastEruption || "Unknown",
            insarUrl: feature.properties.insarUrl || null,
            riskType: feature.properties.riskType || "Unknown",
            glacierCover: feature.properties.glacierCover ?? true,
            deformationRate: feature.properties.deformationRate ?? 0,
            so2Level: feature.properties.so2Level ?? null,
            latitude: feature.geometry.coordinates[1],
            longitude: feature.geometry.coordinates[0],
          }} />
        ))}
      </div>

      <style jsx>{`
        .embed-container {
          font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen,
            Ubuntu, Cantarell, Fira Sans, Droid Sans, Helvetica Neue, sans-serif;
          padding: 0;
          margin: 0;
          max-width: 100%;
        }

        .volcano-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 1rem;
        }

        .loading, .error {
          padding: 1rem;
          text-align: center;
          font-size: 1rem;
        }

        .error {
          color: crimson;
        }
      `}</style>
    </div>
  );
}