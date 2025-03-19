export const fetchStockData = async (symbol, interval) => {
    try {

      let apiType, adjustedInterval, response;

      if (parseInt(interval) < 1440) {
        apiType = "intraday"; // intraday
        adjustedInterval = interval+"min";
      } else if (interval === "1440") {
        apiType = "daily"; // 1D (Daily)
        adjustedInterval = "1D";
      } else if (interval === "10080") {
        apiType = "daily"; // 1W (Weekly)
        adjustedInterval = "1W";
      } else if (interval === "43200") {
        apiType = "daily"; // 1M (Monthly)
        adjustedInterval = "1M";
      } else {
        throw new Error("Invalid interval provided");
      }
      if (apiType === "intraday") {
        response = await fetch(`http://localhost:8000/api/intraday/${symbol}?interval=${adjustedInterval ?? '5min'}&adjusted=true&extended_hours=false&outputsize=full&datatype=json`);
      }else{
        response = await fetch(`http://localhost:8000/api/daily/${symbol}?outputsize=full&datatype=json`);
      }
      
      if (!response.ok) throw new Error('Network response was not ok');
      
      const data = await response.json();
      
      const timeSeriesKey = Object.keys(data).find(key => key.startsWith("Time Series"));
      if (!timeSeriesKey) throw new Error("Time Series data not found in response");

      return Object.entries(data[timeSeriesKey])
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
  