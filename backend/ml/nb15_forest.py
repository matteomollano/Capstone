import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from imblearn.under_sampling import RandomUnderSampler
from sklearn.metrics import classification_report
from sklearn.metrics import make_scorer, precision_score
from preprocess_nb15 import preprocess_nb15

# load datasets
train = pd.read_csv("../datasets/UNSW_NB15_training-set.csv")
test = pd.read_csv("../datasets/real_data_test.csv")
test = test[test.dur <= 60.0] # remove all flows with a duration > 60

# get feature set for model
features = ['sttl', 'dttl', 'ct_state_ttl', 'sload', 'dload', 'sbytes', 'dbytes', 'smean', 'dmean', 'rate', 'dur']

# preprocess the train set
train = preprocess_nb15(train, test)

# model setup with adjusted data
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

# create forest model
forest = RandomForestClassifier(random_state=42) # no class_weight='balanced' anymore

# hyperparameter tuning
param_grid = {
    'n_estimators': [100, 200],            # number of trees to build in the forest
    'max_depth': [10, 15, 20, None],       # maximum depth of each tree
    'min_samples_split': [2, 5],           # minimum number of samples required to split a node (higher values to generalize)
    # 'max_features': ['sqrt', 'log2'],    # number of features to consider for the best split
}

# create precision scorer so that random search cv uses precision as metric
precision_scorer = make_scorer(precision_score, pos_label=1)

# use stratified k-fold to maintain class balance for splits
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# perform random search
search = RandomizedSearchCV(forest, param_grid, n_iter=20, cv=skf, scoring=precision_scorer, n_jobs=-1, random_state=42, verbose=2)
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
    y_pred_adjusted = (y_prob > threshold).astype(int)
    false_positives_adjusted = sum(y_pred_adjusted == 1)
    print(f"\n\nFalse positives with threshold of {threshold}: {false_positives_adjusted}")
    print(classification_report(y_test, y_pred_adjusted, zero_division=0))