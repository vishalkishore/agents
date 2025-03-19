export const fetchStockData = async (symbol, interval) => {
    try {
      const response = await fetch(`http://localhost:8000/api/intraday/${symbol}?interval=5min&adjusted=true&extended_hours=false&outputsize=full&datatype=json`);
      if (!response.ok) throw new Error('Network response was not ok');
      
      const data = await response.json();
      
      return Object.entries(data["Time Series (5min)"])
        .map(([time, values]) => {
          const parsedTime = Math.floor(new Date(time).getTime() / 1000);
      
          if (isNaN(parsedTime)) {
            console.error("Invalid date encountered:", time);
            return null;
          }
      
          return {
            time: parsedTime,
            open: parseFloat(values["1. open"]),
            high: parseFloat(values["2. high"]),
            low: parseFloat(values["3. low"]),
            close: parseFloat(values["4. close"]),
            volume: parseInt(values["5. volume"], 10),
          };
        })
        .filter(item => item !== null)
        .sort((a, b) => a.time - b.time);
    } catch (error) {
      console.error('Error fetching intraday data:', error);
      throw error;
    }
  };
  