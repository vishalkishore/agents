export const TIMEFRAMES = [
    { label: '1m', value: '1' },
    { label: '5m', value: '5' },
    { label: '15m', value: '15' },
    { label: '30m', value: '30' },
    { label: '1H', value: '60' },
    { label: '1D', value: '1440' },
  ];
  
  export const AVAILABLE_INDICATORS = [
    { label: 'RSI', value: 'rsi', icon: 'Activity', description: 'Relative Strength Index - Momentum indicator that measures the magnitude of recent price changes' },
    { label: 'BB', value: 'bollinger', icon: 'Waves', description: 'Bollinger Bands - Shows volatility channels around a moving average' },
    { label: 'EMA', value: 'ema', icon: 'TrendingDown', description: 'Exponential Moving Average - Weighted moving average emphasizing recent prices' },
  ];
  
  export const STOCKS = [
    { symbol: 'AAPL', name: 'Apple Inc.', price: '205.78', change: '+2.35%', sector: 'Technology' },
    { symbol: 'GOOGL', name: 'Alphabet Inc.', price: '172.54', change: '-0.87%', sector: 'Technology' },
    { symbol: 'MSFT', name: 'Microsoft Corporation', price: '415.32', change: '+1.02%', sector: 'Technology' },
    { symbol: 'AMZN', name: 'Amazon.com Inc.', price: '185.67', change: '+0.45%', sector: 'Consumer Cyclical' },
  ];
  