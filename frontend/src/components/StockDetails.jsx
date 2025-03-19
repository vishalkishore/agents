import React from 'react';
import { useSelector } from 'react-redux';
import { BarChart } from 'lucide-react';
import TimeframeSelector from './TimeframeSelector';

const StockDetails = ({ onAnalyzeClick, isAnalyzing }) => {
  const { selectedStock } = useSelector(state => state.stocks);

  return (
    <div className="mb-1 flex justify-between items-center">
      <div>
        <div className="flex items-center gap-1">
          <h2 className="text-base font-bold">{selectedStock.symbol}</h2>
          <span className="text-slate-400 text-sm">{selectedStock.name}</span>
        </div>
        <div className="flex gap-2 items-center">
          <span className="text-sm">${selectedStock.price}</span>
          <span className={`text-sm ${selectedStock.change.startsWith('+') ? 'text-green-500' : 'text-red-500'}`}>
            {selectedStock.change}
          </span>
        </div>
      </div>
      
      <div className="flex items-center gap-2">
        <button
          className="flex items-center gap-1 px-3 py-1 bg-green-600 hover:bg-green-700 text-white rounded font-medium text-sm"
          onClick={onAnalyzeClick}
          disabled={isAnalyzing}
        >
          {isAnalyzing ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <BarChart className="h-4 w-4" />
              <span>Analyze & Predict</span>
            </>
          )}
        </button>
        
        <TimeframeSelector />
      </div>
    </div>
  );
};

export default StockDetails;
