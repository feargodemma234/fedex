import streamlit as st
from supabase import create_client, Client

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Veyra",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# SUPABASE CONNECTION
# ============================================================

@st.cache_resource
def get_supabase() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


supabase = get_supabase()

# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "page": "Store",
    "cart": {},
    "user": None,
    "profile": None,
    "message": "",
    "message_type": "info"
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# HELPERS
# ============================================================

def show_message():
    if st.session_state.message:
        if st.session_state.message_type == "success":
            st.success(st.session_state.message)
        elif st.session_state.message_type == "error":
            st.error(st.session_state.message)
        elif st.session_state.message_type == "warning":
            st.warning(st.session_state.message)
        else:
            st.info(st.session_state.message)

        st.session_state.message = ""


def get_current_user():
    try:
        response = supabase.auth.get_user()

        if response and response.user:
            return response.user

    except Exception:
        pass

    return None


def load_profile(user_id):
    try:
        response = (
            supabase
            .table("profiles")
            .select("*")
            .eq("id", user_id)
            .maybe_single()
            .execute()
        )

        return response.data

    except Exception:
        return None


def get_products():
    try:
        response = (
            supabase
            .table("products")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

        return response.data or []

    except Exception as error:
        st.error(f"Could not load products: {error}")
        return []


def money(amount):
    return f"₦{float(amount):,.2f}"


def cart_count():
    return sum(st.session_state.cart.values())


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


def calculate_cart_total(products):
    total = 0

    for product in products:
        product_id = product["id"]

        if product_id in st.session_state.cart:
            quantity = st.session_state.cart[product_id]
            total += float(product["price"]) * quantity

    return total


# ============================================================
# AUTHENTICATION
# ============================================================

def signup_page():

    st.title("🛍️ Create your Veyra account")

    st.write(
        "Create an account to shop on Veyra."
    )

    with st.form("signup_form"):

        email = st.text_input(
            "📧 Email",
            placeholder="you@example.com"
        )

        password = st.text_input(
            "🔑 Password",
            type="password"
        )

        confirm_password = st.text_input(
            "🔑 Confirm password",
            type="password"
        )

        submitted = st.form_submit_button(
            "Create Account",
            use_container_width=True
        )

        if submitted:

            if not email or not password:

                st.error(
                    "Please enter your email and password."
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            elif len(password) < 6:

                st.error(
                    "Password must be at least 6 characters."
                )

            else:

                try:

                    response = supabase.auth.sign_up({
                        "email": email,
                        "password": password
                    })

                    if response.user:

                        st.success(
                            "Account created! "
                            "Check your email and press the confirmation link."
                        )

                        st.info(
                            "After confirming your email, "
                            "return to Veyra and log in."
                        )

                except Exception as error:

                    st.error(
                        f"Signup failed: {error}"
                    )


def login_page():

    st.title("🛍️ Welcome to Veyra")

    st.write(
        "Login to your Veyra account."
    )

    login_tab, signup_tab = st.tabs(
        ["🔐 Login", "📝 Create Account"]
    )

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    with login_tab:

        with st.form("login_form"):

            email = st.text_input(
                "📧 Email"
            )

            password = st.text_input(
                "🔑 Password",
                type="password"
            )

            submitted = st.form_submit_button(
                "Login",
                use_container_width=True
            )

            if submitted:

                if not email or not password:

                    st.error(
                        "Enter your email and password."
                    )

                else:

                    try:

                        response = (
                            supabase
                            .auth
                            .sign_in_with_password({
                                "email": email,
                                "password": password
                            })
                        )

                        if response.user:

                            st.session_state.user = response.user

                            st.session_state.profile = (
                                load_profile(
                                    response.user.id
                                )
                            )

                            st.session_state.page = "Store"

                            st.success(
                                "Login successful!"
                            )

                            st.rerun()

                    except Exception as error:

                        error_text = str(error).lower()

                        if (
                            "email not confirmed"
                            in error_text
                        ):

                            st.warning(
                                "Please confirm your email "
                                "before logging in."
                            )

                        else:

                            st.error(
                                "Login failed. "
                                "Check your email and password."
                            )

    # --------------------------------------------------------
    # SIGNUP
    # --------------------------------------------------------

    with signup_tab:
        signup_page()


# ============================================================
# GET CURRENT SESSION
# ============================================================

if st.session_state.user is None:

    current_user = get_current_user()

    if current_user:

        st.session_state.user = current_user

        st.session_state.profile = (
            load_profile(current_user.id)
        )


# ============================================================
# LOGIN CHECK
# ============================================================

if st.session_state.user is None:

    login_page()

    st.stop()


# ============================================================
# USER / ROLE
# ============================================================

user = st.session_state.user
profile = st.session_state.profile or {}

user_role = profile.get("role", "customer")


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🛍️ VEYRA")

st.sidebar.caption(
    user.email
)

st.sidebar.divider()


if st.sidebar.button(
    "🏠 Store",
    use_container_width=True
):

    st.session_state.page = "Store"
    st.rerun()


if st.sidebar.button(
    f"🛒 Cart ({cart_count()})",
    use_container_width=True
):

    st.session_state.page = "Cart"
    st.rerun()


if st.sidebar.button(
    "📦 My Orders",
    use_container_width=True
):

    st.session_state.page = "Orders"
    st.rerun()


# OWNER MENU

if user_role == "owner":

    st.sidebar.divider()

    if st.sidebar.button(
        "⚙️ Owner Dashboard",
        use_container_width=True
    ):

        st.session_state.page = "Owner"
        st.rerun()

    if st.sidebar.button(
        "📈 Sales Analytics",
        use_container_width=True
    ):

        st.session_state.page = "Analytics"
        st.rerun()


st.sidebar.divider()


if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):

    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.user = None
    st.session_state.profile = None
    st.session_state.cart = {}
    st.session_state.page = "Store"

    st.rerun()


# ============================================================
# LOAD PRODUCTS
# ============================================================

products = get_products()


# ============================================================
# STORE
# ============================================================

if st.session_state.page == "Store":

    st.title("🛍️ Veyra")

    st.write(
        "Shop. Discover. Enjoy."
    )

    show_message()

    # SEARCH

    search = st.text_input(
        "🔎 Search products",
        placeholder="Search for a product..."
    )

    # CATEGORIES

    categories = ["All"]

    for product in products:

        category = product.get(
            "category",
            "Other"
        )

        if category not in categories:
            categories.append(category)

    selected_category = st.selectbox(
        "Category",
        categories
    )

    # FILTER

    filtered_products = products

    if search:

        filtered_products = [
            product
            for product in filtered_products
            if search.lower()
            in product["name"].lower()
        ]

    if selected_category != "All":

        filtered_products = [
            product
            for product in filtered_products
            if product.get("category")
            == selected_category
        ]

    st.divider()

    # PRODUCTS

    if not filtered_products:

        st.info(
            "No products found."
        )

    else:

        columns = st.columns(3)

        for index, product in enumerate(
            filtered_products
        ):

            with columns[index % 3]:

                image_url = product.get(
                    "image_url"
                )

                if image_url:

                    st.image(
                        image_url,
                        use_container_width=True
                    )

                st.subheader(
                    product["name"]
                )

                st.write(
                    f"### {money(product['price'])}"
                )

                st.caption(
                    product.get(
                        "category",
                        "Other"
                    )
                )

                stock = product.get(
                    "stock",
                    0
                )

                if stock > 0:

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

                else:

                    st.warning(
                        "Out of stock"
                    )


# ============================================================
# CART
# ============================================================

elif st.session_state.page == "Cart":

    st.title("🛒 Your Cart")

    if not st.session_state.cart:

        st.info(
            "Your cart is empty."
        )

        if st.button(
            "Continue Shopping"
        ):

            st.session_state.page = "Store"
            st.rerun()

    else:

        for product in products:

            product_id = product["id"]

            if product_id not in st.session_state.cart:
                continue

            quantity = (
                st.session_state.cart[
                    product_id
                ]
            )

            col1, col2, col3 = st.columns(
                [2, 5, 2]
            )

            with col1:

                if product.get("image_url"):

                    st.image(
                        product["image_url"],
                        width=120
                    )

            with col2:

                st.subheader(
                    product["name"]
                )

                st.write(
                    money(product["price"])
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

        total = calculate_cart_total(products)

        st.subheader(
            f"Total: {money(total)}"
        )

        st.divider()

        if st.button(
            "📦 Place Order",
            use_container_width=True
        ):

            try:

                # Create order

                order_response = (
                    supabase
                    .table("orders")
                    .insert({
                        "user_id": user.id,
                        "total": total,
                        "status": "pending",
                        "payment_status": "unpaid"
                    })
                    .execute()
                )

                if not order_response.data:

                    st.error(
                        "Could not create order."
                    )

                else:

                    order_id = (
                        order_response.data[0]["id"]
                    )

                    # Create order items

                    for product in products:

                        product_id = product["id"]

                        if (
                            product_id
                            in st.session_state.cart
                        ):

                            quantity = (
                                st.session_state.cart[
                                    product_id
                                ]
                            )

                            supabase.table(
                                "order_items"
                            ).insert({
                                "order_id": order_id,
                                "product_id": product_id,
                                "quantity": quantity,
                                "price": product["price"]
                            }).execute()

                    st.session_state.cart = {}

                    st.success(
                        "Order created successfully!"
                    )

                    st.info(
                        "Your order is currently pending payment."
                    )

                    st.session_state.page = "Orders"

                    st.rerun()

            except Exception as error:

                st.error(
                    f"Could not place order: {error}"
                )


# ============================================================
# CUSTOMER ORDERS
# ============================================================

elif st.session_state.page == "Orders":

    st.title("📦 My Orders")

    try:

        response = (
            supabase
            .table("orders")
            .select("*")
            .eq("user_id", user.id)
            .order("created_at", desc=True)
            .execute()
        )

        orders = response.data or []

        if not orders:

            st.info(
                "You haven't placed any orders yet."
            )

        else:

            for order in orders:

                with st.container(border=True):

                    st.subheader(
                        f"Order #{order['id']}"
                    )

                    st.write(
                        f"Total: {money(order['total'])}"
                    )

                    st.write(
                        f"Status: {order['status']}"
                    )

                    st.write(
                        f"Payment: {order['payment_status']}"
                    )

    except Exception as error:

        st.error(
            f"Could not load orders: {error}"
        )


# ============================================================
# OWNER DASHBOARD
# ============================================================

elif st.session_state.page == "Owner":

    if user_role != "owner":

        st.error(
            "You do not have permission to access this page."
        )

        st.stop()

    st.title("⚙️ Veyra Owner Dashboard")

    st.write(
        "Manage your store."
    )

    st.divider()

    # --------------------------------------------------------
    # ADD PRODUCT
    # --------------------------------------------------------

    st.subheader("➕ Add Product")

    with st.form("add_product_form"):

        name = st.text_input(
            "Product name"
        )

        description = st.text_area(
            "Description"
        )

        price = st.number_input(
            "Price (₦)",
            min_value=0.0,
            step=100.0
        )

        category = st.text_input(
            "Category"
        )

        image_url = st.text_input(
            "Image URL"
        )

        stock = st.number_input(
            "Stock",
            min_value=0,
            step=1
        )

        submitted = st.form_submit_button(
            "Add Product",
            use_container_width=True
        )

        if submitted:

            if not name:

                st.warning(
                    "Product name is required."
                )

            elif price <= 0:

                st.warning(
                    "Price must be greater than zero."
                )

            else:

            