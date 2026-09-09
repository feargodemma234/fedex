import streamlit as st
import urllib.parse

st.set_page_config(page_title="QuantumKicks", layout="centered", page_icon="📦")

# Custom CSS
st.markdown("""
<style>
    .hero-box {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        padding: 50px 24px;
        border-radius: 0 0 40px 40px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
    }
    .hero-box h1 {
        font-size: 32px;
        font-weight: 800;
        margin: 0 0 12px 0;
        line-height: 1.2;
    }
    .hero-box p {
        font-size: 15px;
        color: #E0E7FF;
        margin: 0;
    }
    .stButton>button {
        background: linear-gradient(90deg, #EC4899 0%, #8B5CF6 100%);
        color: white;
        border: none;
        padding: 16px 0;
        border-radius: 16px;
        font-size: 18px;
        font-weight: 700;
        width: 100%;
    }
    .info-card {
        background: #1a1a1a;
        padding: 16px;
        border-radius: 16px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# PURPLE HERO BOX
st.markdown("""
<div class="hero-box">
    <h1>Cravings Delivered.<br>Why Wait?</h1>
    <p>From food to essentials — get anything delivered to you in minutes. Request now and get it.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("### 📦 Place Your Request")

with st.form("request_form"):
    item = st.text_input("What do you want?", placeholder="e.g Pizza, Groceries, Phone Charger")
    name = st.text_input("Your Full Name", placeholder="John Doe")
    phone = st.text_input("Your Phone Number", placeholder="0803 123 4567")
    address = st.text_area("Delivery Address", placeholder="123 Street, Port Harcourt", height=100)
    
    submitted = st.form_submit_button("📦 Send Request")
    
    if submitted:
        if not all([item, name, phone, address]):
            st.error("Please fill all fields")
        else:
            subject = f"New Delivery Request - {item}"
            body = f"""Hi QuantumKicks Team,

I would like to place a request:

Item: {item}
Name: {name}
Phone: {phone}
Delivery Address: {address}

Thank you!"""
            
            # Create mailto link
            mailto_link = f"mailto:ebuka2753@gmail.com?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
            
            st.success("Opening your email app...")
            st.markdown(f'<a href="{mailto_link}" target="_blank">Click here if email did not open</a>', unsafe_allow_html=True)
            st.components.v1.html(f'<script>window.location.href = "{mailto_link}";</script>', height=0)

# HOW IT WORKS
st.markdown("### How It Works")
st.markdown('<div class="info-card"><b>1. Fill Form</b><br><span style="color:#aaa">Tell us what you need and where to deliver</span></div>', unsafe_allow_html=True)
st.markdown('<div class="info-card"><b>2. We Confirm</b><br><span style="color:#aaa">We’ll call you with price and delivery time</span></div>', unsafe_allow_html=True)
st.markdown('<div class="info-card"><b>3. Delivered</b><br><span style="color:#aaa">Get it delivered straight to your door</span></div>', unsafe_allow_html=True)

st.markdown("<br><center style='color:#666'>QuantumKicks © 2026 | Deliveries in Port Harcourt</center>", unsafe_allow_html=True)