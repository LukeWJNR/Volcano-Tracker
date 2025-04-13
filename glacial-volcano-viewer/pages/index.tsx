import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { Volcano, GlacialVolcanoData } from '../types/Volcano';
import VolcanoRiskCard from '../components/VolcanoRiskCard';
import GlacialVolcanoMap from '../components/GlacialVolcanoMap';
import VolcanoDetailPanel from '../components/VolcanoDetailPanel';

export default function Home() {
  const [volcanoes, setVolcanoes] = useState<Volcano[]>([]);
  const [filteredVolcanoes, setFilteredVolcanoes] = useState<Volcano[]>([]);
  const [selectedVolcano, setSelectedVolcano] = useState<Volcano | null>(null);
  const [regionFilter, setRegionFilter] = useState<string>('All');
  const [nameFilter, setNameFilter] = useState<string>('');
  const [lastUpdated, setLastUpdated] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isDetailOpen, setIsDetailOpen] = useState<boolean>(false);

  // Load volcano data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/data/glacial_volcanoes.json');
        const data: GlacialVolcanoData = await response.json();
        setVolcanoes(data.volcanoes);
        setFilteredVolcanoes(data.volcanoes);
        setLastUpdated(data.lastUpdated);
        setIsLoading(false);
      } catch (error) {
        console.error('Error loading volcano data:', error);
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  // Apply filters when region or name filters change
  useEffect(() => {
    if (volcanoes.length === 0) return;
    
    let filtered = [...volcanoes];
    
    // Apply region filter
    if (regionFilter !== 'All') {
      filtered = filtered.filter(volcano => volcano.region === regionFilter);
    }
    
    // Apply name filter
    if (nameFilter) {
      const lowercaseName = nameFilter.toLowerCase();
      filtered = filtered.filter(volcano => 
        volcano.name.toLowerCase().includes(lowercaseName) ||
        volcano.country.toLowerCase().includes(lowercaseName)
      );
    }
    
    setFilteredVolcanoes(filtered);
  }, [regionFilter, nameFilter, volcanoes]);

  // Handle volcano selection
  const handleVolcanoSelect = (volcano: Volcano) => {
    setSelectedVolcano(volcano);
    setIsDetailOpen(true);
  };

  // Get unique regions for filter dropdown
  const regions = ['All', ...new Set(volcanoes.map(v => v.region))];

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>Glacial Volcano Viewer</title>
        <meta name="description" content="Interactive viewer for glaciated volcanoes and climate change impacts" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800">
            Glacial Volcano Viewer
          </h1>
          <p className="text-lg text-gray-600 mt-2">
            Exploring the connection between climate change and volcanic activity
          </p>
          {lastUpdated && (
            <p className="text-sm text-gray-500 mt-1">
              Last updated: {formatDate(lastUpdated)}
            </p>
          )}
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Select Region
              </label>
              <select
                value={regionFilter}
                onChange={(e) => setRegionFilter(e.target.value)}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
                {regions.map(region => (
                  <option key={region} value={region}>{region}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Filter by Volcano Name
              </label>
              <input
                type="text"
                value={nameFilter}
                onChange={(e) => setNameFilter(e.target.value)}
                placeholder="Search by name or country..."
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {isLoading ? (
          <div className="text-center py-12">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]"></div>
            <p className="mt-2 text-gray-600">Loading volcano data...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Volcano list */}
            <div className="lg:col-span-1 overflow-y-auto max-h-[700px] pr-2">
              <h2 className="text-xl font-semibold mb-4">
                Glaciated Volcanoes ({filteredVolcanoes.length})
              </h2>
              
              {filteredVolcanoes.length === 0 ? (
                <div className="text-center py-8 bg-gray-100 rounded-lg">
                  <p className="text-gray-600">No volcanoes match your filters</p>
                </div>
              ) : (
                filteredVolcanoes.map(volcano => (
                  <VolcanoRiskCard
                    key={volcano.id}
                    volcano={volcano}
                    onClick={() => handleVolcanoSelect(volcano)}
                  />
                ))
              )}
            </div>
            
            {/* Map view */}
            <div className="lg:col-span-2">
              <h2 className="text-xl font-semibold mb-4">Interactive Map</h2>
              <GlacialVolcanoMap
                volcanoes={filteredVolcanoes}
                selectedVolcano={selectedVolcano}
                onVolcanoSelect={handleVolcanoSelect}
              />
              
              <div className="mt-4 bg-white rounded-lg shadow-md p-4">
                <h3 className="text-lg font-semibold mb-2">Map Legend</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  <div className="flex items-center">
                    <div className="w-4 h-4 rounded-full bg-green-500 mr-2"></div>
                    <span className="text-sm">Low Risk</span>
                  </div>
                  <div className="flex items-center">
                    <div className="w-4 h-4 rounded-full bg-yellow-500 mr-2"></div>
                    <span className="text-sm">Medium Risk</span>
                  </div>
                  <div className="flex items-center">
                    <div className="w-4 h-4 rounded-full bg-orange-500 mr-2"></div>
                    <span className="text-sm">High Risk</span>
                  </div>
                  <div className="flex items-center">
                    <div className="w-4 h-4 rounded-full bg-red-500 mr-2"></div>
                    <span className="text-sm">Extreme Risk</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Volcano detail modal */}
        {isDetailOpen && selectedVolcano && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
              <VolcanoDetailPanel
                volcano={selectedVolcano}
                onClose={() => setIsDetailOpen(false)}
              />
            </div>
          </div>
        )}
        
        {/* Footer information */}
        <footer className="mt-12 text-center text-sm text-gray-500 pb-8">
          <p>
            Data sourced from the Global Volcanism Program (GVP) and enhanced with climate impact analysis.
          </p>
          <p className="mt-1">
            Developed for the Volcano Monitoring Dashboard - &copy; 2025
          </p>
        </footer>
      </main>
    </div>
  );
}