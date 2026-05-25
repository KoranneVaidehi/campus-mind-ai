import { useState } from "react";
import axios from "axios";

export default function CampusMindAI() {

  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([
    {
      sender: "ai",
      text: "Hello! I am Campus Mind AI. Ask me anything."
    }
  ]);

  const sendMessage = async () => {

    if (!message.trim()) return;

    // Add user message
    const userMessage = {
      sender: "user",
      text: message
    };

    setMessages((prev) => [...prev, userMessage]);

    const currentMessage = message;
    setMessage("");

    try {

      const response = await axios.post(
        "http://localhost:8000/chat",
        {
          message: currentMessage
        }
      );

      const aiMessage = {
        sender: "ai",
        text: response.data.response,
        sources: response.data.sources || [],
        isPdf: response.data.is_pdf_request,
        pdfPath: response.data.pdf_path,
        pdfName: response.data.pdf_name
      };

      setMessages((prev) => [...prev, aiMessage]);

    } catch (error) {

      console.error(error);

      setMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          text: "Error connecting to backend."
        }
      ]);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white flex">

      {/* Sidebar */}
      <div className="w-72 bg-zinc-900 border-r border-zinc-800 p-5 flex flex-col">

        <h1 className="text-2xl font-bold mb-2">
          Campus Mind AI
        </h1>

        <p className="text-zinc-400 text-sm mb-8">
          Multilingual Academic Assistant
        </p>

        <div className="space-y-3">

          <button className="w-full bg-zinc-800 rounded-xl p-3 text-left">
            New Chat
          </button>

          <button className="w-full bg-zinc-800 rounded-xl p-3 text-left">
            Ask from PDF
          </button>

          <button className="w-full bg-zinc-800 rounded-xl p-3 text-left">
            Timetable
          </button>

        </div>

      </div>

      {/* Main Area */}
      <div className="flex-1 flex flex-col">

        {/* Header */}
        <div className="h-16 border-b border-zinc-800 flex items-center px-6">
          <h2 className="font-semibold text-lg">
            AI Academic Assistant
          </h2>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">

          {messages.map((msg, index) => (

            <div
              key={index}
              className={`flex ${
                msg.sender === "user"
                  ? "justify-end"
                  : "justify-start"
              }`}
            >

              <div
                className={`max-w-3xl p-5 rounded-2xl ${
                  msg.sender === "user"
                    ? "bg-white text-black"
                    : "bg-zinc-900 border border-zinc-800"
                }`}
              >

                <p className="leading-7">
                  {msg.text}
                </p>

                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-4 text-sm text-zinc-400">
                    Sources:
                    {msg.sources.map((src, i) => (
                      <div key={i}>• {src}</div>
                    ))}
                  </div>
                )}

                {msg.isPdf && msg.pdfPath && (
                  <div className="mt-4">

                    <a
                      href={`http://localhost:8000/${msg.pdfPath}`}
                      target="_blank"
                      rel="noreferrer"
                      className="bg-white text-black px-4 py-2 rounded-xl inline-block"
                    >
                      Download PDF
                    </a>

                  </div>
                )}

              </div>

            </div>

          ))}

        </div>

        {/* Input */}
        <div className="border-t border-zinc-800 p-5">

          <div className="flex gap-4 bg-zinc-900 border border-zinc-800 rounded-2xl px-5 py-4">

            <input
              type="text"
              placeholder="Ask anything..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  sendMessage();
                }
              }}
              className="flex-1 bg-transparent outline-none"
            />

            <button
              onClick={sendMessage}
              className="bg-white text-black px-5 py-2 rounded-xl"
            >
              Send
            </button>

          </div>

        </div>

      </div>

    </div>
  );
}