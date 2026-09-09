import streamlit as st
import webbrowser

st.set_page_config(page_title="QuantumKicks", layout="centered")

# Custom CSS for purple hero
st.markdown("""
<style>
.hero {
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
    padding: 60px 20px;
    border-radius: 0 0 40px 40px;
    text-align: center;
    color: white;
}
.request-btn {
    background: linear-gradient(90deg, #EC4899 0%, #8B5CF6 100%);
    color: white;
    padding: 14px 32px;
    border-radius: 30px;
    font-size: 18px;
    font-weight: 700;
    border: none;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero">', unsafe_allow_html=True)
st.markdown("<h1>Cravings Delivered.<br>Why Wait?</h1>", unsafe_allow_html=True)
st.markdown("<p>From food to essentials — get anything delivered to you in minutes. Request now and get it.</p>", unsafe_allow_html=True)

if st.button("📦 Request Now"):
    subject = "New Request - QuantumKicks"
    body = "Hi QuantumKicks Team,%0A%0AI would like to place a request.%0A%0AProduct/Item:%0ADetails:%0AName:%0APhone:%0ADelivery Address:%0A%0AThank you!"
    webbrowser.open(f"mailto:ebuka2753@gmail.com?subject={subject}&body={body}")
    st.success("Opening your email app...")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("### How It Works")
st.info("**1. Request** - Tap 'Request Now' and tell us what you need")
st.info("**2. We Confirm** - We’ll reach out with price and delivery time")
st.info("**3. Delivered** - Get it delivered straight to your door")