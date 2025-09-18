# File: app.py
# Metal Prices Dashboard - Streamlit Application
# To deploy on Streamlit Community Cloud via GitHub

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io

# Configure page
st.set_page_config(
    page_title="Metal Prices Dashboard",
    page_icon="🥇",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_custom_css():
    """Load custom CSS for better styling"""
    st.markdown("""
    <style>
        .metric-container {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .metal-gold { 
            border-left: 5px solid #FFD700;
            padding-left: 1rem;
            background-color: #fff9e6;
        }
        .metal-silver { 
            border-left: 5px solid #C0C0C0;
            padding-left: 1rem;
            background-color: #f8f8f8;
        }
        .metal-platinum { 
            border-left: 5px solid #E5E4E2;
            padding-left: 1rem;
            background-color: #f5f5f5;
        }
        .metal-palladium { 
            border-left: 5px solid #CED0DD;
            padding-left: 1rem;
            background-color: #f0f0f2;
        }
        .big-font {
            font-size: 1.5rem !important;
            font-weight: bold;
            color: #333;
        }
        .success-box {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        .error-box {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        .info-box {
            background-color: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        .header-container {
            background: linear-gradient(90deg, #FFD700, #FFA500);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            text-align: center;
        }
        .portfolio-summary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'metal_prices' not in st.session_state:
        st.session_state.metal_prices = {
            'gold': 2000.00,
            'silver': 25.00,
            'platinum': 950.00,
            'palladium': 1800.00
        }
    
    if 'price_history' not in st.session_state:
        st.session_state.price_history = pd.DataFrame({
            'date': [datetime.now().date()],
            'gold': [st.session_state.metal_prices['gold']],
            'silver': [st.session_state.metal_prices['silver']],
            'platinum': [st.session_state.metal_prices['platinum']],
            'palladium': [st.session_state.metal_prices['palladium']]
        })
    
    if 'portfolio_holdings' not in st.session_state:
        st.session_state.portfolio_holdings = {
            'gold': 0.0,
            'silver': 0.0,
            'platinum': 0.0,
            'palladium': 0.0
        }

def load_prices_from_excel(uploaded_file):
    """Load prices from uploaded Excel file from cells D4-D7"""
    try:
        # Read Excel file
        df = pd.read_excel(uploaded_file, header=None)
        
        # Check if file has enough rows and columns
        if df.shape[0] >= 7 and df.shape[1] >= 4:
            # Extract prices from D4:D7 (row indices 3-6, column index 3)
            prices = {}
            
            # D4 - Gold
            if pd.notna(df.iloc[3, 3]):
                prices['gold'] = float(df.iloc[3, 3])
            
            # D5 - Silver  
            if pd.notna(df.iloc[4, 3]):
                prices['silver'] = float(df.iloc[4, 3])
            
            # D6 - Platinum
            if pd.notna(df.iloc[5, 3]):
                prices['platinum'] = float(df.iloc[5, 3])
            
            # D7 - Palladium
            if pd.notna(df.iloc[6, 3]):
                prices['palladium'] = float(df.iloc[6, 3])
            
            return prices, None
        else:
            return None, "Excel file doesn't have enough rows/columns to read from D4:D7"
            
    except Exception as e:
        return None, f"Error reading Excel file: {str(e)}"

def update_price_history():
    """Add current prices to history"""
    today = datetime.now().date()
    current_prices = st.session_state.metal_prices
    
    # Check if today already exists in history
    if today not in st.session_state.price_history['date'].values:
        new_row = pd.DataFrame({
            'date': [today],
            'gold': [current_prices['gold']],
            'silver': [current_prices['silver']],
            'platinum': [current_prices['platinum']],
            'palladium': [current_prices['palladium']]
        })
        st.session_state.price_history = pd.concat([st.session_state.price_history, new_row], ignore_index=True)
    else:
        # Update existing row for today
        mask = st.session_state.price_history['date'] == today
        for metal in ['gold', 'silver', 'platinum', 'palladium']:
            st.session_state.price_history.loc[mask, metal] = current_prices[metal]

def create_price_chart():
    """Create an interactive price history chart"""
    df = st.session_state.price_history.copy()
    df = df.sort_values('date')
    
    if len(df) <= 1:
        st.info("📈 Add more price history entries to see the chart!")
        return None
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('🥇 Gold ($/oz)', '🥈 Silver ($/oz)', '⚪ Platinum ($/oz)', '⚫ Palladium ($/oz)'),
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # Define colors for each metal
    colors = {
        'gold': '#FFD700',
        'silver': '#C0C0C0', 
        'platinum': '#E5E4E2',
        'palladium': '#CED0DD'
    }
    
    metals = ['gold', 'silver', 'platinum', 'palladium']
    positions = [(1,1), (1,2), (2,1), (2,2)]
    
    for metal, (row, col) in zip(metals, positions):
        fig.add_trace(
            go.Scatter(
                x=df['date'], 
                y=df[metal],
                name=metal.capitalize(),
                line=dict(color=colors[metal], width=3),
                mode='lines+markers',
                marker=dict(size=8),
                hovertemplate=f'<b>{metal.capitalize()}</b><br>Date: %{{x}}<br>Price: $%{{y:,.2f}}<extra></extra>'
            ),
            row=row, col=col
        )
    
    fig.update_layout(
        height=600,
        showlegend=False,
        title_text="📈 Metal Price History",
        title_x=0.5,
        title_font_size=20,
        plot_bgcolor='white'
    )
    
    return fig

def calculate_portfolio_value():
    """Calculate and display portfolio value"""
    holdings = st.session_state.portfolio_holdings
    prices = st.session_state.metal_prices
    
    total_value = 0
    portfolio_breakdown = []
    
    for metal in ['gold', 'silver', 'platinum', 'palladium']:
        holding = holdings[metal]
        price = prices[metal]
        value = holding * price
        total_value += value
        
        if holding > 0:
            portfolio_breakdown.append({
                'Metal': metal.capitalize(),
                'Holdings (oz)': holding,
                'Price ($/oz)': price,
                'Value ($)': value
            })
    
    return total_value, portfolio_breakdown

def main():
    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Header with styling
    st.markdown("""
    <div class="header-container">
        <h1>🥇 Metal Prices Dashboard</h1>
        <p style="font-size: 1.2em; margin: 0;">Real-time precious metals pricing interface</p>
        <p style="font-size: 0.9em; margin-top: 10px; opacity: 0.8;">Upload Excel files with prices in D4-D7 or enter manually</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for file upload and controls
    with st.sidebar:
        st.header("⚙️ Controls")
        
        # File upload section
        st.subheader("📁 Load from Excel")
        st.markdown("""
        Upload an Excel file with prices in cells:
        - **D4**: Gold price
        - **D5**: Silver price  
        - **D6**: Platinum price
        - **D7**: Palladium price
        """)
        
        uploaded_file = st.file_uploader(
            "Choose Excel file", 
            type=['xlsx', 'xls'],
            help="Upload Excel file with metal prices in D4:D7"
        )
        
        if uploaded_file is not None:
            prices, error = load_prices_from_excel(uploaded_file)
            
            if prices:
                # Update session state with loaded prices
                st.session_state.metal_prices.update(prices)
                
                st.success("✅ Prices loaded successfully!")
                st.markdown("**Loaded prices:**")
                for metal, price in prices.items():
                    st.write(f"• {metal.capitalize()}: ${price:,.2f}")
                
            elif error:
                st.error(f"❌ {error}")
        
        st.markdown("---")
        
        # Quick actions
        st.subheader("🎯 Quick Actions")
        
        if st.button("📊 Update Price History", type="primary", use_container_width=True):
            update_price_history()
            st.success("✅ Price history updated!")
            st.rerun()
        
        if st.button("🔄 Reset All Prices", use_container_width=True):
            st.session_state.metal_prices = {
                'gold': 2000.00,
                'silver': 25.00,
                'platinum': 950.00,
                'palladium': 1800.00
            }
            st.success("✅ Prices reset to defaults!")
            st.rerun()
        
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.price_history = pd.DataFrame({
                'date': [datetime.now().date()],
                'gold': [st.session_state.metal_prices['gold']],
                'silver': [st.session_state.metal_prices['silver']],
                'platinum': [st.session_state.metal_prices['platinum']],
                'palladium': [st.session_state.metal_prices['palladium']]
            })
            st.success("✅ History cleared!")
            st.rerun()
        
        # App info
        st.markdown("---")
        st.markdown("""
        **📱 App Info:**
        - Version: 1.0.0
        - Built with Streamlit
        - Hosted on Streamlit Cloud
        """)
    
    # Main content area - Current Prices
    st.header("💰 Current Metal Prices")
    
    # Create input fields for prices
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metal-gold">', unsafe_allow_html=True)
        gold_price = st.number_input(
            "🥇 Gold ($/oz)",
            min_value=0.01,
            value=st.session_state.metal_prices['gold'],
            step=0.01,
            format="%.2f",
            key="gold_input"
        )
        st.markdown(f'<p class="big-font">${gold_price:,.2f}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metal-silver">', unsafe_allow_html=True)
        silver_price = st.number_input(
            "🥈 Silver ($/oz)",
            min_value=0.01,
            value=st.session_state.metal_prices['silver'],
            step=0.01,
            format="%.2f",
            key="silver_input"
        )
        st.markdown(f'<p class="big-font">${silver_price:,.2f}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metal-platinum">', unsafe_allow_html=True)
        platinum_price = st.number_input(
            "⚪ Platinum ($/oz)",
            min_value=0.01,
            value=st.session_state.metal_prices['platinum'],
            step=0.01,
            format="%.2f",
            key="platinum_input"
        )
        st.markdown(f'<p class="big-font">${platinum_price:,.2f}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metal-palladium">', unsafe_allow_html=True)
        palladium_price = st.number_input(
            "⚫ Palladium ($/oz)",
            min_value=0.01,
            value=st.session_state.metal_prices['palladium'],
            step=0.01,
            format="%.2f",
            key="palladium_input"
        )
        st.markdown(f'<p class="big-font">${palladium_price:,.2f}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Update session state when inputs change
    st.session_state.metal_prices['gold'] = gold_price
    st.session_state.metal_prices['silver'] = silver_price
    st.session_state.metal_prices['platinum'] = platinum_price
    st.session_state.metal_prices['palladium'] = palladium_price
    
    st.markdown("---")
    
    # Price History Chart
    st.header("📈 Price History")
    chart = create_price_chart()
    if chart:
        st.plotly_chart(chart, use_container_width=True)
    
    st.markdown("---")
    
    # Portfolio Calculator
    st.header("📊 Portfolio Calculator")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Enter Your Holdings")
        
        gold_holding = st.number_input(
            "🥇 Gold Holdings (oz)",
            min_value=0.0,
            value=st.session_state.portfolio_holdings['gold'],
            step=0.1,
            format="%.1f"
        )
        
        silver_holding = st.number_input(
            "🥈 Silver Holdings (oz)",
            min_value=0.0,
            value=st.session_state.portfolio_holdings['silver'],
            step=0.1,
            format="%.1f"
        )
        
        platinum_holding = st.number_input(
            "⚪ Platinum Holdings (oz)",
            min_value=0.0,
            value=st.session_state.portfolio_holdings['platinum'],
            step=0.1,
            format="%.1f"
        )
        
        palladium_holding = st.number_input(
            "⚫ Palladium Holdings (oz)",
            min_value=0.0,
            value=st.session_state.portfolio_holdings['palladium'],
            step=0.1,
            format="%.1f"
        )
        
        # Update holdings in session state
        st.session_state.portfolio_holdings = {
            'gold': gold_holding,
            'silver': silver_holding,
            'platinum': platinum_holding,
            'palladium': palladium_holding
        }
    
    with col2:
        st.subheader("Portfolio Value")
        
        total_value, breakdown = calculate_portfolio_value()
        
        if breakdown:
            df_portfolio = pd.DataFrame(breakdown)
            df_portfolio['Value ($)'] = df_portfolio['Value ($)'].apply(lambda x: f"${x:,.2f}")
            df_portfolio['Price ($/oz)'] = df_portfolio['Price ($/oz)'].apply(lambda x: f"${x:,.2f}")
            
            st.dataframe(df_portfolio, use_container_width=True, hide_index=True)
            
            # Portfolio summary
            st.markdown(f"""
            <div class="portfolio-summary">
                <h3 style="margin: 0; text-align: center;">💰 Total Portfolio Value</h3>
                <h2 style="margin: 10px 0 0 0; text-align: center;">${total_value:,.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("💡 Enter your metal holdings to see portfolio value.")
    
    st.markdown("---")
    
    # Data Export Section
    st.header("💾 Export & Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Copy Current Prices", use_container_width=True):
            prices_text = "\n".join([
                f"{metal.capitalize()}: ${price:,.2f}" 
                for metal, price in st.session_state.metal_prices.items()
            ])
            st.code(prices_text, language=None)
    
    with col2:
        # Download price history
        csv = st.session_state.price_history.to_csv(index=False)
        st.download_button(
            label="📊 Download Price History",
            data=csv,
            file_name=f"metal_price_history_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col3:
        if st.button("🔍 Show Raw Data", use_container_width=True):
            with st.expander("📋 Price History Data", expanded=True):
                st.dataframe(st.session_state.price_history, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>💡 <strong>Tip:</strong> Upload an Excel file with prices in cells D4-D7, or manually enter prices above.</p>
        <p>📈 Click 'Update Price History' to track changes over time.</p>
        <p>🔗 <strong>GitHub:</strong> <a href="https://github.com" target="_blank">View Source Code</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()


# =====================================================
# ADDITIONAL FILES NEEDED FOR GITHUB DEPLOYMENT:
# =====================================================

"""
Create these files in your GitHub repository:

1. requirements.txt
-------------------
streamlit>=1.28.0
pandas>=1.5.0
plotly>=5.15.0
openpyxl>=3.1.0
numpy>=1.24.0

2. README.md
------------
# Metal Prices Dashboard 🥇

A comprehensive Streamlit application for tracking and managing precious metals prices.

## Features

- 📊 **Excel Integration**: Upload Excel files with prices in cells D4-D7
- 💰 **Real-time Price Tracking**: Manual input for Gold, Silver, Platinum, and Palladium
- 📈 **Price History Charts**: Interactive visualizations using Plotly  
- 🎯 **Portfolio Calculator**: Calculate total portfolio value based on holdings
- 💾 **Data Export**: Download price history and copy current prices

## Live Demo

🚀 **[View Live App](https://your-app-name.streamlit.app/)**

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/metal-prices-dashboard.git
cd metal-prices-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the app:
```bash
streamlit run app.py
```

## Excel File Format

Upload Excel files with metal prices in specific cells:
- **D4**: Gold price ($/oz)
- **D5**: Silver price ($/oz)  
- **D6**: Platinum price ($/oz)
- **D7**: Palladium price ($/oz)

## Deployment

This app is deployed on Streamlit Community Cloud. Any changes pushed to the main branch will automatically trigger a new deployment.

## Technologies Used

- **Streamlit**: Web app framework
- **Pandas**: Data manipulation  
- **Plotly**: Interactive charts
- **OpenPyXL**: Excel file processing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

3. .streamlit/config.toml (Optional)
---------------------------------
[theme]
primaryColor = "#FFD700"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[server]
maxUploadSize = 10
maxMessageSize = 10

4. .gitignore
-------------
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
.DS_Store
*.log
"""
