import pandas as pd, numpy as np
import matplotlib.pyplot as plt, seaborn as sns
from sklearn.ensemble import IsolationForest
import sys
sys.path.append("../../")
from utils.protocols import get_protocol_number

# load home pi dataset
train = pd.read_csv("../../datasets/real_pi_data.csv")
# convert protocol name to protocol number
train['proto'] = train['proto'].apply(get_protocol_number)

# get features and label for train set
X_train = train.drop(columns=['flow_id', 'label'])
y_train = train['label']

# load test data set (malicious flows)
test = pd.read_csv("../../datasets/malicious_flows.csv")
# convert protocol name to protocol number
test['proto'] = test['proto'].apply(get_protocol_number)

# get features and label for test set
X_test = test.drop(columns=['flow_id', 'label'])
y_test = test['label']

# create model
# contamination of 0.0015 = 0.15%
# anything that lies within the bottom 0.15% is malicious
contamination = 0.0015
model = IsolationForest(contamination=contamination, random_state=42)
model.fit(X_train)

# predictions on train data
print("Predictions on train data:")
train_predictions = model.predict(X_train)
train_binary_pred = np.where(train_predictions == -1, 1, 0)

# count results
train_num_malicious = np.sum(train_binary_pred == 1)
train_num_benign = np.sum(train_binary_pred == 0)
print(f"Number of malicious flows: {train_num_malicious}")
print(f"Number of benign flows: {train_num_benign}")
print(f"Accuracy: {train_num_benign / (train_num_benign + train_num_malicious)}")

# display malicious records (where binary_pred == 1)
train_malicious_records = train[train_binary_pred == 1]
print(f"\nMalicious flows (anomalies):")
print(train_malicious_records)


# predictions on malicious data
print("\n\nPredictions on malicious test data:")
test_predictions = model.predict(X_test)
test_binary_pred = np.where(test_predictions == -1, 1, 0)

# count results
test_num_malicious = np.sum(test_binary_pred == 1)
test_num_benign = np.sum(test_binary_pred == 0)
print(f"Number of malicious flows: {test_num_malicious}")
print(f"Number of benign flows: {test_num_benign}")
print(f"Accuracy: {test_num_malicious / (test_num_malicious + test_num_benign)}")

# display malicious records (where binary_pred == 1)
test_malicious_records = test[test_binary_pred == 1]
print(f"\nMalicious flows (anomalies):")
print(test_malicious_records)

# # plot to show the anomaly scores for each flow
# scores = model.decision_function(X_train)  # the lower, the more anomalous
# cutoff = np.percentile(scores, 100 * contamination)

# # plot using seaborn
# sns.histplot(scores, bins=50, kde=False, color='skyblue', edgecolor='black')
# plt.axvline(x=cutoff, color='red', linestyle='--', label=f"Cutoff = {cutoff:.4e}")
# plt.title("Anomaly Scores (Isolation Forest)", fontsize=14)
# plt.xlabel("Anomaly Score", fontsize=12)
# plt.ylabel("Number of Flows", fontsize=12)
# plt.legend()
# plt.show()


# save model to a file
import joblib
filename = "iso_forest_model.joblib"
joblib.dump(model, filename)