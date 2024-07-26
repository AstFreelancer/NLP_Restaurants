import openai
from flask import Flask, request, jsonify
from model import preprocess_phrase, model, cv
import sqlite3

openai.api_key = 'you_key_here'

app = Flask(__name__)

# Сохраняем предсказание в БД
def save_prediction_to_db(review, prediction):
    conn = sqlite3.connect('reviews.db')
    c = conn.cursor()
    c.execute("INSERT INTO reviews (review, prediction) VALUES (?, ?)", (review, prediction))
    conn.commit()
    conn.close()

# Получаем ответ от OpenAI API
def get_openai_response(prompt):
    response = openai.Completion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message['content'].strip()

# Эндпойнт для предсказания класса отзыва (0 или 1) и сохранения результатов в БД
@app.route('/predict', methods=['POST'])
def predict():
    if not request.json or 'review' not in request.json:
        return jsonify({'ошибка': 'Отсутствует отзыв'}), 400

    review = request.json['review']
    processed_review = preprocess_phrase(review)
    vectorized_review = cv.transform([processed_review]).toarray()

    if not vectorized_review.any():
        return jsonify({'ошибка': 'Вектор текста состоит из нулей.'}), 400

    prediction = model.predict(vectorized_review)
    prediction = int(prediction[0])

    save_prediction_to_db(review, prediction)

    return jsonify({'prediction': prediction})

# Эндпойнт для извлечения всех сохраненных отзывов и соответствующих предсказаний из БД
@app.route('/reviews', methods=['GET'])
def get_reviews():
    conn = sqlite3.connect('reviews.db')
    c = conn.cursor()
    c.execute("SELECT * FROM reviews")
    rows = c.fetchall()
    conn.close()
    reviews = [{'id': row[0], 'review': row[1], 'prediction': row[2]} for row in rows]
    return jsonify(reviews)

# Эндпойнт для анализа сохраненных результатов - подсчета статистики предсказаний для каждого класса
@app.route('/reviews/analysis', methods=['GET'])
def analyze_reviews():
    conn = sqlite3.connect('reviews.db')
    c = conn.cursor()
    c.execute("SELECT prediction, COUNT(*) FROM reviews GROUP BY prediction")
    rows = c.fetchall()
    conn.close()
    analysis = [{'prediction': row[0], 'count': row[1]} for row in rows]
    return jsonify(analysis)

# Эндпойнт для чатбота
@app.route('/chat', methods=['POST'])
def chat():
    if not request.is_json:
        return jsonify({'ошибка': 'Content-Type должен быть application/json'}), 400

    data = request.get_json()

    if 'message' not in data:
        return jsonify({'ошибка': 'Отсутствует сообщение'}), 400

    user_message = data['message']

    if not user_message.strip():
        return jsonify({'ошибка': 'Сообщение пусто'}), 400

    # светские церемонии
    if 'hello' in user_message.lower():
        response_message = "Hello! What's your name?"
    elif 'my name is' in user_message.lower():
        user_name = user_message.split(" ")[-1]
        response_message = f"Nuce to meet you, {user_name}!"
    elif 'goodbye' in user_message.lower() or 'bye' in user_message.lower():
        response_message = "Goodbye!"
    elif 'review:' in user_message.lower():
        review = user_message[user_message.lower().index('review:') + len('review:'):].strip()
        if review:
            processed_review = preprocess_phrase(review)
            vectorized_review = cv.transform([processed_review]).toarray()

            if vectorized_review.any():
                prediction = model.predict(vectorized_review)
                prediction = int(prediction[0])
                save_prediction_to_db(review, prediction)
                response_message = f"Thank you for your {'positive' if prediction == 1 else 'negative'} review!"
            else:
                response_message = "Cannot process the review."
        else:
            response_message = "Please type your review in the format 'Review: ...'."
    else: # основной диалог
        response_message = get_openai_response(user_message)

    return jsonify({'response': response_message})

if __name__ == '__main__':
    app.run(debug=True)