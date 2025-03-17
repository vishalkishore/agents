import { useEffect, useState } from 'react';
import { Send } from 'lucide-react';
import { AdvancedChart } from 'react-tradingview-embed';
import { useMemo } from 'react';

function App() {
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const [messages, setMessages] = useState<Array<{ text: string; isBot: boolean }>>([
    { text: "Hello! I'm your trading assistant. How can I help you today?", isBot: true }
  ]);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim()) {
      setMessages([...messages, { text: input, isBot: false }]);
      setInput('');
      // Simulate bot response
      setTimeout(() => {
        setMessages(prev => [...prev, { 
          text: "I'm analyzing your request. Please note that I'm a demo bot for now.", 
          isBot: true 
        }]);
      }, 1000);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const chartComponent = useMemo(() => (
    <AdvancedChart
      widgetProps={{
        theme: 'dark',
        symbol: 'NASDAQ:AAPL',
        height: '100%',
        width: '100%',
        allow_symbol_change: true,
        container_id: "tradingview_chart"
      }}
    />
  ), []);

  return (
    <div className="min-h-screen bg-gray-900 text-white flex">
      <div className="w-2/3 h-screen">
        {/* Trading View Chart */}
        
        <div className="h-full bg-gray-800">
          {chartComponent} {/* Use the memoized chart */}
        </div>
      </div>
      
      {/* Chat Interface */}
      <div className="w-1/3 h-screen bg-gray-800 flex flex-col">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`${message.isBot ? 'flex' : 'flex justify-end'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-3 ${
                  message.isBot ? 'bg-gray-700 text-white' : 'bg-blue-500 text-white'
                }`}
              >
                {message.text}
              </div>
            </div>
          ))}
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-700 flex">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 bg-gray-700 text-white placeholder-gray-400 resize-none"
            rows={2}
          />
          <button
            onClick={handleSend}
            className="bg-blue-500 text-white hover:bg-blue-600"
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
