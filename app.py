import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import os
import random
from datetime import datetime
from predict import predict
from database import taxi_db

# Инициализация базы данных
taxi_db.init_db()

# Загрузка CSS
def load_css():
    with open("styles.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

st.set_page_config(layout="wide", page_title="Indriver Kazakhstan", page_icon="🚗")

# хедер
st.markdown("""
<div class="header-container">
    <h1 class="main-header">🚗 Indriver Kazakhstan</h1>
    <div class="kz-flag">
        <h3>🇰🇿 Лучший сервис такси в Казахстане</h3>
    </div>
</div>
""", unsafe_allow_html=True)

# Сайдбар с выбором города
with st.sidebar:
    st.markdown('<div class="city-selector">', unsafe_allow_html=True)
    city = st.selectbox("🏙️ Выберите город:", 
                       ["Алматы", "Астана", "Шымкент", "Актобе", "Караганда"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Показать доступных водителей
    if st.button("👨‍💼 Показать доступных водителей", use_container_width=True):
        drivers = taxi_db.get_available_drivers()
        if not drivers.empty:
            st.sidebar.write("### 🚕 Доступные водители:")
            for _, driver in drivers.iterrows():
                st.sidebar.markdown(f"""
                <div class="driver-info">
                    <div class="driver-name">{driver['name']}</div>
                    <div class="driver-car">{driver['car_model']} ({driver['car_number']})</div>
                    <div class="driver-rating">⭐ {driver['rating']}/5.0</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.sidebar.warning("Нет доступных водителей")

# Основной контент
tab1, tab2 = st.tabs(["📸 Анализ автомобиля", "📋 История заказов"])

with tab1:
    st.write("Загрузите фотографию автомобиля, чтобы определить, грязный ли он и есть ли на нем повреждения.")

    uploaded_file = st.file_uploader("Выберите изображение...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Отображаем изображение
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(image, caption='Загруженное изображение', use_container_width=True)

        with col2:
            st.write("### Анализ...")
            # Сохраняем временный файл для predict.py
            with open("temp_image.jpg", "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Получаем предсказание
            try:
                if image.size[0] < 100 or image.size[1] < 100:
                    st.warning("Изображение слишком маленькое для анализа!")
                else:
                    with st.spinner('Модель анализирует изображение...'):
                        prediction = predict("temp_image.jpg")
                    st.success("Анализ завершен!")

                    if prediction and prediction['cleanliness']['class'] != 'ошибка':
                        # Отображение результатов анализа
                        st.markdown("""
                        <div class="analysis-result">
                            <h4>📊 Результаты анализа:</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col_clean, col_damage = st.columns(2)
                        
                        with col_clean:
                            st.subheader("🧹 Чистота:")
                            cleanliness_class = prediction['cleanliness']['class'].capitalize()
                            cleanliness_conf = prediction['cleanliness']['confidence']
                            st.progress(cleanliness_conf)
                            st.metric(label="Результат", value=cleanliness_class, delta=f"{cleanliness_conf:.1%} уверенности")
                            
                        with col_damage:
                            st.subheader("🔧 Повреждения:")
                            damage_class = prediction['damage']['class'].capitalize()
                            damage_conf = prediction['damage']['confidence']
                            st.progress(damage_conf)
                            st.metric(label="Результат", value=damage_class, delta=f"{damage_conf:.1%} уверенности")
                        
                        # функционал вызова такси
                        st.markdown("---")
                        st.subheader("🚕 Вызов такси")
                        
                        # Проверяем доступных водителей
                        drivers = taxi_db.get_available_drivers()
                        
                        if not drivers.empty:
                            # Выбираем случайного водителя
                            random_driver = drivers.sample(1).iloc[0]
                            driver_id = random_driver['id']
                            driver_name = random_driver['name']
                            driver_car = random_driver['car_model']
                            
                            # Генерация цены
                            price = random.randint(500, 2000)
                            
                            st.markdown(f"""
                            <div class="driver-card">
                                <h3>Найден водитель! 🎉</h3>
                                <p><strong>👨‍💼 Водитель:</strong> {driver_name}</p>
                                <p><strong>🚗 Автомобиль:</strong> {driver_car}</p>
                                <p><strong>⭐ Рейтинг:</strong> {random_driver['rating']}/5.0</p>
                                <div class="price-tag">
                                    💰 Цена: {price} ₸
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if st.button("✅ Вызвать такси", type="primary", use_container_width=True):
                                # Создаем заказ
                                order_id = taxi_db.create_order(
                                    driver_id=driver_id,
                                    from_address=f"ул. Примерная, 123, {city}",
                                    to_address=f"ул. Назначения, 456, {city}",
                                    price=price,
                                    cleanliness=prediction['cleanliness']['class'],
                                    damage=prediction['damage']['class'],
                                    cleanliness_confidence=prediction['cleanliness']['confidence'],
                                    damage_confidence=prediction['damage']['confidence']
                                )
                                st.success(f"🎉 Такси вызвано! Номер заказа: #{order_id}")
                                st.info(f"🚗 Водитель {driver_name} скоро приедет в {city}")
                        else:
                            st.warning("😔 К сожалению, сейчас нет доступных водителей")

                    else:
                        st.error("Ошибка при анализе изображения.")

            except Exception as e:
                st.error(f"Произошла ошибка при анализе: {e}")
            finally:
                # Удаляем временный файл
                if os.path.exists("temp_image.jpg"):
                    os.remove("temp_image.jpg")

with tab2:
    st.header("📋 История ваших заказов")
    st.info("Функция истории заказов в разработке...")
    
    # Пример истории
    st.markdown("""
    <div class="history-item">
        <strong>Заказ #001</strong> - 1500 ₸ - Алматы<br>
        <small>Водитель: Иван Петров (Kia Rio)</small>
    </div>
    <div class="history-item">
        <strong>Заказ #002</strong> - 1200 ₸ - Астана<br>
        <small>Водитель: Мария Сидорова (Hyundai Solaris)</small>
    </div>
    """, unsafe_allow_html=True)

# Футер
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d;">
    <p>🚗 Indriver Kazakhstan • 🇰🇿 С любовью к Казахстану</p>
    <p>© 2025 Все права защищены</p>
</div>
""", unsafe_allow_html=True)