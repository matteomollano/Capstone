import pandas as pd, numpy as np
import sys
sys.path.append("../")
from utils.protocols import get_protocol_number
from sklearn.ensemble import RandomForestClassifier
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
pd.set_option('display.max_columns', None)


# load home pi dataset
benign_df = pd.read_csv("../datasets/real_pi_data.csv")
# convert protocol name to protocol number
benign_df['proto'] = benign_df['proto'].apply(get_protocol_number)

# load synthetically created malicious flows set
malicious_df = pd.read_csv("../datasets/malicious_flows_updated.csv")
# update num_packets and dbytes distribution to be more spread out
malicious_df['num_packets'] = np.random.randint(700, 900, size=len(malicious_df))
malicious_df['dbytes'] = np.random.randint(45000, 150000, size=len(malicious_df))
malicious_df = malicious_df[:200]


# combine the data for training
data = pd.concat([benign_df, malicious_df], ignore_index=True)
data = shuffle(data, random_state=42)

# get features and label
X = data.drop(columns=['flow_id', 'label'])
y = data['label']

# split into train/test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# best model from hyperparam tuning
best_params = {
    'max_depth': None,
    'min_samples_leaf': 1,
    'min_samples_split': 2,
    'n_estimators': 100
}
model = RandomForestClassifier(**best_params, random_state=42)

# fit on the full training set
model.fit(X_train, y_train)


# evaluate on train set
y_pred_train = model.predict(X_train)

# evaluate on test set
y_pred_test = model.predict(X_test)

# feature importances
importances = model.feature_importances_
importances_df = pd.DataFrame({
    'Feature': X_train.columns,
    'Importance': importances
})

importances_df = importances_df.sort_values(by='Importance', ascending=False)
print("\nFeature importances:")
print(importances_df)


# get top 2 features by importance
top_features = importances_df['Feature'].values[:2]
print("Using features:", top_features)

# subset training data
X_train_2d = X_train[top_features]
y_train_2d = y_train

# train new model
model_2d = RandomForestClassifier(**best_params, random_state=42)
model_2d.fit(X_train_2d, y_train_2d)


# create a meshgrid over the feature space
x_min, x_max = X_train_2d.iloc[:, 0].min() - 1, X_train_2d.iloc[:, 0].max() + 1
y_min, y_max = X_train_2d.iloc[:, 1].min() - 1, X_train_2d.iloc[:, 1].max() + 1
xx, yy = np.meshgrid(np.linspace(x_min, x_max, 300),
                     np.linspace(y_min, y_max, 300))

# predict labels across mesh grid
grid_points = np.c_[xx.ravel(), yy.ravel()]
Z = model_2d.predict(grid_points)
Z = Z.reshape(xx.shape)

# plot decision boundary and training points
plt.figure(figsize=(8, 5))
plt.contourf(xx, yy, Z, alpha=0.3, cmap=plt.cm.coolwarm)
plt.scatter(X_train_2d.iloc[:, 0], X_train_2d.iloc[:, 1],
            c=y_train_2d, edgecolor='k', cmap=plt.cm.coolwarm)
plt.xlabel(top_features[0])
plt.ylabel(top_features[1])
plt.title("Random Forest Decision Boundary Using Top 2 Features")
plt.grid(True)
plt.show()