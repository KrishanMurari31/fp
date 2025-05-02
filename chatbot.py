from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

app = Flask(__name__)
CORS(app)  # Allow requests from any origin

def fetch_text_and_links(url):
    """Fetch plain text and all internal links from the given URL."""
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract visible text
        text = soup.get_text(separator=' ', strip=True)

        # Extract internal links only
        links = []
        base_domain = urlparse(url).netloc
        for tag in soup.find_all("a", href=True):
            link = urljoin(url, tag["href"])
            if base_domain in urlparse(link).netloc:
                links.append(link)

        return text, list(set(links))  # Remove duplicates
    except:
        return "", []

def generate_answer(question, all_text, all_links):
    question_lower = question.lower()

    # Direct answers for known keywords
    if "admission" in question_lower:
        return "You can visit the admission section here: https://dseu.ac.in/admissions"
    if "courses" in question_lower or "programs" in question_lower:
        return "We offer diploma, undergraduate, and short-term programs: https://dseu.ac.in/programmes/"
    if "contact" in question_lower:
        return "You can reach us here: https://dseu.ac.in/contact-us-2/"
    
    # If asking to "show", "give", or "list", return matching links
    if any(word in question_lower for word in ["show", "give", "list", "link"]):
        matching_links = [link for link in all_links if any(word in link.lower() for word in question_lower.split())]
        if matching_links:
            return "Here are some relevant links:\n" + "\n".join(matching_links[:5])
    
    # Search the combined text content
    words = question_lower.split()
    if any(word in all_text.lower() for word in words):
        return "This topic is mentioned on the site. Please refer to the page content for more details."
    
    return "Sorry, I couldn't find anything relevant. Try rephrasing or exploring the site further."

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    question = data.get("message", "")
    base_url = data.get("url", "")

    if not base_url or not question:
        return jsonify({"reply": "Missing question or URL."})

    # Fetch content from main page
    main_text, links = fetch_text_and_links(base_url)

    # Fetch content from linked pages (limit to 5 for performance)
    linked_text = ""
    for link in links[:5]:
        text, _ = fetch_text_and_links(link)
        linked_text += text + " "

    combined_text = main_text + " " + linked_text

    # Generate and return answer
    reply = generate_answer(question, combined_text, links)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
