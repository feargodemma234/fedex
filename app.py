import streamlit as st

st.set_page_config(page_title="CLOSE FOODS & STYLE", page_icon="🍕", layout="wide")

# DARK YELLOW LUXURY THEME
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300&display=swap');
.stApp {background-color: #B8860B;} /* DARK YELLOW */
h1, h2, h3 {font-family: 'Playfair Display', serif; color: #000000;}
p, label {font-family: 'Inter', sans-serif; color: #1A1A1A;}
.hero {text-align: center; padding: 80px 20px;}
.hero h1 {font-size: 60px; letter-spacing: 3px;}
.hero h2 {font-size: 20px; color: #333333; font-weight: 300;}
.card {background: #DAA520; border-radius: 15px; padding: 15px; border: 1px solid #000;}
.stButton>button {background-color: #000000; color: #FFD700; font-weight: bold; border-radius: 8px; border: 2px solid #FFD700; padding: 10px 25px; width: 100%;}
.orange-bar {background: #000000; height: 4px; width: 60px; margin: 20px auto;}
.stSelectbox>div>div {background-color: #FFD700; color: black;}
</style>
""", unsafe_allow_html=True)

# SESSION STATE FOR TAB
if "tab" not in st.session_state: st.session_state.tab = "Foods"

# HEADER/NAV WITH TABS
col1, col2, col3 = st.columns([2,4,2])
with col2:
    t1, t2 = st.columns(2)
    with t1:
        if st.button("🍽️ FOODS", key="food_tab", use_container_width=True): st.session_state.tab = "Foods"; st.rerun()
    with t2:
        if st.button("👕 STYLE", key="style_tab", use_container_width=True): st.session_state.tab = "Style"; st.rerun()

# HERO SECTION
st.markdown(f"""
<div class="hero">
    <h2>CLOSE FOODS & STYLE</h2>
    <h1>{'STONE-FIRED & GRILLED' if st.session_state.tab=='Foods' else 'TAILORED & STYLED'}</h1>
    <div class="orange-bar"></div>
</div>
""", unsafe_allow_html=True)

if st.session_state.tab == "Foods":
    st.image("https://images.unsplash.com/photo-1513104890138-7c749659a591?q=80&w=2070", use_container_width=True)

    # SIGNATURE DISHES
    st.markdown("<h2 style='text-align:center; margin-top: 60px;'>Signature Dishes</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    dishes = [
        ("Suya Pizza", "Spicy beef suya, onions, peppers", "$18", "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?q=80&w=800"),
        ("Jollof Rice Bowl", "Smoky jollof, grilled chicken", "$16", "https://images.unsplash.com/photo-1606756790138-261d2b9e5d9c?q=80&w=800"),
        ("Pepper Soup Ramen", "Goat pepper soup broth", "$20", "https://images.unsplash.com/photo-1625938142814-2d9fcfc6b8a9?q=80&w=800"),
    ]
    for i, (name, desc, price, img) in enumerate(dishes):
        with [col1, col2, col3][i]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.image(img, use_container_width=True)
            st.write(f"**{name}**")
            st.write(desc)
            st.write(price)
            st.button("Add to Cart", key=f"food_{i}")
            st.markdown('</div>', unsafe_allow_html=True)

    # BUILD YOUR OWN
    st.markdown("<h2 style='text-align:center; margin-top: 80px;'>// 02. Build Your Close Plate</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns([1,1])
    with col1:
        base = st.selectbox("Choose Base", ["Jollof Rice", "Fried Rice", "Yam", "Plantain"])
        protein = st.selectbox("Choose Protein", ["Chicken", "Beef", "Goat", "Fish"])
        st.button("Add to Plate - $14")
    with col2:
        st.image("https://images.unsplash.com/photo-1604908177453-7462950a6a3b?q=80&w=800", use_container_width=True)

else: # STYLE TAB
    st.image("https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?q=80&w=2070", use_container_width=True)
    
    # SIGNATURE PIECES
    st.markdown("<h2 style='text-align:center; margin-top: 60px;'>Signature Pieces</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    clothes = [
        ("Ankara Shirt", "Premium African print", "$45", "https://images.unsplash.com/photo-1618354691323-2e9c1e5b5a2a?q=80&w=800"),
        ("Street Hoodie", "CLOSE embroidered", "$60", "https://images.unsplash.com/photo-1556821840-3a63f95609a7?q=80&w=800"),
        ("Cargo Pants", "Tactical fit", "$55", "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?q=80&w=800"),
    ]
    for i, (name, desc, price, img) in enumerate(clothes):
        with [col1, col2, col3][i]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.image(img, use_container_width=True)
            st.write(f"**{name}**")
            st.write(desc)
            st.write(price)
            st.button("Add to Bag", key=f"cloth_{i}")
            st.markdown('</div>', unsafe_allow_html=True)

    # BUILD YOUR FIT
    st.markdown("<h2 style='text-align:center; margin-top: 80px;'>// 02. Build Your Fit</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns([1,1])
    with col1:
        top = st.selectbox("Choose Top", ["T-Shirt", "Shirt", "Hoodie"])
        bottom = st.selectbox("Choose Bottom", ["Jeans", "Cargo", "Shorts"])
        st.button("Add to Bag - $90")
    with col2:
        st.image("https://images.unsplash.com/photo-1529139573311-1b8ea7c8c1b2?q=80&w=800", use_container_width=True)

# THE CRAFT SECTION - NO LOCATION
st.markdown("<h2 style='text-align:center; margin-top: 80px;'>THE CRAFT</h2>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
col1.metric("Ingredients", "100% Fresh")
col2.metric("Fabrics", "Premium Cotton")
col3.metric("Cook Time", "7 Minutes")

# STORY - NO LOCATION MENTIONED
st.markdown("<h2 style='text-align:center; margin-top: 80px;'>// 03. THE STORY</h2>", unsafe_allow_html=True)
st.write("We feed you. We dress you. CLOSE brings flavor and fashion together.")

st.markdown("<h1 style='text-align:center; margin-top: 60px;'>ORDER NOW</h1>", unsafe_allow_html=True)