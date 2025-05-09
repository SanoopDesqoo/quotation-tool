{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 document.getElementById("send").onclick = async () => \{\
  const userInput = document.getElementById("request").value;\
  const custType = document.getElementById("custType").value;\
  const resp = await fetch("https://<YOUR-BACKEND-URL>/generate-quote", \{\
    method: "POST",\
    headers: \{"Content-Type":"application/json"\},\
    body: JSON.stringify(\{user_input:userInput, customer_type:custType\})\
  \});\
  const data = await resp.json();\
  document.getElementById("output").textContent = `Download your quote: $\{data.quote_url\}`;\
\};\
}