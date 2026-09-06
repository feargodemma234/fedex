import streamlit as st

st.set_page_config(page_title="CLOSE FOODS & STYLE", page_icon="🍕", layout="wide")

# DARK YELLOW LUXURY THEME
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300&display=swap');
.stApp {background-color: #B8860B;}
h1, h2, h3 {font-family: 'Playfair Display', serif; color: #000;}
p, label {font-family: 'Inter', sans-serif; color: #1A1A1A;}
.hero {text-align: center; padding: 80px 20px;}
.hero h1 {font-size: 60px; letter-spacing: 3px;}
.card {background: #DAA520; border-radius: 15px; padding: 15px; border: 1px solid #000; margin-bottom: 15px;}
.stButton>button {background-color: #000; color: #FFD700; font-weight: bold; border-radius: 8px; border: 2px solid #FFD700; width: 100%;}
.orange-bar {background: #000; height: 4px; width: 60px; margin: 20px auto;}
img {border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

if "tab" not in st.session_state: st.session_state.tab = "Foods"

# HEADER/NAV
col1, col2, col3 = st.columns([2,4,2])
with col2:
    t1, t2 = st.columns(2)
    with t1:
        if st.button("🍽️ FOODS", key="food_tab", use_container_width=True): st.session_state.tab = "Foods"; st.rerun()
    with t2:
        if st.button("👕 STYLE", key="style_tab", use_container_width=True): st.session_state.tab = "Style"; st.rerun()

# HERO
st.markdown(f"""
<div class="hero">
    <h2>CLOSE FOODS & STYLE</h2>
    <h1>{'STONE-FIRED PIZZA' if st.session_state.tab=='Foods' else 'TAILORED & STYLED'}</h1>
    <div class="orange-bar"></div>
</div>
""", unsafe_allow_html=True)

if st.session_state.tab == "Foods":
    st.image("https://images.pexels.com/photos/825661/pexels-photo-825661.jpeg?auto=compress&cs=tinysrgb&w=1200", use_container_width=True)

    # REAL PIZZA DISHES
    st.markdown("<h2 style='text-align:center; margin-top: 60px;'>Signature Pizzas</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    pizzas = [
        ("Suya Pizza", "Spicy suya beef, onions, peppers, mozzarella", "$18", "https://images.pexels.com/photos/2147491/pexels-photo-2147491.jpeg?auto=compress&cs=tinysrgb&w=400"),
        ("Pepperoni Classic", "Double pepperoni, cheese, tomato sauce", "$16", "https://images.pexels.com/photos/1566837/pexels-photo-1566837.jpeg?auto=compress&cs=tinysrgb&w=400"),
        ("BBQ Chicken", "Grilled chicken, BBQ sauce, red onions", "$20", "https://images.pexels.com/photos/2619967/pexels-photo-2619967.jpeg?auto=compress&cs=tinysrgb&w=400"),
    ]
    for i, (name, desc, price, img) in enumerate(pizzas):
        with [col1, col2, col3][i]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.image(img, use_container_width=True)
            st.write(f"**{name}**")
            st.write(desc)
            st.write(price)
            st.button("Add to Cart", key=f"food_{i}")
            st.markdown('</div>', unsafe_allow_html=True)

    # BUILD YOUR OWN - REMOVED WEIRD IMAGE, ADDED CLOTHES IMAGE
    st.markdown("<h2 style='text-align:center; margin-top: 80px;'>// 02. Build Your Pizza</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns([1,1])
    with col1:
        crust = st.selectbox("Choose Crust", ["Thin Crust", "Thick Crust", "Stuffed Crust"])
        sauce = st.selectbox("Choose Sauce", ["Tomato", "BBQ", "Pesto", "White Garlic"])
        toppings = st.multiselect("Toppings", ["Pepperoni", "Chicken", "Suya Beef", "Mushroom", "Onions", "Peppers"])
        st.button("Add Pizza - $14")
    with col2:
        # REPLACED THE BAD IMAGE WITH A CLOTHES IMAGE
        st.image("/mnt/data/wa_image_2786539205611050647", use_container_width=True) # YOUR UPLOADED CLOTHES
        st.caption("Style while you wait 👕")

else: # STYLE TAB
    st.image("https://images.pexels.com/photos/298863/pexels-photo-298863.jpeg?auto=compress&cs=tinysrgb&w=1200", use_container_width=True)

    # CLOTHES
    st.markdown("<h2 style='text-align:center; margin-top: 60px;'>Signature Pieces</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    clothes = [
        ("Ankara Shirt", "Premium African print", "$45", "/mnt/data/wa_image_2786539205611050647"), # YOUR IMAGE
        ("Street Hoodie", "CLOSE embroidered", "$60", "https://images.pexels.com/photos/4066292/pexels-photo-4066292.jpeg?auto=compress&cs=tinysrgb&w=400"),
        ("Cargo Pants", "Tactical fit", "$55", "https://images.pexels.com/photos/1124465/pexels-photo-1124465.jpeg?auto=compress&cs=tinysrgb&w=400"),
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

# THE CRAFT
st.markdown("<h2 style='text-align:center; margin-top: 80px;'>THE CRAFT</h2>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
col1.metric("Oven Temp", "485°C")
col2.metric("Cook Time", "90 Seconds")
col3.metric("Fabrics", "Premium Cotton")

st.markdown("<h2 style='text-align:center; margin-top: 80px;'>// 03. THE STORY</h2>", unsafe_allow_html=True)
st.write("Stone-fired pizza. Tailored style. CLOSE brings flavor and fashion together.")

st.markdown("<h1 style='text-align:center; margin-top: 60px;'>ORDER NOW</h1>", unsafe_allow_html=True)