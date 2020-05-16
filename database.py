import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import pickle

dataset = pd.read_csv('./data/bill_authentication.csv')
print(dataset.head())

X = dataset.iloc[:, 0:4].values
y = dataset.iloc[:, 4].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

pd.DataFrame(X_test).to_csv("./data/test_data.csv",index = False)
# print(pd.DataFrame(X_test))

# Feature Scaling
sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

clf = RandomForestClassifier(n_estimators=20, random_state=0)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)

print(confusion_matrix(y_test,y_pred))
print(classification_report(y_test,y_pred))
print(accuracy_score(y_test, y_pred))

filename = './data/finalized_model.sav'
pickle.dump(clf, open(filename, 'wb'))

with open(filename, 'rb') as file:  
    Pickled_RF_Model = pickle.load(file)

print(Pickled_RF_Model)