import streamlit as st
from supabase import create_client

# =========================
# Veyra
# =========================

st.set_page_config(
    page_title="Veyra",
    page_icon="🛍️",
    layout="wide"
)

# =========================
# SUPABASE
# =========================

sb = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# =========================
# SESSION
# =========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "Store"

if "cart" not in st.session_state:
    st.session_state.cart = {}

# =========================
# SAMPLE PRODUCTS
# =========================

SAMPLE_PRODUCTS = [
    {
        "id": "sample1",
        "name": "Veyra Phone X1",
        "description": "Modern smartphone with a powerful camera.",
        "price": 250000,
        "category": "Phones",
        "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9",
        "stock": 20
    },
    {
        "id": "sample2",
        "name": "Veyra AirBuds",
        "description": "Wireless earbuds with clear sound.",
        "price": 45000,
        "category": "Audio",
        "image_url": "https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1",
        "stock": 35
    },
    {
        "id": "sample3",
        "name": "Veyra Smart Watch",
        "description": "Smart watch for everyday use.",
        "price": 75000,
        "category": "Wearables",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30",
        "stock": 15
    },
    {
        "id": "sample4",
        "name": "Veyra Backpack",
        "description": "Durable backpack for school and travel.",
        "price": 30000,
        "category": "Bags",
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62",
        "stock": 25
    },
    {
        "id": "sample5",
        "name": "Veyra Sneakers",
        "description": "Comfortable everyday sneakers.",
        "price": 55000,
        "category": "Fashion",
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
        "stock": 18
    },
    {
        "id": "sample6",
        "name": "Veyra Fast Charger",
        "description": "Fast USB-C charging adapter.",
        "price": 18000,
        "category": "Accessories",
        "image_url": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0",
        "stock": 40
    }
]

# =========================
# FUNCTIONS
# =========================

def money(value):
    return f"₦{value:,.2f}"


def cart_total():
    return sum(
        item["price"] * item["quantity"]
        for item in st.session_state.cart.values()
    )


def cart_count():
    return sum(
        item["quantity"]
        for item in st.session_state.cart.values()
    )


def get_products():
    try:
        result = (
            sb.table("products")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

        data = result.data or []

        # Show built-in products if database is empty
        if not data:
            return SAMPLE_PRODUCTS

        return data

    except Exception as e:
        st.error(f"Could not load products: {e}")
        return SAMPLE_PRODUCTS


def is_owner():
    if not st.session_state.user:
        return False

    # Put your owner's email in Streamlit secrets
    owner_email = st.secrets.get("OWNER_EMAIL", "")

    return (
        owner_email
        and st.session_state.user.email.lower()
        == owner_email.lower()
    )


# =========================
# HEADER
# =========================

st.title("🛍️ Veyra")

# =========================
# LOGIN / SIGNUP
# =========================

if not st.session_state.logged_in:

    login_tab, signup_tab = st.tabs(
        ["🔐 Login", "📝 Create Account"]
    )

    with login_tab:

        email = st.text_input(
            "Email",
            key="login_email"
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

            try:

                result = sb.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })

                st.session_state.user = result.user
                st.session_state.logged_in = True
                st.session_state.page = "Store"

                st.success("✅ Login successful!")
                st.rerun()

            except Exception as e:

                st.error(
                    "Login failed. Check your email, password, "
                    "and email confirmation."
                )

    with signup_tab:

        new_email = st.text_input(
            "Email",
            key="signup_email"
        )

        new_password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password"
        )

        if st.button(
            "Create Account",
            use_container_width=True
        ):

            if new_password != confirm_password:

                st.error("Passwords do not match.")

            elif len(new_password) < 6:

                st.error(
                    "Password must be at least 6 characters."
                )

            else:

                try:

                    sb.auth.sign_up({
                        "email": new_email,
                        "password": new_password
                    })

                    st.success(
                        "Account created! "
                        "Check your email to confirm your account."
                    )

                except Exception as e:

                    st.error(str(e))

    st.stop()


# =========================
# SIDEBAR
# =========================

st.sidebar.title("Veyra")

st.sidebar.write(
    f"👤 {st.session_state.user.email}"
)

st.sidebar.divider()

if st.sidebar.button(
    "🛍️ Store",
    use_container_width=True
):
    st.session_state.page = "Store"

if st.sidebar.button(
    f"🛒 Cart ({cart_count()})",
    use_container_width=True
):
    st.session_state.page = "Cart"

if st.sidebar.button(
    "📦 My Orders",
    use_container_width=True
):
    st.session_state.page = "Orders"

# Owner only
if is_owner():

    if st.sidebar.button(
        "👑 Owner Dashboard",
        use_container_width=True
    ):
        st.session_state.page = "Owner"

st.sidebar.divider()

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):

    sb.auth.sign_out()

    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.cart = {}

    st.rerun()


# =========================
# STORE
# =========================

if st.session_state.page == "Store":

    st.header("🛍️ Veyra Store")

    products = get_products()

    search = st.text_input(
        "🔎 Search products"
    )

    categories = list(
        set(
            p.get("category", "Other")
            for p in products
        )
    )

    category = st.selectbox(
        "Category",
        ["All"] + sorted(categories)
    )

    filtered = []

    for product in products:

        name = product.get("name", "")
        product_category = product.get(
            "category",
            "Other"
        )

        if search.lower() not in name.lower():
            continue

        if (
            category != "All"
            and product_category != category
        ):
            continue

        filtered.append(product)

    if not filtered:

        st.info("No products found.")

    else:

        cols = st.columns(3)

        for i, product in enumerate(filtered):

            with cols[i % 3]:

                image = product.get("image_url")

                if image:
                    st.image(
                        image,
                        use_container_width=True
                    )

                st.subheader(
                    product.get("name", "Product")
                )

                st.write(
                    product.get(
                        "description",
                        ""
                    )
                )

                st.write(
                    f"### {money(product.get('price', 0))}"
                )

                st.write(
                    f"📦 Stock: {product.get('stock', 0)}"
                )

                if st.button(
                    "🛒 Add to Cart",
                    key=f"add_{product['id']}",
                    use_container_width=True
                ):

                    pid = product["id"]

                    if pid in st.session_state.cart:

                        st.session_state.cart[
                            pid
                        ]["quantity"] += 1

                    else:

                        st.session_state.cart[pid] = {
                            "id": pid,
                            "name": product["name"],
                            "price": float(
                                product["price"]
                            ),
                            "quantity": 1
                        }

                    st.success(
                        f"{product['name']} added!"
                    )


# =========================
# CART
# =========================

elif st.session_state.page == "Cart":

    st.header("🛒 Your Cart")

    if not st.session_state.cart:

        st.info("Your cart is empty.")

    else:

        for pid, item in list(
            st.session_state.cart.items()
        ):

            col1, col2, col3, col4 = st.columns(
                [3, 1, 1, 1]
            )

            with col1:
                st.write(
                    f"**{item['name']}**"
                )

            with col2:
                st.write(
                    money(item["price"])
                )

            with col3:

                st.write(
                    f"Qty: {item['quantity']}"
                )

            with col4:

                if st.button(
                    "➖",
                    key=f"minus_{pid}"
                ):

                    item["quantity"] -= 1

                    if item["quantity"] <= 0:
                        del st.session_state.cart[pid]

                    st.rerun()

        st.divider()

        st.subheader(
            f"Total: {money(cart_total())}"
        )

        if st.button(
            "📦 Place Order",
            use_container_width=True
        ):

            try:

                order = (
                    sb.table("orders")
                    .insert({
                        "user_id":
                            st.session_state.user.id,
                        "total":
                            cart_total(),
                        "status":
                            "pending",
                        "payment_status":
                            "unpaid"
                    })
                    .execute()
                )

                order_id = order.data[0]["id"]

                for item in st.session_state.cart.values():

                    sb.table("order_items").insert({
                        "order_id": order_id,
                        "product_id": item["id"],
                        "quantity": item["quantity"],
                        "price": item["price"]
                    }).execute()

                st.session_state.cart = {}

                st.success(
                    "✅ Order created successfully!"
                )

                st.info(
                    "Payment will be connected next."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Could not create order: {e}"
                )


# =========================
# ORDERS
# =========================

elif st.session_state.page == "Orders":

    st.header("📦 My Orders")

    try:

        result = (
            sb.table("orders")
            .select("*")
            .eq(
                "user_id",
                st.session_state.user.id
            )
            .order(
                "created_at",
                desc=True
            )
            .execute()
        )

        orders = result.data or []

        if not orders:

            st.info("You have no orders yet.")

        for order in orders:

            with st.expander(
                f"Order #{order['id']}"
            ):

                st.write(
                    f"💰 Total: "
                    f"{money(order['total'])}"
                )

                st.write(
                    f"📦 Status: "
                    f"{order['status']}"
                )

                st.write(
                    f"💳 Payment: "
                    f"{order['payment_status']}"
                )

    except Exception as e:

        st.error(str(e))


# =========================
# OWNER DASHBOARD
# =========================

elif st.session_state.page == "Owner":

    if not is_owner():

        st.error(
            "🚫 You do not have permission "
            "to access this page."
        )

        st.stop()

    st.header("👑 Owner Dashboard")

    add_tab, products_tab, orders_tab = st.tabs(
        [
            "➕ Add Product",
            "🛍️ Manage Products",
            "📦 Orders"
        ]
    )

    # -------------------------
    # ADD PRODUCT
    # -------------------------

    with add_tab:

        st.subheader(
            "➕ Add a New Product"
        )

        name = st.text_input(
            "Product Name"
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
            "Product Image URL"
        )

        stock = st.number_input(
            "Stock",
            min_value=0,
            step=1
        )

        if st.button(
            "🚀 Add Product",
            use_container_width=True
        ):

            if not name:

                st.error(
                    "Enter a product name."
                )

            elif price <= 0:

                st.error(
                    "Enter a valid price."
                )

            else:

                try:

                    sb.table("products").insert({
                        "name": name,
                        "description": description,
                        "price": price,
                        "category": category,
                        "image_url": image_url,
                        "stock": stock
                    }).execute()

                    st.success(
                        "✅ Product added to Veyra!"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Could not add product: {e}"
                    )

    # -------------------------
    # MANAGE PRODUCTS
    # -------------------------

    with products_tab:

        st.subheader(
            "🛍️ Manage Products"
        )

        try:

            result = (
                sb.table("products")
                .select("*")
                .order(
                    "created_at",
                    desc=True
                )
                .execute()
            )

            db_products = result.data or []

            if not db_products:

                st.info(
                    "No products have been saved yet."
                )

            for product in db_products:

                with st.expander(
                    f"🛍️ {product['name']}"
                ):

                    new_name = st.text_input(
                        "Name",
                        value=product["name"],
                        key=f"name_{product['id']}"
                    )

                    new_description = st.text_area(
                        "Description",
                        value=product.get(
                            "description",
                            ""
                        ),
                        key=f"desc_{product['id']}"
                    )

                    new_price = st.number_input(
                        "Price",
                        value=float(
                            product["price"]
                        ),
                        key=f"price_{product['id']}"
                    )

                    new_category = st.text_input(
                        "Category",
                        value=product.get(
                            "category",
                            ""
                        ),
                        key=f"cat_{product['id']}"
                    )

                    new_image = st.text_input(
                        "Image URL",
                        value=product.get(
                            "image_url",
                            ""
                        ),
                        key=f"img_{product['id']}"
                    )

                    new_stock = st.number_input(
                        "Stock",
                        value=int(
                            product.get(
                                "stock",
                                0
                            )
                        ),
                        key=f"stock_{product['id']}"
                    )

                    c1, c2 = st.columns(2)

                    with c1:

                        if st.button(
                            "💾 Save Changes",
                            key=f"save_{product['id']}",
                            use_container_width=True
                        ):

                            sb.table(
                                "products"
                            ).update({
                                "name": new_name,
                                "description":
                                    new_description,
                                "price":
                                    new_price,
                                "category":
                                    new_category,
                                "image_url":
                                    new_image,
                                "stock":
                                    new_stock
                            }).eq(
                                "id",
                                product["id"]
                            ).execute()

                            st.success(
                                "Product updated!"
                            )

                            st.rerun()

                    with c2:

                        if st.button(
                            "🗑️ Delete",
                            key=f"delete_{product['id']}",
                            use_container_width=True
                        ):

                            sb.table(
                                "products"
                            ).delete().eq(
                                "id",
                                product["id"]
                            ).execute()

                            st.success(
                                "Product deleted."
                            )

                            st.rerun()

        except Exception as e:

            st.error(str(e))

    # -------------------------
    # OWNER ORDERS
    # -------------------------

    with orders_tab:

        st.subhea