import os
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import openai
from jinja2 import Template
import weasyprint
from fastapi.staticfiles import StaticFiles  # <-- Added

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()
catalog = pd.read_excel("catalog.xlsx").set_index("name")

class QuoteRequest(BaseModel):
    user_input: str
    customer_type: str

@app.post("/generate-quote")
def create_quote(req: QuoteRequest):
    # 1. Ask ChatGPT to parse items
    prompt = f"""
You are a parser. Input: {req.user_input}
Output JSON: [{{"name": "string", "quantity": int, "discount": float}}, ...]
"""
    resp = openai.ChatCompletion.create(
      model="gpt-4",
      messages=[{"role":"system","content":prompt}],
      temperature=0
    )
    parsed = resp.choices[0].message.content
    parsed = eval(parsed)  # converts JSON‐like text to Python list

    # 2. Compute prices
    extra = 0.1 if req.customer_type == "premium" else 0
    lines = []
    for item in parsed:
        price = catalog.loc[item["name"], "unit_price"]
        qty = item["quantity"]
        disc = item["discount"] + extra
        subtotal = price * qty * (1 - disc)
        lines.append({**item, "unit_price": price, "subtotal": subtotal})

    # 3. Render PDF
    total = sum(l["subtotal"] for l in lines)
    tax = total * 0.18
    grand = total + tax
    tpl = Template("""
<h1>Quotation</h1>
<ul>
{% for l in lines %}
  <li>{{l.name}} x{{l.quantity}} @ {{l.unit_price}} each, sub={{"{:.2f}".format(l.subtotal)}}</li>
{% endfor %}
</ul>
<p>Tax (18%): {{tax:.2f}}</p>
<h2>Total: {{grand:.2f}}</h2>
    """)
    html = tpl.render(lines=lines, tax=tax, grand=grand)
    out = "quote.pdf"
    weasyprint.HTML(string=html).write_pdf(out)

    return {"quote_url": f"/quote.pdf"}  # relative path

# ✅ Serve quote.pdf and other static files
app.mount("/", StaticFiles(directory=".", html=True), name="static")