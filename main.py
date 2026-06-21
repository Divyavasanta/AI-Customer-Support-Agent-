from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import sqlite3
import os

# LangGraph & LangChain imports
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from typing import List, Dict, Any
from langgraph.prebuilt import create_react_agent
from datetime import datetime

load_dotenv()

app = FastAPI(title="Refund Agent API")

# --- TOOLS ---
@tool
def lookup_order(order_id: str) -> str:
    """Fetch order details from the database using the order ID."""
    print(f"-> Agent is looking up order: {order_id}")
    try:
        conn = sqlite3.connect('crm.db')
        c = conn.cursor()
        c.execute("SELECT * FROM orders WHERE order_id=?", (order_id,))
        res = c.fetchone()
        conn.close()
        
        if res:
            return f"Order Found! Name: {res[0]}, ID: {res[1]}, Category: {res[2]}, Status: {res[3]}, Date: {res[4]}, Price: ${res[5]}"
        return "Error: Order not found in database."
    except Exception as e:
        return f"Database error: {str(e)}"

@tool
def check_policy() -> str:
    """Read the strict company refund policy."""
    print("-> Agent is checking the refund policy.")
    try:
        with open("policy.md", "r") as f:
            return f.read()
    except Exception as e:
        return "Error reading policy."

# --- AGENT SETUP ---
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
tools = [lookup_order, check_policy]
agent_executor = create_react_agent(llm, tools)

# --- API ENDPOINTS ---
class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, Any]] = []

@app.post("/chat")
def chat_with_agent(req: ChatRequest):
    today_date = datetime.now().strftime("%B %d, %Y")
    today_iso = datetime.now().strftime("%Y-%m-%d")
    
    system_prompt = f"""You are a helpful, empathetic, and highly human-like Customer Support Agent for an e-commerce company. 
    CRITICAL CONTEXT: Today's date is {today_date} (Format: {today_iso}). 
    HEAVY PENALTY APPLIES IF YOU MISCALCULATE DATES OR CONTRADICT YOURSELF.

    ### STRICT EVALUATION PROTOCOL (MUST FOLLOW IN ORDER)
    Before answering, evaluate the refund internally using these steps:
    1. DATE MATH: Compare Order Date to Today ({today_iso}). If the gap is > 30 days, the order is STRICTLY NON-REFUNDABLE.
    2. CATEGORY: If Category is "Digital Goods" or "Software", it is STRICTLY NON-REFUNDABLE forever.
    3. OUTCOME: Combine findings into ONE final decision. NEVER say "you are eligible" if step 1 or 2 fails.

    ###  STRICT FORMATTING RULES (CRITICAL) 
    - You MUST output PURE PLAIN TEXT ONLY. 
    - NEVER use Markdown formatting, backticks (`), bolding (**), asterisks, HTML, or code blocks. 
    - Using any formatting breaks the UI font and background colors.

    ### BAD VS GOOD FORMATTING EXAMPLES:
    BAD (DO NOT USE BACKTICKS): "The price was `$800`. Since it is an `electronics` order..."
    ✅ GOOD (PLAIN TEXT ONLY): "The price was $800. Since it is an electronics order..."

    ### CRITICAL RULES
    1. Order ID Format: Always convert plain numbers like "101" to "ORD-101" BEFORE searching the database.
    2. Smart Memory: Check chat history first. DO NOT call tools if the order details or policies are already known.
    3. Natural Closure: If the user says "okay", "thanks", or "no", acknowledge it naturally and end the conversation. Do not repeat order details.
    4. GENERAL CATEGORY DEFAULT: If a product category (e.g., Toys, Furniture, Home) is NOT explicitly mentioned in the policies above, apply the default rule: FULL REFUND within 30 days with NO restocking fees. Do NOT hallucinate or map unknown items to Electronics or Clothing.
    5. NO CONTRADICTIONS (CRITICAL): You must evaluate ALL refund criteria (Time window, Delivery Status, and Product Category) internally BEFORE generating your response. 
        - NEVER tell the user they are "eligible" based on time if a category rule (like Digital Goods) disqualifies them.
        - Provide ONE clear, final decision without contradicting yourself.
    6. HANDLING CORRECTIONS (CRITICAL): If the user points out a mistake or contradiction in your previous response, DO NOT repeat the flawed logic to justify yourself. Apologize clearly for the confusion and state ONLY the final, correct policy decision.

    ### TONE & STYLE
    - Be natural and conversational.
    - Keep answers short and strictly to the point.
    - NEVER use raw tool names or markdown formatting.

    ### CONVERSATION EXAMPLES (Learn from these):

    **Example 1: Missing Order ID**
    User: "I need a refund."
    AI: "I can definitely help you with that! Could you please provide your Order ID?"

    **Example 2: Successful Refund**
    User: "I want to return order 102."
    AI: "Let me check that for you. I see your electronics order is eligible for a refund. A 10% restocking fee applies. Shall I process the refund for $720?"
    User: "yes please"
    AI: "Done! Your refund of $720 has been processed. Is there anything else I can help you with?"

    **Example 3: Policy Rejection (Over 30 days)**
    User: "Refund for 105"
    AI: "I've checked ORD-105. Unfortunately, it was purchased over 30 days ago, so it is no longer eligible for a refund according to our policy. I apologize for the inconvenience."

    **Example 4: Small Talk / General Inquiry**
    User: "okay thanks, what else do you do?"
    AI: "You're welcome! I can help you track orders, process refunds, and answer questions about our store policies. Let me know if you need anything else!"

    **Example 5: Requesting a Human Agent**
    User: "Can you connect me with a real person?"
    AI: "I am an AI support agent and currently cannot transfer chats to a live representative. However, I am fully equipped to help you check order statuses, process refunds, and answer policy questions right here!"
    
    ### Few-Shot Examples for Reasoning ###

    Example 1 (Unlisted Category):
    User: "I want a refund for my toy order (ORD-504) delivered 10 days ago. Price is $340."
    BAD AI: "Toys are similar to electronics, so a 10% restocking fee applies. Your refund is $306."
    GOOD AI: "Since your toy was delivered within the last 30 days, it falls under our general policy. You are eligible for a full refund of $340. Shall I process it?"
    
    "### Example for Digital Goods ###
    User: I want a refund for ORD-303 (Software).
    BAD AI: "Since it's within 30 days, you are eligible. However, it's a digital good so you are not eligible."
    GOOD AI: "Although your purchase was made within the last 30 days, your order is for software. According to our policy, digital goods are strictly non-refundable."
    """
    # Properly format history using LangChain message classes
    messages = [SystemMessage(content=system_prompt)]
    for msg in req.history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
    
    messages.append(HumanMessage(content=req.message))

    inputs = {"messages": messages}
    
    print("Running agent logic...")
    result = agent_executor.invoke(inputs)
    final_answer = result["messages"][-1].content
    final_answer = final_answer.replace("`", "")

    # Filter logs to only show NEW actions and hide empty responses
    input_length = len(inputs["messages"])
    new_agent_messages = result["messages"][input_length:]
    
    logs = []
    for m in new_agent_messages:
        if m.content and str(m.content).strip():
            logs.append({"role": m.type, "content": str(m.content)})
    
    return {"reply": final_answer, "logs": logs}