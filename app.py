
import streamlit as st
import urllib.parse

st.set_page_config(
    page_title="QuantumKicks",
    layout="centered",
    page_icon="📦"
)

st.markdown("""
<style>
.logo {
    font-size: 22px;
    font-weight: 800;
    color: #10B981;
    padding: 16px 20px;
}

.hero-box {
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
    padding: 50px 24px;
    border-radius: 0 0 40px 40px;
    text-align: center;
    color: white;
    margin: 0 0 30px 0;
}

.hero-box h1 {
    font-size: 32px;
    font-weight: 800;
    margin: 0 0 12px 0;
}

.hero-box p {
    font-size: 15px;
    color: #E0E7FF;
    margin: 0;
}

.send-btn {
    background: #EF4444;
    color: white !important;
    padding: 16px 0;
    border-radius: 12px;
    font-size: 18px;
    font-weight: 700;
    width: 100%;
    text-align: center;
    display: block;
    text-decoration: none !important;
    margin-top: 10px;
    border: none;
}

.send-btn-disabled {
    background: #444;
    color: #888;
    padding: 16px 0;
    border-radius: 12px;
    font-size: 18px;
    font-weight: 700;
    width: 100%;
    text-align: center;
    display: block;
    margin-top: 10px;
}

.info-card {
    background: #1a1a1a;
    padding: 16px;
    border-radius: 16px;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)


# HEADER
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown(
        '<div class="logo">🛒 QuantumKicks</div>',
        unsafe_allow_html=True
    )

with col2:
    c1, c2 = st.columns(2)

    with c1:
        st.button("Sign In")

    with c2:
        st.button("Login")


# HERO
st.markdown("""
<div class="hero-box">
    <h1>Cravings Delivered.<br>Why Wait?</h1>
    <p>
        From food to essentials — get anything delivered to you in minutes.
        Request now and get it.
    </p>
</div>
""", unsafe_allow_html=True)


# REQUEST SECTION
st.markdown("### 📦 Place Your Request")

item = st.text_input(
    "What do you want?",
    placeholder="e.g Pizza, Groceries, Phone Charger"
)

name = st.text_input(
    "Your Full Name",
    placeholder="John Doe"
)

phone = st.text_input(
    "Your Phone Number",
    placeholder="0803 123 4567"
)

address = st.text_area(
    "Delivery Address",
    placeholder="123 Street, Port Harcourt",
    height=100
)


# CHECK EVERYTHING IS FILLED
all_filled = all([
    item.strip(),
    name.strip(),
    phone.strip(),
    address.strip()
])


# GMAIL PRE-FILLED EMAIL
if all_filled:

    subject = f"New QuantumKicks Delivery Request - {item}"

    body = f"""Hello Quantum Industries,

I would like to place a delivery request.

━━━━━━━━━━━━━━━━━━━━
ORDER INFORMATION
━━━━━━━━━━━━━━━━━━━━

Item:
{item}

Customer Name:
{name}

Phone Number:
{phone}

Delivery Address:
{address}

━━━━━━━━━━━━━━━━━━━━

Please contact me to confirm the price and delivery time.

Thank you,
{name}
"""

    # Encode the email information
    encoded_subject = urllib.parse.quote(subject)
    encoded_body = urllib.parse.quote(body)

    # Gmail compose URL
    gmail_link = (
        "https://mail.google.com/mail/?view=cm"
        "&fs=1"
        "&to=quantumindustries258@gmail.com"
        f"&su={encoded_subject}"
        f"&body={encoded_body}"
    )

    st.markdown(
        f"""
        <a href="{gmail_link}" target="_blank" class="send-btn">
            📦 Send Request
        </a>
        """,
        unsafe_allow_html=True
    )

else:

    st.markdown(
        """
        <div class="send-btn-disabled">
            📦 Send Request
        </div>
        """,
        unsafe_allow_html=True
    )


# HOW IT WORKS
st.markdown("### How It Works")

st.markdown(
    """
    <div class="info-card">
        <b>1. Fill Form</b><br>
        <span style="color:#aaa">
            Tell us what you need and where to deliver
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="info-card">
        <b>2. We Confirm</b><br>
        <span style="color:#aaa">
            We'll contact you with the price and delivery time
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="info-card">
        <b>3. Delivered</b><br>
        <span style="color:#aaa">
            Get it delivered straight to your door
        </span>
    </div>
    """,
    unsafe_allow_html=True
)