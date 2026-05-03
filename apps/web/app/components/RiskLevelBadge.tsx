import type { RankedStock } from "../lib/types";

export function getRiskLevel(riskScore: number): "Low" | "Medium" | "High" {
  if (riskScore >= 65) {
    return "High";
  }
  if (riskScore >= 45) {
    return "Medium";
  }
  return "Low";
}

export function RiskLevelBadge({ riskScore }: { riskScore: RankedStock["risk_score"] }) {
  const level = getRiskLevel(riskScore);
  return <span className={`riskBadge ${level.toLowerCase()}`}>{level}</span>;
}
