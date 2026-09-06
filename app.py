import streamlit as st
import json

# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(
    page_title="My Store",
    page_icon="🛍️",
    layout="wide"
)

# -----------------------------
# LOAD PRODUCTS
# -----------------------------

def load_products():
    with open("products.json", "r", encoding="utf-8") as file:
        return json.load(file)


products = load_products()

# -----------------------------
# SESSION STATE
# -----------------------------

if "cart" not in st.session_state:
    st.session_state.cart = {}

if "page" not in st.session_state:
    st.session_state.page = "Store"


# -----------------------------
# FUNCTIONS
# -----------------------------

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


# -----------------------------
# SIDEBAR
# -----------------------------

st.sidebar.title("🛍️ My Store")

if st.sidebar.button("🏠 Store", use_container_width=True):
    st.session_state.page = "Store"

if st.sidebar.button(
    f"🛒 Cart ({sum(st.session_state.cart.values())})",
    use_container_width=True
):
    st.session_state.page = "Cart"

if st.sidebar.button("⚙️ Owner Dashboard", use_container_width=True):
    st.session_state.page = "Owner"


# -----------------------------
# STORE PAGE
# -----------------------------

if st.session_state.page == "Store":

    st.title("🛍️ Welcome to My Store")
    st.write("Find products you love.")

    search = st.text_input(
        "🔎 Search products",
        placeholder="Search for a product..."
    )

    categories = ["All"]

    for product in products:
        if product["category"] not in categories:
            categories.append(product["category"])

    category = st.selectbox(
        "Category",
        categories
    )

    filtered_products = products

    if search:
        filtered_products = [
            p for p in filtered_products
            if search.lower() in p["name"].lower()
        ]

    if category != "All":
        filtered_products = [
            p for p in filtered_products
            if p["category"] == category
        ]

    st.divider()

    columns = st.columns(3)

    for index, product in enumerate(filtered_products):

        with columns[index % 3]:

            st.image(
                product["image"],
                use_container_width=True
            )

            st.subheader(product["name"])

            st.write(
                f"₦{product['price']:,.0f}"
            )

            st.caption(
                f"Category: {product['category']}"
            )

            if st.button(
                "🛒 Add to Cart",
                key=f"add_{product['id']}",
                use_container_width=True
            ):
                add_to_cart(product["id"])
                st.success("Added to cart!")

            st.write("")


# -----------------------------
# CART PAGE
# -----------------------------

elif st.session_state.page == "Cart":

    st.title("🛒 Your Cart")

    if not st.session_state.cart:

        st.info("Your cart is empty.")

        if st.button("Continue Shopping"):
            st.session_state.page = "Store"

    else:

        for product in products:

            product_id = product["id"]

            if product_id in st.session_state.cart:

                quantity = st.session_state.cart[product_id]

                col1, col2, col3, col4 = st.columns(
                    [2, 3, 1, 1]
                )

                with col1:
                    st.image(
                        product["image"],
                        width=120
                    )

                with col2:
                    st.write(f"### {product['name']}")
                    st.write(
                        f"₦{product['price']:,.0f} each"
                    )

                with col3:
                    st.write(
                        f"Quantity: {quantity}"
                    )

                with col4:

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
                "Checkout/payment system will be connected here."
            )


# -----------------------------
# OWNER DASHBOARD
# -----------------------------

elif st.session_state.page == "Owner":

    st.title("⚙️ Owner Dashboard")

    st.write(
        "Manage the products displayed in your store."
    )

    st.divider()

    st.subheader("📦 Current Products")

    for product in products:

        col1, col2, col3 = st.columns(
            [2, 4, 2]
        )

        with col1:
            st.image(
                product["image"],
                width=100
            )

        with col2:
            st.write(f"**{product['name']}**")
            st.write(
                f"₦{product['price']:,.0f}"
            )

        with col3:
            st.write(
                product["category"]
            )

    st.divider()

    st.subheader("➕ Add New Product")

    with st.form("add_product"):

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

        submitted = st.form_submit_button(
            "Add Product"
        )

        if submitted:

            if name and price and category and image:

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

                products.append(new_product)

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
                    "Product added successfully!"
                )

                st.rerun()

            else:
                st.warning(
                    "Please fill in every field."
                )