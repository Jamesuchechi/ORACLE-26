import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, User, Bot, Sparkles, X, MessageSquare } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';

const AnalystChat = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState([
    { role: 'bot', text: "Systems online. I am the Zerve Analyst. How can I assist with your tournament intelligence today?" }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    
    const userMsg = { role: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/v1/analyst/chat', { message: userMsg.text });
      setMessages(prev => [...prev, { role: 'bot', text: response.data.response }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', text: "Communication link severed. Please check system status." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div 
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          className="fixed right-0 top-0 h-screen w-96 bg-bg/95 backdrop-blur-xl border-l border-white/10 z-[100] flex flex-col shadow-2xl"
        >
          {/* Header */}
          <div className="p-6 border-b border-white/5 flex justify-between items-center bg-bg1/50">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-amber/10 flex items-center justify-center text-amber">
                <Bot size={20} />
              </div>
              <div>
                <h3 className="text-xs font-bold tracking-widest uppercase">Zerve Analyst</h3>
                <p className="text-[9px] font-mono text-teal uppercase animate-pulse">Neural Link Active</p>
              </div>
            </div>
            <button onClick={onClose} className="p-2 hover:bg-white/5 rounded-full transition-colors text-white/30 hover:text-white">
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
                  msg.role === 'user' ? 'bg-white/10 text-white/40' : 'bg-amber/10 text-amber'
                }`}>
                  {msg.role === 'user' ? <User size={14}/> : <Sparkles size={14}/>}
                </div>
                <div className={`p-4 rounded-2xl max-w-[85%] text-[12px] leading-[1.6] shadow-lg ${
                  msg.role === 'user' 
                    ? 'bg-amber text-bg font-medium rounded-tr-none' 
                    : 'bg-white/[0.03] border border-white/5 backdrop-blur-md rounded-tl-none text-white/90'
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
                <div className="flex gap-1 items-center p-3 rounded-xl bg-bg1 border border-white/5">
                   <div className="w-1 h-1 bg-amber rounded-full animate-bounce" />
                   <div className="w-1 h-1 bg-amber rounded-full animate-bounce [animation-delay:0.2s]" />
                   <div className="w-1 h-1 bg-amber rounded-full animate-bounce [animation-delay:0.4s]" />
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="p-6 border-t border-white/5 bg-bg1/50">
            <div className="relative">
              <input 
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Ask the Analyst anything..."
                className="w-full bg-white/5 border border-white/10 rounded-lg py-3 px-4 text-[11px] focus:outline-none focus:border-amber/50 transition-all placeholder:text-white/10"
              />
              <button 
                onClick={handleSend}
                disabled={!input.trim() || loading}
                className="absolute right-2 top-1.5 p-1.5 bg-amber text-bg rounded-md hover:scale-105 active:scale-95 disabled:opacity-50 disabled:scale-100 transition-all"
              >
                <Send size={16} />
              </button>
            </div>
            <p className="mt-3 text-[9px] font-mono text-white/10 text-center uppercase tracking-widest">
              Secured Neural Uplink v4.0
            </p>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default AnalystChat;
