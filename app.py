import streamlit as st
import uuid
from datetime import datetime
import smtplib
from email.message import EmailMessage

st.set_page_config(page_title="FedEx Shipping Supplies", page_icon="📦", layout="wide")

# ========== CONFIG ==========
STORE_EMAIL = st.secrets.get("STORE_EMAIL", "fedexstore@gmail.com") # CHANGE THIS
SMTP_EMAIL = st.secrets.get("SMTP_EMAIL", "your_gmail@gmail.com") # CHANGE THIS
SMTP_APP_PASSWORD = st.secrets.get("SMTP_APP_PASSWORD", "your_app_password") # CHANGE THIS
ADMIN_EMAILS = st.secrets.get("ADMIN_EMAILS", ["admin@fedex.com"])

# ADD YOUR WALLET DETAILS HERE
PAYMENT_WALLETS = {
    "Bank Transfer": "Account Name: FedEx Store Ltd\nAccount No: 1234567890\nBank: First Bank Nigeria",
    "Gift Card": "Send to Email: giftcards@fedexstore.com",
    "Bitcoin": "bc1qxy2kgaqk...PUT_YOUR_BTC_ADDRESS_HERE" # <-- REPLACE THIS
}

# ========== CSS ==========
st.markdown("""
<style>
.stApp { background: #0b1120; color: #f8fafc; }
.store-card { background: #1e293b; border-radius: 12px; padding: 16px; border: 1px solid #334155; margin-bottom: 20px; }
.price { color: #22c55e; font-size: 22px; font-weight: 800; }
.wallet-box { background: #0f172a; padding: 14px; border-radius: 8px; border: 1px dashed #22c55e; white-space: pre-wrap; }
.success-box { background: #064e3b; padding: 16px; border-radius: 10px; border: 1px solid #059669; }
</style>
""", unsafe_allow_html=True)

# ========== SESSION ==========
if "user" not in st.session_state: st.session_state.user = None
if "cart" not in st.session_state: st.session_state.cart = []
if "page" not in st.session_state: st.session_state.page = "Store"
if "pending_order" not in st.session_state: st.session_state.pending_order = None

def is_admin(): 
    return st.session_state.user and st.session_state.user.email in ADMIN_EMAILS

def logout():
    st.session_state.clear()
    st.session_state.user = None
    st.session_state.cart = []
    st.session_state.page = "Store"
    st.rerun()

# ========== EMAIL WITH ATTACHMENT ==========
def send_proof_email(order, proof_file):
    msg = EmailMessage()
    msg['Subject'] = f"Payment Proof - Order {order['code']}"
    msg['From'] = SMTP_EMAIL
    msg['To'] = STORE_EMAIL

    body = f"""Hello FedEx Store,

NEW PAYMENT PROOF RECEIVED

Order ID: {order['code']}
Name: {order['customer']['name']}
Email: {order['customer']['email']}
Phone: {order['customer']['phone']}
Address: {order['customer']['address']}
Total Paid: ${order['total']:.2f}
Payment Method: {order['method']}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Proof is attached to this email.
"""
    msg.set_content(body)

    # ATTACH THE FILE
    file_data = proof_file.read()
    file_name = proof_file.name
    msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Email error: {e}")
        return False

# ========== PRODUCTS ==========
@st.cache_data
def get_products():
    return [
        {"id": 1, "name": "FedEx 10x13 Poly Mailer", "desc": "Pack of 100", "price": 15.00, "img": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=800"},
        {"id": 2, "name": "FedEx Digital Scale", "desc": "Up to 50lbs", "price": 95.00, "img": "https://images.unsplash.com/photo-1581091226825-a6a2a2aee158?w=800"},
        {"id": 3, "name": "FedEx Shipping Labels", "desc": "Roll of 500", "price": 25.00, "img": "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=800"},
        {"id": 4, "name": "FedEx Envelope", "desc": "Legal size", "price": 10.00, "img": "https://images.unsplash.com/photo-1608198093002-ad4e005484ec?w=800"},
        {"id": 5, "name": "FedEx Thermal Printer", "desc": "4x6 Label Printer", "price": 280.00, "img": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"},
        {"id": 6, "name": "FedEx Tape", "desc": "Pack of 6 rolls", "price": 18.00, "img": "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=800"}
    ]

def add_to_cart(product):
    for item in st.session_state.cart:
        if item["id"] == product["id"]:
            item["qty"] += 1
            st.toast(f"Added another {product['name']}")
            return
    st.session_state.cart.append({**product, "qty": 1})
    st.toast(f"{product['name']} added to cart")

def cart_total():
    return sum(i["price"] * i["qty"] for i in st.session_state.cart)

# ========== AUTH ==========
def show_auth():
    st.title("📦 FedEx Shipping Supplies")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        email = st.text_input("Email", key="login_email")
        pwd = st.text_input("Password", type="password", key="login_pwd")
        if st.button("Login", use_container_width=True, key="login_btn"):
            st.session_state.user = type('obj', (object,), {'email': email})
            st.rerun()
    with tab2:
        email = st.text_input("Email", key="reg_email")
        pwd = st.text_input("Password", type="password", key="reg_pwd")
        cpwd = st.text_input("Confirm Password", type="password", key="reg_cpwd")
        if st.button("Create Account", use_container_width=True, key="reg_btn"):
            if pwd == cpwd: 
                st.success("Account created! Please login")
            else: 
                st.error("Passwords do not match")

# ========== APP ==========
if st.session_state.user is None:
    show_auth()
    st.stop()

# SIDEBAR
with st.sidebar:
    st.write(f"Hi, {st.session_state.user.email}")
    if st.button("🏪 Store", use_container_width=True): st.session_state.page = "Store"; st.rerun()
    cart_count = sum(i['qty'] for i in st.session_state.cart)
    if st.button(f"🛒 Cart ({cart_count})", use_container_width=True): st.session_state.page = "Cart"; st.rerun()
    if st.button("💳 Checkout", use_container_width=True): st.session_state.page = "Checkout"; st.rerun()
    if is_admin():
        if st.button("📊 Admin", use_container_width=True): st.session_state.page = "Admin"; st.rerun()
    st.divider()
    if st.button("Logout", use_container_width=True): logout()

products = get_products()

# ========== STORE ==========
if st.session_state.page == "Store":
    st.title("📦 FedEx Shipping Supplies")
    cols = st.columns(2)
    for i, p in enumerate(products):
        with cols[i % 2]:
            st.markdown('<div class="store-card">', unsafe_allow_html=True)
            st.image(p["img"])
            st.subheader(p["name"])
            st.write(p["desc"])
            st.markdown(f'<div class="price">${p["price"]:.2f}</div>', unsafe_allow_html=True)
            if st.button("Add to Cart", key=f"add{p['id']}"):
                add_to_cart(p)
            st.markdown('</div>', unsafe_allow_html=True)

# ========== CART ==========
elif st.session_state.page == "Cart":
    st.title("🛒 Your Cart")
    if not st.session_state.cart:
        st.info("Your cart is empty")
    else:
        for item in st.session_state.cart:
            c1, c2, c3, c4 = st.columns([4,2,1,1])
            c1.write(item["name"])
            c2.write(f"${item['price']:.2f}")
            c3.write(f"Qty: {item['qty']}")
            c4.write(f"**${item['price']*item['qty']:.2f}**")
        st.divider()
        st.metric("Total", f"${cart_total():.2f}")
        if st.button("Proceed to Checkout", use_container_width=True):
            st.session_state.page = "Checkout"
            st.rerun()

# ========== CHECKOUT ==========
elif st.session_state.page == "Checkout":
    st.title("💳 Checkout")
    
    if st.session_state.pending_order:
        # STEP 2: PAYMENT + PROOF
        order = st.session_state.pending_order
        st.markdown(f'<div class="success-box"><h3>Order Placed: {order["code"]}</h3></div>', unsafe_allow_html=True)
        
        st.subheader(f"1. Pay ${order['total']:.2f} via {order['method']}")
        st.markdown(f'<div class="wallet-box">{PAYMENT_WALLETS[order["method"]]}</div>', unsafe_allow_html=True)
        
        st.subheader("2. Send Proof of Payment")
        proof = st.file_uploader("Attach Proof of Payment", type=["jpg", "png", "pdf"])
        
        if st.button("📤 Send Proof to Store", use_container_width=True):
            if proof is None:
                st.error("Upload proof of payment before sending.") # CHANGED: error instead of warning
            else:
                with st.spinner("Sending proof..."):
                    if send_proof_email(order, proof):
                        st.success(f"✅ Proof sent successfully to {STORE_EMAIL}!")
                        st.info("We will confirm your payment and update your order status within 30 minutes.")
                        st.session_state.cart = []
                        st.session_state.pending_order = None
                    else:
                        st.error("Failed to send. Please check your SMTP settings.")

    else:
        # STEP 1: CUSTOMER INFO
        with st.form("checkout"):
            st.subheader("Shipping Details")
            name = st.text_input("Full Name *", value=st.session_state.user.email)
            email = st.text_input("Email *", value=st.session_state.user.email, disabled=True)
            phone = st.text_input("Phone *")
            address = st.text_area("Address *")
            country = st.text_input("Country *", "Nigeria")
            state = st.text_input("State *")
            
            st.subheader("Payment Method")
            method = st.selectbox("Select Payment Method", list(PAYMENT_WALLETS.keys()))
            
            if st.form_submit_button("Place Order", use_container_width=True):
                if not all([name, phone, address, country, state]):
                    st.error("Please fill all required fields")
                else:
                    code = f"FEDEX-{uuid.uuid4().hex[:6].upper()}"
                    st.session_state.pending_order = {
                        "code": code,
                        "customer": {"name": name, "email": email, "phone": phone, "address": address},
                        "total": cart_total(),
                        "method": method
                    }
                    st.rerun()

# ========== ADMIN ==========
elif st.session_state.page == "Admin" and is_admin():
    st.title("📊 Admin Dashboard")
    st.info("Connect Supabase to see real orders here")