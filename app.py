import streamlit as st
import json
import hashlib

# ==========================================
# VEYRA
# ==========================================

st.set_page_config(
    page_title="Veyra",
    page_icon="🛍️",
    layout="wide"
)

# ==========================================
# CONFIG
# ==========================================

OWNER_USERNAME = "owner"
OWNER_PASSWORD = "veyra123"

# ==========================================
# SESSION STATE
# ==========================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "is_owner" not in st.session_state:
    st.session_state.is_owner = False

if "page" not in st.session_state:
    st.session_state.page = "Store"

if "cart" not in st.session_state:
    st.session_state.cart = {}

if "accounts" not in st.session_state:
    st.session_state.accounts = {}


# ==========================================
# PRODUCTS
# ==========================================

def load_products():

    try:
        with open("products.json", "r", encoding="utf-8") as file:
            return json.load(file)

    except:
        return []


products = load_products()


# ==========================================
# PASSWORD HASH
# ==========================================

def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()


# ==========================================
# CART FUNCTIONS
# ==========================================

def add_to_cart(product_id):

    if product_id in st.session_state.cart:

        st.session_state.cart[product_id] += 1

    else:

        st.session_state.cart[product_id] = 1


def remove_from_cart(product_id):

    if product_id in st.session_state.cart:

        st.session_state.cart[product_id] -= 1

        if st.session_state.cart[product_id] <= 0:

            del st.session_state.cart[product_id]


def cart_total():

    total = 0

    for product in products:

        product_id = product["id"]

        if product_id in st.session_state.cart:

            quantity = st.session_state.cart[product_id]

            total += product["price"] * quantity

    return total


# ==========================================
# LOGIN PAGE
# ==========================================

def login_page():

    st.title("🛍️ Welcome to Veyra")

    st.write(
        "Login or create an account to continue."
    )

    tab1, tab2 = st.tabs(
        ["🔐 Login", "📝 Create Account"]
    )

    # ======================================
    # LOGIN
    # ======================================

    with tab1:

        username = st.text_input(
            "Username",
            key="login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            use_container_width=True
        ):

            # OWNER LOGIN

            if (
                username == OWNER_USERNAME
                and password == OWNER_PASSWORD
            ):

                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.is_owner = True
                st.session_state.page = "Store"

                st.success(
                    "Owner login successful!"
                )

                st.rerun()

            # CUSTOMER LOGIN

            elif username in st.session_state.accounts:

                saved_password = (
                    st.session_state.accounts[username]
                )

                if (
                    saved_password
                    == hash_password(password)
                ):

                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.is_owner = False
                    st.session_state.page = "Store"

                    st.success(
                        "Login successful!"
                    )

                    st.rerun()

                else:

                    st.error(
                        "Incorrect password."
                    )

            else:

                st.error(
                    "Account not found."
                )

    # ======================================
    # CREATE ACCOUNT
    # ======================================

    with tab2:

        new_username = st.text_input(
            "Choose a username",
            key="new_username"
        )

        new_password = st.text_input(
            "Choose a password",
            type="password",
            key="new_password"
        )

        confirm_password = st.text_input(
            "Confirm password",
            type="password",
            key="confirm_password"
        )

        if st.button(
            "Create Account",
            use_container_width=True
        ):

            if not new_username or not new_password:

                st.warning(
                    "Please fill in all fields."
                )

            elif new_password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            elif new_username == OWNER_USERNAME:

                st.error(
                    "That username is reserved."
                )

            elif new_username in st.session_state.accounts:

                st.error(
                    "Username already exists."
                )

            else:

                st.session_state.accounts[
                    new_username
                ] = hash_password(new_password)

                st.success(
                    "Account created! You can now log in."
                )


# ==========================================
# STOP HERE IF NOT LOGGED IN
# ==========================================

if not st.session_state.logged_in:

    login_page()

    st.stop()


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("🛍️ VEYRA")

st.sidebar.write(
    f"👋 Welcome, **{st.session_state.username}**"
)

st.sidebar.divider()


if st.sidebar.button(
    "🏠 Store",
    use_container_width=True
):

    st.session_state.page = "Store"


if st.sidebar.button(
    f"🛒 Cart ({sum(st.session_state.cart.values())})",
    use_container_width=True
):

    st.session_state.page = "Cart"


# OWNER DASHBOARD

if st.session_state.is_owner:

    if st.sidebar.button(
        "⚙️ Owner Dashboard",
        use_container_width=True
    ):

        st.session_state.page = "Owner"


st.sidebar.divider()


if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):

    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.is_owner = False
    st.session_state.page = "Store"
    st.session_state.cart = {}

    st.rerun()


# ==========================================
# STORE
# ==========================================

if st.session_state.page == "Store":

    st.title("🛍️ Veyra")

    st.write(
        "Shop. Discover. Enjoy."
    )

    search = st.text_input(
        "🔎 Search products",
        placeholder="Search for a product..."
    )

    categories = ["All"]

    for product in products:

        if product["category"] not in categories:

            categories.append(
                product["category"]
            )

    category = st.selectbox(
        "Category",
        categories
    )

    filtered_products = products

    if search:

        filtered_products = [
            p for p in filtered_products
            if search.lower()
            in p["name"].lower()
        ]

    if category != "All":

        filtered_products = [
            p for p in filtered_products
            if p["category"] == category
        ]

    st.divider()

    columns = st.columns(3)

    for index, product in enumerate(
        filtered_products
    ):

        with columns[index % 3]:

            st.image(
                product["image"],
                use_container_width=True
            )

            st.subheader(
                product["name"]
            )

            st.write(
                f"### ₦{product['price']:,.0f}"
            )

            st.caption(
                product["category"]
            )

            if st.button(
                "🛒 Add to Cart",
                key=f"add_{product['id']}",
                use_container_width=True
            ):

                add_to_cart(
                    product["id"]
                )

                st.success(
                    "Added to cart!"
                )


# ==========================================
# CART
# ==========================================

elif st.session_state.page == "Cart":

    st.title("🛒 Your Cart")

    if not st.session_state.cart:

        st.info(
            "Your cart is empty."
        )

    else:

        for product in products:

            product_id = product["id"]

            if product_id in st.session_state.cart:

                quantity = (
                    st.session_state.cart[
                        product_id
                    ]
                )

                col1, col2, col3 = st.columns(
                    [2, 4, 2]
                )

                with col1:

                    st.image(
                        product["image"],
                        width=120
                    )

                with col2:

                    st.write(
                        f"### {product['name']}"
                    )

                    st.write(
                        f"₦{product['price']:,.0f}"
                    )

                    st.write(
                        f"Quantity: {quantity}"
                    )

                with col3:

                    if st.button(
                        "➕",
                        key=f"plus_{product_id}"
                    ):

                        add_to_cart(product_id)
                        st.rerun()

                    if st.button(
                        "➖",
                        key=f"minus_{product_id}"
                    ):

                        remove_from_cart(product_id)
                        st.rerun()

                st.divider()

        st.subheader(
            f"Total: ₦{cart_total():,.0f}"
        )

        if st.button(
            "💳 Checkout",
            use_container_width=True
        ):

            st.info(
                "Payment system will be connected next."
            )


# ==========================================
# OWNER DASHBOARD
# ==========================================

elif st.session_state.page == "Owner":

    if not st.session_state.is_owner:

        st.error(
            "You do not have permission to access this page."
        )

        st.stop()

    st.title("⚙️ Veyra Owner Dashboard")

    st.write(
        "Manage your products."
    )

    st.divider()

    st.subheader("📦 Products")

    for product in products:

        col1, col2, col3 = st.columns(
            [2, 5, 2]
        )

        with col1:

            st.image(
                product["image"],
                width=100
            )

        with col2:

            st.write(
                f"**{product['name']}**"
            )

            st.write(
                f"₦{product['price']:,.0f}"
            )

        with col3:

            st.write(
                product["category"]
            )

    st.divider()

    st.subheader(
        "➕ Add New Product"
    )

    with st.form("new_product"):

        name = st.text_input(
            "Product name"
        )

        price = st.number_input(
            "Price",
            min_value=0,
            step=100
        )

        category = st.text_input(
            "Category"
        )

        image = st.text_input(
            "Image URL"
        )

        submit = st.form_submit_button(
            "Add Product"
        )

        if submit:

            if (
                name
                and price
                and category
                and image
            ):

                new_id = max(
                    [p["id"] for p in products],
                    default=0
                ) + 1

                new_product = {
                    "id": new_id,
                    "name": name,
                    "price": price,
                    "category": category,
                    "image": image
                }

                products.append(
                    new_product
                )

                with open(
                    "products.json",
                    "w",
                    encoding="utf-8"
                ) as file:

                    json.dump(
                        products,
                        file,
                        indent=2
                    )

                st.success(
                    "Product added!"
                )

                st.rerun()

            else:

                st.warning(
                    "Fill in every field."
                )