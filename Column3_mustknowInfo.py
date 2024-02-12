import streamlit as st
col1, col2, col3 = st.columns([1, 2, 2])
col3.write ("Wanna take a look at the map?")
col3.map()