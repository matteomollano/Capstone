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
predictions = model.predict(X_train)
binary_pred = np.where(predictions == -1, 1, 0)

# count results
num_malicious = np.sum(binary_pred == 1)
num_benign = np.sum(binary_pred == 0)
print(f"Number of malicious flows: {num_malicious}")
print(f"Number of benign flows: {num_benign}")

# display malicious records (where binary_pred == 1)
malicious_records = train[binary_pred == 1]
print(f"\nMalicious flows (anomalies):")
print(malicious_records)


# predictions on malicious data
print("\n\nPredictions on malicious test data:")
predictions = model.predict(X_test)
binary_pred = np.where(predictions == -1, 1, 0)

# count results
num_malicious = np.sum(binary_pred == 1)
num_benign = np.sum(binary_pred == 0)
print(f"Number of malicious flows: {num_malicious}")
print(f"Number of benign flows: {num_benign}")

# display malicious records (where binary_pred == 1)
malicious_records = test[binary_pred == 1]
print(f"\nMalicious flows (anomalies):")
print(malicious_records)

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