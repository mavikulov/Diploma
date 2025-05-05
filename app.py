import streamlit as st
import json
from confluent_kafka import Consumer


st.set_page_config(page_title="DATA STOCK DATA", layout="wide")

print(st.session_state)
if "price" not in st.session_state:
    st.session_state["price"] = []

bootstrap_servers = 'localhost:9095'
topic = "stock_price"
config = {
    "bootstrap.servers" : bootstrap_servers,
    "group.id": 'my_consumers'
}

consumer = Consumer(config)
consumer.subscribe([topic])

st.title("Prices")
chart_holder = st.empty()

while True:
    message = consumer.poll(1000)
    if message is not None:
        stock_data = json.loads(message.value().decode('utf-8'))
    st.session_state["price"].append(stock_data["price"])
    chart_holder.line_chart(st.session_state["price"])

