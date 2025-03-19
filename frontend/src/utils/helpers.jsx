// Generate a simulated prediction based on the current stock data
export const generatePrediction = (stock, timeframe) => {
    const trend = Math.random() > 0.5 ? 'bullish' : 'bearish';
    const confidence = (60 + Math.floor(Math.random() * 30)).toFixed(1);
    const targetPrice = trend === 'bullish' 
      ? (parseFloat(stock.price) * (1 + Math.random() * 0.05)).toFixed(2)
      : (parseFloat(stock.price) * (1 - Math.random() * 0.05)).toFixed(2);
    
    return {
      trend,
      confidence,
      targetPrice,
      timeframe: timeframe.label,
      supportLevel: (parseFloat(stock.price) * 0.95).toFixed(2),
      resistanceLevel: (parseFloat(stock.price) * 1.05).toFixed(2)
    };
  };
  