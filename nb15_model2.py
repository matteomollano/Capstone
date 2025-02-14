import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

df1 = pd.read_csv("datasets/UNSW_NB15_training-set.csv")
df2 = pd.read_csv("datasets/UNSW_NB15_testing-set.csv")

df1 = df1.drop(columns=['id'])
df2 = df2.drop(columns=['id'])

data = pd.concat([df1, df2], ignore_index=True)

print(data.head())

# all columns
# X = data.drop(columns=['label', 'attack_cat'])
# selected features
# features = ['ct_state_ttl', 'sttl', 'dttl', 'rate', 'sload', 'dload', 'sbytes', 'dbytes', 'smean', 'dmean', 'ct_dst_src_ltm', 'ct_srv_dst', 'dur']
features = ['sttl', 'dttl', 'ct_state_ttl', 'sload', 'dload', 'sbytes', 'dbytes', 'smean', 'dmean', 'rate', 'dur']
X = data[features]
# target variable
y = data['label']

# create 80% train set and 20% test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2) # can add random_state=42 if needed

# label encode the three object columns before training the model (not needed when using selected features)
# columns_to_encode = ['proto', 'service', 'state']
# label_encoders = {}
# for col in columns_to_encode:
#     le = LabelEncoder()
#     X_train[col] = le.fit_transform(X_train[col])
#     # X_test[col] = le.transform(X_test[col])
#     label_encoders[col] = le
#     X_test[col] = X_test[col].map(lambda s: le.transform([s])[0] if s in le.classes_ else -1)

# create the model and fit it to the train data
rf_model = RandomForestClassifier(n_estimators=100, n_jobs=-1) # can add random_state=42 if needed
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