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
    "BUY": {"en": "Positive", "fr": "Positif", "ar": "إيجابية"},
    "HOLD": {"en": "Neutral", "fr": "Neutre", "ar": "محايدة"},
    "SELL": {"en": "Negative", "fr": "Négatif", "ar": "سلبية"},
}

RISK_LABELS = {
    "low": {"en": "low", "fr": "faible", "ar": "منخفض"},
    "medium": {"en": "medium", "fr": "modéré", "ar": "متوسط"},
    "high": {"en": "high", "fr": "élevé", "ar": "مرتفع"},
}

ACTION_BY_SIGNAL = {
    "BUY": {
        "en": "Review whether the trend, liquidity, and risk level still fit your research criteria before making any manual decision.",
        "fr": "Vérifiez que la tendance, la liquidité et le niveau de risque correspondent toujours à vos critères de recherche avant toute décision manuelle.",
        "ar": "راجع ما إذا كان الاتجاه والسيولة ومستوى المخاطر ما زالوا مناسبين لمعايير البحث الخاصة بك قبل أي قرار يدوي.",
    },
    "HOLD": {
        "en": "Keep monitoring the next price update, liquidity, and signal drivers before changing your view.",
        "fr": "Continuez à surveiller le prochain prix, la liquidité et les facteurs du signal avant de modifier votre analyse.",
        "ar": "استمر في متابعة تحديث السعر القادم والسيولة والعوامل المؤثرة في الإشارة قبل تغيير تقييمك.",
    },
    "SELL": {
        "en": "Review the risk drivers, data freshness, and position exposure; treat this as a caution flag, not an order.",
        "fr": "Examinez les facteurs de risque, la fraîcheur des données et l'exposition; considérez ceci comme un signal de prudence, pas comme un ordre.",
        "ar": "راجع عوامل المخاطر وحداثة البيانات وحجم التعرض؛ اعتبر ذلك تنبيهاً للحذر وليس أمراً بالتداول.",
    },
}

FALLBACK_REASON = {
    "en": "the available indicators are mixed",
    "fr": "les indicateurs disponibles sont mitigés",
    "ar": "المؤشرات المتاحة متباينة",
}

DISCLAIMER = {
    "en": "This is market analytics only, not financial advice.",
    "fr": "Il s'agit uniquement d'analyses de marché, pas d'un conseil financier.",
    "ar": "هذه تحليلات سوقية فقط وليست نصيحة مالية.",
}

REASON_TRANSLATIONS = {
    "price above 50-day moving average": {
        "en": "price is above the 50-day moving average",
        "fr": "le prix est au-dessus de la moyenne mobile à 50 jours",
        "ar": "السعر أعلى من المتوسط المتحرك لـ 50 يوماً",
    },
    "strong 3-month momentum": {
        "en": "3-month momentum is strong",
        "fr": "la dynamique sur 3 mois est solide",
        "ar": "زخم 3 أشهر قوي",
    },
    "liquidity acceptable": {
        "en": "liquidity looks acceptable",
        "fr": "la liquidité semble acceptable",
        "ar": "السيولة تبدو مقبولة",
    },
    "volatility medium": {
        "en": "volatility is moderate",
        "fr": "la volatilité est modérée",
        "ar": "التقلبات متوسطة",
    },
    "the 20-day moving average is above the 50-day moving average": {
        "en": "the short-term trend is above the medium-term trend",
        "fr": "la tendance courte est au-dessus de la tendance moyenne",
        "ar": "الاتجاه قصير الأجل أعلى من الاتجاه متوسط الأجل",
    },
    "3-month momentum confirms a stronger trend": {
        "en": "3-month momentum supports the trend",
        "fr": "la dynamique sur 3 mois soutient la tendance",
        "ar": "زخم 3 أشهر يدعم الاتجاه",
    },
    "average daily traded value suggests healthy liquidity": {
        "en": "daily traded value suggests healthy liquidity",
        "fr": "la valeur échangée quotidienne suggère une liquidité saine",
        "ar": "قيمة التداول اليومية تشير إلى سيولة جيدة",
    },
    "30-day volatility is contained": {
        "en": "30-day volatility is contained",
        "fr": "la volatilité à 30 jours reste contenue",
        "ar": "تقلب 30 يوماً لا يزال محدوداً",
    },
    "average daily traded value is low for retail execution quality": {
        "en": "liquidity is low, which can make real-world execution harder",
        "fr": "la liquidité est faible, ce qui peut rendre l'exécution réelle plus difficile",
        "ar": "السيولة منخفضة، ما قد يجعل التنفيذ الفعلي أصعب",
    },
    "30-day volatility is elevated": {
        "en": "30-day volatility is elevated",
        "fr": "la volatilité à 30 jours est élevée",
        "ar": "تقلب 30 يوماً مرتفع",
    },
}


def generate_multilingual_explanation(payload: SignalExplanationInput) -> MultilingualExplanation:
    signal = payload["signal"].upper()
    confidence = max(0, min(100, int(payload["confidence"])))
    reasons = [reason.strip() for reason in payload["reasons"] if reason.strip()]
    risk_level = payload.get("risk_level") or _infer_risk_level(reasons)

    return {
        "en": _compose("en", signal, confidence, risk_level, reasons),
        "fr": _compose("fr", signal, confidence, risk_level, reasons),
        "ar": _compose("ar", signal, confidence, risk_level, reasons),
    }


def _infer_risk_level(reasons: list[str]) -> RiskLevel:
    joined = " ".join(reason.lower() for reason in reasons)
    if "high" in joined or "elevated" in joined or "low liquidity" in joined or "faible" in joined:
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
        return FALLBACK_REASON[language]
    if len(reasons) == 1:
        return reasons[0]
    connector = {"en": ", and ", "fr": ", et ", "ar": "، و"}[language]
    separator = {"en": ", ", "fr": ", ", "ar": "، "}[language]
    return separator.join(reasons[:-1]) + connector + reasons[-1]


def _compose(language: LanguageCode, signal: str, confidence: int, risk_level: RiskLevel, reasons: list[str]) -> str:
    label = SIGNAL_LABELS[signal][language]
    risk = RISK_LABELS[risk_level][language]
    reason_text = _join_reasons(_translated_reasons(reasons, language), language)
    action = ACTION_BY_SIGNAL[signal][language]

    if language == "en":
        return (
            f"Research signal: {label} with {confidence}% confidence. "
            f"Why: {reason_text}. Risk level: {risk}. "
            f"Next step: {action} {DISCLAIMER[language]}"
        )
    if language == "fr":
        return (
            f"Signal de recherche : {label} avec {confidence}% de confiance. "
            f"Pourquoi : {reason_text}. Niveau de risque : {risk}. "
            f"Prochaine étape : {action} {DISCLAIMER[language]}"
        )
    return (
        f"إشارة بحثية: {label} بدرجة ثقة {confidence}%. "
        f"السبب: {reason_text}. مستوى المخاطر: {risk}. "
        f"الخطوة التالية: {action} {DISCLAIMER[language]}"
    )
