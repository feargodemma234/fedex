import streamlit as st

st.set_page_config(page_title="FEDEX", page_icon="📦", layout="wide")

# DARK YELLOW THEME
st.markdown("""
<style>
.stApp {background-color: #B8860B;} /* Dark Goldenrod / Dark Yellow */
h1, h2, h3, h4, p, label {color: #FFFFFF;} /* White text for contrast */

/* Product Card - Darker Yellow/Brown */
.product-card {
    background: linear-gradient(135deg, #DAA520 0%, #B8860B 100%);
    border-radius: 20px;
    margin-bottom: 15px;
    overflow: hidden;
}
.product-info {
    background: rgba(0,0,0,0.3); /* Dark overlay so text pops */
    border-radius: 15px;
    padding: 10px;
    margin: 8px;
    color: white;
}

/* HORIZONTAL CATEGORIES */
.categories-wrapper {
    display: flex;
    gap: 15px;
    overflow-x: auto;
    padding: 10px 0px;
}
.category-circle {
    text-align: center;
    min-width: 80px;
}
.category-circle img {
    border-radius: 50%;
    border: 3px solid #FFD700; /* Gold border */
}
.category-circle p {font-size: 12px; font-weight: 500; color: white;}

.stButton>button {
    background-color: #000000; /* Black button for contrast */
    color: #FFD700; /* Gold text */
    font-weight: bold; 
    border-radius: 12px; 
    border: 2px solid #FFD700;
    width: 100%;
}
.stTextInput>div>div>input {background-color: #FFD700; color: black; border-radius: 20px; border: 1px solid black;}
.stMetric {background-color: rgba(0,0,0,0.2); padding: 5px; border-radius: 10px;}
/* Hide scrollbar */
.categories-wrapper::-webkit-scrollbar {display: none;}
</style>
""", unsafe_allow_html=True)

# SESSION STATE
if "cart" not in st.session_state: st.session_state.cart = []
if "search" not in st.session_state: st.session_state.search = ""
if "selected_cat" not in st.session_state: st.session_state.selected_cat = "All"

# FAKE PRODUCTS
def get_products():
    return [
        {"id": 1, "name": "Berrylush", "desc": "Casual Cottonwear", "price": 120, "stock": 12, "image_url": "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?q=80&w=800", "category": "Women"},
        {"id": 2, "name": "Twinkle", "desc": "Bodycon with stripes", "price": 150, "stock": 8, "image_url": "https://images.unsplash.com/photo-1496747611176-843222e1e57c?q=80&w=800", "category": "Women"},
        {"id": 3, "name": "Street Tee", "desc": "Oversized T-shirt", "price": 110, "stock": 20, "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?q=80&w=800", "category": "Men"},
        {"id": 4, "name": "Blazers", "desc": "Casual Cottonwear", "price": 130, "stock": 5, "image_url": "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?q=80&w=800", "category": "Women"},
        {"id": 5, "name": "Kids Hoodie", "desc": "Cotton Hoodie", "price": 80, "stock": 15, "image_url": "https://images.unsplash.com/photo-1620799139517-2a76f4a2a01d?q=80&w=800", "category": "Kids"},
        {"id": 6, "name": "Running Shoes", "desc": "Sport Shoes", "price": 200, "stock": 10, "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=800", "category": "Footwear"},
    ]

products = get_products()

# HEADER
col1, col2 = st.columns([6,1])
with col1: st.title("FEDEX")
with col2: st.metric("Cart", len(st.session_state.cart))

st.subheader("Discover")
st.write("Explore Our New Collections")

# HORIZONTAL CATEGORIES
st.write("**Categories**")
categories = {
    "All": "https://via.placeholder.com/80/FFD700/000?text=All",
    "Women": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?q=80&w=200",
    "Men": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=200",
    "Kids": "https://images.unsplash.com/photo-1519345182560-3f2917c472ef?q=80&w=200",
    "Footwear": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=200"
}

st.markdown('<div class="categories-wrapper">', unsafe_allow_html=True)
cols = st.columns(len(categories))
for i, (cat, img) in enumerate(categories.items()):
    with cols[i]:
        st.markdown('<div class="category-circle">', unsafe_allow_html=True)
        if st.button(cat, key=cat, use_container_width=True):
            st.session_state.selected_cat = cat
        st.image(img, width=70)
        st.write(cat)
        st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# SEARCH BAR
st.session_state.search = st.text_input("Search", placeholder="Search for products", label_visibility="collapsed")

# PRODUCTS GRID - 2 PER ROW
st.write("**New Arrivals**")
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