import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, User, Bot, Sparkles, X, MessageSquare } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';

const AnalystChat = ({ isOpen, onClose, activePage }) => {
  const [messages, setMessages] = useState([]);
  
  useEffect(() => {
    if (messages.length === 0) {
      const greetings = {
        'bracket': "Neural link stable. I am the Zerve Analyst. Ready to dive into the **Tournament Bracket Simulation**. Which group should we dissect first?",
        'fusion': "Fusion matrix synchronized. I'm here to help you interpret the **cross-domain interactions** between sports, markets, and climate.",
        'alpha': "Alpha Radar active. I've spotted some significant **market mispricings**. Would you like to review the high-conviction value plays?",
        'prophecy': "Prophecy Engine online. We are currently simulating **macro-signal shifts**. What global event shall we model next?"
      };
      const defaultGreeting = "Systems online. I am the Zerve Analyst. How can I assist with your tournament intelligence today?";
      setMessages([{ role: 'bot', text: greetings[activePage] || defaultGreeting }]);
    }
  }, [activePage, messages.length]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async (overrideInput = null) => {
    const text = overrideInput || input;
    if (!text.trim() || loading) return;
    
    const userMsg = { role: 'user', text: text };
    const history = messages.slice(-5).map(m => ({ role: m.role === 'user' ? 'user' : 'assistant', content: m.text }));
    
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      // Use fetch for streaming support
      const response = await fetch(`${axios.defaults.baseURL}/v1/analyst/chat`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-API-Key': 'conflux_dev_2026'
        },
        body: JSON.stringify({ 
          message: text, 
          history: history,
          context: { activePage: activePage },
          stream: true 
        })
      });

      if (!response.ok) throw new Error('Stream failed');

      // Add a placeholder bot message for the stream
      setMessages(prev => [...prev, { role: 'bot', text: '' }]);
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let botText = '';

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        const chunk = decoder.decode(value, { stream: true });
        botText += chunk;
        
        // Update the last message
        setMessages(prev => {
          const newMessages = [...prev];
          let displayText = botText;
          
          // Fallback: If the response is a JSON object (common if backend hasn't restarted)
          // we parse it to show only the 'response' field
          if (botText.trim().startsWith('{')) {
            try {
              const parsed = JSON.parse(botText);
              displayText = parsed.response || parsed.message || botText;
            } catch (e) {
              // Partial JSON, wait for more chunks or keep raw
            }
          }
          
          newMessages[newMessages.length - 1].text = displayText;
          return newMessages;
        });
      }
    } catch (err) {
      console.error('Chat error:', err);
      setMessages(prev => [...prev, { role: 'bot', text: "Communication link severed. Falling back to heuristic reasoning..." }]);
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    { label: "Who will win WC2026?", query: "Analyze the top 3 contenders for the World Cup based on all signals." },
    { label: "Top Upset Picks?", query: "Identify the top 3 teams currently most undervalued by markets." },
    { label: "Market Alpha?", query: "Where is the biggest mispricing in prediction markets right now?" },
    { label: "Climate Briefing", query: "Which venues pose the highest biometric risk for top teams?" },
    { label: "Cultural Moments", query: "Which social trends are reaching a tipping point and how do they link to markets?" }
  ];

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div 
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          className="fixed right-0 top-0 h-screen w-96 bg-bg/95 backdrop-blur-xl border-l border-border z-[100] flex flex-col shadow-2xl"
        >
          {/* Header */}
          <div className="p-6 border-b border-border flex justify-between items-center bg-bg1/50">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-amber/10 flex items-center justify-center text-amber">
                <Bot size={20} />
              </div>
              <div>
                <h3 className="text-xs font-bold tracking-widest uppercase">Zerve Analyst</h3>
                <p className="text-[9px] font-mono text-teal uppercase animate-pulse">Neural Link Active</p>
              </div>
            </div>
            <button onClick={onClose} className="p-2 hover:bg-foreground/20 rounded-full transition-colors text-foreground/30 hover:text-foreground">
              <X size={20} />
            </button>
          </div>

          {/* Messages */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-hide">
            {messages.map((msg, i) => (
              <motion.div 
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
              >
                <div className={`w-8 h-8 rounded flex items-center justify-center shrink-0 ${
                  msg.role === 'user' ? 'bg-foreground/25 text-muted' : 'bg-amber/10 text-amber'
                }`}>
                  {msg.role === 'user' ? <User size={14}/> : <Sparkles size={14}/>}
                </div>
                <div className={`p-4 rounded-2xl max-w-[85%] text-[12px] leading-[1.6] shadow-lg ${
                  msg.role === 'user' 
                    ? 'bg-amber text-bg font-medium rounded-tr-none' 
                    : 'bg-[var(--card-bg)] border border-border backdrop-blur-md rounded-tl-none text-foreground/90'
                }`}>
                  <div className="prose prose-invert prose-xs max-w-none 
                    prose-p:leading-relaxed prose-p:mb-2 last:prose-p:mb-0
                    prose-strong:text-amber prose-strong:font-bold
                    prose-ul:my-2 prose-li:my-1">
                    <ReactMarkdown>{msg.text}</ReactMarkdown>
                  </div>
                </div>
              </motion.div>
            ))}
            {loading && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded bg-amber/10 flex items-center justify-center text-amber">
                  <Bot size={14}/>
                </div>
                <div className="flex gap-1 items-center p-3 rounded-xl bg-bg1 border border-border">
                   <div className="w-1 h-1 bg-amber rounded-full animate-bounce" />
                   <div className="w-1 h-1 bg-amber rounded-full animate-bounce [animation-delay:0.2s]" />
                   <div className="w-1 h-1 bg-amber rounded-full animate-bounce [animation-delay:0.4s]" />
                </div>
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="px-6 py-2 overflow-x-auto scrollbar-hide flex gap-2 shrink-0 border-t border-border">
            {quickActions.map(action => (
              <button
                key={action.label}
                onClick={() => handleSend(action.query)}
                disabled={loading}
                className="whitespace-nowrap px-3 py-1.5 rounded-full bg-foreground/20 border border-border text-[9px] font-mono text-muted hover:text-foreground hover:bg-foreground/25 transition-all uppercase tracking-widest disabled:opacity-80 dark:opacity-50"
              >
                {action.label}
              </button>
            ))}
          </div>

          {/* Input */}
          <div className="p-6 border-t border-border bg-bg1/50">
            <div className="relative">
              <input 
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Ask the Analyst anything..."
                className="w-full bg-foreground/20 border border-border rounded-lg py-3 px-4 text-[11px] focus:outline-none focus:border-amber/50 transition-all placeholder:text-foreground/10"
              />
              <button 
                onClick={handleSend}
                disabled={!input.trim() || loading}
                className="absolute right-2 top-1.5 p-1.5 bg-amber text-bg rounded-md hover:scale-105 active:scale-95 disabled:opacity-80 dark:opacity-50 disabled:scale-100 transition-all"
              >
                <Send size={16} />
              </button>
            </div>
            <p className="mt-3 text-[9px] font-mono text-foreground/10 text-center uppercase tracking-widest">
              Secured Neural Uplink v4.0
            </p>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default AnalystChat;
