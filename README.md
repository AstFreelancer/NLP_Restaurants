## Проект по классификации отзывов ресторанов с помощью [метода случайного леса](https://ru.wikipedia.org/wiki/Метод_случайного_леса)

**Стек:** Python, SQLite, scikit-learn, Flask.

### Предобработка данных и обучение модели в файле [model.py](model.py)

[Датасет с отзывами на английском языке](Restaurant_Reviews.json)

Для подготовки текстовых данных используется [стеммер Портера](https://ru.wikipedia.org/wiki/Стеммер_Портера). Кроме того, из текста удаляются все лишние символы, кроме латиницы.

Создается матрица термин-документ с помощью CountVectorizer.

Целевой признак - 0 или 1 (отрицательный или положительный отзыв).

75% датасета отводятся под обучающую выборку, 25% - под тестовую, чтобы избежать переобучения.

Обучаем нейронную сеть для классификации отзывов на позитивные и негативные.

### Работа с API в файле [app.py](app.py)

API реализован на Flask и включает следующие эндпойнты:
- predict - возвращает класс отзыва - 0 или 1;
![Predict screenshot](https://github.com/AstFreelancer/NLP_Restaurants/blob/main/screens/predict.PNG)
- reviews - возвращает сохраненные в БД отзывы с их предсказаниями (0 или 1);
![Reviews screenshot](https://github.com/AstFreelancer/NLP_Restaurants/blob/main/screens/reviews.PNG)
- reviews/analysis - подсчитывает статистику для каждого класса предсказаний;
![Analysis screenshot](https://github.com/AstFreelancer/NLP_Restaurants/blob/main/screens/analysis.PNG)
- chat - чатбот, о нем ниже. 

### Работа с SQLite

В файле [database.py](database.py) создается таблица reviews, в которой хранятся отзывы и предсказания модели для них. Эта таблица заполняется функцией save_prediction_to_db(), расположенной в файле app.py.

### Работа с OpenAI API

Подключение производится в функции get_openai_response(). Используется модель GPT-4.

Для успешной работы необходимо указать свой OpenAI API ключ в переменной openai.api_key.

Собственно диалоговая схема реализована в эндпойнте chat. Диалог с чатботом производится на английском языке.

Дежурные реплики определяются по наличию триггеров 'hello', 'my name is' и 'goodbye' в сообщении пользователя.

Здороваемся:
![Hello screenshot](https://github.com/AstFreelancer/NLP_Restaurants/blob/main/screens/hello.PNG)

Прощаемся:
![Goodbye screenshot](https://github.com/AstFreelancer/NLP_Restaurants/blob/main/screens/goodbye.PNG)

Знакомимся:
![Mynameis screenshot](https://github.com/AstFreelancer/NLP_Restaurants/blob/main/screens/mynameis.PNG)

Отзыв должен начинаться со слова review: с двоеточием. Вся часть сообщения после двоеточия и возможного пробела рассматривается как отзыв.

Полученный отзыв направляется нейросети на классификацию. В зависимости от ее предсказания пользователь получит сообщение "Thank you for your positive/negative review!".

Этот отзыв модель классифицировала как положительный:
![Positive screenshot](https://github.com/AstFreelancer/NLP_Restaurants/blob/main/screens/positivereview.PNG)

А этот - как негативный:
![Negative screenshot](https://github.com/AstFreelancer/NLP_Restaurants/blob/main/screens/negativereview.PNG)
