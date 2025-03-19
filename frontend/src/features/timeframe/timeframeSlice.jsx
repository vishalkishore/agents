import { createSlice } from '@reduxjs/toolkit';
import { TIMEFRAMES } from '../../constants';

const initialState = {
  availableTimeframes: TIMEFRAMES,
  selectedTimeframe: TIMEFRAMES[1]
};

export const timeframeSlice = createSlice({
  name: 'timeframe',
  initialState,
  reducers: {
    setSelectedTimeframe: (state, action) => {
      state.selectedTimeframe = action.payload;
    }
  }
});

export const { setSelectedTimeframe } = timeframeSlice.actions;

export default timeframeSlice.reducer;
