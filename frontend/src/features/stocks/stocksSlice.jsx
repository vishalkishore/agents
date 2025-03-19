import { createSlice } from '@reduxjs/toolkit';
import { STOCKS } from '../../constants';

const initialState = {
  availableStocks: STOCKS,
  selectedStock: STOCKS[0],
  chartData: []
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
    }
  }
});

export const { setSelectedStock, setChartData } = stocksSlice.actions;

export default stocksSlice.reducer;
