import streamlit as st

st.set_page_config(page_title="FEDEX", page_icon="📦", layout="wide")

# DARK YELLOW THEME
st.markdown("""
<style>
.stApp {background-color: #B8860B;}
h1, h2, h3, h4, p, label {color: #FFFFFF;}

/* HORIZONTAL SCROLL CATEGORIES - TEXT ONLY */
.categories-container {
    display: flex;
    overflow-x: auto;
    gap: 10px;
    padding: 10px 5px;
    scrollbar-width: none;
}
.categories-container::-webkit-scrollbar {display: none;}

.category-pill {
    flex: 0 0 auto;
    padding: 8px 18px;
    border-radius: 25px;
    background: #000;
    color: #FFD700;
    border: 2px solid #FFD700;
    font-weight: bold;
    font-size: 14px;
    cursor: pointer;
    white-space: nowrap;
}
.category-pill.active {
    background: #FFD700;
    color: #000;
}

/* Product Card */
.product-card {
    background: linear-gradient(135deg, #DAA520 0%, #B8860B 100%);
    border-radius: 20px;
    margin-bottom: 15px;
    overflow: hidden;
}
.product-info {
    background: rgba(0,0,0,0.3);
    border-radius: 15px;
    padding: 10px;
    margin: 8px;
    color: white;
}
.stButton>button {
    background-color: #000;
    color: #FFD700; 
    font-weight: bold; 
    border-radius: 12px; 
    border: 2px solid #FFD700;
    width: 100%;
}
.stTextInput>div>div>input {background-color: #FFD700; color: black; border-radius: 20px; border: 1px solid black;}
</style>
""", unsafe_allow_html=True)

# SESSION STATE
if "cart" not in st.session_state: st.session_state.cart = []
if "search" not in st.session_state: st.session_state.search = ""
if "selected_cat" not in st.session_state: st.session_state.selected_cat = "All"

# PRODUCTS - ADDED CATEGORIES AS PRODUCTS TOO
def get_products():
    return [
        # WOMEN
        {"id": 1, "name": "Berrylush Dress", "desc": "Casual Cottonwear", "price": 120, "stock": 12, "image_url": "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?q=80&w=800", "category": "Women"},
        {"id": 2, "name": "Twinkle Bodycon", "desc": "Striped Dress", "price": 150, "stock": 8, "image_url": "https://images.unsplash.com/photo-1496747611176-843222e1e57c?q=80&w=800", "category": "Women"},
        # MEN
        {"id": 3, "name": "Street Tee", "desc": "Oversized T-shirt", "price": 110, "stock": 20, "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?q=80&w=800", "category": "Men"},
        {"id": 4, "name": "Formal Shirt", "desc": "White Cotton Shirt", "price": 130, "stock": 15, "image_url": "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?q=80&w=800", "category": "Men"},
        # KIDS
        {"id": 5, "name": "Kids Hoodie", "desc": "Cotton Hoodie", "price": 80, "stock": 15, "image_url": "https://images.unsplash.com/photo-1620799139517-2a76f4a2a01d?q=80&w=800", "category": "Kids"},
        {"id": 6, "name": "Kids Jeans", "desc": "Denim Pants", "price": 70, "stock": 10, "image_url": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?q=80&w=800", "category": "Kids"},
        # FOOTWEAR
        {"id": 7, "name": "Running Shoes", "desc": "Sport Shoes", "price": 200, "stock": 10, "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=800", "category": "Footwear"},
        {"id": 8, "name": "Casual Sneakers", "desc": "White Sneakers", "price": 180, "stock": 12, "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?q=80&w=800", "category": "Footwear"},
    ]

products = get_products()

# HEADER
col1, col2 = st.columns([6,1])
with col1: st.title("FEDEX")
with col2: st.metric("Cart", len(st.session_state.cart))

st.subheader("Discover")

# HORIZONTAL TEXT CATEGORIES
st.write("**Categories**")
categories = ["All", "Women", "Men", "Kids", "Footwear"]

st.markdown('<div class="categories-container">', unsafe_allow_html=True)
cols = st.columns(len(categories))
for i, cat in enumerate(categories):
    with cols[i]:
        if st.button(cat, key=f"cat_{cat}", use_container_width=True):
            st.session_state.selected_cat = cat
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# SEARCH BAR
st.session_state.search = st.text_input("Search", placeholder="Search for products", label_visibility="collapsed")

# PRODUCTS GRID - 2 PER ROW
st.write(f"**New Arrivals - {st.session_state.selected_cat}**")
filtered = products
if st.session_state.selected_cat!= "All":
    filtered = [p for p in filtered if p["category"] == st.session_state.selected_cat]
if st.session_state.search:
    filtered = [p for p in filtered if st.session_state.search.lower() in p["name"].lower()]

cols = st.columns(2)
for i, p in enumerate(filtered):
    with cols[i % 2]:
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        st.image(p["image_url"], use_container_width=True)
        st.markdown(f"""
        <div class="product-info">
            <b>{p["name"]}</b> <span style="float:right"><b>${p["price"]}</b></span><br>
            <small>{p["desc"]}</small><br>
            ⭐ 4.5 | Stock: {p["stock"]}
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