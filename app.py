import streamlit as st
import uuid
from datetime import datetime
import urllib.parse
import qrcode
from io import BytesIO

st.set_page_config(page_title="FedEx Shipping Supplies", page_icon="📦", layout="wide")

# ========== CONFIG ==========
STORE_EMAIL = "quantumindustries258@gmail.com"
ADMIN_EMAILS = ["quantumindustries258@gmail.com"]
BTC_ADDRESS = "bc1qtl8hcsssakafwa4a9xrzjfl8thwdkjdmv292tm" # YOUR BTC ADDRESS

PAYMENT_WALLETS = {
    "Bank Transfer": "Bank: OPay\nAccount No: 9032113433\nAccount Name: Deborah Oluchukwu Phillips",
    "Gift Card": "Send to Email: quantumindustries258@gmail.com",
    "Bitcoin": BTC_ADDRESS
}

# ========== CSS ==========
st.markdown("""
<style>
.stApp { background: #0b1120; color: #f8fafc; }
.store-card { background: #1e293b; border-radius: 12px; padding: 16px; border: 1px solid #334155; margin-bottom: 20px; }
.price { color: #22c55e; font-size: 22px; font-weight: 800; }
.wallet-box { background: #0f172a; padding: 14px; border-radius: 8px; border: 1px dashed #22c55e; white-space: pre-wrap; word-break: break-all; }
.success-box { background: #064e3b; padding: 16px; border-radius: 10px; border: 1px solid #059669; }
.qr-box { text-align: center; background: white; padding: 10px; border-radius: 8px; max-width: 300px; margin: auto; }
</style>
""", unsafe_allow_html=True)

# ========== SESSION ==========
if "user" not in st.session_state: st.session_state.user = None
if "cart" not in st.session_state: st.session_state.cart = []
if "page" not in st.session_state: st.session_state.page = "Store"
if "pending_order" not in st.session_state: st.session_state.pending_order = None

def is_admin(): return st.session_state.user and st.session_state.user.email in ADMIN_EMAILS
def logout():
    st.session_state.clear(); st.session_state.user = None; st.session_state.cart = []; st.session_state.page = "Store"; st.rerun()

def generate_qr(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

@st.cache_data
def get_products():
    return [
        {
            "id": 1, 
            "name": "Wireless Bluetooth Headphones", 
            "desc": "Noise Cancelling, 40hr Battery", 
            "price": 65.00, 
            "img": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800"
        },
        {
            "id": 2, 
            "name": "Men's Running Sneakers", 
            "desc": "Breathable Mesh, Size 40-45", 
            "price": 120.00, 
            "img": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800"
        },
        {
            "id": 3, 
            "name": "Women's Casual Sneakers", 
            "desc": "Lightweight, All-Day Comfort", 
            "price": 110.00, 
            "img": "https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=800"
        },
        {
            "id": 4, 
            "name": "Wireless Earbuds", 
            "desc": "Bluetooth 5.3, Touch Control", 
            "price": 45.00, 
            "img": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800"
        },
        {
            "id": 5, 
            "name": "Smartwatch", 
            "desc": "Heart Rate, Fitness Tracker", 
            "price": 95.00, 
            "img": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800"
        },
        {
            "id": 6, 
            "name": "Backpack", 
            "desc": "Waterproof, Laptop Compartment", 
            "price": 55.00, 
            "img": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800"
        }
    ]

def add_to_cart(product):
    for item in st.session_state.cart:
        if item["id"] == product["id"]: item["qty"] += 1; st.toast(f"Added another {product['name']}"); return
    st.session_state.cart.append({**product, "qty": 1}); st.toast(f"{product['name']} added to cart")
def cart_total(): return sum(i["price"] * i["qty"] for i in st.session_state.cart)

def show_auth():
    st.title("📦 FedEx Shipping Supplies")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        email = st.text_input("Email", key="login_email"); pwd = st.text_input("Password", type="password", key="login_pwd")
        if st.button("Login", use_container_width=True, key="login_btn"): st.session_state.user = type('obj', (object,), {'email': email}); st.rerun()
    with tab2:
        email = st.text_input("Email", key="reg_email"); pwd = st.text_input("Password", type="password", key="reg_pwd"); cpwd = st.text_input("Confirm Password", type="password", key="reg_cpwd")
        if st.button("Create Account", use_container_width=True, key="reg_btn"):
            if pwd == cpwd: st.success("Account created! Please login")
            else: st.error("Passwords do not match")

if st.session_state.user is None: show_auth(); st.stop()

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

if st.session_state.page == "Store":
    st.title("📦 FedEx Shipping Supplies")
    cols = st.columns(2)
    for i, p in enumerate(products):
        with cols[i % 2]:
            st.markdown('<div class="store-card">', unsafe_allow_html=True); st.image(p["img"]); st.subheader(p["name"]); st.write(p["desc"])
            st.markdown(f'<div class="price">${p["price"]:.2f}</div>', unsafe_allow_html=True)
            if st.button("Add to Cart", key=f"add{p['id']}"): add_to_cart(p)
            st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "Cart":
    st.title("🛒 Your Cart")
    if not st.session_state.cart: st.info("Your cart is empty")
    else:
        for item in st.session_state.cart:
            c1, c2, c3, c4 = st.columns([4,2,1,1]); c1.write(item["name"]); c2.write(f"${item['price']:.2f}"); c3.write(f"Qty: {item['qty']}"); c4.write(f"**${item['price']*item['qty']:.2f}**")
        st.divider(); st.metric("Total", f"${cart_total():.2f}")
        if st.button("Proceed to Checkout", use_container_width=True): st.session_state.page = "Checkout"; st.rerun()

elif st.session_state.page == "Checkout":
    st.title("💳 Checkout")
    if st.session_state.pending_order:
        order = st.session_state.pending_order
        st.markdown(f'<div class="success-box"><h3>Order Placed: {order["code"]}</h3></div>', unsafe_allow_html=True)
        st.subheader(f"1. Pay ${order['total']:.2f} via {order['method']}")
        st.markdown(f'<div class="wallet-box">{PAYMENT_WALLETS[order["method"]]}</div>', unsafe_allow_html=True)
        
        if order['method'] == "Bitcoin":
            st.markdown('<div class="qr-box">', unsafe_allow_html=True)
            qr_bytes = generate_qr(BTC_ADDRESS) # GENERATE QR FROM ADDRESS
            st.image(qr_bytes, caption="Scan to pay with Bitcoin", width=250)
            st.markdown('</div>', unsafe_allow_html=True)

        st.subheader("2. Send Proof of Payment")
        st.write("After payment, click below. It will open your Gmail app with everything filled. Attach your proof and send.")
        
        subject = f"Payment Proof - Order {order['code']}"
        body = f"""Hello FedEx Store,\n\nI have made payment for Order ID: {order['code']}\n\nCustomer Details:\nName: {order['customer']['name']}\nEmail: {order['customer']['email']}\nPhone: {order['customer']['phone']}\nAddress: {order['customer']['address']}\n\nOrder Total: ${order['total']:.2f}\nPayment Method: {order['method']}\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nI have attached my proof of payment to this email.\n\nThank you."""
        mailto_link = f"mailto:{STORE_EMAIL}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
        
        st.link_button("📧 Open Gmail App to Send Proof", mailto_link, use_container_width=True)
        if st.button("✅ I have sent the email", use_container_width=True):
            st.success("Thank you! We will confirm your payment and process your order within 30 minutes.")
            st.session_state.cart = []; st.session_state.pending_order = None
    else:
        with st.form("checkout"):
            st.subheader("Shipping Details")
            name = st.text_input("Full Name *", value=st.session_state.user.email); email = st.text_input("Email *", value=st.session_state.user.email, disabled=True)
            phone = st.text_input("Phone *"); address = st.text_area("Address *"); country = st.text_input("Country *", "Nigeria"); state = st.text_input("State *")
            st.subheader("Payment Method"); method = st.selectbox("Select Payment Method", list(PAYMENT_WALLETS.keys()))
            if st.form_submit_button("Place Order", use_container_width=True):
                if not all([name, phone, address, country, state]): st.error("Please fill all required fields")
                else:
                    code = f"FEDEX-{uuid.uuid4().hex[:6].upper()}"
                    st.session_state.pending_order = {"code": code, "customer": {"name": name, "email": email, "phone": phone, "address": address}, "total": cart_total(), "method": method}
                    st.rerun()

elif st.session_state.page == "Admin" and is_admin():
    st.title("📊 Admin Dashboard")
    st.info("Connect Supabase to see real orders here")