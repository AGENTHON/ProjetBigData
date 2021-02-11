import pandas as pd
import numpy as np
import nltk
nltk.download('stopwords')
nltk.download('wordnet')

from sklearn import feature_extraction, model_selection, pipeline, svm, metrics
from utils import preprocess_text, macroDisparateImpact
print("Starting processing of data ...")


# Resources
df = pd.read_json("./data.json")
label = pd.read_csv("./label.csv")
category = pd.read_csv("./categories_string.csv")


# preprocessing
stopwords = nltk.corpus.stopwords.words("english")
df["text_clean"] = df["description"].apply(lambda x: 
      preprocess_text(x, flg_stemm=False, flg_lemm=True, 
      lst_stopwords=stopwords))

df["y"]=label.Category.values

# split dataset
dtf_train, dtf_test = model_selection.train_test_split(df, test_size=0.2, random_state=211101) 
# get target
y_train = dtf_train["y"].values
y_test = dtf_test["y"].values

y = dtf_train["y"]


# Vectorizer before feature selection
vectorizer = feature_extraction.text.TfidfVectorizer(max_features=10000, ngram_range=(1,2))

corpus = dtf_train["text_clean"]
vectorizer.fit(corpus)
X_train = vectorizer.transform(corpus)
dic_vocabulary = vectorizer.vocabulary_


# define classifier : linear kernel SVM
classifier=svm.LinearSVC(max_iter=5000) 

model = pipeline.Pipeline([("vectorizer", vectorizer),  
                           ("classifier", classifier)])
## train classifier
model["classifier"].fit(X_train, y_train)


## test
X_test = dtf_test["text_clean"].values

predicted = model.predict(X_test)


classes = np.unique(y_test)
y_test_array = pd.get_dummies(y_test, drop_first=False).values
    
## Accuracy, Precision
accuracy = metrics.accuracy_score(y_test, predicted)
print("Accuracy:",  round(accuracy,2))
macro_f1=metrics.f1_score(y_test, predicted, average='macro')
print("Macro F1 Score:", round(macro_f1,2))
score_test=macroDisparateImpact(dtf_test,y_test)
score_prediction=macroDisparateImpact(dtf_test,predicted)
print("Fairness impact on test set:",score_test)
print("Fairness impact on predicted set:",score_prediction)

predict=pd.DataFrame(columns=["true","predicted"])
predict.true=y_test
predict.predicted=predicted

# to csv
predict.to_csv('./predict.csv',index=False)

