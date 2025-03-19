import { createSlice } from '@reduxjs/toolkit';
import { STOCKS } from '../../constants';

const initialState = {
  availableStocks: STOCKS,
  currentStockMetaData: {
    symbol: 'AAPL',
    name: 'Apple Inc.',
    price: '205.78',
    change: '+2.35%',
  },
  selectedStock: STOCKS[0],
  chartData: [],
};

export const stocksSlice = createSlice({
  name: 'stocks',
  initialState,
  reducers: {
    setSelectedStock: (state, action) => {
      state.selectedStock = action.payload;
    },
    setChartData: (state, action) => {
      state.chartData = action.payload;
    },
    setCurrentStockMetaData: (state, action) => {
      if (state.chartData.length > 0) {
        state.currentStockMetaData = action.payload;
      }
    },
  },
});

export const { setSelectedStock, setChartData, setCurrentStockMetaData } = stocksSlice.actions;

export default stocksSlice.reducer;
