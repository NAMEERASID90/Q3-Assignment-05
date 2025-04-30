import streamlit as st
from cryptography.fernet import Fernet
import hashlib

# ---------- GLOBALS ----------
# In-memory data store
if "stored_data" not in st.session_state:
    st.session_state.stored_data = {}

# Login session and failed attempts
if "authenticated" not in st.session_state:
    st.session_state.authenticated = True
if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0

# Static login credentials (in production, use secure methods)
LOGIN_USERNAME = "admin"
LOGIN_PASSWORD_HASH = hashlib.sha256("password123".encode()).hexdigest()

# ---------- FUNCTIONS ----------
def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

def generate_key(passkey):
    hashed = hashlib.sha256(passkey.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(hashed[:32]))

def encrypt_data(plain_text, passkey):
    key = generate_key(passkey)
    return key.encrypt(plain_text.encode()).decode()

def decrypt_data(cipher_text, passkey):
    try:
        key = generate_key(passkey)
        return key.decrypt(cipher_text.encode()).decode()
    except Exception:
        return None

# ---------- LOGIN PAGE ----------
def login_page():
    st.title("🔐 Reauthorization Required")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == LOGIN_USERNAME and hash_passkey(password) == LOGIN_PASSWORD_HASH:
            st.session_state.authenticated = True
            st.session_state.failed_attempts = 0
            st.success("Login successful! You can now access secure features.")
            st.switch_page("Home")
        else:
            st.error("Invalid credentials!")

# ---------- INSERT DATA ----------
def insert_data_page():
    st.title("🔒 Store Secure Data")
    data_key = st.text_input("Enter a unique key (e.g., user1_data):")
    plain_text = st.text_area("Enter the text to store:")
    passkey = st.text_input("Enter secret phrase:", type="password", key="pass_input")


    if st.button("Encrypt & Store"):
        if data_key in st.session_state.stored_data:
            st.warning("This key already exists. Use a new key.")
        else:
            hashed_passkey = hash_passkey(passkey)
            encrypted_text = encrypt_data(plain_text, passkey)
            st.session_state.stored_data[data_key] = {
                "encrypted_text": encrypted_text,
                "passkey": hashed_passkey
            }
            st.success(f"Data stored successfully under key: {data_key}")

# ---------- RETRIEVE DATA ----------
def retrieve_data_page():
    if st.session_state.failed_attempts >= 3:
        st.session_state.authenticated = False
        st.warning("🔒 Too many failed attempts. Redirecting to login...")
        st.experimental_rerun()

    st.title("🔓 Retrieve Secure Data")
    data_key = st.text_input("Enter the key of the data:")
    passkey = st.text_input("Enter your passkey:", type="password")

    if st.button("Decrypt & Retrieve"):
        data_entry = st.session_state.stored_data.get(data_key)
        if not data_entry:
            st.error("❌ No data found with this key.")
            return

        hashed_input = hash_passkey(passkey)
        if hashed_input == data_entry["passkey"]:
            decrypted = decrypt_data(data_entry["encrypted_text"], passkey)
            if decrypted:
                st.success("Data decrypted successfully!")
                st.text_area("Decrypted Data:", decrypted, height=150)
                st.session_state.failed_attempts = 0
            else:
                st.error("Decryption failed. Invalid passkey.")
                st.session_state.failed_attempts += 1
        else:
            st.error("❌ Incorrect passkey.")
            st.session_state.failed_attempts += 1

        st.info(f"Failed Attempts: {st.session_state.failed_attempts} / 3")

# ---------- HOME PAGE ----------
def home_page():
    st.title("🔐 Secure Data Storage System")
    st.write("Select an option from the sidebar to proceed.")

# ---------- ROUTER ----------
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ("Home", "Insert Data", "Retrieve Data", "Login"))

    if not st.session_state.authenticated and page != "Login":
        login_page()
    elif page == "Home":
        home_page()
    elif page == "Insert Data":
        insert_data_page()
    elif page == "Retrieve Data":
        retrieve_data_page()
    elif page == "Login":
        login_page()

# Required imports for Fernet key generation
import base64

if __name__ == "__main__":
    main()
