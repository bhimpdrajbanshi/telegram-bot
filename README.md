# Local AI Telegram Bot 🤖

A lightweight, asynchronous Telegram bot built with **aiogram v3** and integrated with **Ollama** to run a large language model (LLM) completely locally with conversation memory.

## 🚀 Features
- **Local Execution:** Uses Ollama; your data never leaves your machine.
- **Contextual Memory:** Remembers up to 10 past messages per user session.
- **Asynchronous Stack:** Built using `aiogram` and `asyncio` for high performance.
- **Logging Integration:** Real-time console diagnostics for connection tracing.

---

## 🛠️ Prerequisites
Before running the bot, ensure you have the following installed on your machine:
1. **Python 3.10+**
2. **Ollama** ([Download here](https://ollama.com))

---

## 📦 Installation & Setup

### 1. Clone the Repository
```bash
git https://github.com/bhimpdrajbanshi/telegram-bot.git
cd telegram-bot
```

### 2. Create a Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the template configuration file to create your local environment file:
```bash
# Windows (Command Prompt)
copy .env.example .env

# macOS / Linux / PowerShell
cp .env.example .env
```
Open the newly created `.env` file and insert your secret Telegram bot token obtained from [@BotFather](https://t.me):
```env
BOT_TOKEN="1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ"
OLLAMA_MODEL="llama3"
```

---

---

## 🧠 Setting Up Your Local LLM

1. Ensure the Ollama core daemon or desktop client application is actively running on your machine.
2. Open a terminal and download your targeted base model configuration:
   ```bash
   ollama run llama3
   ```
   *Tip: If you are running on lower-spec hardware or a laptop with limited VRAM, consider swapping `llama3` for `llama3.2` or `mistral` inside your `.env` file for faster streaming speeds.*

---

## Launching the System

Start the asynchronous polling lifecycle loop from your terminal:
```bash
python app.py
```
Upon a successful handshake with Telegram's servers, the application logs will initialize:
```text
INFO - ⚡ Streaming Engine running on model: llama3
```

---

## 🎭 Interactive Commands & Personas

Open your Telegram bot interface and type or select any of these interactive layout options:

| Command | Action | AI Persona Archetype Description |
| :--- | :--- | :--- |
| `/start` | Reset System | Clears user context logs and restores the default assistant framework. |
| `/assistant` | Core AI | Standard, general-purpose helpful utility bot. |
| `/coder` | Dev Mode | Elite Senior Engineer producing clean code blocks and minimal text chatter. |
| `/teacher` | Tutor Mode | Patient educator using beginner-friendly concepts and everyday analogies. |
| `/pirate` | Fun Mode | High-energy pirate captain answering requests using historic maritime slang. |
| `Plain Text` | Continuous Chat | Streams contextually aware responses utilizing active conversation memory. |

---

## 🔧 Troubleshooting

* **Bot exits immediately on launch?** Check that your `.env` file is located exactly in the root directory alongside `app.py`, and run `dir /a` to verify Windows hasn't hidden a `.txt` extension at the end of it (e.g., `.env.txt`).
* **Streaming looks choppy or gets stuck?** Ensure no other processing heavy instances are competing for your system GPU/CPU. The `update_interval = 0.5` setting in the code balances terminal output safety against Telegram rate limiting.