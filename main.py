import streamlit as st
from visualize import visualize_data

# --- Initialize session state for navigation ---
if "page" not in st.session_state:
    st.session_state.page = "Home"

# --- Persistent Sidebar Menu ---
with st.sidebar:
    st.title("Menu")
    
    # Menu as a list of clickable options
    if st.button("🏠 Home"):
        st.session_state.page = "Home"
    if st.button("📊 Analyze Whatsapp Chat"):
        st.session_state.page = "Analyze Whatsapp Chat"


# --- PAGE 1: Project Description ---
if st.session_state.page == "Home":
    st.title("📊 Harate: Chat Analysis")

    st.write(
        """
        Unlock the hidden stories within your WhatsApp chats! This tool transforms your exported `.txt` files into powerful insights.

        **Discover:**

        * **Who dominates the conversation:** Identify your most active chatters.
        * **When your group is most lively:** Uncover peak chat times.
        * **How your chats evolve over time:** Visualize message trends and activity patterns.
        * **A clear overview of your chat history:** Explore your activity with an intuitive GitHub-style heatmap.

        Upload your `.txt` chat export on the next page and start exploring!
        """
    )

    # Button to switch to Analyze whatsapp Chat
    if st.button("🚀 Start Analyzing Whatsapp Chats"):
        st.session_state.page = "Analyze Whatsapp Chat"
        st.rerun()

# --- PAGE 2: File Upload & Analysis ---
elif st.session_state.page == "Analyze Whatsapp Chat":
    # Button to go back to Home
    if st.button("⬅️ Back to Home"):
        st.session_state.page = "Home"
        st.rerun()

    st.title("📂 Upload WhatsApp Chat File")

    uploaded_file = st.file_uploader("Upload your WhatsApp chat (.txt)", type=["txt"])

    if uploaded_file is not None:
        visualize_data(uploaded_file)


