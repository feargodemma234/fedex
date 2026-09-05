import streamlit as st

st.set_page_config(page_title="FEDEX", page_icon="📦", layout="wide")

# DARK THEME LIKE THE VIDEO
st.markdown("""
<style>
.stApp {background-color: #0A1128;} /* Deep Navy */
div[data-testid="stSidebar"] {background-color: #1C2541;}
h1, h2, h3, h4, p, label {color: white;}

.product-card {
    background-color: #1C2541;
    padding: 12px;
    border-radius: 16px;
    margin-bottom: 15px;
}

.banner {
    background: linear-gradient(90deg, #1C2541 0%, #3A86FF 100%);
    padding: 20px;
    border-radius: 20px;
    margin-bottom: 20px;
}

.stButton>button {
    background-color: #FF3131; /* Red accent like cart icon */
    color: white; 
    font-weight: bold; 
    border-radius: 12px; 
    border: none;
    width: 100%;
}
.stTextInput>div>div>input {color: white; background-color: #1C2541; border-radius: 12px;}
</style>
""", unsafe_allow_html=True)

# SESSION STATE
if "cart" not in st.session_state: st.session_state.cart = []
if "user" not in st.session_state: st.session_state.user = None
if "search" not in st.session_state: st.session_state.search = ""
if "category" not in st.session_state: st.session_state.category = "All"

# FAKE PRODUCTS
def get_products():
    return [
        {"id": 1, "name": "Running Shoes", "price": 65000, "stock": 12, "description": "Nike Air Max style", "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=800", "brand": "Nike", "gender": "Men"},
        {"id": 2, "name": "White Sneakers", "price": 55000, "stock": 8, "description": "Clean white sneakers", "image_url": "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?q=80&w=800", "brand": "Adidas", "gender": "Men"},
        {"id": 3, "name": "Sport Shoes Red", "price": 33000, "stock": 20, "description": "Red sports shoes", "image_url": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?q=80&w=800", "brand": "Puma", "gender": "Women"},
        {"id": 4, "name": "Autumn Boots", "price": 89000, "stock": 5, "description": "Black leather boots", "image_url": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?q=80&w=800", "brand": "ZARA", "gender": "Women"},
        {"id": 5, "name": "Athletic Shoes", "price": 99000, "stock": 10, "description": "Blue running shoes", "image_url": "https://images.unsplash.com/photo-1600185365926-3a2ce3cdb9eb?q=80&w=800", "brand": "Nike", "gender": "Men"},
        {"id": 6, "name": "Leather Shoes", "price": 120000, "stock": 7, "description": "Formal leather shoes", "image_url": "https://images.unsplash.com/photo-1614251059479-8612d1b11eae?q=80&w=800", "brand": "LV", "gender": "Men"},
    ]

products = get_products()

# FAKE AUTH
def login(email, password):
    st.session_state.user = {"email": email}
    st.success("Logged in!"); st.rerun()

def signup(email, password):
    st.session_state.user = {"email": email}
    st.success("Account created!"); st.rerun()

def logout():
    st.session_state.user = None; st.session_state.cart = []; st.rerun()

# HEADER WITH CART ICON
col1, col2 = st.columns([6,1])
with col1: st.title("FEDEX")  # CHANGED HERE
with col2: st.metric("Cart", len(st.session_state.cart))

# BANNER
st.markdown("""
<div class="banner">
    <h2>40% OFF NEW ARRIVALS</h2>
    <p>Premium products. Limited time.</p>
</div>
""", unsafe_allow_html=True)

# SEARCH BAR
st.session_state.search = st.text_input("Search", placeholder="Search Products", label_visibility="collapsed")

# BRAND FILTER
st.write("**Popular Brands**")
brands = ["All", "Nike", "Adidas", "ZARA", "Puma", "LV"]
st.session_state.category = st.selectbox("Filter", brands, label_visibility="collapsed")

# TABS
tab1, tab2, tab3 = st.tabs(["All", "Men's", "Women's"])

def show_products(product_list):
    if not product_list:
        st.write("No products found")
        return
    cols = st.columns(2) # 2 per row
    for i, p in enumerate(product_list):
        with cols[i % 2]:
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            
            # FIX: Placeholder if no image
            img_url = p.get("image_url") or "https://via.placeholder.com/400x400/1C2541/FFFFFF?text=FEDEX"
            st.image(img_url, use_column_width=True)
            
            st.subheader(p["name"])
            st.write(f"**₦{p['price']:,.0f}**")
            st.write(f"⭐ 4.5 | Stock: {p['stock']}")
            if st.button("Add to Cart", key=f"btn_{p['id']}"):
                st.session_state.cart.append(p)
                st.toast(f"✅ {p['name']} added!")
            st.markdown('</div>', unsafe_allow_html=True)

def filter_products(gender):
    filtered = products
    if st.session_state.category != "All":
        filtered = [p for p in filtered if p["brand"] == st.session_state.category]
    if gender != "All":
        filtered = [p for p in filtered if p["gender"] == gender]
    if st.session_state.search:
        filtered = [p for p in filtered if st.session_state.search.lower() in p["name"].lower()]
    return filtered

with tab1: show_products(filter_products("All"))
with tab2: show_products(filter_products("Men"))
with tab3: show_products(filter_products("Women"))

# SIDEBAR = CART + LOGIN
with st.sidebar:
    st.title("Account")
    if st.session_state.user:
        st.write(f"Hi, {st.session_state.user['email']}")
        st.button("Logout", on_click=logout)
    else:
        t1, t2 = st.tabs(["Login", "Sign Up"])
        with t1:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            st.button("Login", on_click=login, args=(email, password))
        with t2:
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_pass")
            st.button("Sign Up", on_click=signup, args=(email, password))
    
    st.divider()
    st.header("🛒 Your Cart")
    if len(st.session_state.cart) == 0: 
        st.write("Cart is empty")
    else:
        total = sum(item['price'] for item in st.session_state.cart)
        for item in st.session_state.cart: 
            st.write(f"- {item['name']} : ₦{item['price']:,.0f}")
        st.subheader(f"Total: ₦{total:,.0f}")
        if st.button("Checkout"):
            if st.session_state.user: 
                st.success("Order placed!"); st.session_state.cart = []
            else: 
                st.warning("Please login to checkout")