export interface Volcano {
  name: string;
  country: string;
  latitude: number;
  longitude: number;
  alertLevel: string | null;
  lastEruption: string;
  insarUrl?: string | null;
  riskType?: string | null;
  glacierCover?: boolean;
  deformationRate?: number;
  so2Level?: number;
}