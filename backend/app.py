from flask import Flask,request,jsonify,render_template_string
from dotenv import load_dotenv
import os
import requests

app=Flask(__name__)
load_dotenv()
API_KEY=os.getenv("API_KEY")
chat_history=[]
skill_counter = {
    "recursion": 0,
    "dp": 0,
    "graphs": 0,
    "arrays": 0,
    "strings": 0
}
def detect_topic(text):
    t = text.lower()

    if "recursion" in t:
        return "recursion"
    elif "dp" in t or "dynamic programming" in t:
        return "dp"
    elif "graph" in t:
        return "graphs"
    elif "array" in t:
        return "arrays"
    elif "string" in t:
        return "strings"
    else:
        return None
def generate_insight():
    for skill, count in skill_counter.items():
        if count >= 2:
            return f"Observation: You seem to be struggling with {skill}."
    return ""

HTML_PAGE="""
<!DOCTYPE html>
<html>
<head>
<title>"AI Coding Mentor"</title>
</head>

<body>
<h2>AI Mentor</h2>
<div id="chat"></div>
<input id="msg" placeholder="Ask Something..."/>
<button onclick="sendmessage()">Send</button>
<script>
async function sendmessage(){
let message=document.getElementById("msg").value;
let res=await fetch("/chat",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({message:message})
});
let data=await res.json()
let chat=document.getElementById("chat");
chat.innerHTML+="<p><b>You:</b>" +message+ "</p>";
chat.innerHTML+="<p><b>Bot:</b>" +data.reply+ "</p>";
document.getElementById("msg").value="";
}

</script>
</body>

</html>


"""


@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/chat",methods=["POST"])
def chat():
    user_input=request.json["message"]
    url=f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={API_KEY}"
    
    topic = detect_topic(user_input)
    if topic:
     skill_counter[topic] += 1

    context=""
    for cht in chat_history[-2:]:
       context+=f"User:{cht['user']}\nbob: {cht['bot']}\n\n"
    insight = generate_insight()

    final_input = context + f"User: {user_input}\n"

    if insight:
     final_input += f"\nSystem Insight: {insight}\n"

    data={
        "contents":[{
            "parts":[{"text":final_input}]
        }]
    }
    

    response=requests.post(url,json=data)
    res=response.json()
    try:
      reply=res["candidates"][0]["content"]["parts"][0]["text"]
      chat_history.append({
         "user":user_input,"bot":reply
      })
    except:
      reply="Error generating response"
    return jsonify({"reply":reply})


if __name__=="__main__":
    app.run(debug=True)

