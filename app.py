import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import uuid

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="My Store",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>
    .product-card {
        border: 1px solid #ddd;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        background: white;
    }

    .product-title {
        font-size: 20px;
        font-weight: bold;
    }

    .product-price {
        font-size: 18px;
        font-weight: bold;
    }

    .order-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
    }

    .admin-box {
        border: 2px solid #ddd;
        border-radius: 12px;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SUPABASE CONNECTION
# ============================================================

try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

    supabase: Client = create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )

except Exception as e:
    st.error("Could not connect to Supabase.")
    st.code(str(e))
    st.stop()


# ============================================================
# ADMIN EMAIL
# ============================================================

# Change this to the email address that should have admin access.
ADMIN_EMAIL = "youradmin@email.com"


# ============================================================
# SESSION STATE
# ============================================================

if "user" not in st.session_state:
    st.session_state.user = None

if "cart" not in st.session_state:
    st.session_state.cart = []

if "page" not in st.session_state:
    st.session_state.page = "Home"


# ============================================================
# AUTHENTICATION HELPERS
# ============================================================

def get_current_user():
    try:
        response = supabase.auth.get_user()

        if response and response.user:
            return response.user

    except Exception:
        pass

    return None


def logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.user = None
    st.session_state.cart = []
    st.session_state.page = "Home"

    st.rerun()


# ============================================================
# LOAD CURRENT USER
# ============================================================

if st.session_state.user is None:
    st.session_state.user = get_current_user()


# ============================================================
# AUTHENTICATION PAGE
# ============================================================

def authentication_page():

    st.title("🛒 My Store")

    st.write("Welcome to our online store.")

    login_tab, signup_tab = st.tabs([
        "🔐 Login",
        "📝 Create Account"
    ])

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    with login_tab:

        st.subheader("Login")

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

            if not email or not password:
                st.warning("Please enter your email and password.")

            else:

                try:

                    result = supabase.auth.sign_in_with_password({
                        "email": email,
                        "password": password
                    })

                    if result.user:

                        st.session_state.user = result.user

                        st.success("Login successful!")

                        st.rerun()

                except Exception as e:

                    st.error(
                        "Login failed. Please check your email and password."
                    )

                    st.code(str(e))


    # --------------------------------------------------------
    # SIGN UP
    # --------------------------------------------------------

    with signup_tab:

        st.subheader("Create an Account")

        name = st.text_input(
            "Full name",
            key="signup_name"
        )

        email = st.text_input(
            "Email address",
            key="signup_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        confirm_password = st.text_input(
            "Confirm password",
            type="password",
            key="signup_confirm_password"
        )

        if st.button(
            "Create Account",
            use_container_width=True
        ):

            if not name or not email or not password:
                st.warning("Please fill in all fields.")

            elif password != confirm_password:
                st.error("Passwords do not match.")

            elif len(password) < 6:
                st.error("Password must contain at least 6 characters.")

            else:

                try:

                    result = supabase.auth.sign_up({
                        "email": email,
                        "password": password,
                        "options": {
                            "data": {
                                "full_name": name
                            }
                        }
                    })

                    st.success(
                        "Account created! Check your email and click the confirmation link."
                    )

                except Exception as e:

                    st.error("Could not create your account.")

                    st.code(str(e))


# ============================================================
# REQUIRE LOGIN
# ============================================================

if st.session_state.user is None:

    authentication_page()

    st.stop()


# ============================================================
# CURRENT USER INFORMATION
# ============================================================

user = st.session_state.user

user_email = getattr(user, "email", "")

user_id = getattr(user, "id", "")


# ============================================================
# ADMIN CHECK
# ============================================================

is_admin = (
    user_email.lower() == ADMIN_EMAIL.lower()
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🛒 My Store")

    st.write(f"👤 {user_email}")

    st.divider()

    if st.button(
        "🏠 Home",
        use_container_width=True
    ):
        st.session_state.page = "Home"
        st.rerun()

    if st.button(
        "🛍️ Cart",
        use_container_width=True
    ):
        st.session_state.page = "Cart"
        st.rerun()

    if st.button(
        "📦 My Orders",
        use_container_width=True
    ):
        st.session_state.page = "Orders"
        st.rerun()

    if is_admin:

        st.divider()

        st.subheader("Admin")

        if st.button(
            "⚙️ Admin Dashboard",
            use_container_width=True
        ):
            st.session_state.page = "Admin"
            st.rerun()

    st.divider()

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):
        logout()# ============================================================
# PRODUCT FUNCTIONS
# ============================================================

def load_products():

    try:

        response = (
            supabase
            .table("products")
            .select("*")
            .execute()
        )

        return response.data or []

    except Exception as e:

        st.error("Could not load products.")
        st.code(str(e))

        return []


def get_product(product_id):

    try:

        response = (
            supabase
            .table("products")
            .select("*")
            .eq("id", product_id)
            .limit(1)
            .execute()
        )

        if response.data:
            return response.data[0]

    except Exception:
        pass

    return None


# ============================================================
# CART FUNCTIONS
# ============================================================

def add_to_cart(product):

    product_id = str(product["id"])

    for item in st.session_state.cart:

        if str(item["id"]) == product_id:

            item["quantity"] += 1

            return

    st.session_state.cart.append({
        "id": product["id"],
        "name": product.get("name", "Product"),
        "price": float(product.get("price", 0)),
        "quantity": 1,
        "image_url": product.get("image_url", "")
    })


def remove_from_cart(product_id):

    st.session_state.cart = [
        item
        for item in st.session_state.cart
        if str(item["id"]) != str(product_id)
    ]


def increase_quantity(product_id):

    for item in st.session_state.cart:

        if str(item["id"]) == str(product_id):

            item["quantity"] += 1


def decrease_quantity(product_id):

    for item in st.session_state.cart:

        if str(item["id"]) == str(product_id):

            item["quantity"] -= 1

            if item["quantity"] <= 0:

                remove_from_cart(product_id)

            return


def cart_total():

    total = 0

    for item in st.session_state.cart:

        total += (
            float(item["price"])
            *
            int(item["quantity"])
        )

    return total


# ============================================================
# HOME PAGE
# ============================================================

def home_page():

    st.title("🛍️ Our Products")

    products = load_products()

    if not products:

        st.info(
            "There are currently no products available."
        )

        return


    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    search = st.text_input(
        "🔎 Search products",
        placeholder="Search for a product..."
    )


    # --------------------------------------------------------
    # CATEGORIES
    # --------------------------------------------------------

    categories = sorted(
        list(
            set(
                str(p.get("category", "Other"))
                for p in products
            )
        )
    )

    category_options = ["All"] + categories

    selected_category = st.selectbox(
        "Category",
        category_options
    )


    # --------------------------------------------------------
    # FILTER PRODUCTS
    # --------------------------------------------------------

    filtered_products = []

    for product in products:

        name = str(
            product.get("name", "")
        )

        description = str(
            product.get("description", "")
        )

        category = str(
            product.get("category", "Other")
        )

        matches_search = (
            not search
            or search.lower() in name.lower()
            or search.lower() in description.lower()
        )

        matches_category = (
            selected_category == "All"
            or category == selected_category
        )

        if matches_search and matches_category:

            filtered_products.append(product)


    if not filtered_products:

        st.warning("No products matched your search.")

        return


    # --------------------------------------------------------
    # PRODUCT GRID
    # --------------------------------------------------------

    columns = st.columns(3)

    for index, product in enumerate(filtered_products):

        column = columns[index % 3]

        with column:

            st.markdown(
                '<div class="product-card">',
                unsafe_allow_html=True
            )

            image_url = product.get(
                "image_url",
                ""
            )

            if image_url:

                try:

                    st.image(
                        image_url,
                        use_container_width=True
                    )

                except Exception:
                    pass


            product_name = product.get(
                "name",
                "Product"
            )

            product_description = product.get(
                "description",
                ""
            )

            product_price = float(
                product.get("price", 0)
            )


            st.markdown(
                f'<div class="product-title">{product_name}</div>',
                unsafe_allow_html=True
            )

            if product_description:

                st.write(
                    product_description
                )


            st.markdown(
                f'<div class="product-price">₦{product_price:,.2f}</div>',
                unsafe_allow_html=True
            )


            st.write("")


            if st.button(
                "🛒 Add to Cart",
                key=f"add_{product['id']}",
                use_container_width=True
            ):

                add_to_cart(product)

                st.success(
                    f"{product_name} added to cart!"
                )


            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )


# ============================================================
# CART PAGE
# ============================================================

def cart_page():

    st.title("🛒 Your Cart")

    if not st.session_state.cart:

        st.info(
            "Your cart is empty."
        )

        if st.button("Continue Shopping"):

            st.session_state.page = "Home"

            st.rerun()

        return


    for item in st.session_state.cart:

        col1, col2, col3, col4, col5 = st.columns(
            [3, 1, 1, 1, 1]
        )

        with col1:

            st.write(
                f"**{item['name']}**"
            )

        with col2:

            st.write(
                f"₦{item['price']:,.2f}"
            )

        with col3:

            if st.button(
                "➖",
                key=f"minus_{item['id']}"
            ):

                decrease_quantity(
                    item["id"]
                )

                st.rerun()

            st.write(
                item["quantity"]
            )

            if st.button(
                "➕",
                key=f"plus_{item['id']}"
            ):

                increase_quantity(
                    item["id"]
                )

                st.rerun()

        with col4:

            subtotal = (
                item["price"]
                *
                item["quantity"]
            )

            st.write(
                f"₦{subtotal:,.2f}"
            )

        with col5:

            if st.button(
                "🗑️",
                key=f"remove_{item['id']}"
            ):

                remove_from_cart(
                    item["id"]
                )

                st.rerun()


    st.divider()


    total = cart_total()

    st.subheader(
        f"Total: ₦{total:,.2f}"
    )


    if st.button(
        "💳 Proceed to Checkout",
        type="primary",
        use_container_width=True
    ):

        st.session_state.page = "Checkout"

        st.rerun()


# ============================================================
# CHECKOUT PAGE
# ============================================================

def checkout_page():

    st.title("💳 Checkout")

    if not st.session_state.cart:

        st.warning(
            "Your cart is empty."
        )

        return


    st.subheader("Order Summary")


    for item in st.session_state.cart:

        subtotal = (
            item["price"]
            *
            item["quantity"]
        )

        st.write(
            f"**{item['name']}** × "
            f"{item['quantity']} — "
            f"₦{subtotal:,.2f}"
        )


    st.divider()


    total = cart_total()

    st.subheader(
        f"Total: ₦{total:,.2f}"
    )


    st.write(
        "Enter your delivery information."
    )


    full_name = st.text_input(
        "Full name"
    )

    phone = st.text_input(
        "Phone number"
    )

    address = st.text_area(
        "Delivery address"
    )


    if st.button(
        "Place Order",
        type="primary",
        use_container_width=True
    ):

        if not full_name or not phone or not address:

            st.warning(
                "Please complete all delivery fields."
            )

            return


        create_order(
            full_name,
            phone,
            address
        )# ============================================================
# CREATE ORDER
# ============================================================

def create_order(
    full_name,
    phone,
    address
):

    try:

        # ----------------------------------------------------
        # CREATE ORDER
        # ----------------------------------------------------

        order_id = str(uuid.uuid4())

        total_amount = cart_total()


        order_data = {
            "id": order_id,
            "user_id": str(user_id),
            "total_amount": total_amount,
            "status": "Pending",
            "customer_name": full_name,
            "phone": phone,
            "address": address
        }


        order_response = (
            supabase
            .table("orders")
            .insert(order_data)
            .execute()
        )


        if not order_response.data:

            st.error(
                "The order could not be created."
            )

            return


        # ----------------------------------------------------
        # CREATE ORDER ITEMS
        # ----------------------------------------------------

        order_items = []


        for item in st.session_state.cart:

            order_items.append({

                "order_id": order_id,

                "product_id": str(
                    item["id"]
                ),

                # IMPORTANT:
                # Store the product name directly
                # with the order.

                "product_name": item["name"],

                "quantity": int(
                    item["quantity"]
                ),

                # IMPORTANT:
                # We use "price", NOT "unit_price".
                # This fixes the previous error.

                "price": float(
                    item["price"]
                )
            })


        if order_items:

            try:

                supabase \
                    .table("order_items") \
                    .insert(order_items) \
                    .execute()

            except Exception as item_error:

                st.error(
                    "The order was created, but the order items could not be saved."
                )

                st.code(
                    str(item_error)
                )

                return


        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        st.session_state.cart = []

        st.success(
            "🎉 Your order was placed successfully!"
        )

        st.info(
            f"Order ID: {order_id}"
        )

        st.balloons()


        if st.button(
            "View My Orders"
        ):

            st.session_state.page = "Orders"

            st.rerun()


    except Exception as e:

        st.error(
            "Could not create your order."
        )

        st.code(
            str(e)
        )


# ============================================================
# ORDERS PAGE
# ============================================================

def orders_page():

    st.title("📦 My Orders")


    try:

        orders_response = (
            supabase
            .table("orders")
            .select("*")
            .eq(
                "user_id",
                str(user_id)
            )
            .order(
                "id",
                desc=True
            )
            .execute()
        )


        orders = (
            orders_response.data
            or []
        )


    except Exception as e:

        st.error(
            "Could not load your orders."
        )

        st.code(
            str(e)
        )

        return


    if not orders:

        st.info(
            "You haven't placed any orders yet."
        )

        return


    for order in orders:

        order_id = order.get(
            "id",
            ""
        )

        status = order.get(
            "status",
            "Pending"
        )

        total = float(
            order.get(
                "total_amount",
                0
            )
        )


        with st.expander(
            f"Order {order_id} — {status}"
        ):

            st.write(
                f"**Status:** {status}"
            )

            st.write(
                f"**Total:** ₦{total:,.2f}"
            )

            st.write(
                f"**Customer:** "
                f"{order.get('customer_name', '')}"
            )

            st.write(
                f"**Phone:** "
                f"{order.get('phone', '')}"
            )

            st.write(
                f"**Address:** "
                f"{order.get('address', '')}"
            )


            # ------------------------------------------------
            # LOAD ORDER ITEMS
            # ------------------------------------------------

            try:

                items_response = (
                    supabase
                    .table("order_items")
                    .select("*")
                    .eq(
                        "order_id",
                        order_id
                    )
                    .execute()
                )

                items = (
                    items_response.data
                    or []
                )


                if items:

                    st.write("### Products ordered")

                    for item in items:

                        name = item.get(
                            "product_name",
                            "Unknown product"
                        )

                        quantity = int(
                            item.get(
                                "quantity",
                                1
                            )
                        )

                        price = float(
                            item.get(
                                "price",
                                0
                            )
                        )


                        st.write(
                            f"🛍️ **{name}** — "
                            f"Quantity: {quantity} — "
                            f"₦{price:,.2f} each"
                        )


            except Exception as e:

                st.warning(
                    "Could not load the products in this order."
                )


# ============================================================
# ADMIN PRODUCT FUNCTIONS
# ============================================================

def admin_add_product():

    st.subheader(
        "➕ Add New Product"
    )


    with st.form(
        "add_product_form"
    ):

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

        submitted = st.form_submit_button(
            "Add Product",
            use_container_width=True
        )


        if submitted:

            if not name:

                st.warning(
                    "Product name is required."
                )

            else:

                try:

                    product_data = {
                        "id": str(uuid.uuid4()),
                        "name": name,
                        "description": description,
                        "price": float(price),
                        "category": category or "Other",
                        "image_url": image_url
                    }


                    supabase \
                        .table("products") \
                        .insert(product_data) \
                        .execute()


                    st.success(
                        f"{name} was added successfully!"
                    )

                    st.rerun()


                except Exception as e:

                    st.error(
                        "Could not add the product."
                    )

                    st.code(
                        str(e)
                    )


# ============================================================
# ADMIN PRODUCT MANAGEMENT
# ============================================================

def admin_products():

    st.subheader(
        "📦 Manage Products"
    )


    products = load_products()


    if not products:

        st.info(
            "No products found."
        )

        return


    for product in products:

        product_id = product.get(
            "id"
        )

        name = product.get(
            "name",
            "Product"
        )


        with st.expander(
            f"🛍️ {name}"
        ):

            new_name = st.text_input(
                "Name",
                value=name,
                key=f"name_{product_id}"
            )

            new_description = st.text_area(
                "Description",
                value=product.get(
                    "description",
                    ""
                ),
                key=f"description_{product_id}"
            )

            new_price = st.number_input(
                "Price",
                value=float(
                    product.get(
                        "price",
                        0
                    )
                ),
                min_value=0.0,
                key=f"price_{product_id}"
            )

            new_category = st.text_input(
                "Category",
                value=product.get(
                    "category",
                    "Other"
                ),
                key=f"category_{product_id}"
            )

            new_image = st.text_input(
                "Image URL",
                value=product.get(
                    "image_url",
                    ""
                ),
                key=f"image_{product_id}"
            )


            col1, col2 = st.columns(2)


            with col1:

                if st.button(
                    "💾 Save Changes",
                    key=f"save_{product_id}",
                    use_container_width=True
                ):

                    try:

                        supabase \
                            .table("products") \
                            .update({
                                "name": new_name,
                                "description": new_description,
                                "price": float(new_price),
                                "category": new_category,
                                "image_url": new_image
                            }) \
                            .eq(
                                "id",
                                product_id
                            ) \
                            .execute()


                        st.success(
                            "Product updated."
                        )

                        st.rerun()


                    except Exception as e:

                        st.error(
                            "Could not update product."
                        )

                        st.code(
                            str(e)
                        )


            with col2:

                if st.button(
                    "🗑️ Delete Product",
                    key=f"delete_{product_id}",
                    use_container_width=True
                ):

                    try:

                        supabase \
                            .table("products") \
                            .delete() \
                            .eq(
                                "id",
                                product_id
                            ) \
                            .execute()


                        st.success(
                            "Product deleted."
                        )

                        st.rerun()


                    except Exception as e:

                        st.error(
                            "Could not delete product."
                        )

                        st.code(
                            str(e)
                        )# ============================================================
# ADMIN ORDERS
# ============================================================

def admin_orders():

    st.subheader(
        "📦 Customer Orders"
    )


    try:

        response = (
            supabase
            .table("orders")
            .select("*")
            .order(
                "id",
                desc=True
            )
            .execute()
        )

        orders = (
            response.data
            or []
        )


    except Exception as e:

        st.error(
            "Could not load customer orders."
        )

        st.code(
            str(e)
        )

        return


    if not orders:

        st.info(
            "There are no orders yet."
        )

        return


    for order in orders:

        order_id = order.get(
            "id",
            ""
        )

        current_status = order.get(
            "status",
            "Pending"
        )

        total = float(
            order.get(
                "total_amount",
                0
            )
        )

        customer_name = order.get(
            "customer_name",
            "Unknown"
        )

        phone = order.get(
            "phone",
            ""
        )

        address = order.get(
            "address",
            ""
        )


        with st.expander(
            f"📦 {customer_name} — ₦{total:,.2f} — {current_status}"
        ):

            st.write(
                f"**Order ID:** {order_id}"
            )

            st.write(
                f"**Customer:** {customer_name}"
            )

            st.write(
                f"**Phone:** {phone}"
            )

            st.write(
                f"**Address:** {address}"
            )

            st.write(
                f"**Total:** ₦{total:,.2f}"
            )


            # ------------------------------------------------
            # ORDER PRODUCTS
            # ------------------------------------------------

            try:

                items_response = (
                    supabase
                    .table("order_items")
                    .select("*")
                    .eq(
                        "order_id",
                        order_id
                    )
                    .execute()
                )

                items = (
                    items_response.data
                    or []
                )


                if items:

                    st.write(
                        "### Products ordered"
                    )

                    for item in items:

                        product_name = item.get(
                            "product_name",
                            "Unknown product"
                        )

                        quantity = int(
                            item.get(
                                "quantity",
                                1
                            )
                        )

                        price = float(
                            item.get(
                                "price",
                                0
                            )
                        )


                        st.write(
                            f"🛍️ **{product_name}** "
                            f"× {quantity} "
                            f"— ₦{price:,.2f} each"
                        )


            except Exception:

                st.warning(
                    "Could not load order items."
                )


            # ------------------------------------------------
            # CHANGE STATUS
            # ------------------------------------------------

            statuses = [
                "Pending",
                "Processing",
                "Shipped",
                "Delivered",
                "Cancelled"
            ]


            selected_status = st.selectbox(
                "Order status",
                statuses,
                index=(
                    statuses.index(
                        current_status
                    )
                    if current_status in statuses
                    else 0
                ),
                key=f"status_{order_id}"
            )


            if st.button(
                "Update Status",
                key=f"update_status_{order_id}",
                use_container_width=True
            ):

                try:

                    supabase \
                        .table("orders") \
                        .update({
                            "status": selected_status
                        }) \
                        .eq(
                            "id",
                            order_id
                        ) \
                        .execute()


                    st.success(
                        "Order status updated."
                    )

                    st.rerun()


                except Exception as e:

                    st.error(
                        "Could not update order status."
                    )

                    st.code(
                        str(e)
                    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

def admin_page():

    if not is_admin:

        st.error(
            "You do not have permission to access the admin dashboard."
        )

        return


    st.title("⚙️ Admin Dashboard")


    product_tab, orders_tab = st.tabs([
        "🛍️ Products",
        "📦 Orders"
    ])


    with product_tab:

        admin_add_product()

        st.divider()

        admin_products()


    with orders_tab:

        admin_orders()


# ============================================================
# PAGE ROUTER
# ============================================================

if st.session_state.page == "Home":

    home_page()


elif st.session_state.page == "Cart":

    cart_page()


elif st.session_state.page == "Checkout":

    checkout_page()


elif st.session_state.page == "Orders":

    orders_page()


elif st.session_state.page == "Admin":

    admin_page()


else:

    st.session_state.page = "Home"

    home_page()