import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
import openai
from jinja2 import Template
import weasyprint

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# Mount static folder to serve files like PDF
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load catalog data
catalog = pd.read_excel("catalog.xlsx").set_index("name")

# Request schema
class QuoteRequest(BaseModel):
    user_input: str
    customer_type: str

# Endpoint for generating the quote
@app.post("/generate-quote")
def create_quote(req: QuoteRequest):
    # Step 1: Ask ChatGPT to parse items
    prompt = f"""
You are a parser. Input: {req.user_input}
Output JSON: [{{"name": "string", "quantity": int, "discount": float}}, ...]
"""
    resp = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}],
        temperature=0
    )
    parsed = eval(resp.choices[0].message.content)  # WARNING: eval is unsafe in production

    # Step 2: Compute prices
    extra = 0.1 if req.customer_type == "premium" else 0
    lines = []
    for item in parsed:
        price = catalog.loc[item["name"], "unit_price"]
        qty = item["quantity"]
        disc = item["discount"] + extra
        subtotal = price * qty * (1 - disc)
        lines.append({**item, "unit_price": price, "subtotal": subtotal})

    # Step 3: Render PDF
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

    # Save to static folder
    os.makedirs("static", exist_ok=True)
    out = "static/quote.pdf"
    weasyprint.HTML(string=html).write_pdf(out)

    return {"quote_url": f"/static/quote.pdf"}
