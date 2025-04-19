"use client";
import { useState } from "react";

const AGENT_API = "/api/ai";

export default function Home() {
  const [messages, setMessages] = useState<{role: "user"|"agent", text: string}[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (input.trim() === "") return;
    const newMessages: { role: "user"|"agent", text: string }[] = [...messages, { role: "user", text: input }];
    setMessages(newMessages);
    setIsLoading(true);
    const userInput = input;
    setInput("");
    try {
      const res = await fetch(AGENT_API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: userInput })
      });
      const data = await res.json();
      console.log('AI応答:', data.result);
      let agentMsg = "";
      if (data.result) {
        agentMsg = data.result;
      } else if (data.error) {
        agentMsg = "エラー: " + data.error;
      } else {
        agentMsg = "不明な応答です";
      }
      setMessages((msgs: { role: "user"|"agent", text: string }[]) => [...msgs, { role: "agent", text: agentMsg }]);
    } catch {
      setMessages((msgs: { role: "user"|"agent", text: string }[]) => [...msgs, { role: "agent", text: "エラーが発生しました" }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", background: "#f7f7f7" }}>
      <main style={{ width: "100%", maxWidth: 480, flex: 1, display: "flex", flexDirection: "column", justifyContent: "flex-end", padding: 16 }}>
        <div style={{ flex: 1, overflowY: "auto", marginBottom: 16 }}>
          {messages.map((msg, idx) => (
            <div key={idx} style={{ display: "flex", justifyContent: msg.role === "user" ? "flex-end" : "flex-start", marginBottom: 8 }}>
              <div
                style={{ background: msg.role === "user" ? "#4f8cff" : "#eee", color: msg.role === "user" ? "#fff" : "#333", borderRadius: 16, padding: "8px 16px", maxWidth: "80%", wordBreak: "break-word" }}
                data-testid="chat-bubble"
              >
                {msg.text}
              </div>
            </div>
          ))}
          {isLoading && (
            <div style={{ display: "flex", justifyContent: "flex-start", marginBottom: 8 }}>
              <div style={{ background: "#eee", color: "#333", borderRadius: 16, padding: "8px 16px", maxWidth: "80%", wordBreak: "break-word" }}>
                <span>...</span> {/* ローディングスピナーの代用 */}
              </div>
            </div>
          )}
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => {
              const nativeEvent = e.nativeEvent as CompositionEvent & KeyboardEvent;
              if (e.key === "Enter" && !(nativeEvent.isComposing)) {
                handleSend();
              }
            }}
            placeholder="食材や分量を入力..."
            style={{ flex: 1, padding: 12, borderRadius: 8, border: "1px solid #ccc", fontSize: 16 }}
            data-testid="chat-input"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            style={{ padding: "0 20px", borderRadius: 8, background: "#4f8cff", color: "#fff", border: "none", fontSize: 16 }}
            data-testid="send-button"
            disabled={isLoading}
          >
            送信
          </button>
        </div>
      </main>
    </div>
  );
}
