class FrontendPage:
    def render(self) -> str:
        return """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AI Resume Coach</title>
  <style>
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Arial, sans-serif;
      background: #f6f7f9;
      color: #1f2937;
    }
    main {
      width: min(1100px, calc(100% - 32px));
      margin: 32px auto;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }
    h1 {
      grid-column: 1 / -1;
      margin: 0;
      font-size: 28px;
    }
    section {
      background: white;
      border: 1px solid #dfe3ea;
      border-radius: 8px;
      padding: 18px;
    }
    label {
      display: block;
      margin: 14px 0 6px;
      font-weight: 700;
    }
    input, textarea {
      width: 100%;
      border: 1px solid #c8ced8;
      border-radius: 6px;
      padding: 10px;
      font: inherit;
    }
    textarea {
      min-height: 210px;
      resize: vertical;
      line-height: 1.45;
    }
    button {
      margin-top: 14px;
      border: 0;
      border-radius: 6px;
      background: #0f766e;
      color: white;
      padding: 10px 14px;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
    }
    button.secondary { background: #475569; }
    button:disabled {
      background: #94a3b8;
      cursor: wait;
    }
    pre {
      min-height: 500px;
      margin: 0;
      white-space: pre-wrap;
      line-height: 1.5;
      font-family: Consolas, monospace;
    }
    .actions {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
    .status {
      margin-top: 10px;
      color: #64748b;
      font-size: 14px;
    }
    @media (max-width: 800px) {
      main { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <main>
    <h1>AI Resume Coach</h1>

    <section>
      <label for="sessionId">Session id</label>
      <input id="sessionId" value="demo" />

      <label for="role">Target role</label>
      <input id="role" value="Backend Developer" />

      <label for="resume">Resume text</label>
      <textarea id="resume">Summary: Backend developer with experience building Python APIs, improving database performance, and deploying cloud applications.

Experience:
- Built REST APIs using FastAPI and PostgreSQL for an internal dashboard used by 200 employees.
- Improved API response time by 35 percent by optimizing database queries and adding caching.
- Created automated tests with pytest and reduced production bugs by 25 percent.
- Worked with Docker, GitHub Actions, and AWS to deploy backend services.</textarea>

      <label for="message">Message</label>
      <input id="message" value="Review this resume and tell me what to improve first." />

      <div class="actions">
        <button id="sendButton">Send</button>
        <button id="resetButton" class="secondary">Reset Memory</button>
      </div>
      <div id="status" class="status">Ready</div>
    </section>

    <section>
      <pre id="output">Streaming output will appear here...</pre>
    </section>
  </main>

  <script>
    const sendButton = document.getElementById("sendButton");
    const resetButton = document.getElementById("resetButton");
    const output = document.getElementById("output");
    const status = document.getElementById("status");

    sendButton.addEventListener("click", async () => {
      sendButton.disabled = true;
      status.textContent = "Streaming...";

      const message = document.getElementById("message").value;
      output.textContent += "\\n\\nYou: " + message + "\\nAI: ";

      try {
        const response = await postChat({ reset_memory: false });
        await appendStream(response);
        status.textContent = "Done. This turn is now in memory.";
      } catch (error) {
        status.textContent = "Something went wrong";
        output.textContent += String(error);
      } finally {
        sendButton.disabled = false;
      }
    });

    resetButton.addEventListener("click", async () => {
      resetButton.disabled = true;
      try {
        await postChat({ reset_memory: true });
        output.textContent = "Memory cleared.";
        status.textContent = "Ready";
      } finally {
        resetButton.disabled = false;
      }
    });

    async function postChat(options) {
      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: document.getElementById("sessionId").value || "demo",
          target_role: document.getElementById("role").value,
          resume_text: document.getElementById("resume").value,
          message: document.getElementById("message").value,
          reset_memory: options.reset_memory
        })
      });

      if (!response.ok || !response.body) {
        throw new Error("Request failed");
      }

      return response;
    }

    async function appendStream(response) {
      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        output.textContent += decoder.decode(value, { stream: true });
      }
    }
  </script>
</body>
</html>
"""
