import streamlit as st
import urllib.parse

st.set_page_config(page_title="QuantumKicks", layout="centered", page_icon="📦")

# Custom CSS - same as before
st.markdown("""
<style>
    .topbar { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; }
    .logo { font-size: 22px; font-weight: 800; color: #10B981; display: flex; align-items: center; gap: 8px; }
    .hero-box { background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%); padding: 50px 24px; border-radius: 0 0 40px 40px; text-align: center; color: white; margin: 20px 0 30px 0; }
    .hero-box h1 { font-size: 32px; font-weight: 800; margin: 0 0 12px 0; }
    .hero-box p { font-size: 15px; color: #E0E7FF; margin: 0; }
    .send-link { background: #EF4444; color: white; padding: 14px 0; border-radius: 12px; font-size: 18px; font-weight: 700; width: 100%; text-align: center; display: block; text-decoration: none; }
    .info-card { background: #1a1a1a; padding: 16px; border-radius: 16px; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

# TOP BAR
col1, col2 = st.columns([3,2])
with col1: st.markdown('<div class="logo">🛒 QuantumKicks</div>', unsafe_allow_html=True)
with col2:
    c1, c2 = st.columns(2)
    with c1: st.button("Sign In")
    with c2: st.button("Login")

# PURPLE HERO
st.markdown("""<div class="hero-box"><h1>Cravings Delivered.<br>Why Wait?</h1><p>From food to essentials — get anything delivered to you in minutes. Request now and get it.</p></div>""", unsafe_allow_html=True)

st.markdown("### 📦 Place Your Request")

# USE SESSION STATE TO HOLD FORM DATA
if 'item' not in st.session_state: st.session_state.item = ""
if 'name' not in st.session_state: st.session_state.name = ""
if 'phone' not in st.session_state: st.session_state.phone = ""
if 'address' not in st.session_state: st.session_state.address = ""

item = st.text_input("What do you want?", placeholder="e.g Pizza, Groceries, Phone Charger", key="item")
name = st.text_input("Your Full Name", placeholder="John Doe", key="name")
phone = st.text_input("Your Phone Number", placeholder="0803 123 4567", key="phone")
address = st.text_area("Delivery Address", placeholder="123 Street, Port Harcourt", height=100, key="address")

# BUILD MAILTO LINK
if all([item, name, phone, address]):
    subject = f"New Delivery Request - {item}"
    body = f"""Hi QuantumKicks Team,

I would like to place a request:

Item: {item}
Name: {name}
Phone: {phone}
Delivery Address: {address}

Thank you!"""
    mailto_link = f"mailto:ebuka2753@gmail.com?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
    
    # THIS BUTTON NOW OPENS GMAIL DIRECTLY
    st.markdown(f'<a href="{mailto_link}" class="send-link">📦 Send Request</a>', unsafe_allow_html=True)
    st.success("Tap the red button above to open Gmail")
else:
    st.button("📦 Send Request", disabled=True)
    st.warning("Please fill all fields")

# HOW IT WORKS
st.markdown("### How It Works")
st.markdown('<div class="info-card"><b>1. Fill Form</b><br><span style="color:#aaa">Tell us what you need and where to deliver</span></div>', unsafe_allow_html=True)
st.markdown('<div class="info-card"><b>2. We Confirm</b><br><span style="color:#aaa">We’ll call you with price and delivery time</span></div>', unsafe_allow_html=True)
st.markdown('<div class="info-card"><b>3. Delivered</b><br><span style="color:#aaa">Get it delivered straight to your door</span></div>', unsafe_allow_html=True)