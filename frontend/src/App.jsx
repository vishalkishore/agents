import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import NavBar from './components/NavBar';
import SidebarPanel from './components/SidebarPanel';
import Chart from './components/Chart';
import StockDetails from './components/StockDetails';
import AnalysisPopup from './components/AnalysisPopup';
import ChatPanel from './components/ChatPanel';
import { fetchStockData } from './features/stocks/stocksAPI';
import { setChartData } from './features/stocks/stocksSlice';
import { startAnalyzing, stopAnalyzing, setPrediction, setShowAnalysisPopup } from './features/analysis/analysisSlice';
import { addMessage } from './features/chat/chatSlice';
import { generatePrediction } from './utils/helpers';

function App() {
  const dispatch = useDispatch();
  const { selectedStock } = useSelector(state => state.stocks);
  const { selectedTimeframe } = useSelector(state => state.timeframe);
  const { sidebarOpen } = useSelector(state => state.indicators);
  const { chatOpen } = useSelector(state => state.chat);
  const { isAnalyzing } = useSelector(state => state.analysis);
  const { messages } = useSelector(state => state.chat);

  useEffect(() => {
    if (selectedTimeframe?.value !== '1D' && selectedTimeframe?.value !== '1W') {
      const loadData = async () => {
        try {
          const data = await fetchStockData(selectedStock.symbol, selectedTimeframe.value);
          dispatch(setChartData(data));
        } catch (error) {
          console.error('Error loading stock data:', error);
        }
      };
      
      loadData();
    }
  }, [dispatch, selectedStock, selectedTimeframe]);

  const handleAnalyzeClick = () => {
    dispatch(startAnalyzing());
    
    // Simulate analysis process
    setTimeout(() => {
      const prediction = generatePrediction(selectedStock, selectedTimeframe);
      dispatch(setPrediction(prediction));
      dispatch(stopAnalyzing());
      dispatch(setShowAnalysisPopup(true));
      
      // Add analysis to chat
      const analysisMessage = {
        id: messages.length + 3,
        user: 'TradeBot',
        text: `Analysis complete for ${selectedStock.symbol}: ${prediction.trend.toUpperCase()} outlook with ${prediction.confidence}% confidence. Target price: $${prediction.targetPrice} within this ${selectedTimeframe.label} timeframe.`,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      dispatch(addMessage(analysisMessage));
    }, 2000);
  };

  return (
    <div className="h-screen flex flex-col bg-slate-950 text-white">
      <NavBar />

      <div className="flex-1 flex overflow-hidden relative">
        {/* Left Sidebar - Indicators */}
        <div className={`${sidebarOpen ? 'w-32' : 'w-0'} bg-slate-900 border-r border-slate-800 flex flex-col transition-all duration-300 overflow-hidden z-40`}>
          <SidebarPanel />
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col p-1.5 z-10">
          {/* Stock Detail Header */}
          <StockDetails onAnalyzeClick={handleAnalyzeClick} isAnalyzing={isAnalyzing} />
          
          {/* Chart Area */}
          <div className="flex-1 bg-slate-900 rounded border border-slate-800 overflow-hidden z-20 relative">
            <Chart />
            <AnalysisPopup />
          </div>
        </div>
        
        {/* Right Chat Section */}
        {chatOpen && <ChatPanel />}
      </div>
    </div>
  );
}

export default App;
