import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  isAnalyzing: false,
  showAnalysisPopup: false,
  prediction: null
};

export const analysisSlice = createSlice({
  name: 'analysis',
  initialState,
  reducers: {
    startAnalyzing: (state) => {
      state.isAnalyzing = true;
    },
    stopAnalyzing: (state) => {
      state.isAnalyzing = false;
    },
    setPrediction: (state, action) => {
      state.prediction = action.payload;
    },
    setShowAnalysisPopup: (state, action) => {
      state.showAnalysisPopup = action.payload;
    }
  }
});

export const { startAnalyzing, stopAnalyzing, setPrediction, setShowAnalysisPopup } = analysisSlice.actions;

export default analysisSlice.reducer;
