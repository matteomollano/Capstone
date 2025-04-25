import pandas as pd, numpy as np
import sys
sys.path.append("../")
from utils.protocols import get_protocol_number
from sklearn.ensemble import RandomForestClassifier
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

# load home pi dataset
benign_df = pd.read_csv("../datasets/real_pi_data.csv")
# convert protocol name to protocol number
benign_df['proto'] = benign_df['proto'].apply(get_protocol_number)

# load synthetically created malicious flows set
malicious_df = pd.read_csv("../datasets/malicious_flows_updated.csv")

# print("Benign flows:")
# print(benign_df.head())

# print("\nMalicious flows:")
# print(malicious_df.head())

data = pd.concat([benign_df, malicious_df], ignore_index=True)
data = shuffle(data, random_state=42)

X = data.drop(columns=['flow_id', 'label'])
y = data['label']

# split into train/test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# # train a random forest model
# model = RandomForestClassifier(n_estimators=100, random_state=42)
# model.fit(X_train, y_train)

# # predictions
# y_pred = model.predict(X_test)

# # evaluations
# print("Evaluations for first model (without hyperparameter tuning)")
# print("Accuracy:", accuracy_score(y_test, y_pred))
# print("Precision:", precision_score(y_test, y_pred))
# print("Recall:", recall_score(y_test, y_pred))
# print("F1 Score:", f1_score(y_test, y_pred))
# print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
# print("Classification Report:\n", classification_report(y_test, y_pred))



# HYPERPARAMETER TUNING
rf = RandomForestClassifier(random_state=42)

# define hyperparam grid
param_grid = {
    'n_estimators': [100, 150, 200, 250],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5],
    'min_samples_leaf': [1, 2]
}

# Set up GridSearch with 5-fold CV
grid_search = GridSearchCV(
    estimator=rf,
    param_grid=param_grid,
    cv=5,          # 5-fold cross-validation (uses StratifiedKFold by default for balanced class splits)
    scoring='f1',  # or 'accuracy', 'roc_auc', etc.
    n_jobs=-1,     # use all CPU cores
    # verbose=2
)

# fit on the full training set
grid_search.fit(X_train, y_train)

# best model and parameters
print(f"Best params: {grid_search.best_params_}")
print(f"Best score (CV): {grid_search.best_score_}")
best_model = grid_search.best_estimator_


# evaluate on train set
y_pred_train = best_model.predict(X_train)

# evaluate on test set
y_pred_test = best_model.predict(X_test)

print("Classification Report on train set:")
print(classification_report(y_train, y_pred_train) + "\n")

print("Classification Report on test set:")
print(classification_report(y_test, y_pred_test))


# feature importances
importances = best_model.feature_importances_
importances_df = pd.DataFrame({
    'Feature': X_train.columns,
    'Importance': importances
})

importances_df = importances_df.sort_values(by='Importance', ascending=False)
print("\nFeature importances:")
print(importances_df)


# other test set evaluations
print("\nOther test set evaluations:")
print("Accuracy:", accuracy_score(y_test, y_pred_test))
print("Precision:", precision_score(y_test, y_pred_test))
print("Recall:", recall_score(y_test, y_pred_test))
print("F1 Score:", f1_score(y_test, y_pred_test))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred_test))


# save the best model to a file
import joblib
filename = "random_forest_model.joblib"
joblib.dump(best_model, filename)