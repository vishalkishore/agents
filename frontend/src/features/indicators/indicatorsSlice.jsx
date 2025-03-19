import { createSlice } from '@reduxjs/toolkit';
import { AVAILABLE_INDICATORS } from '../../constants';

const initialState = {
  availableIndicators: AVAILABLE_INDICATORS,
  selectedIndicators: [],
  sidebarOpen: true
};

export const indicatorsSlice = createSlice({
  name: 'indicators',
  initialState,
  reducers: {
    setSelectedIndicators: (state, action) => {
      state.selectedIndicators = action.payload;
    },
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    }
  }
});

export const { setSelectedIndicators, toggleSidebar } = indicatorsSlice.actions;

export default indicatorsSlice.reducer;
