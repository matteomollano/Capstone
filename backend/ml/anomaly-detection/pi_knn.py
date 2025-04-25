import pandas as pd, numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import seaborn as sns
import sys
sys.path.append("../../")
from utils.protocols import get_protocol_number
from sklearn.metrics import classification_report

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



# normalize features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)



# function to visualize anomaly scores distribution
def anomaly_scores_dist(n_neighbors, train_anomaly_scores, test_anomaly_scores):
    # plot train anomaly scores
    sns.histplot(train_anomaly_scores, color='lightblue', label='Train Scores', stat='density', bins=20)

    # plot test anomaly scores
    sns.histplot(test_anomaly_scores, color='green', label='Test Scores', stat='density', bins=20)

    # plot the threshold as a vertical line
    plt.axvline(x=threshold, color='red', linestyle='--', label=f'Threshold: {threshold:.2f}')

    # labels and title
    plt.xlabel('Anomaly Score')
    plt.ylabel('Density')
    plt.title(f'Anomaly Score Distribution (Train vs Test) for k = {n_neighbors}')
    plt.legend(loc='upper left')

    # set y-axis limit to a reasonable range (e.g., between 0 and 2, since the density max is under 2)
    plt.ylim(0, 0.005)

    # show plot
    plt.show()



# # hyperparameter tuning (finding best n)
# for n in [5, 10, 15, 20, 25, 30, 35, 40]:
#     print(f"\nFOR N = {n}")
#     knn = NearestNeighbors(n_neighbors=n)
#     knn.fit(X_train_scaled)

#     # determine a threshold for anomaly — for now, use the max distance from training set as cutoff
#     # (can also use a percentile, like 95th)
#     train_distances, _ = knn.kneighbors(X_train_scaled)
#     threshold = train_distances.mean(axis=1).max()
#     # threshold = np.percentile(train_distances.mean(axis=1), 99.95)


#     # === Detect anomalies in TRAIN set ===
#     print("Train set results:")
#     # use mean distance to k-nearest neighbors as anomaly score for training data
#     train_anomaly_scores = train_distances.mean(axis=1)

#     # predict anomalies
#     train_y_pred = (train_anomaly_scores > threshold).astype(int)

#     # count anomalies detected in train set
#     train_num_malicious = np.sum(train_y_pred == 1)
#     train_num_benign = np.sum(train_y_pred == 0)
#     print(f"[Train Set] Number of malicious flows: {train_num_malicious}")
#     print(f"[Train Set] Number of benign flows: {train_num_benign}")
#     print(f"[Train Set] Accuracy: {train_num_benign / (train_num_benign + train_num_malicious)}")

#     # display anomalous records from train set
#     train_malicious_flows = train[train_y_pred == 1]
#     # print(f"[Train Set] Malicious flows:")
#     # print(train_malicious_flows)



#     # === Detect anomalies in TEST set ===
#     print("\nTest set results:")

#     # get distances to the k-nearest neighbors for each test point
#     test_distances, _ = knn.kneighbors(X_test_scaled)

#     # use the mean distance as the anomaly score
#     test_anomaly_scores = test_distances.mean(axis=1)

#     # predict anomalies
#     test_y_pred = (test_anomaly_scores > threshold).astype(int)

#     # count anomalies detected
#     test_num_malicious = np.sum(test_y_pred == 1)
#     test_num_benign = np.sum(test_y_pred == 0)
#     print(f"[Test Set] Number of malicious flows: {test_num_malicious}")
#     print(f"[Test Set] Number of benign flows: {test_num_benign}")
#     print(f"[Test Set] Accuracy: {test_num_malicious / (test_num_malicious + test_num_benign)}")

#     # display malicious records (where binary_pred == 1)
#     test_malicious_flows = test[test_y_pred == 1]
#     print(f"[Test Set] Malicious flows (anomalies):")
#     print(test_malicious_flows)
    
    

#     # display anomaly scores for train set vs test set
#     # (used to see how far outside of the train boundary the test malicious flows are)
#     print(f"\nTrain anomaly score range: {train_anomaly_scores.min()} to {train_anomaly_scores.max()}")
#     print(f"Test anomaly score range: {test_anomaly_scores.min()} to {test_anomaly_scores.max()}")
#     print(f"Threshold used: {threshold}")
#     print(f"Range difference: {test_anomaly_scores.max() - threshold}\n\n")
    
#     # display anomaly scores dist plot
#     # anomaly_scores_dist(n, train_anomaly_scores, test_anomaly_scores)
    
    
# final model
best_model = NearestNeighbors(n_neighbors=7)
best_model.fit(X_train_scaled)

# determine a threshold for anomaly — use the max distance from training set as cutoff
train_distances, _ = best_model.kneighbors(X_train_scaled)
threshold = train_distances.mean(axis=1).max()

# evaluations
# === Detect anomalies in TRAIN set ===
print("Train set results:")

# use mean distance to k-nearest neighbors as anomaly score for training data
train_anomaly_scores = train_distances.mean(axis=1)

# predict anomalies
train_y_pred = (train_anomaly_scores > threshold).astype(int)

# count anomalies detected in train set
train_num_malicious = np.sum(train_y_pred == 1)
train_num_benign = np.sum(train_y_pred == 0)
print(f"[Train Set] Number of malicious flows: {train_num_malicious}")
print(f"[Train Set] Number of benign flows: {train_num_benign}")
print(f"[Train Set] Accuracy: {train_num_benign / (train_num_benign + train_num_malicious)}")


# === Detect anomalies in TEST set ===
print("\nTest set results:")

# get distances to the k-nearest neighbors for each test point
test_distances, _ = best_model.kneighbors(X_test_scaled)

# use the mean distance as the anomaly score
test_anomaly_scores = test_distances.mean(axis=1)

# predict anomalies
test_y_pred = (test_anomaly_scores > threshold).astype(int)

# count anomalies detected
test_num_malicious = np.sum(test_y_pred == 1)
test_num_benign = np.sum(test_y_pred == 0)
print(f"[Test Set] Number of malicious flows: {test_num_malicious}")
print(f"[Test Set] Number of benign flows: {test_num_benign}")
print(f"[Test Set] Accuracy: {test_num_malicious / (test_num_malicious + test_num_benign)}")

# display malicious records (where binary_pred == 1)
test_malicious_flows = test[test_y_pred == 1]
print(f"[Test Set] Malicious flows (anomalies):")
print(test_malicious_flows)


# display anomaly scores for train set vs test set
# (used to see how far outside of the train boundary the test malicious flows are)
print(f"\nTrain anomaly score range: {train_anomaly_scores.min()} to {train_anomaly_scores.max()}")
print(f"Test anomaly score range: {test_anomaly_scores.min()} to {test_anomaly_scores.max()}")
print(f"Threshold used: {threshold}")
print(f"Range difference: {test_anomaly_scores.max() - threshold}")


# save model, scaler, and threshold value to a file
import joblib
filename = "knn_model_with_scaler.joblib"
joblib.dump({"model": best_model, "scaler": scaler, "threshold": threshold}, filename)