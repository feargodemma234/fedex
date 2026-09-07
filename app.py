import streamlit as st
import uuid
from datetime import datetime
import pytz
import urllib.parse
import qrcode
from io import BytesIO
import re

st.set_page_config(page_title="QuantumKicks", page_icon="🛒", layout="wide")

# ========== CLEAN CSS ==========
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    
    .stApp { background: #0b1120; color: #f8fafc; }
    .store-card { background: #1e293b; border-radius: 12px; padding: 16px; border: 1px solid #334155; margin-bottom: 20px; }
    .price { color: #22c55e; font-size: 22px; font-weight: 800; }
    .wallet-box { background: #0f172a; padding: 14px; border-radius: 8px; border: 1px dashed #22c55e; white-space: pre-wrap; word-break: break-all; }
    .success-box { background: #064e3b; padding: 16px; border-radius: 10px; border: 1px solid #059669; }
    .warning-box { background: #7c2d12; padding: 16px; border-radius: 10px; border: 1px solid #dc2626; }
    .qr-box { text-align: center; background: white; padding: 10px; border-radius: 8px; max-width: 300px; margin: auto; }
    .reply-box { background: #1e293b; padding: 16px; border-radius: 8px; border: 1px solid #475569; white-space: pre-wrap; }
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
</style>
""", unsafe_allow_html=True)

# ========== CONFIG ==========
STORE_EMAIL = "quantumindustries258@gmail.com"
ADMIN_EMAILS = ["quantumindustries258@gmail.com"]
BTC_ADDRESS = "bc1qtl8hcsssakafwa4a9xrzjfl8thwdkjdmv292tm"

ILLEGAL_KEYWORDS = [
    'gun', 'weapon', 'drug', 'cocaine', 'weed', 'marijuana', 'heroin', 
    'knife', 'explosive', 'bomb', 'passport', 'id card', 'fake id',
    'adult', 'porn', 'xxx', 'nude'
]

PAYMENT_WALLETS = {
    "Bank Transfer": "Bank: OPay\nAccount No: 9032113433\nAccount Name: Deborah Oluchukwu Phillips",
    "Gift Card": "Send to Email: quantumindustries258@gmail.com\nAccepted: iTunes, Amazon, Steam, Google Play",
    "Bitcoin": BTC_ADDRESS
}

COUNTRY_TIMEZONES = {
    "Nigeria": "Africa/Lagos", "USA": "America/New_York", "United States": "America/New_York",
    "UK": "Europe/London", "United Kingdom": "Europe/London", "Canada": "America/Toronto",
    "Ghana": "Africa/Accra", "South Africa": "Africa/Johannesburg", "Kenya": "Africa/Nairobi",
    "Germany": "Europe/Berlin", "France": "Europe/Paris", "India": "Asia/Kolkata", "UAE": "Asia/Dubai"
}

# ========== SESSION ==========
if "user" not in st.session_state: st.session_state.user = None
if "cart" not in st.session_state: st.session_state.cart = []
if "page" not in st.session_state: st.session_state.page = "Store"
if "pending_order" not in st.session_state: st.session_state.pending_order = None

def is_admin(): return st.session_state.user and st.session_state.user.email in ADMIN_EMAILS
def logout():
    st.session_state.clear(); st.rerun()

def check_illegal(text):
    text_lower = text.lower()
    for word in ILLEGAL_KEYWORDS:
        if word in text_lower:
            return True
    return False

def generate_qr(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data); qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO(); img.save(buf, format="PNG"); return buf.getvalue()

def get_local_time(country):
    tz_name = COUNTRY_TIMEZONES.get(country.strip().title(), "UTC")
    try:
        tz = pytz.timezone(tz_name)
        local_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
        tz_abbr = datetime.now(tz).strftime('%Z')
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
    st.title("🛒 QuantumKicks")
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
if is_admin():
    c1, c2, c3, c4, c5, c6 = st.columns([2,1,1,1,1,1])
else:
    c1, c2, c3, c4, c5 = st.columns([2.5,1,1,1,1])
    
with c1: st.write(f"**Hi, {st.session_state.user.email}**")
with c2:
    if st.button("🏪 Store"): st.session_state.page = "Store"; st.rerun()
with c3:
    if st.button("📦 Request"): st.session_state.page = "Request"; st.rerun()
with c4:
    if st.button(f"🛒 {cart_count()}"): st.session_state.page = "Cart"; st.rerun()
if is_admin():
    with c5:
        if st.button("⚙️ Admin"): st.session_state.page = "Admin"; st.rerun()
    with c6:
        if st.button("Logout"): logout()
else:
    with c5:
        if st.button("Logout"): logout()

products = get_products()

if st.session_state.page == "Store":
    st.title("🛒 QuantumKicks")
    cols = st.columns(2)
    for i, p in enumerate(products):
        with cols[i % 2]:
            st.markdown('<div class="store-card">', unsafe_allow_html=True)
            st.image(p["img"])
            st.subheader(p["name"]); st.write(p["desc"])
            st.markdown(f'<div class="price">${p["price"]:.2f}</div>', unsafe_allow_html=True)
            if st.button("Add to Cart", key=f"add{p['id']}", use_container_width=True): add_to_cart(p)
            st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "Request":
    st.title("📦 Request a Product")
    st.write("Can't find what you're looking for? Request it here and we'll get back to you with price + availability.")
    
    with st.form("product_request"):
        req_name = st.text_input("Your Full Name *")
        req_email = st.text_input("Your Email *", value=st.session_state.user.email, disabled=True)
        req_product = st.text_input("Product Name *", placeholder="e.g: iPhone 15 Pro Max 256GB")
        req_qty = st.number_input("Quantity *", min_value=1, max_value=100, value=1)
        req_details = st.text_area("Additional Details", placeholder="Color, Size, Model, etc")
        
        submitted = st.form_submit_button("Submit Request", use_container_width=True, type="primary")
        
        if submitted:
            if not req_name or not req_product:
                st.error("Please fill in Name and Product Name")
            elif check_illegal(req_product + " + req_details):  # FIXED: added space in quotes
                st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                st.error("❌ We don't provide that. Sorry, we cannot process requests for illegal or restricted items.")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                subject = f"Product Request - {req_product}"
                body = f"""New Product Request\nName: {req_name}\nEmail: {req_email}\nProduct: {req_product}\nQuantity: {req_qty}\nDetails: {req_details}\n\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
                mailto_link = f"mailto:{STORE_EMAIL}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
                
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.success(f"✅ Request Sent! We will reply to {req_email} within 24 hours with price and availability.")
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown(f'<meta http-equiv="refresh" content="0; url={mailto_link}">', unsafe_allow_html=True)
                st.link_button("📧 Click if Gmail didn't open", mailto_link)

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
        local_time = get_local_time(order['customer']['country'])
        subject = f"Payment Proof - Order {order['code']}"
        body = f"""Hello QuantumKicks,\n\nI have made payment for Order ID: {order['code']}\n\nCustomer Details:\nName: {order['customer']['name']}\nEmail: {order['customer']['email']}\nPhone: {order['customer']['phone']}\nAddress: {order['customer']['address']}, {order['customer']['state']}, {order['customer']['country']}\n\nOrder Total: ${order['total']:.2f}\nPayment Method: {order['method']}\nDate: {local_time}\n\nI have attached my proof of payment to this email.\n\nThank you."""
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
    st.title("⚙️ Admin Dashboard")
    
    tab1, tab2 = st.tabs(["Reply Generator", "Info"])
    
    with tab1:
        st.subheader("📧 Generate Quote + Payment Reply")
        st.write("Fill this to generate a professional reply for product requests")
        
        cust_name = st.text_input("Customer Name")
        cust_email = st.text_input("Customer Email")
        prod_name = st.text_input("Product Requested")
        prod_price = st.number_input("Price $", min_value=0.0, step=5.0)
        availability = st.selectbox("Availability", ["In Stock", "Available in 3-5 days", "Available in 1-2 weeks"])
        
        st.markdown("---")
        st.subheader("Payment Methods to Include")
        show_bank = st.checkbox("Bank Transfer", value=True)
        show_gift = st.checkbox("Gift Card", value=True)
        show_btc = st.checkbox("Bitcoin", value=False)
        
        if st.button("Generate Reply", type="primary", use_container_width=True):
            payment_section = ""
            if show_bank:
                payment_section += f"\n**🏦 BANK TRANSFER**\n{PAYMENT_WALLETS['Bank Transfer']}\n"
            if show_gift:
                payment_section += f"\n**🎁 GIFT CARD**\n{PAYMENT_WALLETS['Gift Card']}\n"
            if show_btc:
                payment_section += f"\n**₿ BITCOIN**\n{PAYMENT_WALLETS['Bitcoin']}\n"
            
            reply = f"""Hello {cust_name},

Thank you for reaching out to QuantumKicks! 🙏

Regarding your request for: **{prod_name}**

**Availability:** {availability}
**Price:** ${prod_price:.2f}

If you're ready to proceed, please kindly make your payment using any of the options below:

{payment_section}
After payment, please reply to this email with your proof of payment and delivery address. 
We will confirm and ship your order within 24 hours.

Thank you for choosing QuantumKicks - Quality Delivered! 🔥

Best regards,  
Team QuantumKicks  
{STORE_EMAIL}
"""
            st.markdown('<div class="reply-box">', unsafe_allow_html=True)
            st.code(reply, language=None)
            st.markdown('</div>', unsafe_allow_html=True)
            
            mailto_reply = f"mailto:{cust_email}?subject={urllib.parse.quote(f'Quote for {prod_name} - QuantumKicks')}&body={urllib.parse.quote(reply)}"
            st.link_button("📧 Open Gmail to Send Reply", mailto_reply, use_container_width=True, type="primary")
    
    with tab2:
        st.info("Orders will appear here once we connect Supabase")