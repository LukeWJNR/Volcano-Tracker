export interface Volcano {
  id: string;
  name: string;
  region: string;
  country: string;
  latitude: number;
  longitude: number;
  elevation: number;
  type: string;
  last_eruption?: string;
  risk_level: 'Low' | 'Medium' | 'High' | 'Extreme';
  risk_factor: number; // 0-100
  climate_impact: string;
  glacial_coverage?: number; // Percentage of glacier coverage
  glacial_retreat_rate?: number; // Annual retreat rate in meters
  glacier_name?: string;
  population_within_100km?: number;
  description?: string;
  monitoring_level?: string;
  image_url?: string;
  references?: string[];
}

export interface GlacialVolcanoData {
  volcanoes: Volcano[];
  lastUpdated: string;
}