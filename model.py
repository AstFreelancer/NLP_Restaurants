import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# с помощью алгоритма стемминга Портера подготовим тексты
def preprocess_dataset(dataset):
    import nltk

    nltk.download('stopwords')
    corpus = []
    for i, row in dataset.iterrows():
        review = preprocess_phrase(row['Review'])
        corpus.append(review)
    return corpus


def preprocess_phrase(phrase):
    import re
    from nltk.corpus import stopwords
    from nltk.stem.porter import PorterStemmer

    review = phrase.lower()
    review = re.sub('[^a-z]', ' ', review)  # убираем все символы, кроме букв
    review = review.split()
    ps = PorterStemmer()
    # все слова, кроме стоп-слов, заменяем на их основы
    review = [ps.stem(word) for word in review
              if not word in set(stopwords.words('english'))]
    review = ' '.join(review)
    return review

# Обучение модели
def train_model():
    dataset = pd.read_json('Restaurant_Reviews.json')

    corpus = preprocess_dataset(dataset)

    cv = CountVectorizer(max_features=1500)
    X = cv.fit_transform(corpus).toarray() # bag of words
    y = dataset.iloc[:, 1].values  # собственно целевой признак - 0 или 1

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25) # 75% - обучающая выборка, 25% - тестовая
    model = RandomForestClassifier(n_estimators=501,
                                   criterion='entropy')
    model.fit(X_train, y_train) # обучение на обучающей выборке
#    y_pred = model.predict(X_test) # предсказания на тестовой выборке

 #   example = preprocess_phrase("The food is very amazing.")
 #   example = cv.transform([example]).toarray()
 #   prediction = model.predict(example)
 #   print(prediction[0])

    return model, cv

# Инициализация модели и векторизатора
model, cv = train_model()