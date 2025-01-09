import streamlit as st
import pandas as pd
from datetime import datetime
import json
from snowflake.snowpark.context import get_active_session
from streamlit_extras.switch_page_button import switch_page

def get_recommendations(session, query, user_id):
    dummy_data = {
        'CATEGORY_1': ['Electronics', 'Fashion', 'Fashion', 'Electronics'],
        'CATEGORY_2': ['Phones', 'Clothing', 'Footwear', 'Laptops'],
        'CATEGORY_3': ['Smartphones', 'Traditional', 'Casual', 'Gaming'],
        'TITLE': [
            'iPhone 13 Pro Max',
            'Designer Wedding Saree',
            'Comfortable Running Shoes',
            'Gaming Laptop Pro'
        ],
        'PRODUCT_RATING': [4.5, 4.8, 4.3, 4.6],
        'SELLER_NAME': ['Apple Store', 'Fashion Hub', 'SportsZone', 'TechMart'],
        'SELLER_RATING': [4.8, 4.6, 4.4, 4.7],
        'DESCRIPTION': [
            'Latest iPhone model with advanced features',
            'Beautiful wedding saree with intricate designs',
            'Professional running shoes for athletes',
            'High-performance gaming laptop'
        ],
        'HIGHLIGHTS': [
            json.dumps(['5G ready', 'A15 chip', 'Pro camera system']),
            json.dumps(['Pure silk', 'Handcrafted', 'Designer piece']),
            json.dumps(['Cushioned sole', 'Breathable mesh', 'Durable']),
            json.dumps(['RTX 4080', '32GB RAM', '1TB SSD'])
        ],
        'IMAGE_LINKS': [
            json.dumps(['https://example.com/iphone.jpg']),
            json.dumps(['https://example.com/saree.jpg']),
            json.dumps(['https://example.com/shoes.jpg']),
            json.dumps(['https://example.com/laptop.jpg'])
        ],
        'PRODUCT_ID': [1001, 1002, 1003, 1004],
        'MRP': [149999, 25999, 8999, 189999],
        'SELLING_PRICE': [139999, 19999, 6999, 169999]
    }
    return pd.DataFrame(dummy_data)

if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'cart_items' not in st.session_state:
    st.session_state.cart_items = []
if 'current_product' not in st.session_state:
    st.session_state.current_product = None
if 'page' not in st.session_state:
    st.session_state.page = 'home'

def log_interaction(session, user_id, product_id, interaction_type):
    if user_id:
        try:
            interaction_data = {
                'INTERACTION_TIMESTAMP': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'INTERACTION_TYPE': interaction_type,
                'PRODUCT_ID': product_id,
                'USER_ID': user_id
            }
            interaction_df = pd.DataFrame([interaction_data])
            session.write_pandas(interaction_df, 'USER_INTERACTIONS')
        except Exception as e:
            st.error(f"Error logging interaction: {str(e)}")

def change_page(page_name):
    st.session_state.page = page_name
    st.session_state.rerun = True

def display_product_card(product, col, session):
    with col:
        with st.container():
            try:
                image_links = json.loads(product['IMAGE_LINKS'])
                if image_links and len(image_links) > 0:
                    st.image(image_links[0], use_column_width=True)
            except:
                st.write("Image not available")
           
            st.markdown(f"### {product['TITLE'][:50]}...")
            st.write(f"💰 MRP: ₹{product['MRP']:,.2f}")
            st.write(f"🏷️ Price: ₹{product['SELLING_PRICE']:,.2f}")
            st.write(f"⭐ Rating: {product['PRODUCT_RATING']}/5")
           
            cols = st.columns(2)
            with cols[0]:
                if st.button('View Details', key=f"view_{product['PRODUCT_ID']}"):
                    st.session_state.current_product = product
                    st.session_state.page = 'detail'
                    if st.session_state.user_id:
                        log_interaction(session, st.session_state.user_id, product['PRODUCT_ID'], 'view')
           
            with cols[1]:
                if st.button('Add to Cart', key=f"cart_{product['PRODUCT_ID']}"):
                    if product['PRODUCT_ID'] not in st.session_state.cart_items:
                        st.session_state.cart_items.append(product['PRODUCT_ID'])
                        if st.session_state.user_id:
                            log_interaction(session, st.session_state.user_id, product['PRODUCT_ID'], 'add_to_cart')
                        st.success('Added to cart!')

def display_product_details(product, session):
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        if st.button("← Back to Home"):
            st.session_state.page = 'home'
            st.session_state.current_product = None
            return

    st.title(product['TITLE'])
   
    col1, col2 = st.columns([1, 1])
   
    with col1:
        try:
            image_links = json.loads(product['IMAGE_LINKS'])
            if image_links and len(image_links) > 0:
                st.image(image_links[0], use_column_width=True)
        except:
            st.write("Image not available")
   
    with col2:
        st.markdown("### Product Details")
        st.write(f"**Category:** {product['CATEGORY_1']} > {product['CATEGORY_2']} > {product['CATEGORY_3']}")
        st.write(f"**Price:** ₹{product['SELLING_PRICE']:,.2f} _(MRP: ₹{product['MRP']:,.2f})_")
        st.write(f"**Seller:** {product['SELLER_NAME']} (⭐{product['SELLER_RATING']}/5)")
        st.write(f"**Product Rating:** ⭐{product['PRODUCT_RATING']}/5")
       
        cols = st.columns(2)
        with cols[0]:
            if st.button('Add to Cart', key=f"detail_cart_{product['PRODUCT_ID']}"):
                if product['PRODUCT_ID'] not in st.session_state.cart_items:
                    st.session_state.cart_items.append(product['PRODUCT_ID'])
                    if st.session_state.user_id:
                        log_interaction(session, st.session_state.user_id, product['PRODUCT_ID'], 'add_to_cart')
                    st.success('Added to cart!')
       
        with cols[1]:
            if st.button('Buy Now', key=f"buy_{product['PRODUCT_ID']}"):
                if st.session_state.user_id:
                    log_interaction(session, st.session_state.user_id, product['PRODUCT_ID'], 'purchase')
                st.success('Order placed successfully!')
   
    description, highlights = st.tabs(["Description", "Highlights"])
   
    with description:
        st.write(product['DESCRIPTION'])
   
    with highlights:
        try:
            highlights_list = json.loads(product['HIGHLIGHTS']) if product['HIGHLIGHTS'] else []
            for highlight in highlights_list:
                st.write(f"• {highlight}")
        except:
            st.write("No highlights available")

def main():
    st.set_page_config(page_title="Smart Shopping", layout="wide")
   
    session = get_active_session()
   
    with st.sidebar:
        st.title("🛍️ Smart Shopping")
       
        user_id = st.number_input("Enter User ID (optional)", min_value=0, value=0, step=1)
        if user_id > 0:
            st.session_state.user_id = user_id
       
        st.markdown("### 🛒 Shopping Cart")
        st.write(f"Items in cart: {len(st.session_state.cart_items)}")
       
        if st.button("Clear Cart"):
            st.session_state.cart_items = []
            st.success("Cart cleared!")
       
        if st.button("Go to Home"):
            st.session_state.page = 'home'
            st.session_state.current_product = None
   
    if st.session_state.page == 'home':
        st.title("🔍 Smart Product Search")
        search_query = st.text_input(
            "Search products or describe what you're looking for...",
            placeholder="E.g., 'suggest me a good wedding outfit in india' or 'comfortable running shoes'"
        )
       
        if search_query:
            with st.spinner('Finding the perfect products for you...'):
                try:
                    suggestions_df = get_recommendations(session, search_query, st.session_state.user_id or 1)
                   
                    if not suggestions_df.empty:
                        st.success('Here are some products you might like!')
                       
                        for i in range(0, len(suggestions_df), 2):
                            cols = st.columns(2)
                            if i < len(suggestions_df):
                                display_product_card(suggestions_df.iloc[i], cols[0], session)
                            if i + 1 < len(suggestions_df):
                                display_product_card(suggestions_df.iloc[i + 1], cols[1], session)
                    else:
                        st.info("No products found matching your search.")
               
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.markdown("### 📈 Trending Products")
            try:
                default_products = session.sql("SELECT * FROM PRODUCT_TABLE LIMIT 6").collect()
                default_df = pd.DataFrame(default_products)
            except:
                default_df = get_recommendations(session, "", 1)
           
            for i in range(0, len(default_df), 2):
                cols = st.columns(2)
                if i < len(default_df):
                    display_product_card(default_df.iloc[i], cols[0], session)
                if i + 1 < len(default_df):
                    display_product_card(default_df.iloc[i + 1], cols[1], session)
   
    elif st.session_state.page == 'detail' and st.session_state.current_product is not None:
        display_product_details(st.session_state.current_product, session)

if __name__ == "__main__":
    main()
