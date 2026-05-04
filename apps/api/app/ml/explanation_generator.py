from __future__ import annotations

from typing import Literal, TypedDict


LanguageCode = Literal["en", "fr", "ar"]
SignalLabel = Literal["BUY", "HOLD", "SELL"]
RiskLevel = Literal["low", "medium", "high"]


class SignalExplanationInput(TypedDict):
    signal: SignalLabel
    confidence: int
    reasons: list[str]
    risk_level: RiskLevel | None


class MultilingualExplanation(TypedDict):
    en: str
    fr: str
    ar: str


RISK_WORDS = {
    "risk",
    "volatility",
    "overbought",
    "weak",
    "low liquidity",
    "elevated",
    "negative",
    "resistance",
    "missing",
    "invalid",
}

TRANSLATIONS = {
    "strong 3m momentum": {
        "en": "Strong 3M momentum",
        "fr": "Momentum 3M solide",
        "ar": "\u0632\u062e\u0645 3 \u0623\u0634\u0647\u0631 \u0642\u0648\u064a",
    },
    "strong 3-month momentum": {
        "en": "Strong 3M momentum",
        "fr": "Momentum 3M solide",
        "ar": "\u0632\u062e\u0645 3 \u0623\u0634\u0647\u0631 \u0642\u0648\u064a",
    },
    "3-month momentum confirms a stronger trend": {
        "en": "Strong 3M momentum",
        "fr": "Momentum 3M solide",
        "ar": "\u0632\u062e\u0645 3 \u0623\u0634\u0647\u0631 \u0642\u0648\u064a",
    },
    "above 50-day trend": {
        "en": "Above 50-day trend",
        "fr": "Au-dessus de la tendance 50 jours",
        "ar": "\u0623\u0639\u0644\u0649 \u0645\u0646 \u0627\u062a\u062c\u0627\u0647 50 \u064a\u0648\u0645\u0627",
    },
    "price above 50-day moving average": {
        "en": "Above 50-day trend",
        "fr": "Au-dessus de la tendance 50 jours",
        "ar": "\u0623\u0639\u0644\u0649 \u0645\u0646 \u0627\u062a\u062c\u0627\u0647 50 \u064a\u0648\u0645\u0627",
    },
    "the 20-day moving average is above the 50-day moving average": {
        "en": "Short-term trend is above the 50-day trend",
        "fr": "La tendance courte est au-dessus de la tendance 50 jours",
        "ar": "\u0627\u0644\u0627\u062a\u062c\u0627\u0647 \u0627\u0644\u0642\u0635\u064a\u0631 \u0623\u0639\u0644\u0649 \u0645\u0646 \u0627\u062a\u062c\u0627\u0647 50 \u064a\u0648\u0645\u0627",
    },
    "liquidity stable": {
        "en": "Liquidity stable",
        "fr": "Liquidite stable",
        "ar": "\u0627\u0644\u0633\u064a\u0648\u0644\u0629 \u0645\u0633\u062a\u0642\u0631\u0629",
    },
    "liquidity acceptable": {
        "en": "Liquidity stable",
        "fr": "Liquidite stable",
        "ar": "\u0627\u0644\u0633\u064a\u0648\u0644\u0629 \u0645\u0633\u062a\u0642\u0631\u0629",
    },
    "average daily traded value suggests healthy liquidity": {
        "en": "Liquidity stable",
        "fr": "Liquidite stable",
        "ar": "\u0627\u0644\u0633\u064a\u0648\u0644\u0629 \u0645\u0633\u062a\u0642\u0631\u0629",
    },
    "volatility rising": {
        "en": "Volatility rising",
        "fr": "Volatilite en hausse",
        "ar": "\u0627\u0644\u062a\u0642\u0644\u0628\u0627\u062a \u0641\u064a \u0627\u0631\u062a\u0641\u0627\u0639",
    },
    "volatility medium": {
        "en": "Volatility is moderate",
        "fr": "Volatilite moderee",
        "ar": "\u0627\u0644\u062a\u0642\u0644\u0628\u0627\u062a \u0645\u062a\u0648\u0633\u0637\u0629",
    },
    "30-day volatility is elevated": {
        "en": "Volatility rising",
        "fr": "Volatilite en hausse",
        "ar": "\u0627\u0644\u062a\u0642\u0644\u0628\u0627\u062a \u0641\u064a \u0627\u0631\u062a\u0641\u0627\u0639",
    },
    "near resistance level": {
        "en": "Near resistance level",
        "fr": "Proche d'un niveau de resistance",
        "ar": "\u0642\u0631\u064a\u0628 \u0645\u0646 \u0645\u0633\u062a\u0648\u0649 \u0645\u0642\u0627\u0648\u0645\u0629",
    },
}

LABELS = {
    "en": {
        "why": "Why",
        "risks": "Risks",
        "action": "Action",
        "disclaimer": "Market analytics only, not financial advice.",
        "default_action": {
            "BUY": "Watch for confirmation above the next resistance level.",
            "HOLD": "Keep monitoring price, liquidity, and the next signal update.",
            "SELL": "Review risk drivers and data freshness before making any manual decision.",
        },
        "fallback_why": "Indicators are mixed",
        "fallback_risk": "No major risk flag in the supplied reasons",
    },
    "fr": {
        "why": "Pourquoi",
        "risks": "Risques",
        "action": "Action",
        "disclaimer": "Analyse de marche uniquement, pas un conseil financier.",
        "default_action": {
            "BUY": "Surveiller une confirmation au-dessus de la prochaine resistance.",
            "HOLD": "Continuer a suivre le prix, la liquidite et la prochaine mise a jour du signal.",
            "SELL": "Revoir les facteurs de risque et la fraicheur des donnees avant toute decision manuelle.",
        },
        "fallback_why": "Les indicateurs sont mixtes",
        "fallback_risk": "Aucun risque majeur dans les raisons fournies",
    },
    "ar": {
        "why": "\u0627\u0644\u0633\u0628\u0628",
        "risks": "\u0627\u0644\u0645\u062e\u0627\u0637\u0631",
        "action": "\u0627\u0644\u0625\u062c\u0631\u0627\u0621",
        "disclaimer": "\u062a\u062d\u0644\u064a\u0644 \u0633\u0648\u0642\u064a \u0641\u0642\u0637\u060c \u0648\u0644\u064a\u0633 \u0646\u0635\u064a\u062d\u0629 \u0645\u0627\u0644\u064a\u0629.",
        "default_action": {
            "BUY": "\u0631\u0627\u0642\u0628 \u062a\u0623\u0643\u064a\u062f\u0627 \u0641\u0648\u0642 \u0645\u0633\u062a\u0648\u0649 \u0627\u0644\u0645\u0642\u0627\u0648\u0645\u0629 \u0627\u0644\u062a\u0627\u0644\u064a.",
            "HOLD": "\u0627\u0633\u062a\u0645\u0631 \u0641\u064a \u0645\u062a\u0627\u0628\u0639\u0629 \u0627\u0644\u0633\u0639\u0631 \u0648\u0627\u0644\u0633\u064a\u0648\u0644\u0629 \u0648\u062a\u062d\u062f\u064a\u062b \u0627\u0644\u0625\u0634\u0627\u0631\u0629 \u0627\u0644\u0642\u0627\u062f\u0645.",
            "SELL": "\u0631\u0627\u062c\u0639 \u0639\u0648\u0627\u0645\u0644 \u0627\u0644\u0645\u062e\u0627\u0637\u0631 \u0648\u062d\u062f\u0627\u062b\u0629 \u0627\u0644\u0628\u064a\u0627\u0646\u0627\u062a \u0642\u0628\u0644 \u0623\u064a \u0642\u0631\u0627\u0631 \u064a\u062f\u0648\u064a.",
        },
        "fallback_why": "\u0627\u0644\u0645\u0624\u0634\u0631\u0627\u062a \u0645\u062a\u0628\u0627\u064a\u0646\u0629",
        "fallback_risk": "\u0644\u0627 \u062a\u0648\u062c\u062f \u0625\u0634\u0627\u0631\u0629 \u0645\u062e\u0627\u0637\u0631 \u0643\u0628\u064a\u0631\u0629 \u0641\u064a \u0627\u0644\u0623\u0633\u0628\u0627\u0628 \u0627\u0644\u0645\u062f\u062e\u0644\u0629",
    },
}


def generate_multilingual_explanation(payload: SignalExplanationInput) -> MultilingualExplanation:
    signal = payload["signal"].upper()
    confidence = max(0, min(100, int(payload["confidence"])))
    reasons = [reason.strip() for reason in payload["reasons"] if reason.strip()]

    return {
        "en": _compose("en", signal, confidence, reasons),
        "fr": _compose("fr", signal, confidence, reasons),
        "ar": _compose("ar", signal, confidence, reasons),
    }


def _split_reasons(reasons: list[str]) -> tuple[list[str], list[str]]:
    why: list[str] = []
    risks: list[str] = []
    for reason in reasons:
        normalized = reason.lower()
        if any(word in normalized for word in RISK_WORDS):
            risks.append(reason)
        else:
            why.append(reason)
    return why[:4], risks[:3]


def _translate(reason: str, language: LanguageCode) -> str:
    normalized = reason.lower().strip(".")
    return TRANSLATIONS.get(normalized, {}).get(language, reason)


def _bullets(items: list[str], language: LanguageCode, fallback: str) -> str:
    translated = [_translate(item, language) for item in items]
    if not translated:
        translated = [fallback]
    return "\n".join(f"- {item}" for item in translated)


def _compose(language: LanguageCode, signal: str, confidence: int, reasons: list[str]) -> str:
    labels = LABELS[language]
    why, risks = _split_reasons(reasons)
    action = labels["default_action"][signal]
    return (
        f"{signal} ({confidence}% confidence)\n\n"
        f"{labels['why']}:\n{_bullets(why, language, labels['fallback_why'])}\n\n"
        f"{labels['risks']}:\n{_bullets(risks, language, labels['fallback_risk'])}\n\n"
        f"{labels['action']}:\n{action}\n\n"
        f"{labels['disclaimer']}"
    )
