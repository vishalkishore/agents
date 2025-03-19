import { configureStore } from '@reduxjs/toolkit';
import stocksReducer from '../features/stocks/stocksSlice';
import indicatorsReducer from '../features/indicators/indicatorsSlice';
import timeframeReducer from '../features/timeframe/timeframeSlice';
import analysisReducer from '../features/analysis/analysisSlice';
import chatReducer from '../features/chat/chatSlice';

export const store = configureStore({
  reducer: {
    stocks: stocksReducer,
    indicators: indicatorsReducer,
    timeframe: timeframeReducer,
    analysis: analysisReducer,
    chat: chatReducer
  }
});
