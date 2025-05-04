import os
from pathlib import Path
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from groq import Groq

# Load env and initialize Groq client
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Load all website content from main + linked .html pages
def load_website_content(main_file="main.html"):
    visited, combined_text = set(), []
    base_path = Path(main_file).parent

    def load_file(path):
        if path in visited: return
        visited.add(path)
        try:
            with open(path, encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")
                combined_text.append(f"\n--- Content from {path} ---\n" + soup.get_text())
                for a in soup.find_all("a", href=True):
                    href = (base_path / a["href"]).resolve()
                    if href.suffix == ".html" and href.exists(): load_file(str(href))
        except: pass

    load_file(str(Path(main_file).resolve()))
    return "\n".join(combined_text)

website_text = load_website_content()

# Setup FastAPI app
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    user_input = body.get("message", "").strip().lower()

    # Commands & quick replies
    commands = {"open search box": "ACTION:open_search_box",
                "go to contact section": "ACTION:scroll_to_contact",
                "show notification": "ACTION:show_notification"}
    if user_input in commands:
        return {"response": commands[user_input]}
    
    if any(greet in user_input for greet in ["hello", "hi", "hey"]):
        return {"response": "Hello! How can I assist you today?"}
    
    replies = {
        "how are you": "I'm just a bot, but thanks for asking!",
        "what's your name": "I'm your friendly chatbot.",
        "who are you": "I'm your assistant for this website.",
        "what can you do": "I can help you with website info and navigation."
    }
    if user_input in replies:
        return {"response": replies[user_input]}

    try:
        chat_response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content":
                 "You are a helpful assistant. Be concise, friendly, and reply based only on this website content:"
                 "Do NOT start your answers with phrases like 'According to the data','According to the provided content', 'Based on the website','According to the website' or similar. "
                 "\n\n" + website_text},
                {"role": "user", "content": user_input}
            ]
        )
        return {"response": chat_response.choices[0].message.content.strip()}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

print("✅ WEBSITE CONTENT LOADED")
