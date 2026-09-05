import streamlit as st

st.set_page_config(page_title="FEDEX", page_icon="📦", layout="wide")

# LIGHT THEME LIKE THE VIDEO
st.markdown("""
<style>
.stApp {background-color: #F5F5F7;} /* Light gray bg */
h1, h2, h3, h4, p, label {color: #1C1C1E;}

/* Product Card - Purple */
.product-card {
    background: linear-gradient(135deg, #A78BFA 0%, #8B5CF6 100%);
    padding: 0px;
    border-radius: 20px;
    margin-bottom: 15px;
    position: relative;
    overflow: hidden;
}
.product-info {
    background: rgba(255,255,255,0.9);
    border-radius: 15px;
    padding: 10px;
    margin: 8px;
    color: black;
}

/* Circle Category */
.category-circle {
    text-align: center;
    padding: 5px;
}
.category-circle img {
    border-radius: 50%;
    border: 3px solid #E9D5FF;
}

.stButton>button {
    background-color: #8B5CF6; /* Purple */
    color: white; 
    font-weight: bold; 
    border-radius: 12px; 
    border: none;
    width: 100%;
}
.stTextInput>div>div>input {background-color: white; border-radius: 20px; border: 1px solid #E5E7EB;}
</style>
""", unsafe_allow_html=True)

# SESSION STATE
if "cart" not in st.session_state: st.session_state.cart = []
if "search" not in st.session_state: st.session_state.search = ""

# FAKE PRODUCTS - CLOTHES LIKE THE VIDEO
def get_products():
    return [
        {"id": 1, "name": "Berrylush", "desc": "Casual Cottonwear", "price": 120, "stock": 12, "image_url": "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?q=80&w=800", "category": "Women"},
        {"id": 2, "name": "Twinkle", "desc": "Bodycon with stripes", "price": 150, "stock": 8, "image_url": "https://images.unsplash.com/photo-1496747611176-843222e1e57c?q=80&w=800", "category": "Women"},
        {"id": 3, "name": "Street Tee", "desc": "Oversized T-shirt", "price": 110, "stock": 20, "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?q=80&w=800", "category": "Men"},
        {"id": 4, "name": "Blazers", "desc": "Casual Cottonwear", "price": 130, "stock": 5, "image_url": "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?q=80&w=800", "category": "Women"},
    ]

products = get_products()

# HEADER
st.title("FEDEX")
st.subheader("Discover")
st.write("Explore Our New Collections")

# CIRCLE CATEGORIES
st.write("**Categories**")
col1, col2, col3, col4 = st.columns(4)
with col1: 
    st.markdown('<div class="category-circle">', unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1494790108377-be9c29b29330?q=80&w=200", width=70)
    st.write("Women")
    st.markdown('</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="category-circle">', unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=200", width=70)
    st.write("Men")
    st.markdown('</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="category-circle">', unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1519345182560-3f2917c472ef?q=80&w=200", width=70)
    st.write("Kids")
    st.markdown('</div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="category-circle">', unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=200", width=70)
    st.write("Footwear")
    st.markdown('</div>', unsafe_allow_html=True)

# SEARCH BAR
st.session_state.search = st.text_input("Search", placeholder="Search for products", label_visibility="collapsed")

# PRODUCTS GRID
st.write("**New Arrivals**")
cols = st.columns(2) # 2 per row like video
for i, p in enumerate(products):
    with cols[i % 2]:
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        st.image(p["image_url"], use_container_width=True)
        st.markdown(f"""
        <div class="product-info">
            <b>{p["name"]}</b> <span style="float:right">${p["price"]}</span><br>
            <small>{p["desc"]}</small><br>
            ⭐ 4.5
        </div>
        """, unsafe_allow_html=True)
        if st.button("Add to Cart", key=f"btn_{p['id']}"):
            st.session_state.cart.append(p)
            st.toast(f"✅ {p['name']} added!")
        st.markdown('</div>', unsafe_allow_html=True)

# SIDEBAR CART
with st.sidebar:
    st.header("🛒 Your Cart")
    if len(st.session_state.cart) == 0: 
        st.write("Cart is empty")
    else:
        total = sum(item['price'] for item in st.session_state.cart)
        for item in st.session_state.cart: 
            st.write(f"- {item['name']} : ${item['price']}")
        st.subheader(f"Total: ${total}")
        if st.button("Checkout"):
            st.success("Order placed!"); st.session_state.cart = []