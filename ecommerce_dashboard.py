import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='white')

#functions
def create_daily_orders(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp_x').agg({
    "order_id": "nunique",
    "price": "sum"
    })

    daily_orders_df.index = daily_orders_df.index.strftime('%Y-%m')
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "monthly_revenue"
    }, inplace=True)

    return daily_orders_df

def create_sum_orders(df):
    sum_order_df = df.groupby("product_category_name_english").order_item_id.sum().sort_values(ascending=False).reset_index()
    return sum_order_df


url='https://drive.google.com/file/d/136N_d3L-OurX7ULdmuZQgm4vzaPn1AO6/view?usp=sharing'
url='https://drive.google.com/uc?id=' + url.split('/')[-2]
all_df = pd.read_csv(url)

datetime_columns = ["order_purchase_timestamp_x", "order_approved_at_x","order_delivered_carrier_date_x", "order_delivered_customer_date_x", "order_estimated_delivery_date_x"]
all_df.sort_values(by="order_purchase_timestamp_x", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_purchase_timestamp_x"].min()
max_date = all_df["order_purchase_timestamp_x"].max()

with st.sidebar:
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu Penjualan',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp_x"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp_x"] <= str(end_date))]

daily_orders_df = create_daily_orders(main_df)
sum_order_df = create_sum_orders(main_df)    

st.header(':shopping_bags: E Commerce Dashboard :shopping_bags:')
st.subheader('Daily Orders')

col1, col2 = st.columns(2)
 
with col1:
    ordertotal = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=ordertotal)
 
with col2:
    revenuetotal = format_currency(daily_orders_df.monthly_revenue.sum(), "USD", locale='es_CO') 
    st.metric("Total Revenue", value=revenuetotal)
 
fig, ax = plt.subplots(figsize=(32, 16))
ax.plot(
    daily_orders_df["order_purchase_timestamp_x"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="blue"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

st.subheader("Best & Worst Performing Product")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(52, 30))

colors = ["green", "grey", "grey", "grey", "grey"]

sns.barplot(x="order_item_id", y="product_category_name_english", data=sum_order_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Product", loc="center", fontsize=100)
ax[0].tick_params(axis ='y', labelsize=50)
ax[0].tick_params(axis ='x', labelsize=50)

sns.barplot(x="order_item_id", y="product_category_name_english", data=sum_order_df.sort_values(by="order_item_id", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("left")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=100)
ax[1].tick_params(axis='y', labelsize=50)
ax[0].tick_params(axis ='x', labelsize=50) 

st.pyplot(fig)


# Visualization for payment type
# declaring data
value_counts = main_df["payment_type"].value_counts()

# # plotting data on chart
st.title('Payment Type of All Sales')
fig_payment= px.pie(value_counts, labels=value_counts.index, names= main_df["payment_type"])
st.plotly_chart(fig_payment)


# Visualization for order status
# declaring data
order_status_counts = main_df["order_status_x"].value_counts()

# # plotting data on chart
st.title('Order Status of All Sales')
fig_payment= px.pie(order_status_counts, labels=order_status_counts.index, names= main_df["order_status_x"])
st.plotly_chart(fig_payment)


# Visualization of Customer Distribution
df_geo = main_df.iloc[:,25:]
df_geo.rename(columns={'geolocation_lat': 'LAT', 'geolocation_lng': 'LON'}, inplace=True)
df_geo['LAT'].astype(float)
df_geo['LON'].astype(float)
df_geo = df_geo.dropna()
st.title('Distribution of Customer Locations')
st.map(df_geo)
# st.write(df_geo)
