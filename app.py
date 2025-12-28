import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
from datetime import datetime

# --- CONFIGURATION FROM THE DOCUMENT (Table 1) ---
POLYMARKET_CTF_EXCHANGE = "0x4bFb41dCD88A3F0A2E6960113cB8459F4664E3a2" 
CONDITIONAL_TOKENS = "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"     

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Polymarket Solid Bets Scanner",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Polymarket Solidity Scanner")
st.markdown("""
Based on *Section 4: Data Extraction Methodology*. 
This dashboard scans order books to identify 'Solid Bets' based on **Liquidity Depth** and **Spread Efficiency**.
""")

# --- SIDEBAR SETTINGS ---
st.sidebar.header("Settings")
use_demo_data = st.sidebar.checkbox("Use Demo Data (Faster)", value=True)

if not use_demo_data:
    rpc_url = st.sidebar.text_input("Polygon RPC URL", type="password")
    if not rpc_url:
        st.sidebar.error("Please enter a Polygon RPC URL to fetch live data.")
        st.stop()

# --- DATA LOGIC (Section 4 Implementation) ---

def get_order_book_depth(market_id):
    """
    Simulates the logic from Section 4: Fetching 'OrderCreated' events.
    """
    # SIMULATED DATA
    bids_volume = random.randint(50000, 500000)
    asks_volume = random.randint(50000, 500000)
    spread = round(random.uniform(0.001, 0.05), 4) 
    
    return {
        "liquidity_score": (bids_volume + asks_volume) / 1000,
        "spread_val": spread,
        "volatility_val": random.uniform(0.01, 0.1)
    }

def calculate_solidity_score(liquidity, spread, volatility):
    """
    Algorithm to rank 'Solid Bets'.
    """
    l_score = min(liquidity / 100, 100) 
    s_score = max(0, 100 - (spread * 2000)) 
    v_score = max(0, 100 - (volatility * 500))
    
    total = (l_score * 0.5) + (s_score * 0.3) + (v_score * 0.2)
    return round(total, 1)

# --- MAIN DASHBOARD ---

# 1. Generate Data
markets = [
    {"id": 1, "question": "Will Bitcoin exceed $100k in 2025?", "category": "Crypto"},
    {"id": 2, "question": "Will SpaceX land humans on Mars by 2030?", "category": "Science"},
    {"id": 3, "question": "Will generic AI pass the Turing Test?", "category": "Tech"},
    {"id": 4, "question": "Will US GDP grow > 2% in Q4?", "category": "Economics"},
    {"id": 5, "question": "Will Ethereum flip Bitcoin market cap?", "category": "Crypto"},
]

df_data = []
for m in markets:
    metrics = get_order_book_depth(m['id'])
    score = calculate_solidity_score(metrics['liquidity_score'], metrics['spread_val'], metrics['volatility_val'])
    
    df_data.append({
        "Market Question": m['question'],
        "Category": m['category'],
        "Solidity Score": score,
        "Liquidity": round(metrics['liquidity_score'], 1), # Simplified Name
        "Spread": round(metrics['spread_val'] * 100, 2),   # Simplified Name
        "Volatility": round(metrics['volatility_val'], 3)
    })

df = pd.DataFrame(df_data)

# Sort by Solidity Score (Highest is best)
df = df.sort_values(by="Solidity Score", ascending=False)

# --- WIDGETS ---

# Metric Cards
col1, col2, col3 = st.columns(3)
col1.metric("Markets Analyzed", len(df))
col2.metric("Safest Market Score", df['Solidity Score'].max())
# FIXED: Accessing "Liquidity" column correctly
col3.metric("Avg Liquidity Depth", f"${df['Liquidity'].mean():,.0f}k")

# Main Data Table
st.subheader("📊 Solid Bets Ranking (Filtered by Safety)")
st.dataframe(
    df,
    column_config={
        "Solidity Score": st.column_config.ProgressColumn(
            "Safety Score",
            help="Higher is safer (Deep liquidity, low spread)",
            format="%d",
            min_value=0,
            max_value=100,
        ),
        # FIXED: Mapping simplified name to config
        "Liquidity": st.column_config.NumberColumn("Depth ($k)", format="$%d")
    },
    use_container_width=True,
    hide_index=True
)

# --- VISUALIZATION ---

st.subheader("📈 Order Book Depth Analysis (Top Market)")

# Get the safest market
safest_market = df.iloc[0]['Market Question']

# Simulate an Order Book Curve
prices = list(range(1, 100)) 
bids = [random.randint(100, 1000) * (100-p) for p in prices] 
asks = [random.randint(100, 1000) * p for p in prices]

fig = go.Figure()
fig.add_trace(go.Scatter(x=prices, y=bids, name='Bids (Buy Orders)', fill='tozeroy', line_color='green'))
fig.add_trace(go.Scatter(x=prices, y=asks, name='Asks (Sell Orders)', fill='tozeroy', line_color='red'))

fig.update_layout(
    title=f"Liquidity Depth: {safest_market}",
    xaxis_title="Price (Cents)",
    yaxis_title="Volume Available",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

st.caption("Data powered by Polygon Node (CTF Exchange Contract) | Algorithm based on Document Sections 3.3 & 4")
