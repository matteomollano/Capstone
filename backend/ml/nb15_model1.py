import pandas as pd
from sklearn.ensemble import RandomForestClassifier
# from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

train = "datasets/UNSW_NB15_training-set.csv"
test = "datasets/UNSW_NB15_testing-set.csv"
train_data = pd.read_csv(train)
test_data = pd.read_csv(test)

print(train_data.head())

# have to label encode these three
# print(train_data['proto'].unique())
# print(train_data['service'].unique())
# print(train_data['state'].unique())

target_column = 'label'

# set us test and train datasets
columns_to_drop = ['id', 'attack_cat', 'label']
X_train = train_data.drop(columns=columns_to_drop)
y_train = train_data[target_column]

X_test = test_data.drop(columns=columns_to_drop)
y_test = test_data[target_column]

# label encode the three object columns before training the model
columns_to_encode = ['proto', 'service', 'state']
label_encoders = {}
for col in columns_to_encode:
    le = LabelEncoder()
    X_train[col] = le.fit_transform(X_train[col])
    # X_test[col] = le.transform(X_test[col])
    label_encoders[col] = le
    X_test[col] = X_test[col].map(lambda s: le.transform([s])[0] if s in le.classes_ else -1)

# create the model and fit it with the train data
rf_model = RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=42)
rf_model.fit(X_train, y_train)

# predictions
y_pred = rf_model.predict(X_test)

# accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.4f}")

# feature importances
importances = rf_model.feature_importances_
importances_df = pd.DataFrame({
    'Feature': X_train.columns,
    'Importance': importances
})

importances_df = importances_df.sort_values(by='Importance', ascending=False)
print("\nFeature importances:")
print(importances_df)