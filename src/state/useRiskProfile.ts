import { useState } from "react";

export function useRiskProfile() {
  const [riskScore, setRiskScore] = useState(5);

  return {
    riskScore,
    setRiskScore,
  };
}
