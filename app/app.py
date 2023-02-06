import streamlit as st
import pickle
import pandas as pd
from streamlit import session_state as session
from recommendation_engine import recommender

st.set_page_config(page_title="Skincare Recommender", page_icon=":shell:", layout="wide")

dataframe = None

def load_data():
    """
    load and cache data
    :return: sample skincare data
    """
    data = pd.read_csv("data/sample_skincare.csv")
    return data


sample_skincare = load_data()

with open("data/product_names.pkl", "rb") as f:
    products = pickle.load(f)

# ---- HEADER SECTION ----
with st.container():
    st.subheader("Need help with finding the right skincare product for you? :wave:")
    st.title("Skincare Recommender 🫧")
    st.write(
        "All products are scraped from Dermstore (https://www.dermstore.com/)"
    )


session.options = st.selectbox(label="Select Product", options=products)

st.text("")

session.slider_count = st.slider(label="Product Count", min_value=5, max_value=50)

base_recommend = st.radio("Recommend based on: ", ('Ingredients (Content-based)', 'Description (Collaborative)'))

by_ingred = False
by_desc  = False

if(base_recommend == 'Ingredients (Content-based)'):
    by_ingred = True
elif(base_recommend == 'Description (Collaborative)'):
    by_desc  = True

buffer1, col1, buffer2 = st.columns([1.45, 1, 1])

is_clicked = col1.button(label="Recommend")

if is_clicked:
    with st.spinner('Generating Recommendations...'):
        dataframe = recommender(session.options,sample_skincare, ingred=by_ingred, description=by_desc, product_count=session.slider_count)

st.text("")
st.text("")

table = None
if dataframe is not None:
    df = dataframe.reset_index(drop=True)
    res_df = df[['name','brand', 'link', 'price', 'prod_type']]
    view_dataframe = st.dataframe(res_df)

placeholder = st.empty()
remove_table = placeholder.button('Clear Table')
if remove_table:
    view_dataframe = None
