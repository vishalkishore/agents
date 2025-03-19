import React, { useEffect, useRef } from 'react';
import { createChart, CandlestickSeries, LineSeries, HistogramSeries } from 'lightweight-charts';
import { useSelector } from 'react-redux';
import { RSI, BollingerBands, EMA } from 'technicalindicators';

const Chart = () => {
  const chartContainerRef = useRef();
  const { chartData } = useSelector(state => state.stocks);
  const { selectedIndicators } = useSelector(state => state.indicators);
  const { selectedTimeframe } = useSelector(state => state.timeframe);

  useEffect(() => {
    if (!chartContainerRef.current || chartData.length === 0) return;

    const container = chartContainerRef.current;
    const chart = createChart(container, {
      layout: {
        background: { color: '#1E293B' },
        textColor: '#D1D5DB',
      },
      grid: {
        vertLines: { color: '#334155' },
        horzLines: { color: '#334155' },
      },
      width: container.clientWidth,
      height: container.clientHeight,
    });

    const candlestickSeries = chart.addSeries(CandlestickSeries ,{
      upColor: '#22C55E',
      downColor: '#EF4444',
      borderVisible: false,
      wickUpColor: '#22C55E',
      wickDownColor: '#EF4444',
    });

    candlestickSeries.setData(chartData);

    const volumeSeries = chart.addSeries(HistogramSeries,{
      color: '#60A5FA',
      priceFormat: { type: 'volume' },
      priceScaleId: 'volume', // Assign a dedicated price scale for volume
      scaleMargins: {
        top: 0.75, // Move volume lower
        bottom: 0,
      },
    });

    // Configure the separate volume price scale
    chart.priceScale('volume').applyOptions({
      position: 'left',
      scaleMargins: { top: 0.75, bottom: 0 },
      borderColor: '#334155',
      autoScale: true,
    });

    volumeSeries.setData(
      chartData.map(d => ({
        time: d.time,
        value: d.volume,
        color: d.close >= d.open ? '#22C55E66' : '#EF444466', // Softer colors
      }))
    );


    // Add Technical Indicators

    // ✅ EMA (Exponential Moving Average)
    if (selectedIndicators.includes('ema')) {
      const emaValues = EMA.calculate({ period: 14, values: chartData.map(d => d.close) });
      const emaSeries = chart.addSeries(LineSeries, { color: '#60A5FA', lineWidth: 2 });

      const emaData = chartData.slice(-emaValues.length).map((item, index) => ({
        time: item.time,
        value: emaValues[index],
      }));

      emaSeries.setData(emaData);
    }

    // ✅ RSI (Relative Strength Index)
    if (selectedIndicators.includes('rsi')) {
      const rsiValues = RSI.calculate({ period: 14, values: chartData.map(d => d.close) });
      const rsiSeries = chart.addSeries(LineSeries,{ color: '#F59E0B', lineWidth: 2 });

      const rsiData = chartData.slice(-rsiValues.length).map((item, index) => ({
        time: item.time,
        value: rsiValues[index],
      }));

      rsiSeries.setData(rsiData);
    }

    // ✅ Bollinger Bands
    if (selectedIndicators.includes('bollinger')) {
      const bbValues = BollingerBands.calculate({
        period: 20,
        values: chartData.map(d => d.close),
        stdDev: 2,
      });

      const upperBandSeries = chart.addSeries(LineSeries, { color: '#EF4444', lineWidth: 1 });
      const lowerBandSeries = chart.addSeries(LineSeries, { color: '#10B981', lineWidth: 1 });

      const bbData = chartData.slice(-bbValues.length).map((item, index) => ({
        time: item.time,
        upper: bbValues[index].upper,
        lower: bbValues[index].lower,
      }));

      upperBandSeries.setData(bbData.map(d => ({ time: d.time, value: d.upper })));
      lowerBandSeries.setData(bbData.map(d => ({ time: d.time, value: d.lower })));
    }

    // Cleanup function
    return () => {
      chart.remove();
    };
  }, [chartData, selectedIndicators, selectedTimeframe]);

  return <div ref={chartContainerRef} className="w-full h-full" />;
};

export default Chart;
