export const appConfig = {
  appName: import.meta.env.VITE_APP_NAME ?? "Maroq",
  aiSignalMode: import.meta.env.VITE_AI_SIGNAL_MODE ?? "mock",
  marketDataMode: import.meta.env.VITE_MARKET_DATA_MODE ?? "mock",
};
