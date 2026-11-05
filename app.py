from flask import Flask, request, render_template, session, redirect
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = "fakejob123"

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def home():
    result = session.pop('result', None)
    used_model = session.pop('model', None)
    if request.method == "POST":
        jd = request.form.get("jd_text")

        # Ye wale model 100% chalte hai
        models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-flash-lite"]

        prompt = f"Check if this job is scam. JD: {jd}. Give Verdict REAL/FAKE, Risk Score, Red Flags in Hinglish. Keep short."

        for model_name in models:
            try:
                print(f"Trying {model_name}...")
                response = client.models.generate_content(model=model_name, contents=prompt)
                result = response.text
                used_model = model_name
                break
            except Exception as e:
                print(f"{model_name} fail: {e}")
                continue

        if not result:
            # Agar AI fail ho toh Rule-Based fallback, taaki kabhi 'All models busy' na aaye
            jd_low = jd.lower()
            red_flags = []
            if "telegram" in jd_low or "whatsapp" in jd_low: red_flags.append("Telegram/WhatsApp pe contact - Scam ka sign")
            if "registration fee" in jd_low or "security deposit" in jd_low or "pay" in jd_low and "fee" in jd_low: red_flags.append("Pehle paisa mang rahe hai - 99% FAKE")
            if "no experience" in jd_low and "50000" in jd_low: red_flags.append("Bina experience ke zyada salary - Doubtful")
            if not red_flags:
                red_flags.append("Koi bada Red Flag nahi mila, but company verify karo")

            result = f"Verdict: {'FAKE / HIGH RISK' if len(red_flags) >= 2 else 'SUSPICIOUS - Verify Karo'}\nRisk Score: {80 if len(red_flags) >= 2 else 50}/100\nRed Flags:\n- " + "\n- ".join(red_flags)

        session['result'] = result
        session['model'] = used_model or "Rule-Based Fallback"
        return redirect("/")
    return render_template("index.html", result=result, model=used_model)

if __name__ == "__main__":
    app.run(debug=True)
