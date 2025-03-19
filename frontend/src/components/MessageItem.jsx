import React from 'react';

const MessageItem = ({ message }) => {
  return (
    <div 
      className={`p-1.5 rounded-lg text-sm ${message.user === 'You' ? 'bg-blue-900 ml-4' : 'bg-slate-800 mr-4'}`}
    >
      <div className="flex justify-between items-center mb-0.5">
        <span className={`font-medium ${message.user === 'TradeBot' ? 'text-green-400' : 'text-blue-400'}`}>
          {message.user}
        </span>
        <span className="text-slate-400 text-xs">{message.time}</span>
      </div>
      <p>{message.text}</p>
    </div>
  );
};

export default MessageItem;
