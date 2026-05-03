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


SIGNAL_LABELS = {
    "BUY": {"en": "Buy", "fr": "Achat", "ar": "شراء"},
    "HOLD": {"en": "Hold", "fr": "Conserver", "ar": "احتفاظ"},
    "SELL": {"en": "Sell", "fr": "Vente", "ar": "بيع"},
}

RISK_LABELS = {
    "low": {"en": "low", "fr": "faible", "ar": "منخفض"},
    "medium": {"en": "medium", "fr": "modere", "ar": "متوسط"},
    "high": {"en": "high", "fr": "eleve", "ar": "مرتفع"},
}

REASON_TRANSLATIONS = {
    "price above 50-day moving average": {
        "en": "the price is above its 50-day moving average",
        "fr": "le prix est au-dessus de sa moyenne mobile a 50 jours",
        "ar": "السعر أعلى من المتوسط المتحرك لـ 50 يوما",
    },
    "strong 3-month momentum": {
        "en": "3-month momentum is strong",
        "fr": "la dynamique sur 3 mois est forte",
        "ar": "الزخم خلال 3 أشهر قوي",
    },
    "liquidity acceptable": {
        "en": "liquidity appears acceptable",
        "fr": "la liquidite semble acceptable",
        "ar": "تبدو السيولة مقبولة",
    },
    "volatility medium": {
        "en": "volatility is medium",
        "fr": "la volatilite est moyenne",
        "ar": "التقلبات متوسطة",
    },
}


def generate_multilingual_explanation(payload: SignalExplanationInput) -> MultilingualExplanation:
    signal = payload["signal"].upper()
    confidence = max(0, min(100, int(payload["confidence"])))
    reasons = [reason.strip() for reason in payload["reasons"] if reason.strip()]
    risk_level = payload.get("risk_level") or _infer_risk_level(reasons)

    en_reasons = _translated_reasons(reasons, "en")
    fr_reasons = _translated_reasons(reasons, "fr")
    ar_reasons = _translated_reasons(reasons, "ar")

    return {
        "en": _english(signal, confidence, risk_level, en_reasons),
        "fr": _french(signal, confidence, risk_level, fr_reasons),
        "ar": _arabic(signal, confidence, risk_level, ar_reasons),
    }


def _infer_risk_level(reasons: list[str]) -> RiskLevel:
    joined = " ".join(reason.lower() for reason in reasons)
    if "high" in joined or "elevated" in joined or "low liquidity" in joined:
        return "high"
    if "medium" in joined or "moderate" in joined or "volatility" in joined:
        return "medium"
    return "low"


def _translated_reasons(reasons: list[str], language: LanguageCode) -> list[str]:
    translated: list[str] = []
    for reason in reasons[:4]:
        normalized = reason.lower().strip(".")
        translated.append(REASON_TRANSLATIONS.get(normalized, {}).get(language, reason))
    return translated


def _join_reasons(reasons: list[str], language: LanguageCode) -> str:
    if not reasons:
        return {
            "en": "the available indicators are mixed",
            "fr": "les indicateurs disponibles sont mixtes",
            "ar": "المؤشرات المتاحة متباينة",
        }[language]
    if len(reasons) == 1:
        return reasons[0]
    connector = {"en": ", and ", "fr": ", et ", "ar": "، و"}[language]
    separator = {"en": ", ", "fr": ", ", "ar": "، "}[language]
    return separator.join(reasons[:-1]) + connector + reasons[-1]


def _english(signal: str, confidence: int, risk_level: RiskLevel, reasons: list[str]) -> str:
    label = SIGNAL_LABELS[signal]["en"]
    risk = RISK_LABELS[risk_level]["en"]
    details = _join_reasons(reasons, "en")
    return f"{label} signal with {confidence}% confidence. The setup looks {risk} risk because {details}. This is research support only, not financial advice."


def _french(signal: str, confidence: int, risk_level: RiskLevel, reasons: list[str]) -> str:
    label = SIGNAL_LABELS[signal]["fr"]
    risk = RISK_LABELS[risk_level]["fr"]
    details = _join_reasons(reasons, "fr")
    return f"Signal {label} avec {confidence}% de confiance. Le profil de risque est {risk} car {details}. Ceci est une aide a la recherche, pas un conseil financier."


def _arabic(signal: str, confidence: int, risk_level: RiskLevel, reasons: list[str]) -> str:
    label = SIGNAL_LABELS[signal]["ar"]
    risk = RISK_LABELS[risk_level]["ar"]
    details = _join_reasons(reasons, "ar")
    return f"إشارة {label} بثقة {confidence}%. مستوى المخاطر {risk} لأن {details}. هذا دعم بحثي فقط وليس نصيحة مالية."
