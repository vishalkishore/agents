import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { BarChart, AlertTriangle } from 'lucide-react';
import { setShowAnalysisPopup } from '../features/analysis/analysisSlice';

const AnalysisPopup = () => {
  const dispatch = useDispatch();
  const { showAnalysisPopup, prediction } = useSelector(state => state.analysis);

  if (!showAnalysisPopup || !prediction) return null;

  return (
    <div className="absolute top-4 right-4 w-64 bg-slate-800 border border-slate-700 rounded-lg shadow-lg p-3 z-50">
      <div className="flex justify-between items-center mb-2">
        <div className="flex items-center gap-1">
          <BarChart className="h-4 w-4 text-blue-400" />
          <h3 className="font-bold text-sm">Prediction Results</h3>
        </div>
        <button 
          className="text-slate-400 hover:text-white"
          onClick={() => dispatch(setShowAnalysisPopup(false))}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-slate-300">Outlook:</span>
          <span className={`font-medium ${prediction.trend === 'bullish' ? 'text-green-400' : 'text-red-400'}`}>
            {prediction.trend.toUpperCase()}
          </span>
        </div>
        
        <div className="flex justify-between">
          <span className="text-slate-300">Confidence:</span>
          <span className="font-medium">{prediction.confidence}%</span>
        </div>
        
        <div className="flex justify-between">
          <span className="text-slate-300">Target Price:</span>
          <span className="font-medium">${prediction.targetPrice}</span>
        </div>
        
        <div className="flex justify-between">
          <span className="text-slate-300">Support Level:</span>
          <span className="font-medium">${prediction.supportLevel}</span>
        </div>
        
        <div className="flex justify-between">
          <span className="text-slate-300">Resistance:</span>
          <span className="font-medium">${prediction.resistanceLevel}</span>
        </div>
        
        <div className="mt-2 bg-slate-700 p-2 rounded-md flex items-center gap-1">
          <AlertTriangle className="h-4 w-4 text-yellow-400" />
          <span className="text-xs text-yellow-200">This is a simulated prediction for demonstration purposes only.</span>
        </div>
      </div>
    </div>
  );
};

export default AnalysisPopup;
