"use client";
import Image from "next/image";
import styles from "./page.module.css";
import { useState } from "react";

export default function Home() {
  const [messages, setMessages] = useState<string[]>([]);
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (input.trim() === "") return;
    setMessages([...messages, input]);
    setInput("");
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", background: "#f7f7f7" }}>
      <main style={{ width: "100%", maxWidth: 480, flex: 1, display: "flex", flexDirection: "column", justifyContent: "flex-end", padding: 16 }}>
        <div style={{ flex: 1, overflowY: "auto", marginBottom: 16 }}>
          {messages.map((msg, idx) => (
            <div key={idx} style={{ display: "flex", justifyContent: "flex-end", marginBottom: 8 }}>
              <div
                style={{ background: "#4f8cff", color: "#fff", borderRadius: 16, padding: "8px 16px", maxWidth: "80%", wordBreak: "break-word" }}
                data-testid="chat-bubble"
              >
                {msg}
              </div>
            </div>
          ))}
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="食材や分量を入力..."
            style={{ flex: 1, padding: 12, borderRadius: 8, border: "1px solid #ccc", fontSize: 16 }}
            data-testid="chat-input"
          />
          <button
            onClick={handleSend}
            style={{ padding: "0 20px", borderRadius: 8, background: "#4f8cff", color: "#fff", border: "none", fontSize: 16 }}
            data-testid="send-button"
          >
            送信
          </button>
        </div>
      </main>
      <footer className={styles.footer}>
        <a
          href="https://nextjs.org/learn?utm_source=create-next-app&utm_medium=appdir-template&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/file.svg"
            alt="File icon"
            width={16}
            height={16}
          />
          Learn
        </a>
        <a
          href="https://vercel.com/templates?framework=next.js&utm_source=create-next-app&utm_medium=appdir-template&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/window.svg"
            alt="Window icon"
            width={16}
            height={16}
          />
          Examples
        </a>
        <a
          href="https://nextjs.org?utm_source=create-next-app&utm_medium=appdir-template&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/globe.svg"
            alt="Globe icon"
            width={16}
            height={16}
          />
          Go to nextjs.org →
        </a>
      </footer>
    </div>
  );
}
