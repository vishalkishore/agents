import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { LineChart, ChevronDown, Activity, MessageCircle } from 'lucide-react';
import { setSelectedStock } from '../features/stocks/stocksSlice';
import { toggleSidebar } from '../features/indicators/indicatorsSlice';
import { toggleChat } from '../features/chat/chatSlice';

const NavBar = () => {
  const dispatch = useDispatch();
  const { availableStocks, selectedStock } = useSelector(state => state.stocks);
  const { sidebarOpen } = useSelector(state => state.indicators);
  const { chatOpen } = useSelector(state => state.chat);

  return (
    <div className="flex items-center justify-between px-3 py-1.5 bg-slate-900 border-b border-slate-800">
      <div className="flex items-center gap-2">
        <LineChart className="w-5 h-5 text-blue-500" />
        <h1 className="text-base font-bold">TradePro</h1>
      </div>
      
      <div className="flex items-center gap-2">
        <div className="relative">
          <select
            className="bg-slate-800 rounded text-sm px-2 py-1 focus:outline-none focus:ring-1 focus:ring-blue-500 appearance-none pr-7"
            value={selectedStock.symbol}
            onChange={(e) => {
              const stock = availableStocks.find(s => s.symbol === e.target.value);
              dispatch(setSelectedStock(stock));
            }}
          >
            {availableStocks.map((stock) => (
              <option key={stock.symbol} value={stock.symbol}>
                {stock.symbol}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-1.5 top-1.5 h-3 w-3 text-slate-400 pointer-events-none" />
        </div>
        
        <button 
          className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-sm"
          onClick={() => dispatch(toggleSidebar())}
        >
          {sidebarOpen ? 'Hide' : ''}
          <Activity className="h-4 w-4 inline ml-0.5" />
        </button>
        
        <button 
          className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-sm"
          onClick={() => dispatch(toggleChat())}
        >
          <MessageCircle className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

export default NavBar;
