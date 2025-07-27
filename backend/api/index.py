from flask import Flask, request, jsonify
import os
from google import genai
from google.genai import types

app = Flask(__name__)

genai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = (
    "You are \"codespotter\", a code reviewer. Only flag *very serious* mistakes you are highly confident about (>=90% certainty); do not speculate or call out anything you're uncertain of."
    " Do not flag moderate issues, style nits, or unchanged code. Do not analyze or comment previously-existing code. You analyze only code changes. If some code functionality is being removed/modified, you must assume that it's intentional and not report it as an error. If some local file is referenced you must assume it does exist, and not raise an error."
    " If there are *no* serious mistakes, respond with exactly NOTHING_TO_REPORT (with no HTML)."
    " IMPORTANT: Otherwise respond **only** in valid HTML; do not use any Markdown syntax; do not use any HTML classes, as your output will be rendered directly by a browser with its default stylesheet."
    " **When you emit any HTML code snippet in your report (e.g. `<script>...</script>`, `<link>…>`), you must HTML‑escape every `<` and `>` (so they appear as `&lt;` and `&gt;`).**"
    " In the `<head>` of your HTML, include the following CDN imports for syntax highlighting:"
    "\n<link rel=\"stylesheet\" href=\"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles/default.min.css\">"
    "\n<script src=\"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/highlight.min.js\"></script>"
    "\n<script>document.addEventListener('DOMContentLoaded', () => { hljs.highlightAll(); });</script>"
    "\n\nMake sure to specify the right class when you output code, e.g. <pre><code class=\"language-html\">...</code></pre> for HTML, etc."
    "\nAlso, when your response actually is HTML code (and not the NOTHING_TO_REPORT special code), add this styling to the generated HTML page:"
    '\n<style>body{max-width:850px;margin:1em auto;font-family:system-ui,-apple-system,BlinkMacSystemFont,sans-serif;line-height:1.5;color:#333;background:#fafafa}h1,h2,h3,h4{margin:1.5em 0 0.5em;border-bottom:1px solid #ddd;padding-bottom:.3em}a{color:#0366d6;text-decoration:none}a:hover{text-decoration:underline}table{border-collapse:collapse;margin:1em 0}th,td{border:1px solid #ddd;padding:.4em .8em}th{background:#eee}</style>'
)

@app.route("/analyze", methods=["POST"])
def analyze():
    changes = request.get_json(force=True)

    prompt_lines = ["Code changes to review:\n"]
    for entry in changes:
        path = entry.get("path", "<unknown file>")
        base = entry.get("base", "").strip()
        patch = entry.get("patch", "").strip()

        prompt_lines.append(f"==== FILE: {path} ====")
        prompt_lines.append("----- BASE (HEAD^) -----")
        prompt_lines.append(base or "(empty file)")
        prompt_lines.append("----- PATCH (HEAD) -----")
        prompt_lines.append(patch or "(no changes)")
        prompt_lines.append("")

    user_prompt = "\n".join(prompt_lines)

    response = genai_client.models.generate_content(
        model="gemini-2.5-pro",
        contents=SYSTEM_PROMPT + "\n\n" + user_prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=20000),
            temperature=0.0,
        ),
    )

    feedback = response.text.strip()
    if feedback == "NOTHING_TO_REPORT":
        return "NOTHING_TO_REPORT", 200, {"Content-Type": "text/plain"}
    
    return jsonify(html=feedback)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
