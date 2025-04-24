
import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import random

st.set_page_config(page_title="InsightHub Dashboard", layout="wide")
st.title("📊 InsightHub: Анализ отзывов локального бизнеса")

@st.cache_data
def load_data():
    return pd.read_csv("analyzed_reviews.csv")

data = load_data()

if st.sidebar.button("🔁 Сгенерировать новые отзывы"):
    businesses = ['Кафе Латте', 'Бар Ночной Лис', 'Булочная Уют', 'Магазин Вкусняшек', 'Пиццерия Додо', 'Кофейня WakeUp', 'Ресторан Кавказ', 'Бургерная #1']
    sentiments = ['positive', 'neutral', 'negative']
    reviews = {
        'positive': ['Отличное обслуживание!', 'Очень понравилось!', 'Лучшее место в городе!', 'Приду ещё!', 'Всё супер!'],
        'neutral': ['Нормально, без изысков.', 'Средне.', 'Обычное место.', 'Так себе, но сойдет.', 'Окей.'],
        'negative': ['Ужасный сервис!', 'Больше не приду.', 'Очень разочарован.', 'Не рекомендую.', 'Еда была холодной.']
    }
    new_data = []
    for _ in range(10):
        biz = random.choice(businesses)
        sentiment = random.choice(sentiments)
        review_text = random.choice(reviews[sentiment])
        lat = round(55.7 + random.uniform(-0.05, 0.05), 6)
        lon = round(37.6 + random.uniform(-0.05, 0.05), 6)
        new_data.append({
            'business_name': biz,
            'review_text': review_text,
            'sentiment_label': sentiment,
            'latitude': lat,
            'longitude': lon
        })
    new_df = pd.DataFrame(new_data)
    data = pd.concat([data, new_df], ignore_index=True)
    data.to_csv("analyzed_reviews.csv", index=False)
    st.success("✅ Новые отзывы добавлены!")

st.sidebar.header("🔍 Фильтры")
sentiments = st.sidebar.multiselect("Выберите тональность:", options=data['sentiment_label'].unique(), default=data['sentiment_label'].unique())
data_filtered = data[data['sentiment_label'].isin(sentiments)]

st.subheader("📈 Распределение отзывов по тональности")
sentiment_counts = data_filtered['sentiment_label'].value_counts()
fig1, ax1 = plt.subplots()
sentiment_counts.plot(kind='bar', color=['green', 'gray', 'red'], ax=ax1)
st.pyplot(fig1)

st.subheader("📊 Доля каждого типа отзывов")
fig2, ax2 = plt.subplots()
ax2.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', colors=['green', 'gray', 'red'])
ax2.axis('equal')
st.pyplot(fig2)

st.subheader("🗺️ Карта заведений и отзывов")
map_center = [data_filtered['latitude'].mean(), data_filtered['longitude'].mean()]
m = folium.Map(location=map_center, zoom_start=12)
marker_cluster = MarkerCluster().add_to(m)

for idx, row in data_filtered.iterrows():
    if pd.notnull(row['latitude']) and pd.notnull(row['longitude']):
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"{row['business_name']}\nSentiment: {row['sentiment_label']}",
            icon=folium.Icon(color='green' if row['sentiment_label'] == 'positive' else 'red' if row['sentiment_label'] == 'negative' else 'gray')
        ).add_to(marker_cluster)

folium_static(m)
