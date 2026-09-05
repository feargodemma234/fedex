import streamlit as st
import random

st.set_page_config(page_title="FEDEX", page_icon="📦", layout="wide")

# DARK YELLOW THEME
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
img {border-radius: 15px 15px 0 0;} /* round top of images */
</style>
""", unsafe_allow_html=True)

# SESSION STATE
if "cart" not in st.session_state: st.session_state.cart = []
if "search" not in st.session_state: st.session_state.search = ""
if "selected_cat" not in st.session_state: st.session_state.selected_cat = "All"
if "load_count" not in st.session_state: st.session_state.load_count = 20

# GENERATE 25 PRODUCTS PER CATEGORY WITH WORKING IMAGES
@st.cache_data
def get_products():
    products = []
    id_counter = 1
    
    catalog = {
        "Women": [
            ("Dress", 10), ("Top", 11), ("Skirt", 12), ("Jeans", 13), ("Blazer", 14), 
            ("Jumpsuit", 15), ("Blouse", 16), ("Coat", 17), ("Cardigan", 18), ("Gown", 19)
        ],
        "Men": [
            ("T-Shirt", 20), ("Shirt", 21), ("Jeans", 22), ("Jacket", 23), ("Hoodie", 24), 
            ("Pants", 25), ("Sweater", 26), ("Shorts", 27), ("Suit", 28), ("Polo", 29)
        ],
        "Kids": [
            ("Hoodie", 30), ("Jeans", 31), ("Tee", 32), ("Dress", 33), ("Jacket", 34), 
            ("Shorts", 35), ("Sweater", 36), ("Set", 37), ("Joggers", 38), ("Onesie", 39)
        ],
        "Footwear": [
            ("Sneakers", 40), ("Boots", 41), ("Sandals", 42), ("Heels", 43), ("Loafers", 44), 
            ("Running Shoes", 45), ("Slides", 46), ("Flats", 47), ("Crocs", 48), ("Wedges", 49)
        ]
    }
    
    for category, items in catalog.items():
        for i in range(25):
            item_name, base_id = random.choice(items)
            
            # PICSUM ALWAYS WORKS. base_id + i makes it unique but still looks like fashion
            image_url = f"https://picsum.photos/seed/{base_id+i}/400/400"
            
            name = f"{category} {item_name} #{i+1}"
            products.append({
                "id": id_counter,
                "name": name,
                "desc": f"Premium {item_name.lower()}",
                "price": random.randint(40, 250),
                "stock": random.randint(1, 30),
                "image_url": image_url,
                "category": category
            })
            id_counter += 1
    return products

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
            st.session_state.load_count = 20
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# SEARCH BAR
st.session_state.search = st.text_input("Search", placeholder="Search 100 products...", label_visibility="collapsed")

# FILTER PRODUCTS
filtered = products
if st.session_state.selected_cat!= "All":
    filtered = [p for p in filtered if p["category"] == st.session_state.selected_cat]
if st.session_state.search:
    filtered = [p for p in filtered if st.session_state.search.lower() in p["name"].lower()]

st.write(f"**{len(filtered)} Products - {st.session_state.selected_cat}**")

# SHOW PRODUCTS WITH LOAD MORE
cols = st.columns(2)
for i, p in enumerate(filtered[:st.session_state.load_count]):
    with cols[i % 2]:
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        st.image(p["image_url"], use_container_width=True) # THIS WILL NOW LOAD
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

# LOAD MORE BUTTON
if st.session_state.load_count < len(filtered):
    if st.button(f"Load More {min(20, len(filtered)-st.session_state.load_count)} Products"):
        st.session_state.load_count += 20
        st.rerun()

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