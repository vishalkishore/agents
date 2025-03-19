import React from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import remarkGfm from 'remark-gfm';

const Card = ({ children }) => {
  return <div className="markdown-card">{children}</div>;
};

const Citation = ({ href, children }) => {
  return (
    <a href={href} className="citation" target="_blank" rel="noopener noreferrer">
      {children} <span className="citation-icon">📚</span>
    </a>
  );
};


const MessageItem = ({ message }) => {
  const isBot = message.user === 'TradeBot';

  const components = {
    // Convert div with class "card" to our Card component
    div: ({ node, ...props }) => {
      if (node.properties?.className === 'card') {
        return <Card {...props} />;
      }
      return <div {...props} />;
    },
    a: ({ node, ...props }) => {
      if (props.href && (props.href.startsWith('http') || props.href.startsWith('https'))) {
        return <Citation {...props} />;
      }
      return <a {...props} />;
    },
  };

  return (
    <div className={`p-1.5 rounded-lg text-sm ${message.user === 'You' ? 'bg-blue-900 ml-4' : 'bg-slate-800 mr-4'}`}>
      <div className="flex justify-between items-center mb-0.5">
        <span className={`font-medium ${message.user === 'TradeBot' ? 'text-green-400' : 'text-blue-400'}`}>
          {message.user}
        </span>
        <span className="text-slate-400 text-xs">{message.time}</span>
      </div>
      
      <div className="markdown-content text-sm">
        {isBot ? (
          <ReactMarkdown
            components={components}
            rehypePlugins={[rehypeRaw]}
            remarkPlugins={[remarkGfm]}
          >
            {message.text}
          </ReactMarkdown>
        ) : (
          <p>{message.text}</p>
        )}
      </div>
    </div>
  );
};

export default MessageItem;
