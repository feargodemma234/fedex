import streamlit as st
import random

st.set_page_config(page_title="FEDEX", page_icon="📦", layout="wide")

st.markdown("""
<style>
.stApp {background-color: #B8860B;}
h1, h2, h3, h4, p, label {color: #FFFFFF;}
.categories-container {display: flex; overflow-x: auto; gap: 10px; padding: 10px 5px; scrollbar-width: none;}
.categories-container::-webkit-scrollbar {display: none;}
.product-card {background: linear-gradient(135deg, #DAA520 0%, #B8860B 100%); border-radius: 20px; margin-bottom: 15px; overflow: hidden;}
.product-info {background: rgba(0,0,0,0.3); border-radius: 15px; padding: 10px; margin: 8px; color: white;}
.stButton>button {background-color: #000; color: #FFD700; font-weight: bold; border-radius: 12px; border: 2px solid #FFD700; width: 100%;}
.stTextInput>div>div>input {background-color: #FFD700; color: black; border-radius: 20px; border: 1px solid black;}
img {border-radius: 15px 15px 0 0;}
</style>
""", unsafe_allow_html=True)

if "cart" not in st.session_state: st.session_state.cart = []
if "selected_cat" not in st.session_state: st.session_state.selected_cat = "All"
if "load_count" not in st.session_state: st.session_state.load_count = 20

# YOUR UPLOADED + GENERATED IMAGES
WOMEN_IMG = "https://picsum.photos/seed/women_dress/400/400" # Generated
MEN_IMG = "/mnt/data/wa_image_1383163712576310337_0" # Varsity Jacket
KIDS_IMG = "/mnt/data/wa_image_1383163712576310337_2" # Kids tracksuit
FOOTWEAR_IMG = "/mnt/data/wa_image_1383163712576310337_1" # Knit set

@st.cache_data
def get_products():
    products = []
    id_counter = 1
    
    # 25 products per category. First 1 uses your real image, rest use picsum
    for i in range(25):
        products.append({"id": id_counter, "name": f"Women Dress #{i+1}", "desc": "Premium dress", "price": random.randint(80, 200), "stock": random.randint(1, 30), "image_url": WOMEN_IMG if i==0 else f"https://picsum.photos/seed/w{i}/400/400", "category": "Women"})
        id_counter += 1
    
    for i in range(25):
        products.append({"id": id_counter, "name": f"Men Jacket #{i+1}", "desc": "Premium jacket", "price": random.randint(80, 200), "stock": random.randint(1, 30), "image_url": MEN_IMG if i==0 else f"https://picsum.photos/seed/m{i}/400/400", "category": "Men"})
        id_counter += 1

    for i in range(25):
        products.append({"id": id_counter, "name": f"Kids Set #{i+1}", "desc": "Premium kids wear", "price": random.randint(40, 120), "stock": random.randint(1, 30), "image_url": KIDS_IMG if i==0 else f"https://picsum.photos/seed/k{i}/400/400", "category": "Kids"})
        id_counter += 1

    for i in range(25):
        products.append({"id": id_counter, "name": f"Footwear Set #{i+1}", "desc": "Premium footwear", "price": random.randint(60, 180), "stock": random.randint(1, 30), "image_url": FOOTWEAR_IMG if i==0 else f"https://picsum.photos/seed/f{i}/400/400", "category": "Footwear"})
        id_counter += 1
        
    return products

products = get_products()

# HEADER
col1, col2 = st.columns([6,1])
with col1: st.title("FEDEX")
with col2: st.metric("Cart", len(st.session_state.cart))

st.subheader("Discover")

# CATEGORIES
st.write("**Categories**")
categories = ["All", "Women", "Men", "Kids", "Footwear"]
st.markdown('<div class="categories-container">', unsafe_allow_html=True)
cols = st.columns(len(categories))
for i, cat in enumerate(categories):
    with cols[i]:
        if st.button(cat, key=f"cat_{cat}", use_container_width=True):
            st.session_state.selected_cat = cat
            st.session_state.load_count = 20
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# SEARCH + PRODUCTS
st.session_state.search = st.text_input("Search", placeholder="Search 100 products...", label_visibility="collapsed")
filtered = products
if st.session_state.selected_cat!= "All":
    filtered = [p for p in filtered if p["category"] == st.session_state.selected_cat]
if st.session_state.search:
    filtered = [p for p in filtered if st.session_state.search.lower() in p["name"].lower()]

st.write(f"**{len(filtered)} Products - {st.session_state.selected_cat}**")

cols = st.columns(2)
for i, p in enumerate(filtered[:st.session_state.load_count]):
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

if st.session_state.load_count < len(filtered):
    if st.button(f"Load More {min(20, len(filtered)-st.session_state.load_count)} Products"):
        st.session_state.load_count += 20
        st.rerun()

with st.sidebar:
    st.header("🛒 Your Cart")
    if len(st.session_state.cart) == 0: st.write("Cart is empty")
    else:
        total = sum(item['price'] for item in st.session_state.cart)
        for item in st.session_state.cart: st.write(f"- {item['name']} : ${item['price']}")
        st.subheader(f"Total: ${total}")
        if st.button("Checkout"):
            st.success("Order placed!"); st.session_state.cart = []