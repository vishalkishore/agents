export const generatePrediction = (stock, timeframe) => {
  return fetchPrediction(stock.symbol)
      .then(response => {
          const apiResponse = response.prediction;
          console.log("API response:", apiResponse);
          let confidence = apiResponse.bullish_probability > 0.5 ? apiResponse.bullish_probability : 1 - apiResponse.bullish_probability;
          return {
              trend: apiResponse.direction.toLowerCase(), // 'bullish' or 'bearish'
              confidence: (confidence * 100).toFixed(1),
              targetPrice: apiResponse.predicted_price.toFixed(2),
              timeframe: timeframe.label,
              supportLevel: apiResponse.closest_support ? apiResponse.closest_support.toFixed(2) : (parseFloat(stock.price) * 0.95).toFixed(2),
              resistanceLevel: apiResponse.closest_resistance ? apiResponse.closest_resistance.toFixed(2) : (parseFloat(stock.price) * 1.05).toFixed(2),
              indicators: apiResponse.indicators
          };
      })
      .catch(error => {
          console.error("Error fetching prediction:", error);
          const trend = Math.random() > 0.5 ? "bullish" : "bearish";
          return {
              trend,
              confidence: (60 + Math.floor(Math.random() * 30)).toFixed(1),
              targetPrice: trend === "bullish"
                  ? (parseFloat(stock.price) * (1 + Math.random() * 0.05)).toFixed(2)
                  : (parseFloat(stock.price) * (1 - Math.random() * 0.05)).toFixed(2),
              timeframe: timeframe.label,
              supportLevel: (parseFloat(stock.price) * 0.95).toFixed(2),
              resistanceLevel: (parseFloat(stock.price) * 1.05).toFixed(2)
          };
      });
};

function fetchPrediction(symbol) {
  return fetch("http://localhost:8000/api/analyse_prediction", {
      method: "POST",
      headers: {
          "Content-Type": "application/json"
      },
      body: JSON.stringify({ symbol })
  })
  .then(response => {
      if (!response.ok) {
          throw new Error("Failed to fetch prediction");
      }
      return response.json();
  });
}
