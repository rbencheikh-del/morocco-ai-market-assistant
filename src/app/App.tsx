import { useState } from "react";
import { Bell, LineChart, Search, ShieldCheck, SlidersHorizontal } from "lucide-react";
import { AskStocksPage } from "../components/AskStocksPage";
import { DraftPage } from "../components/DraftPage";
import { MaroqLogo } from "../components/MaroqLogo";
import { MarketOpportunity } from "../components/MarketOpportunity";
import { PortfolioChart } from "../components/PortfolioChart";
import { RiskSignalPanel } from "../components/RiskSignalPanel";
import { RiskAlertsPanel } from "../components/RiskAlertsPanel";
import { SolutionPillars } from "../components/SolutionPillars";
import { TradingShowcase } from "../components/TradingShowcase";
import { WatchlistTable } from "../components/WatchlistTable";
import { appConfig } from "../config/appConfig";
import {
  dummyPortfolio,
  marketSummary,
  portfolioSeries,
  riskAlerts,
  riskSimulations,
  signalExplanations,
  watchlist,
} from "../data/mockMarketData";
import { buildRiskSignal, type Locale } from "../services/aiSignalService";
import { useRiskProfile } from "../state/useRiskProfile";
import type { DummyHolding, MarketSummaryItem, RiskSimulation, WatchlistItem } from "../types/market";

type PageKey = "dashboard" | "ask" | "signals" | "portfolio" | "research" | "risk";

const pageKeys: PageKey[] = ["dashboard", "ask", "signals", "portfolio", "research", "risk"];

const copy = {
  en: {
    aiConfidence: "AI Confidence",
    alertLabel: "Alerts",
    brandSubtitle: "AI stock research workspace",
    chartHeading: "MAD 120,000 growth path",
    chartLatest: "Latest simulated value",
    chartBadge: "Manual portfolio",
    chartEyebrow: "Portfolio simulation",
    checklist: ["Suitability profile", "Paper trading ledger", "Compliance audit log", "Broker integration review"],
    educationBadge: "Reviewable",
    educationEyebrow: "Explainability",
    educationHeading: "Why this signal?",
    heroEyebrow: "Morocco retail market",
    heroSubtitle:
      "Ranked Casablanca-listed stocks, explainable AI signals, manual portfolios, and risk alerts. No trade execution.",
    heroStatus: "No execution enabled",
    heroTitle: "AI stock research for Moroccan retail investors",
    languageLabel: "Language",
    marketAria: "Market summary",
    nav: ["Dashboard", "Ask AI", "Signals", "Portfolio", "Research", "Risk"],
    askPage: {
      answerTitle: "Simulated AI response",
      disclaimer:
        "Maroq is in research mode. This response is educational, simulated, and not financial advice.",
      emptyHint: "Ask Maroq AI about a Moroccan stock, signal, risk, or paper portfolio.",
      examples: [
        "Should I add ATW or IAM to a balanced paper portfolio?",
        "What risks should I check before buying LHM?",
        "Compare BOA and TQM for a low-risk investor.",
      ],
      inputLabel: "Ask about Moroccan stocks",
      orbitCenter: "Loading phase",
      orbitSubcopy: "Generating research response",
      placeholder: "Ask about ATW, IAM, LHM, TQM, BOA, portfolio risk, or paper trading...",
      send: "Ask Maroq AI",
      stages: [
        "Tickers / watchlist",
        "Pricing / charting",
        "Stats refreshed",
        "Reports / filings",
        "Criteria / options",
        "Markets scoped",
        "Memory updated",
        "Response / exports",
      ],
      subtitle:
        "A user-facing assistant for stock questions, watchlist context, risk checks, and explainable research.",
      tickerLabel: "Collected tickers",
    },
    pageSectionEyebrow: "MVP page",
    newWatchlist: "New Watchlist",
    riskCardEyebrow: "Retail guardrail",
    riskCardTitle: "No trade execution.",
    riskCardText: "Maroq ranks, explains, tracks, and alerts. Users cannot place orders inside this MVP.",
    roadmapBadge: "Controls",
    roadmapEyebrow: "MVP control plane",
    roadmapHeading: "MVP boundaries",
    searchLabel: "Search",
    signalHeading: "Risk-profile guidance",
    signalModelBadge: "Model stub",
    signalRiskAppetite: "Risk appetite",
    opportunityEyebrow: "Market opportunity",
    opportunityHeading: "Why Morocco is ready for AI investing tools",
    opportunityMetrics: [
      {
        label: "Public equity market",
        value: "+1T MAD",
        detail: "CSE capitalization history showed about MAD 1.03T on 04/02/2026.",
      },
      {
        label: "Listed universe",
        value: "70+ issuers",
        detail: "Enough listed companies and sectors for watchlists, screening, and education.",
      },
      {
        label: "MVP wedge",
        value: "Research first",
        detail: "Start with education, paper trading, and risk controls before live execution.",
      },
    ],
    opportunityCards: [
      {
        title: "Current opportunities",
        text: "Retail investors need simpler tools for watchlists, company research, risk explanations, and MAD portfolio planning.",
        source: "Opportunity: underserved retail research workflows",
      },
      {
        title: "Market size signal",
        text: "A market capitalization above MAD 1 trillion gives Maroq a credible local equity universe to analyze without starting with global assets.",
        source: "Source: Casablanca Stock Exchange capitalization history",
      },
      {
        title: "Financial services momentum",
        text: "Morocco's regulators and financial institutions are actively discussing fintech, payments infrastructure, financial inclusion, and market modernization.",
        source: "Sources: AMMC FinTech portal, Bank Al-Maghrib reports",
      },
      {
        title: "AI trading potential",
        text: "AI can help screen securities, explain signals, detect concentration risk, simulate scenarios, and keep every output auditable.",
        source: "Product wedge: decision support, not autonomous trading",
      },
    ],
    solutionEyebrow: "Solution",
    solutionHeading: "What Maroq delivers in the MVP",
    solutionPillars: [
      {
        title: "AI watchlist analysis",
        text: "Ranks Moroccan equities by liquidity, trend quality, dividends, sector exposure, and portfolio fit.",
        status: "Screen",
      },
      {
        title: "Explainable stock signals",
        text: "Shows reasons, risks, confidence, data used, and what would change the signal before a user simulates a trade.",
        status: "Explain",
      },
      {
        title: "Risk-profile guidance",
        text: "Adapts warnings and allocations to conservative, balanced, growth, or speculative investor profiles.",
        status: "Guide",
      },
      {
        title: "Manual portfolio tracking",
        text: "Lets users track holdings, allocations, MAD value, concentration, and P/L manually.",
        status: "Track",
      },
      {
        title: "Compliance-first UX",
        text: "Keeps outputs educational with disclaimers, audit logs, source timestamps, and no live trading in the MVP.",
        status: "Protect",
      },
      {
        title: "French / English interface",
        text: "Supports English and French today, with Arabic planned once product copy and workflows stabilize.",
        status: "Localize",
      },
    ],
    showcase: {
      action: "Signal",
      aiAnalysis: "AI analysis",
      aiScore: "AI score",
      allocation: "Allocation",
      expectedReturn: "Return",
      heading: "Manual 5-stock portfolio with AI risk analysis",
      holding: "Holding",
      maxDrawdown: "Max drawdown",
      projectedValue: "Projected value",
      revenue: "Simulated revenue",
      risk: { low: "Low", medium: "Medium", high: "High" },
      sector: "Sector",
      simulated: "Simulated",
      subheading: "Manual portfolio showcase",
      trades: "Suggested review actions",
      value: "Portfolio value",
      volatility: "Volatility",
      winRate: "Win rate",
    },
    pages: {
      dashboard: {
        eyebrow: "Morocco retail market",
        title: "AI stock research for Moroccan retail investors",
        description: "",
        metrics: [],
        sections: [],
      },
      ask: {
        eyebrow: "app.maroqai.com",
        title: "Ask Maroq AI about stocks",
        description: "",
        metrics: [],
        sections: [],
      },
      signals: {
        eyebrow: "AI signal center",
        title: "Review model-ranked opportunities before acting",
        description:
          "A dedicated page for explainable AI signals, confidence, risk warnings, and the data that shaped each recommendation.",
        metrics: [
          { label: "Signals generated", value: "18", tone: "positive" },
          { label: "High-risk flags", value: "4", tone: "negative" },
          { label: "Audit records", value: "100%", tone: "positive" },
        ],
        sections: [
          {
            title: "AI watchlist analysis",
            text: "Rank Moroccan equities by liquidity, momentum, dividend quality, concentration risk, and fit with the user's risk profile.",
            items: ["Liquidity score", "Trend quality", "Dividend stability", "Portfolio fit", "Data freshness"],
          },
          {
            title: "Explainable stock signals",
            text: "Show the model reasoning in plain language so a user can inspect the recommendation before simulating a trade.",
            items: ["Reasons", "Risks", "Confidence", "Data used", "What would change the signal"],
          },
          {
            title: "Audit trail",
            text: "Record every generated signal with inputs, timestamp, model mode, disclaimer state, and user risk profile.",
            items: ["Audit ID", "Source timestamp", "Risk profile", "Disclaimer shown"],
          },
        ],
      },
      portfolio: {
        eyebrow: "Paper portfolio",
        title: "Track simulated holdings and MAD performance",
        description:
          "A manual portfolio workspace for holdings, allocation, P/L, concentration, and AI-generated risk alerts.",
        metrics: [
          { label: "Paper value", value: "MAD 145,870", tone: "positive" },
          { label: "Cash buffer", value: "MAD 18,000", tone: "neutral" },
          { label: "Largest exposure", value: "45% LHM", tone: "negative" },
        ],
        sections: [
          {
            title: "Manual MAD portfolio tracking",
            text: "Let users enter and monitor holdings in Moroccan dirham without any order placement.",
            items: ["Cash notes", "Manual positions", "Portfolio value", "No order execution"],
          },
          {
            title: "Portfolio simulation",
            text: "Use the risk profile to highlight concentration, liquidity, drawdown, and dividend-risk issues.",
            items: ["Low risk scenario", "Medium risk scenario", "High risk scenario", "Projected drawdown"],
          },
          {
            title: "Rebalance assistant",
            text: "Recommend simulated rebalances that are consistent with risk tolerance and concentration limits.",
            items: ["Trim concentration", "Raise cash", "Add defensive names", "Review volatility"],
          },
        ],
      },
      research: {
        eyebrow: "Market research",
        title: "Turn market data into investor-friendly insight",
        description:
          "A research page for market briefs, company notes, sector explainers, source timestamps, and AI summaries.",
        metrics: [
          { label: "Company notes", value: "12", tone: "positive" },
          { label: "Sectors tracked", value: "7", tone: "neutral" },
          { label: "Data freshness", value: "Mock", tone: "neutral" },
        ],
        sections: [
          {
            title: "Daily market brief",
            text: "Summarize MASI movement, volume shifts, top movers, sector themes, and watchlist changes.",
            items: ["Market summary", "Top movers", "Liquidity notes", "Dividend calendar"],
          },
          {
            title: "Company research card",
            text: "Give each listed company a simple research profile with fundamentals, trend, risks, and AI explanation.",
            items: ["Business profile", "Trend quality", "Dividend note", "Risk factors"],
          },
          {
            title: "Localization roadmap",
            text: "Keep French and English complete in the MVP, then add Arabic once the workflows and compliance copy are stable.",
            items: ["English", "French", "Arabic later", "Localized MAD formatting"],
          },
        ],
      },
      risk: {
        eyebrow: "Risk profile",
        title: "Keep AI recommendations aligned with suitability",
        description:
          "A risk and compliance page for user suitability, allocation limits, education acknowledgements, and AI audit trails.",
        metrics: [
          { label: "Risk mode", value: "Balanced", tone: "positive" },
          { label: "Max drawdown", value: "10%", tone: "neutral" },
          { label: "Acknowledgements", value: "Pending", tone: "negative" },
        ],
        sections: [
          {
            title: "Risk-profile guidance",
            text: "Capture investing experience, horizon, loss tolerance, liquidity needs, income stability, and goals.",
            items: ["Conservative", "Balanced", "Growth", "Speculative"],
          },
          {
            title: "Compliance-first disclaimers",
            text: "Keep every AI output reviewable and ensure users understand the simulated, educational nature of the product.",
            items: ["Not financial advice", "No guaranteed returns", "No live trading in MVP", "User acknowledgement"],
          },
          {
            title: "Audit logs",
            text: "Store a reviewable record for each AI output and paper order so product, compliance, and support teams can inspect decisions.",
            items: ["Signal inputs", "Model output", "Timestamp", "User risk mode"],
          },
        ],
      },
    },
    watchlistEyebrow: "Casablanca watchlist",
    riskAlertsEyebrow: "Risk alerts",
    riskAlertsHeading: "Manual portfolio alerts",
    watchlistAlert: "Alert",
    watchlistHeading: "Ranked Casablanca stocks",
    watchlistReason: "Why",
    watchlistSignal: "Signal",
    watchlistSort: "Sort",
  },
  fr: {
    aiConfidence: "Confiance IA",
    alertLabel: "Alertes",
    brandSubtitle: "Espace recherche actions IA",
    chartHeading: "Parcours de croissance de 120 000 MAD",
    chartLatest: "Derniere valeur simulee",
    chartBadge: "Portefeuille manuel",
    chartEyebrow: "Simulation de portefeuille",
    checklist: ["Profil d'adequation", "Journal de paper trading", "Audit de conformite", "Revue integration broker"],
    educationBadge: "Verifiable",
    educationEyebrow: "Explicabilite",
    educationHeading: "Pourquoi ce signal ?",
    heroEyebrow: "Marche retail marocain",
    heroSubtitle:
      "Actions casablancaises classees, signaux IA explicables, portefeuilles manuels et alertes risque. Pas d'execution.",
    heroStatus: "Execution desactivee",
    heroTitle: "Recherche actions IA pour investisseurs retail marocains",
    languageLabel: "Langue",
    marketAria: "Resume du marche",
    nav: ["Tableau de bord", "Demander IA", "Signaux", "Portefeuille", "Recherche", "Risque"],
    askPage: {
      answerTitle: "Reponse IA simulee",
      disclaimer:
        "Maroq est en mode recherche. Cette reponse est educative, simulee et ne constitue pas un conseil financier.",
      emptyHint: "Posez une question a Maroq IA sur une action marocaine, un signal, un risque ou un portefeuille papier.",
      examples: [
        "Dois-je ajouter ATW ou IAM a un portefeuille papier equilibre ?",
        "Quels risques verifier avant d'acheter LHM ?",
        "Comparer BOA et TQM pour un investisseur prudent.",
      ],
      inputLabel: "Question sur les actions marocaines",
      orbitCenter: "Phase de chargement",
      orbitSubcopy: "Generation de la reponse recherche",
      placeholder: "Demandez ATW, IAM, LHM, TQM, BOA, le risque portefeuille ou le paper trading...",
      send: "Demander a Maroq IA",
      stages: [
        "Tickers / watchlist",
        "Prix / graphiques",
        "Stats actualisees",
        "Rapports / filings",
        "Criteres / options",
        "Marches scopes",
        "Memoire actualisee",
        "Reponse / exports",
      ],
      subtitle:
        "Un assistant utilisateur pour questions actions, contexte watchlist, controles risque et recherche explicable.",
      tickerLabel: "Tickers collectes",
    },
    pageSectionEyebrow: "Page MVP",
    newWatchlist: "Nouvelle watchlist",
    riskCardEyebrow: "Garde-fou retail",
    riskCardTitle: "Pas d'execution d'ordres.",
    riskCardText:
      "Maroq classe, explique, suit et alerte. Aucun ordre ne peut etre place dans ce MVP.",
    roadmapBadge: "Controles",
    roadmapEyebrow: "Plan MVP",
    roadmapHeading: "Limites MVP",
    searchLabel: "Recherche",
    signalHeading: "Guidage profil risque",
    signalModelBadge: "Modele test",
    signalRiskAppetite: "Appetit au risque",
    opportunityEyebrow: "Opportunite marche",
    opportunityHeading: "Pourquoi le Maroc est pret pour des outils d'investissement IA",
    opportunityMetrics: [
      {
        label: "Marche actions",
        value: "+1T MAD",
        detail: "L'historique de capitalisation CSE affichait environ 1,03T MAD au 04/02/2026.",
      },
      {
        label: "Univers cote",
        value: "70+ emetteurs",
        detail: "Assez de societes et secteurs pour watchlists, filtrage et education.",
      },
      {
        label: "Angle MVP",
        value: "Recherche d'abord",
        detail: "Commencer par education, paper trading et controles risque avant execution reelle.",
      },
    ],
    opportunityCards: [
      {
        title: "Opportunites actuelles",
        text: "Les investisseurs retail ont besoin d'outils simples pour watchlists, recherche societes, explications de risque et planification MAD.",
        source: "Opportunite: workflows recherche retail peu servis",
      },
      {
        title: "Signal de taille marche",
        text: "Une capitalisation au-dessus de 1 trillion MAD donne a Maroq un univers actions local credible a analyser.",
        source: "Source: historique capitalisation Bourse de Casablanca",
      },
      {
        title: "Avancee des services financiers",
        text: "Les institutions marocaines discutent activement fintech, infrastructures de paiement, inclusion financiere et modernisation du marche.",
        source: "Sources: portail FinTech AMMC, rapports Bank Al-Maghrib",
      },
      {
        title: "Potentiel IA pour trading",
        text: "L'IA peut filtrer les valeurs, expliquer les signaux, detecter la concentration, simuler des scenarios et auditer chaque sortie.",
        source: "Angle produit: aide a la decision, pas trading autonome",
      },
    ],
    solutionEyebrow: "Solution",
    solutionHeading: "Ce que Maroq livre dans le MVP",
    solutionPillars: [
      {
        title: "Analyse IA de watchlist",
        text: "Classe les actions marocaines par liquidite, tendance, dividendes, exposition sectorielle et adequation portefeuille.",
        status: "Filtrer",
      },
      {
        title: "Signaux actions explicables",
        text: "Affiche raisons, risques, confiance, donnees utilisees et conditions qui changeraient le signal.",
        status: "Expliquer",
      },
      {
        title: "Guidage par profil de risque",
        text: "Adapte alertes et allocations aux profils prudent, equilibre, croissance ou speculatif.",
        status: "Guider",
      },
      {
        title: "Suivi portefeuille manuel",
        text: "Permet de suivre positions, allocations, valeur MAD, concentration et P/L manuellement.",
        status: "Suivre",
      },
      {
        title: "UX conformite d'abord",
        text: "Garde les sorties educatives avec disclaimers, audits, horodatage des sources et pas de trading reel dans le MVP.",
        status: "Proteger",
      },
      {
        title: "Interface francais / anglais",
        text: "Prend en charge anglais et francais aujourd'hui, avec arabe prevu apres stabilisation des parcours.",
        status: "Localiser",
      },
    ],
    showcase: {
      action: "Signal",
      aiAnalysis: "Analyse IA",
      aiScore: "Score IA",
      allocation: "Allocation",
      expectedReturn: "Rendement",
      heading: "Portefeuille manuel de 5 actions avec analyse risque IA",
      holding: "Ligne",
      maxDrawdown: "Baisse max",
      projectedValue: "Valeur projetee",
      revenue: "Revenu simule",
      risk: { low: "Faible", medium: "Moyen", high: "Eleve" },
      sector: "Secteur",
      simulated: "Simulation",
      subheading: "Demonstration portefeuille manuel",
      trades: "Actions de revue proposees",
      value: "Valeur du portefeuille",
      volatility: "Volatilite",
      winRate: "Taux de reussite",
    },
    pages: {
      dashboard: {
        eyebrow: "Marche retail marocain",
        title: "Recherche actions IA pour investisseurs retail marocains",
        description: "",
        metrics: [],
        sections: [],
      },
      ask: {
        eyebrow: "app.maroqai.com",
        title: "Posez vos questions actions a Maroq IA",
        description: "",
        metrics: [],
        sections: [],
      },
      signals: {
        eyebrow: "Centre de signaux IA",
        title: "Examiner les opportunites classees par le modele",
        description:
          "Une page pour les signaux IA explicables, la confiance, les alertes de risque et les donnees utilisees.",
        metrics: [
          { label: "Signaux generes", value: "18", tone: "positive" },
          { label: "Alertes risque", value: "4", tone: "negative" },
          { label: "Audits", value: "100%", tone: "positive" },
        ],
        sections: [
          {
            title: "Analyse IA de watchlist",
            text: "Classer les actions marocaines par liquidite, momentum, qualite des dividendes, risque de concentration et profil utilisateur.",
            items: ["Score liquidite", "Qualite tendance", "Stabilite dividende", "Adequation portefeuille", "Fraicheur donnees"],
          },
          {
            title: "Signaux actions explicables",
            text: "Afficher le raisonnement du modele en langage simple avant toute simulation de trade.",
            items: ["Raisons", "Risques", "Confiance", "Donnees utilisees", "Ce qui changerait le signal"],
          },
          {
            title: "Journal d'audit",
            text: "Enregistrer chaque signal avec entrees, horodatage, mode modele, disclaimer et profil de risque utilisateur.",
            items: ["ID audit", "Horodatage source", "Profil risque", "Disclaimer affiche"],
          },
        ],
      },
      portfolio: {
        eyebrow: "Portefeuille papier",
        title: "Suivre les positions simulees et la performance MAD",
        description:
          "Un espace portefeuille manuel pour positions, allocation, P/L, concentration et alertes risque IA.",
        metrics: [
          { label: "Valeur papier", value: "145 870 MAD", tone: "positive" },
          { label: "Cash", value: "18 000 MAD", tone: "neutral" },
          { label: "Plus forte exposition", value: "45% LHM", tone: "negative" },
        ],
        sections: [
          {
            title: "Suivi portefeuille manuel en MAD",
            text: "Permettre aux utilisateurs de saisir et suivre leurs positions en dirham marocain sans placement d'ordre.",
            items: ["Notes cash", "Positions manuelles", "Valeur portefeuille", "Aucune execution"],
          },
          {
            title: "Simulation portefeuille",
            text: "Signaler concentration, liquidite, drawdown et risques de dividende selon le profil utilisateur.",
            items: ["Scenario faible risque", "Scenario moyen risque", "Scenario risque eleve", "Drawdown projete"],
          },
          {
            title: "Assistant reequilibrage",
            text: "Proposer des reequilibrages simules coherents avec la tolerance au risque et les limites de concentration.",
            items: ["Reduire concentration", "Augmenter cash", "Ajouter defensives", "Revoir volatilite"],
          },
        ],
      },
      research: {
        eyebrow: "Recherche marche",
        title: "Transformer les donnees marche en insights simples",
        description:
          "Une page pour briefs marche, notes societes, analyses sectorielles, horodatage des sources et resumes IA.",
        metrics: [
          { label: "Notes societes", value: "12", tone: "positive" },
          { label: "Secteurs suivis", value: "7", tone: "neutral" },
          { label: "Fraicheur donnees", value: "Mock", tone: "neutral" },
        ],
        sections: [
          {
            title: "Brief marche quotidien",
            text: "Resumer MASI, volumes, top movers, themes sectoriels et changements de watchlist.",
            items: ["Resume marche", "Top movers", "Notes liquidite", "Calendrier dividendes"],
          },
          {
            title: "Fiche recherche societe",
            text: "Donner a chaque societe cotee un profil simple avec fondamentaux, tendance, risques et explication IA.",
            items: ["Profil activite", "Qualite tendance", "Note dividende", "Facteurs de risque"],
          },
          {
            title: "Roadmap localisation",
            text: "Garder le francais et l'anglais complets dans le MVP, puis ajouter l'arabe apres stabilisation des parcours.",
            items: ["Anglais", "Francais", "Arabe plus tard", "Formatage MAD localise"],
          },
        ],
      },
      risk: {
        eyebrow: "Profil de risque",
        title: "Aligner les recommandations IA avec l'adequation",
        description:
          "Une page risque et conformite pour adequation, limites d'allocation, validations education et audits IA.",
        metrics: [
          { label: "Mode risque", value: "Equilibre", tone: "positive" },
          { label: "Baisse max", value: "10%", tone: "neutral" },
          { label: "Validations", value: "En attente", tone: "negative" },
        ],
        sections: [
          {
            title: "Guidage par profil de risque",
            text: "Capturer experience, horizon, tolerance aux pertes, besoins de liquidite, revenus et objectifs.",
            items: ["Prudent", "Equilibre", "Croissance", "Speculatif"],
          },
          {
            title: "Disclaimers conformite",
            text: "Rendre chaque sortie IA auditable et rappeler le caractere simule et educatif du produit.",
            items: ["Pas un conseil financier", "Pas de rendement garanti", "Pas de trading reel MVP", "Validation utilisateur"],
          },
          {
            title: "Journaux d'audit",
            text: "Conserver un enregistrement consultable pour chaque sortie IA et ordre papier afin d'inspecter les decisions.",
            items: ["Entrees signal", "Sortie modele", "Horodatage", "Mode risque utilisateur"],
          },
        ],
      },
    },
    watchlistEyebrow: "Watchlist Casablanca",
    riskAlertsEyebrow: "Alertes risque",
    riskAlertsHeading: "Alertes portefeuille manuel",
    watchlistAlert: "Alerte",
    watchlistHeading: "Actions casablancaises classees",
    watchlistReason: "Pourquoi",
    watchlistSignal: "Signal",
    watchlistSort: "Trier",
  },
};

const marketTranslations: Record<string, Partial<MarketSummaryItem>> = {
  "MAD Liquidity": { label: "Liquidite MAD", detail: "Normale" },
  "Risk Mode": { label: "Mode risque", value: "Equilibre", detail: "Actif" },
};

const stanceTranslations: Record<string, string> = {
  "Defensive cash flow": "Cash-flow defensif",
  "Dividend stability": "Stabilite dividende",
  "Income quality": "Qualite des revenus",
  "Momentum watch": "Momentum a suivre",
  "Volume recovery": "Reprise des volumes",
};

const sectorTranslations: Record<string, string> = {
  Banking: "Banque",
  Materials: "Materiaux",
  Telecom: "Telecom",
  Utilities: "Services publics",
};

const actionTranslations: Record<string, DummyHolding["aiAction"]> = {
  Buy: "Buy",
  Hold: "Hold",
  Sell: "Sell",
};

const actionLabelsFr: Record<DummyHolding["aiAction"], string> = {
  Buy: "Acheter",
  Hold: "Conserver",
  Sell: "Vendre",
};

const simulationTranslations: Record<RiskSimulation["mode"], Pick<RiskSimulation, "aiSummary" | "recommendedTrades" | "title">> = {
  low: {
    title: "Risque faible",
    aiSummary:
      "L'IA conserve plus de liquidites, reduit la concentration sur les materiaux et privilegie la stabilite des dividendes.",
    recommendedTrades: ["Revoir la concentration LHM", "Surveiller IAM pour exposition defensive", "Garder une note de liquidite"],
  },
  medium: {
    title: "Risque moyen",
    aiSummary:
      "L'IA equilibre les valeurs de rendement avec un momentum selectif, tout en limitant l'exposition par titre au-dessus de 30%.",
    recommendedTrades: ["Revoir l'allocation LHM", "Garder ATW en conservation", "Surveiller l'exposition defensive TQM"],
  },
  high: {
    title: "Risque eleve",
    aiSummary:
      "L'IA augmente la rotation et l'exposition momentum, mais signale un risque de baisse plus important.",
    recommendedTrades: ["Revoir le risque momentum BOA", "Signaler la sensibilite drawdown LHM", "Garder l'execution hors Maroq"],
  },
};

const frenchExplanations = [
  "Filtre les valeurs cotees a Casablanca selon la liquidite, la qualite de tendance, la regularite des dividendes et le risque de concentration.",
  "Classe les opportunites en MAD afin que les investisseurs retail puissent planifier la taille d'allocation avant tout ordre.",
  "Ajoute une justification simple pour rendre chaque sortie IA verifiable avant action.",
];

export function App() {
  const [locale, setLocale] = useState<Locale>("en");
  const [activePage, setActivePage] = useState<PageKey>("dashboard");
  const { riskScore, setRiskScore } = useRiskProfile();
  const t = copy[locale];
  const pageCopy = t.pages[activePage];
  const signal = buildRiskSignal(riskScore, locale);
  const localizedMarketSummary: MarketSummaryItem[] =
    locale === "fr"
      ? marketSummary.map((item) => ({ ...item, ...marketTranslations[item.label] }))
      : marketSummary;
  const localizedWatchlist: WatchlistItem[] =
    locale === "fr"
      ? watchlist.map((item) => ({
          ...item,
          sector: sectorTranslations[item.sector] ?? item.sector,
          stance: stanceTranslations[item.stance] ?? item.stance,
        }))
      : watchlist;
  const localizedDummyPortfolio: DummyHolding[] =
    locale === "fr"
      ? dummyPortfolio.map((holding) => ({
          ...holding,
          aiAction: actionTranslations[holding.aiAction] ?? holding.aiAction,
          name: holding.name,
          sector: sectorTranslations[holding.sector] ?? holding.sector,
        }))
      : dummyPortfolio;
  const localizedRiskSimulations: RiskSimulation[] =
    locale === "fr"
      ? riskSimulations.map((simulation) => ({
          ...simulation,
          ...simulationTranslations[simulation.mode],
        }))
      : riskSimulations;
  const localizedExplanations = locale === "fr" ? frenchExplanations : signalExplanations;

  return (
    <div className="app-shell" lang={locale}>
      <aside className="sidebar" aria-label="Primary navigation">
        <MaroqLogo title={appConfig.appName} subtitle={t.brandSubtitle} />

        <nav className="nav-list">
          {t.nav.map((item, index) => (
            <button
              className={`nav-item ${pageKeys[index] === activePage ? "active" : ""}`}
              key={item}
              type="button"
              onClick={() => setActivePage(pageKeys[index])}
            >
              <span>{item}</span>
            </button>
          ))}
        </nav>

        <section className="risk-card">
          <span className="eyebrow">{t.riskCardEyebrow}</span>
          <strong>{t.riskCardTitle}</strong>
          <p>{t.riskCardText}</p>
        </section>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <div className="hero-copy">
            <p className="eyebrow">{pageCopy.eyebrow}</p>
            <h1>{pageCopy.title}</h1>
            {activePage === "dashboard" ? <p className="hero-subtitle">{t.heroSubtitle}</p> : null}
          </div>
          <div className="actions">
            <span className="hero-status">{t.heroStatus}</span>
            <div className="language-tabs" role="tablist" aria-label={t.languageLabel}>
              <button
                aria-selected={locale === "en"}
                className={locale === "en" ? "active" : ""}
                role="tab"
                type="button"
                onClick={() => setLocale("en")}
              >
                EN
              </button>
              <button
                aria-selected={locale === "fr"}
                className={locale === "fr" ? "active" : ""}
                role="tab"
                type="button"
                onClick={() => setLocale("fr")}
              >
                FR
              </button>
            </div>
            <button className="icon-button" type="button" aria-label={t.searchLabel}>
              <Search size={18} />
            </button>
            <button className="icon-button" type="button" aria-label={t.alertLabel}>
              <Bell size={18} />
            </button>
            <button className="primary-button" type="button">
              {t.newWatchlist}
            </button>
          </div>
        </header>

        {activePage === "dashboard" ? (
          <>
        <section className="market-strip" aria-label={t.marketAria}>
          {localizedMarketSummary.map((item) => (
            <article key={item.label}>
              <span>{item.label}</span>
              <strong>{item.value}</strong>
              <em className={item.tone}>{item.detail}</em>
            </article>
          ))}
          <article>
            <span>{t.aiConfidence}</span>
            <strong>{signal.confidence}%</strong>
            <em className={signal.tone}>{signal.label}</em>
          </article>
        </section>

        <section className="layout-grid">
          <SolutionPillars eyebrow={t.solutionEyebrow} heading={t.solutionHeading} pillars={t.solutionPillars} />

          <MarketOpportunity
            cards={t.opportunityCards}
            eyebrow={t.opportunityEyebrow}
            heading={t.opportunityHeading}
            metrics={t.opportunityMetrics}
          />

          <div className="panel chart-panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">{t.chartEyebrow}</p>
                <h2>{t.chartHeading}</h2>
              </div>
              <span className="signal-badge">
                <LineChart size={15} />
                {t.chartBadge}
              </span>
            </div>
            <PortfolioChart latestLabel={t.chartLatest} series={portfolioSeries} />
          </div>

          <RiskSignalPanel
            labels={{
              heading: t.signalHeading,
              modelBadge: t.signalModelBadge,
              riskAppetite: t.signalRiskAppetite,
            }}
            riskScore={riskScore}
            signal={signal}
            onRiskScoreChange={setRiskScore}
          />

          <WatchlistTable
            items={localizedWatchlist}
            labels={{
              alert: t.watchlistAlert,
              eyebrow: t.watchlistEyebrow,
              heading: t.watchlistHeading,
              reason: t.watchlistReason,
              signal: t.watchlistSignal,
              sort: t.watchlistSort,
            }}
          />

          <RiskAlertsPanel alerts={riskAlerts} eyebrow={t.riskAlertsEyebrow} heading={t.riskAlertsHeading} />

          <div className="panel education-panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">{t.educationEyebrow}</p>
                <h2>{t.educationHeading}</h2>
              </div>
              <span className="signal-badge">
                <ShieldCheck size={15} />
                {t.educationBadge}
              </span>
            </div>
            <ul>
              {localizedExplanations.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>

          <div className="panel roadmap-panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">{t.roadmapEyebrow}</p>
                <h2>{t.roadmapHeading}</h2>
              </div>
              <span className="signal-badge">
                <SlidersHorizontal size={15} />
                {t.roadmapBadge}
              </span>
            </div>
            <div className="checklist">
              {t.checklist.map((item) => (
                <span key={item}>{item}</span>
              ))}
            </div>
          </div>

          <TradingShowcase
            actionLabels={locale === "fr" ? actionLabelsFr : undefined}
            holdings={localizedDummyPortfolio}
            labels={t.showcase}
            simulations={localizedRiskSimulations}
          />
        </section>
          </>
        ) : activePage === "ask" ? (
          <AskStocksPage labels={t.askPage} />
        ) : (
          <DraftPage
            description={pageCopy.description}
            metrics={pageCopy.metrics}
            sectionEyebrow={t.pageSectionEyebrow}
            sections={pageCopy.sections}
          />
        )}
      </main>
    </div>
  );
}
