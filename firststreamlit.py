import streamlit as st

st.title("My Streamlit App")
st.write("Hello, World!")

# st.title("This is Title")
# st.header("This is Header")
# st.subheader("This is Subheader")
# st.write("This is normal text")
# st.markdown("This is **Markdown** text")

# Input Components
name = st.text_input("Enter your name")
st.write(f"Hello, {name}!")

number = st.number_input("Enter your age")
st.write(f"Your Age is: {number} years old")

# Button
if st.button("Submit"):
    st.write(f"Hello, {name}! You submitted")

# Slider
slider_value = st.slider("Select a value", 0, 100, 10)
st.write(f"Slider value: {slider_value}")

#Selectbox
selectbox_value = st.selectbox("Select City", ["Chennai", "Bangalore", "Salem", "Coimbatore"])
st.write(f"Selected City: {selectbox_value}")

#Checkbox
agree = st.checkbox("I agree to the terms and conditions")
if agree:
    st.write("You have agreed to the terms and conditions")


# Showing Messages
st.success("You have agreed to the terms and conditions")
st.warning("This is a warning message")
st.error("This is an error message")
st.info("This is an info message")