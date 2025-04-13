import React from "react";
import { Volcano } from "../types/Volcano";

interface Props {
  volcano: Volcano;
}

export default function VolcanoRiskCard({ volcano }: Props) {
  const {
    name,
    country,
    alertLevel,
    lastEruption,
    insarUrl,
    riskType,
    glacierCover,
    deformationRate,
    so2Level
  } = volcano;

  const riskColor =
    alertLevel === "High" || riskType === "Phreatomagmatic" || deformationRate > 10
      ? "crimson"
      : alertLevel === "Moderate"
      ? "orange"
      : "green";

  return (
    <div style={{
      border: `2px solid ${riskColor}`,
      borderRadius: "10px",
      padding: "1rem",
      margin: "1rem 0",
      background: "#fff",
      boxShadow: "0 0 10px rgba(0,0,0,0.1)"
    }}>
      <h2>{name} ({country})</h2>
      <p><strong>Risk Type:</strong> {riskType || "Unknown"}</p>
      <p><strong>Glacier Covered:</strong> {glacierCover ? "Yes" : "No"}</p>
      <p><strong>Last Eruption:</strong> {lastEruption}</p>
      <p><strong>Alert Level:</strong> {alertLevel}</p>
      <p><strong>Deformation Rate:</strong> {deformationRate || "N/A"} mm/year</p>
      <p><strong>SO₂ Level:</strong> {so2Level || "N/A"} ppm</p>
      {insarUrl && (
        <p>
          <a href={insarUrl} target="_blank" rel="noreferrer">
            View InSAR Imagery →
          </a>
        </p>
      )}
    </div>
  );
}