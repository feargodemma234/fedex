import streamlit as st
import uuid
from datetime import datetime
import pytz
import urllib.parse
import qrcode
from io import BytesIO

st.set_page_config(page_title="Quantum Store", page_icon="🛒", layout="wide")

# HIDE STREAMLIT BRANDING
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
  .stDeployButton {display:none;}
    [data-testid="stToolbar"] {display: none;}
  .viewerBadge_container__1QSob {display: none;}
</style>
""", unsafe_allow_html=True)

# ========== CONFIG ==========
STORE_EMAIL = "quantumindustries258@gmail.com"
ADMIN_EMAILS = ["quantumindustries258@gmail.com"]
BTC_ADDRESS = "bc1qtl8hcsssakafwa4a9xrzjfl8thwdkjdmv292tm"

PAYMENT_WALLETS = {
    "Bank Transfer": "Bank: OPay\nAccount No: 9032113433\nAccount Name: Deborah Oluchukwu Phillips",
    "Gift Card": "Send to Email: quantumindustries258@gmail.com",
    "Bitcoin": BTC_ADDRESS
}

# COUNTRY TO TIMEZONE MAP - ADD MORE AS NEEDED
COUNTRY_TIMEZONES = {
    "Nigeria": "Africa/Lagos",
    "USA": "America/New_York",
    "United States": "America/New_York",
    "UK": "Europe/London",
    "United Kingdom": "Europe/London",
    "Canada": "America/Toronto",
    "Ghana": "Africa/Accra",
    "South Africa": "Africa/Johannesburg",
    "Kenya": "Africa/Nairobi",
    "Germany": "Europe/Berlin",
    "France": "Europe/Paris",
    "India": "Asia/Kolkata",
    "UAE": "Asia/Dubai",
    "Saudi Arabia": "Asia/Riyadh"
}

st.markdown("""
<style>
    /* Hide everything Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Hide the red crown deploy button */
    .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    
    /* Hide "Manage app" badge + profile robot */
    .viewerBadge_container__1QSob {display: none !important;}
    .st-emotion-cache-1cypcdb {display: none !important;} /* new robot icon class */
    .st-emotion-cache-18ni7ap {display: none !important;} /* old robot icon class */
    
    /* Hide top right corner completely */
    [data-testid="stHeader"] {display: none !important;}
</style>
""", unsafe_allow_html=True)

# ========== SESSION ==========
if "user" not in st.session_state: st.session_state.user = None
if "cart" not in st.session_state: st.session_state.cart = []
if "page" not in st.session_state: st.session_state.page = "Store"
if "pending_order" not in st.session_state: st.session_state.pending_order = None

def is_admin(): return st.session_state.user and st.session_state.user.email in ADMIN_EMAILS
def logout():
    st.session_state.clear(); st.rerun()

def generate_qr(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data); qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO(); img.save(buf, format="PNG"); return buf.getvalue()

def get_local_time(country):
    # Default to UTC if country not found
    tz_name = COUNTRY_TIMEZONES.get(country.strip().title(), "UTC")
    try:
        tz = pytz.timezone(tz_name)
        local_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
        tz_abbr = datetime.now(tz).strftime('%Z') # WAT, EST, GMT etc
        return f"{local_time} {tz_abbr}"
    except:
        return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S') + " UTC"

@st.cache_data
def get_products():
    return [
        {"id": 1, "name": "Wireless Bluetooth Headphones", "desc": "Noise Cancelling, 40hr Battery", "price": 65.00, "img": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800"},
        {"id": 2, "name": "Men's Running Sneakers", "desc": "Breathable Mesh, Size 40-45", "price": 120.00, "img": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800"},
        {"id": 3, "name": "Women's Casual Sneakers", "desc": "Lightweight, All-Day Comfort", "price": 110.00, "img": "https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=800"},
        {"id": 4, "name": "Wireless Earbuds", "desc": "Bluetooth 5.3, Touch Control", "price": 45.00, "img": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800"},
        {"id": 5, "name": "Smartwatch", "desc": "Heart Rate, Fitness Tracker", "price": 95.00, "img": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800"},
        {"id": 6, "name": "Backpack", "desc": "Waterproof, Laptop Compartment", "price": 55.00, "img": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800"}
    ]

def add_to_cart(product):
    for item in st.session_state.cart:
        if item["id"] == product["id"]: item["qty"] += 1; st.toast(f"Added another {product['name']}"); return
    st.session_state.cart.append({**product, "qty": 1}); st.toast(f"{product['name']} added to cart")

def cart_total(): return sum(i["price"] * i["qty"] for i in st.session_state.cart)
def cart_count(): return sum(i['qty'] for i in st.session_state.cart)

def show_auth():
    st.title("🛒 Quantum Store")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        email = st.text_input("Email", key="login_email"); pwd = st.text_input("Password", type="password", key="login_pwd")
        if st.button("Login", use_container_width=True, type="primary"):
            st.session_state.user = type('obj', (object,), {'email': email}); st.rerun()
    with tab2:
        email = st.text_input("Email", key="reg_email"); pwd = st.text_input("Password", type="password", key="reg_pwd"); cpwd = st.text_input("Confirm Password", type="password", key="reg_cpwd")
        if st.button("Create Account", use_container_width=True, type="primary"):
            if pwd == cpwd: st.success("Account created! Please login")
            else: st.error("Passwords do not match")

if st.session_state.user is None: show_auth(); st.stop()

# ========== TOP NAV FOR MOBILE ==========
c1, c2, c3, c4 = st.columns([3,1,1,1])
with c1: st.write(f"**Hi, {st.session_state.user.email}**")
with c2:
    if st.button("🏪 Store"): st.session_state.page = "Store"; st.rerun()
with c3:
    if st.button(f"🛒 {cart_count()}"): st.session_state.page = "Cart"; st.rerun()
with c4:
    if st.button("Logout"): logout()

products = get_products()

if st.session_state.page == "Store":
    st.title("🛒 Quantum Store")
    cols = st.columns(2)
    for i, p in enumerate(products):
        with cols[i % 2]:
            st.markdown('<div class="store-card">', unsafe_allow_html=True)
            st.image(p["img"])
            st.subheader(p["name"]); st.write(p["desc"])
            st.markdown(f'<div class="price">${p["price"]:.2f}</div>', unsafe_allow_html=True)
            if st.button("Add to Cart", key=f"add{p['id']}", use_container_width=True): add_to_cart(p)
            st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "Cart":
    st.title("🛒 Your Cart")
    if not st.session_state.cart: st.info("Your cart is empty")
    else:
        for item in st.session_state.cart:
            c1, c2, c3, c4 = st.columns([4,2,1,1]); c1.write(item["name"]); c2.write(f"${item['price']:.2f}"); c3.write(f"Qty: {item['qty']}"); c4.write(f"**${item['price']*item['qty']:.2f}**")
        st.divider(); st.metric("Total", f"${cart_total():.2f}")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("← Continue Shopping", use_container_width=True): st.session_state.page = "Store"; st.rerun()
        with c2:
            if st.button("Proceed to Checkout →", use_container_width=True, type="primary"): st.session_state.page = "Checkout"; st.rerun()

elif st.session_state.page == "Checkout":
    st.title("💳 Checkout")
    if st.session_state.pending_order:
        order = st.session_state.pending_order
        st.markdown(f'<div class="success-box"><h3>✅ Order Placed: {order["code"]}</h3></div>', unsafe_allow_html=True)
        st.subheader(f"1. Pay ${order['total']:.2f} via {order['method']}")
        st.markdown(f'<div class="wallet-box">{PAYMENT_WALLETS[order["method"]]}</div>', unsafe_allow_html=True)
        if order['method'] == "Bitcoin":
            st.markdown('<div class="qr-box">', unsafe_allow_html=True)
            qr_bytes = generate_qr(BTC_ADDRESS)
            st.image(qr_bytes, caption="Scan to pay with Bitcoin", width=250)
            st.markdown('</div>', unsafe_allow_html=True)
        st.subheader("2. Send Proof of Payment")

        # AUTO TIMEZONE BASED ON COUNTRY
        local_time = get_local_time(order['customer']['country'])

        subject = f"Payment Proof - Order {order['code']}"
        body = f"""Hello Quantum Store,

I have made payment for Order ID: {order['code']}

Customer Details:
Name: {order['customer']['name']}
Email: {order['customer']['email']}
Phone: {order['customer']['phone']}
Address: {order['customer']['address']}, {order['customer']['state']}, {order['customer']['country']}

Order Total: ${order['total']:.2f}
Payment Method: {order['method']}
Date: {local_time}

I have attached my proof of payment to this email.

Thank you."""
        mailto_link = f"mailto:{STORE_EMAIL}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"

        st.link_button("📧 Open Gmail App to Send Proof", mailto_link, use_container_width=True, type="primary")
        if st.button("✅ I have sent the email", use_container_width=True):
            st.success("Thank you! We will confirm your payment and process your order within 30 minutes.")
            st.session_state.cart = []; st.session_state.pending_order = None; st.rerun()
    else:
        with st.form("checkout"):
            st.subheader("Shipping Details")
            name = st.text_input("Full Name *"); email = st.text_input("Email *", value=st.session_state.user.email, disabled=True)
            phone = st.text_input("Phone *"); address = st.text_area("Address *"); country = st.text_input("Country *", "Nigeria"); state = st.text_input("State *")
            st.subheader("Payment Method"); method = st.selectbox("Select Payment Method", list(PAYMENT_WALLETS.keys()))
            if st.form_submit_button("Place Order", use_container_width=True, type="primary"):
                if not all([name, phone, address, country, state]): st.error("Please fill all required fields")
                else:
                    code = f"QNT-{uuid.uuid4().hex[:6].upper()}"
                    st.session_state.pending_order = {"code": code, "customer": {"name": name, "email": email, "phone": phone, "address": address, "country": country, "state": state}, "total": cart_total(), "method": method}
                    st.rerun()

elif st.session_state.page == "Admin" and is_admin():
    st.title("📊 Admin Dashboard")
    st.info("Connect Supabase to see real orders here")