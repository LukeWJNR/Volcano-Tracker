import React, { useEffect, useState } from 'react';
import Head from 'next/head';
import VolcanoRiskCard from '../components/VolcanoRiskCard';
import { Volcano } from '../types/Volcano';

export default function Home() {
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
    <div className="container">
      <Head>
        <title>Glacial Volcano Viewer</title>
        <meta name="description" content="Interactive viewer for glacial volcanoes" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main>
        <h1>Glacial Volcanoes Risk Assessment</h1>
        <p className="description">
          Climate change is affecting volcanic activity by melting glaciers that have historically stabilized volcanic systems.
          This dashboard shows risk assessments for volcanoes affected by glacial melt.
        </p>

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
      </main>

      <style jsx>{`
        .container {
          font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen,
            Ubuntu, Cantarell, Fira Sans, Droid Sans, Helvetica Neue, sans-serif;
          padding: 0 1rem;
        }

        main {
          padding: 2rem 0;
          flex: 1;
          display: flex;
          flex-direction: column;
        }

        h1 {
          margin: 0;
          font-size: 2rem;
          color: #333;
        }

        .description {
          margin: 1rem 0 2rem;
          line-height: 1.5;
          font-size: 1.1rem;
        }

        .volcano-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 1.5rem;
        }

        .loading, .error {
          padding: 2rem;
          text-align: center;
          font-size: 1.2rem;
        }

        .error {
          color: crimson;
        }
      `}</style>
    </div>
  );
}