import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import RandomizedSearchCV
from xgboost import XGBClassifier
from imblearn.under_sampling import RandomUnderSampler
from sklearn.metrics import classification_report
from preprocess_nb15 import preprocess_nb15
pd.set_option('display.max_columns', None)

# load datasets
train = pd.read_csv("../datasets/UNSW_NB15_training-set.csv")
test = pd.read_csv("../datasets/real_data_test.csv")
# filter out all flows with duration > 60 (to align with UNSW-NB15 dataset)
test = test[test.dur <= 60.0]

# get features for model
features = ['sttl', 'dttl', 'ct_state_ttl', 'sload', 'dload', 'sbytes', 'dbytes', 'smean', 'dmean', 'rate', 'dur']

# preprocess the UNSW-NB15 dataset
train = preprocess_nb15(train, test)

# set up train and test sets
X_train = train[features]
y_train = train['label']
X_test = test[features]
y_test = test['label']

# undersample data to create class balance
rus = RandomUnderSampler(random_state=42)
X_train_resampled, y_train_resampled = rus.fit_resample(X_train, y_train)

# perform standardization on train and test sets
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_resampled)
X_test_scaled = scaler.transform(X_test)

# model
xgb = XGBClassifier(eval_metric='logloss') # scale_pos_weight removed after using undersampling

# hyperparameter grid
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [3, 5, 7],
    'learning_rate': [0.01, 0.1, 0.3],
    'subsample': [0.7, 0.9, 1.0]
}

# random search with cross-validation
search = RandomizedSearchCV(xgb, param_grid, n_iter=20, cv=5, scoring='f1', random_state=42, n_jobs=-1, verbose=2)
search.fit(X_train_scaled, y_train_resampled)

# best model
best_model = search.best_estimator_
print("Best parameters:", search.best_params_)

# evaluation on default threshold
y_pred = best_model.predict(X_test_scaled)
false_positives = sum(y_pred == 1)
print(f"False positives on {len(y_test)} filtered home flows: {false_positives}")
print(classification_report(y_test, y_pred, zero_division=0))

# try on higher thresholds
y_prob = best_model.predict_proba(X_test_scaled)[:, 1]
for threshold in [0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.99]:
    y_pred_adjusted = (y_prob >= threshold).astype(int)
    false_positives_adjusted = sum(y_pred == 1)
    print(f"\n\nFalse positives with threshold {threshold}: {false_positives_adjusted}")
    print(classification_report(y_test, y_pred_adjusted, zero_division=0))