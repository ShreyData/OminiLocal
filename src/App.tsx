import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Globe, Code, Loader2 } from "lucide-react";
import ReactMarkdown from "react-markdown";

interface Message {
  role: "user" | "assistant";
  content: string;
  thought?: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });

      if (!response.ok) throw new Error("Failed to reach assistant");

      const data = await response.json();
      const assistantMessage: Message = {
        role: "assistant",
        content: data.final_answer,
        thought: data.thought_process,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Error: Could not connect to the local AI sidecar." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const [isCloud, setIsCloud] = useState(false);

  useEffect(() => {
    // Check health/mode status from backend
    fetch("http://localhost:8000/health")
      .then(res => res.json())
      .then(data => setIsCloud(data.mode === "cloud"))
      .catch(() => {});
  }, []);

  return (
    <div className="flex flex-col h-screen w-screen bg-slate-900 text-slate-100 overflow-hidden">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 bg-slate-800/50 border-b border-slate-700 backdrop-blur-md">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-indigo-600 rounded-lg">
            <Bot size={24} />
          </div>
          <div className="flex flex-col">
            <h1 className="text-xl font-bold tracking-tight">OmniLocal AI</h1>
            <span className="text-[10px] text-slate-400 uppercase tracking-widest font-semibold">
              {isCloud ? "Cloud Powered (Gemini API)" : "Local Powered (Ollama)"}
            </span>
          </div>
        </div>
        <div className="flex gap-4">
          <div className="flex items-center gap-1 text-xs text-slate-400">
            <Globe size={14} /> Web Search: Active
          </div>
          <div className="flex items-center gap-1 text-xs text-slate-400">
            <Code size={14} /> Python REPL: Active
          </div>
        </div>
      </header>

      {/* Chat Area */}
      <main className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 gap-4">
            <Bot size={64} className="opacity-20" />
            <p className="text-lg">Ask me to search the web or run Python code.</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex gap-4 ${
              msg.role === "user" ? "flex-row-reverse" : "flex-row"
            }`}
          >
            <div
              className={`p-2 rounded-full h-fit ${
                msg.role === "user" ? "bg-indigo-600" : "bg-slate-700"
              }`}
            >
              {msg.role === "user" ? <User size={20} /> : <Bot size={20} />}
            </div>
            <div
              className={`max-w-[85%] rounded-2xl px-5 py-4 shadow-lg ${
                msg.role === "user"
                  ? "bg-indigo-600 text-white shadow-indigo-500/10"
                  : "bg-slate-800/80 border border-slate-700/50 backdrop-blur-sm"
              }`}
            >
              {msg.thought && (
                <div className="mb-3 flex items-center gap-2 text-[10px] text-slate-400 font-mono bg-slate-900/50 p-2 rounded-md border border-slate-700/30">
                  <Code size={12} className="text-indigo-400" />
                  <span className="opacity-70">{msg.thought}</span>
                </div>
              )}
              <div className={`prose prose-sm max-w-none ${msg.role === 'user' ? 'prose-invert text-white' : 'prose-invert'}`}>
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-4">
            <div className="p-2 rounded-full h-fit bg-slate-700">
              <Bot size={20} />
            </div>
            <div className="bg-slate-800 border border-slate-700 rounded-2xl px-4 py-3 flex items-center gap-3">
              <Loader2 className="animate-spin text-indigo-500" size={18} />
              <span className="text-slate-400 text-sm">Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </main>

      {/* Input Area */}
      <footer className="p-6 bg-slate-900">
        <div className="max-w-4xl mx-auto relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Search the web or solve math with Python..."
            className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-4 pr-12 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-indigo-600 rounded-lg hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send size={20} />
          </button>
        </div>
        <p className="text-center text-[10px] text-slate-600 mt-4">
          Powered by Ollama (Gemma 4) & LangChain. Privacy first, fully local.
        </p>
      </footer>
    </div>
  );
}

export default App;
