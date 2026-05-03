import type { AiSignal } from "../types/market";

export type Locale = "en" | "fr";

export function buildRiskSignal(riskScore: number, locale: Locale = "en"): AiSignal {
  if (riskScore <= 3) {
    return {
      confidence: Math.max(52, 88 - riskScore * 2),
      label: locale === "fr" ? "Prudent" : "Conservative",
      narrative:
        locale === "fr"
          ? "L'assistant privilegie la resilience des dividendes, une volatilite plus faible et des tailles de position qui gardent plus de liquidites."
          : "The assistant is prioritizing dividend resilience, lower volatility, and position sizes that leave more cash unallocated.",
      title: locale === "fr" ? "Protection du capital" : "Capital protection",
      tone: "positive",
    };
  }

  if (riskScore <= 7) {
    return {
      confidence: Math.max(52, 86 - riskScore * 2),
      label: locale === "fr" ? "Modere" : "Moderate",
      narrative:
        locale === "fr"
          ? "Le filtrage actuel favorise des actions marocaines defensives avec des dividendes stables, une dette maitrisee et une meilleure confirmation des volumes."
          : "Current screening favors defensive Moroccan equities with stable dividends, manageable debt, and stronger volume confirmation.",
      title: locale === "fr" ? "Achat selectif" : "Selective buy",
      tone: "positive",
    };
  }

  return {
    confidence: Math.max(52, 82 - riskScore * 2),
    label: locale === "fr" ? "Risque eleve" : "Elevated risk",
    narrative:
      locale === "fr"
        ? "L'assistant autorise des valeurs plus volatiles, donc la taille des positions et les niveaux de sortie deviennent plus importants."
        : "The assistant is allowing higher volatility names, so position sizing and stop planning become more important.",
    title: locale === "fr" ? "Surveillance momentum" : "Momentum watch",
    tone: "negative",
  };
}
