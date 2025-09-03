import React, { useState, useRef, useEffect } from 'react';
import { ChatBubbleLeftRightIcon, SparklesIcon, PaperAirplaneIcon } from '@heroicons/react/24/outline';
import { Loader2, Bot, User } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = 'http://localhost:8000';

const AIAssistant = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: '👋 Olá! Sou o assistente AI da El Dorado P2P! Posso te ajudar com informações sobre influenciadores, analytics, performance e muito mais. Como posso te ajudar hoje?',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    fetchSuggestions();
  }, []);

  const fetchSuggestions = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/ai-assistant/suggestions`);
      setSuggestions(response.data.suggestions);
    } catch (error) {
      console.error('Erro ao carregar sugestões:', error);
    }
  };

  const sendMessage = async (message = inputMessage) => {
    if (!message.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/v1/ai-assistant/chat`, {
        message: message
      });

      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response.data.response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
      
      // Update suggestions if provided
      if (response.data.suggestions && response.data.suggestions.length > 0) {
        setSuggestions(response.data.suggestions);
      }

    } catch (error) {
      console.error('Erro no chat:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: '❌ Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
      toast.error('Erro ao enviar mensagem');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    sendMessage(suggestion);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg">
            <SparklesIcon className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-800">El Dorado AI Assistant</h1>
            <p className="text-gray-600">Assistente inteligente com acesso aos dados dos influenciadores</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Chat Area */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow-sm h-[600px] flex flex-col">
            {/* Messages */}
            <div className="flex-1 p-4 overflow-y-auto">
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`flex max-w-[80%] ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'} gap-3`}>
                      {/* Avatar */}
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        message.type === 'user' 
                          ? 'bg-blue-500' 
                          : 'bg-gradient-to-r from-purple-500 to-blue-500'
                      }`}>
                        {message.type === 'user' ? (
                          <User className="h-4 w-4 text-white" />
                        ) : (
                          <Bot className="h-4 w-4 text-white" />
                        )}
                      </div>
                      
                      {/* Message Bubble */}
                      <div className={`px-4 py-2 rounded-lg ${
                        message.type === 'user'
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        <div className="whitespace-pre-wrap">{message.content}</div>
                        <div className={`text-xs mt-1 ${
                          message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                        }`}>
                          {formatTimestamp(message.timestamp)}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                
                {/* Loading indicator */}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="flex gap-3">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 flex items-center justify-center">
                        <Bot className="h-4 w-4 text-white" />
                      </div>
                      <div className="px-4 py-2 bg-gray-100 rounded-lg">
                        <div className="flex items-center gap-2">
                          <Loader2 className="h-4 w-4 animate-spin" />
                          <span className="text-gray-600">Pensando...</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 border-t border-gray-200">
              <div className="flex gap-2">
                <textarea
                  ref={inputRef}
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Digite sua pergunta sobre influenciadores, analytics, performance..."
                  className="flex-1 p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={1}
                  disabled={isLoading}
                />
                <button
                  onClick={() => sendMessage()}
                  disabled={!inputMessage.trim() || isLoading}
                  className="px-4 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                >
                  <PaperAirplaneIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Suggestions Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-sm p-4">
            <div className="flex items-center gap-2 mb-4">
              <ChatBubbleLeftRightIcon className="h-5 w-5 text-gray-600" />
              <h3 className="font-semibold text-gray-800">Perguntas Sugeridas</h3>
            </div>
            <div className="space-y-2">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="w-full text-left p-3 text-sm bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                  disabled={isLoading}
                >
                  {suggestion}
                </button>
              ))}
            </div>

            {/* Quick Stats */}
            <div className="mt-6 p-3 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg">
              <h4 className="font-semibold text-gray-800 mb-2">💡 Dicas</h4>
              <ul className="text-xs text-gray-600 space-y-1">
                <li>• Pergunte sobre qualquer influenciador</li>
                <li>• Solicite comparações de performance</li>
                <li>• Peça insights sobre campanhas</li>
                <li>• Consulte stats por período</li>
                <li>• Análise de engagement e trends</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;