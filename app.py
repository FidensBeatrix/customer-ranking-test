import streamlit as st

st.set_page_config(
    page_title="Customer Ranking",
    page_icon="🎮",
    layout="wide",
)

st.title("Customer Ranking")
st.write("If you can see this, the Streamlit browser app works 🎉")

name = st.text_input("Your name")

if st.button("Test button"):
    if name:
        st.success(f"Hello {name}! Everything works.")
    else:
        st.warning("Enter a name first.")
