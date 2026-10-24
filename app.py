from flask import Flask, request, render_template, url_for,session,redirect
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = "fakejob123"
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def home():
    result = session.pop('result',None)
    used_model = session.pop('model',None)
    if request.method == "POST":
        jd = request.form.get("jd_text")
        models = ["gemini-3.5-flash","gemini-flash-latest","gemini-3-flash-preview"]
        prompt = f"Check if this job is scam. JD: {jd}. Give Verdict REAL/FAKE, Risk Score, Red Flags in Hinglish."

        for model_name in models:
            try:
                print(f"Trying {model_name}...")
                response = client.models.generate_content(model=model_name,contents=prompt)
                result = response.text
                used_model = model_name
                break
            except Exception as e:
                print(f"{model_name} fail: {e}")
                continue
        if not result:
            result = "All models busy,try again."
        session['result'] = result
        session['model'] = used_model 
        return redirect("/")
    return render_template("index.html",result=result,model=used_model)
if __name__ == "__main__":
    app.run(debug=True)
