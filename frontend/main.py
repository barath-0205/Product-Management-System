import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

API_URL = "http://localhost:8000"  # Replace with your actual API base URL

if 'token' not in st.session_state:
    st.session_state.token = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = None

def login(email, password):
    response = requests.post(f"{API_URL}/login", data={"username": email, "password": password})
    if response.status_code == 200:
        token = response.json()['access_token']
        st.session_state.token = token
        st.session_state.user_email = email
        st.success("Login successful!")
    else:
        st.error("Login failed")

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}

def get_data(endpoint):
    res = requests.get(f"{API_URL}/{endpoint}", headers=get_headers())
    if res.status_code == 200:
        return res.json()
    st.warning(f"Failed to fetch from {endpoint}")
    return []

def create_data(endpoint, data):
    res = requests.post(f"{API_URL}/{endpoint}", json=data, headers=get_headers())
    return res

def update_data(endpoint, data):
    res = requests.put(f"{API_URL}/{endpoint}", json=data, headers=get_headers())
    return res

def delete_data(endpoint):
    res = requests.delete(f"{API_URL}/{endpoint}", headers=get_headers())
    return res

# --- Login Section ---
if not st.session_state.token:
    st.title("Inventory Management Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            login(email, password)
    st.stop()

# --- Main Dashboard ---
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", ["Dashboard", "Products", "Suppliers", "Logout"])

if selection == "Logout":
    st.session_state.token = None
    st.rerun()

# --- Dashboard with Charts ---
if selection == "Dashboard":
    st.title("Dashboard Overview")
    products = get_data("products")
    suppliers = get_data("suppliers")

    df_products = pd.DataFrame(products)
    df_suppliers = pd.DataFrame(suppliers)

    if not df_products.empty:
        st.subheader("Product Categories Distribution")
        category_counts = df_products["category"].value_counts()
        fig1, ax1 = plt.subplots()
        ax1.pie(category_counts, labels=category_counts.index, autopct="%1.1f%%", startangle=90)
        st.pyplot(fig1)

    if not df_suppliers.empty and not df_products.empty:
        st.subheader("Stock Count by Supplier")
        df_suppliers_renamed = df_suppliers.rename(columns={"name": "supplier_name"})
        merged = df_products.merge(df_suppliers_renamed, left_on="supplier_id", right_on="id")
        stock_by_supplier = merged.groupby("supplier_name")["stock"].sum()
        st.bar_chart(stock_by_supplier)

elif selection == "Products":
    st.title("Products")

    products = get_data("products")
    df = pd.DataFrame(products)

    st.dataframe(df)

    with st.expander("➕ Create New Product"):
        form_data = {
            "name": st.text_input("Name"),
            "category": st.text_input("Category"),
            "price": st.number_input("Price", min_value=0.01),
            "stock": st.number_input("Stock", min_value=1, max_value=1000, step=1),
            "sku": st.text_input("SKU"),
            "supplier_id": st.number_input("Supplier ID", min_value=1),
            "status": st.text_input("Status", value="available"),
        }
        if st.button("Create Product"):
            res = create_data("createProduct", form_data)
            if res.status_code == 201:
                st.success("Product created successfully")
                st.rerun()
            else:
                st.error(res.json().get("detail", "Error creating product"))

    st.subheader("Update or Delete Product")
    selected_id = st.selectbox("Select Product ID", df["id"] if not df.empty else [])
    if selected_id:
        selected_row = df[df["id"] == selected_id].iloc[0]
        updated_data = {
            "name": st.text_input("Name", selected_row["name"], key=f"name_{selected_id}"),
            "category": st.text_input("Category", selected_row["category"], key=f"category_{selected_id}"),
            "price": st.number_input("Price", value=selected_row["price"], key=f"price_{selected_id}"),
            "stock": st.number_input("Stock", value=selected_row["stock"], key=f"stock_{selected_id}"),
            "sku": st.text_input("SKU", selected_row["sku"], key=f"sku_{selected_id}"),
            "supplier_id": st.number_input("Supplier ID", value=selected_row["supplier_id"], key=f"supplier_Id_{selected_id}"),
            "status": st.text_input("Status", selected_row["status"], key=f"status_{selected_id}"),
        }

        col1, col2 = st.columns(2)
        if col1.button("Update Product"):
            res = update_data(f"updateProduct/{selected_id}", updated_data)
            if res.status_code == 200:
                st.success("Product updated")
                st.rerun()

        if col2.button("Delete Product"):
            res = delete_data(f"deleteProduct/{selected_id}")
            if res.status_code == 200:
                st.success("Product deleted")
                st.rerun()

# --- Supplier Management ---
elif selection == "Suppliers":
    st.title("Suppliers")

    suppliers = get_data("suppliers")
    df = pd.DataFrame(suppliers)
    st.dataframe(df)

    with st.expander("Create New Supplier"):
        supplier_data = {
            "name": st.text_input("Supplier Name"),
            "contact_info": st.text_input("Contact Info"),
            "address": st.text_input("Address"),
            "phone_number": st.text_input("Phone Number"),
            "email": st.text_input("Email"),
        }
        if st.button("Create Supplier"):
            res = create_data("createSupplier", supplier_data)
            if res.status_code == 200:
                st.success("Supplier created")
                st.rerun()
            else:
                try:
                    error_detail = res.json().get("detail", "Unknown error")
                except requests.exceptions.JSONDecodeError:
                    error_detail = f"Non-JSON response: {res.text}"  # fallback to raw text

                st.error(error_detail)


    st.subheader("Update or Delete Supplier")
    selected_id = st.selectbox("Select Supplier ID", df["id"] if not df.empty else [])
    if selected_id:
        selected_row = df[df["id"] == selected_id].iloc[0]
        updated_supplier = {
            "name": st.text_input("Name", selected_row["name"]),
            "contact_info": st.text_input("Contact Info", selected_row["contact_info"]),
            "address": st.text_input("Address", selected_row["address"]),
            "phone_number": st.text_input("Phone", selected_row["phone_number"]),
            "email": st.text_input("Email", selected_row["email"]),
        }

        col1, col2 = st.columns(2)
        if col1.button("Update Supplier"):
            res = update_data(f"updateSupplier/{selected_id}", updated_supplier)
            if res.status_code == 200:
                st.success("Supplier updated")
                st.rerun()

        if col2.button("Delete Supplier"):
            res = delete_data(f"deleteSupplier/{selected_id}")
            if res.status_code == 200:
                st.success("Supplier deleted")
                st.rerun()
