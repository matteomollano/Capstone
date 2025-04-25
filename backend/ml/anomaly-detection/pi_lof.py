import pandas as pd, numpy as np
from sklearn.neighbors import LocalOutlierFactor
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

# # model
# lof = LocalOutlierFactor(n_neighbors=5, novelty=True, contamination=0.0753)
# lof.fit(X_train.values)

# # fit the model and predict on train set
# print("Predictions on train data:")
# predictions = lof.predict(X_train.values)
# binary_pred = np.where(predictions == -1, 1, 0)

# # count anomalies detected
# num_malicious = np.sum(binary_pred == 1)
# num_benign = np.sum(binary_pred == 0)
# print(f"Number of malicious flows: {num_malicious}")
# print(f"Number of benign flows: {num_benign}")

# # display malicious records (where binary_pred == 1)
# malicious_records = train[binary_pred == 1]
# print(f"\nMalicious flows (anomalies):")
# print(malicious_records)


# # fit the model and predict on the test set (malicious flows)
# print("\n\nPredictions on test data:")
# predictions = lof.predict(X_test.values)
# binary_pred = np.where(predictions == -1, 1, 0)

# # count anomalies detected
# num_malicious = np.sum(binary_pred == 1)
# num_benign = np.sum(binary_pred == 0)
# print(f"Number of malicious flows: {num_malicious}")
# print(f"Number of benign flows: {num_benign}")

# # display malicious records (where binary_pred == 1)
# malicious_records = test[binary_pred == 1]
# print(f"\nMalicious flows (anomalies):")
# print(malicious_records)


print("\nTrying grid search:")

print("Finding best model using contamination")

best_n = 0
best_cont = 0
fp_count = np.inf
for n in [5, 10, 15, 20, 25, 30, 35, 40]:
    for cont in [0.075, 0.0751, 0.0752, 0.0753, 0.0754, 0.0755]:
        lof = LocalOutlierFactor(n_neighbors=n, contamination=cont, novelty=True)
        lof.fit(X_train.values)
        
        train_predictions = lof.predict(X_train.values)
        test_predictions = lof.predict(X_test.values)
        
        train_binary_pred = np.where(train_predictions == -1, 1, 0)
        test_binary_pred = np.where(test_predictions == -1, 1, 0)

        false_pos = np.sum(train_binary_pred == 1)
        num_malicious = np.sum(test_binary_pred == 1)
        
        # print(f"n: {n} | cont: {cont} false_pos: {false_pos} | num_malicious: {num_malicious}")
        
        if num_malicious == 2 and false_pos < fp_count:
            best_n = n
            best_cont = cont
            fp_count = false_pos
    # print()

print("Best params for model via contamination:")
print(f"Best n: {best_n}")
print(f"Best contamination: {best_cont}")
print(f"False positive count: {fp_count}")


from sklearn.preprocessing import StandardScaler

# scale train and test features before training models
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

"""below code is used to find threshold range to test on"""
# for n in [5, 10, 15, 20, 25, 30, 35, 40]:
#     lof = LocalOutlierFactor(n_neighbors=n, novelty=True)
#     lof.fit(X_train_scaled)
    
#     print(f"\n\nFor n = {n}")
#     train_scores = lof.decision_function(X_train_scaled)
#     print("Train scores:")
#     print("Min score (most anomalous):", round(np.min(train_scores), 4))
#     print("Max score (least anomalous):", round(np.max(train_scores), 4))
#     print("Mean score:", round(np.mean(train_scores), 4))
#     print("Standard deviation:", round(np.std(train_scores), 4))
    
#     test_scores = lof.decision_function(X_test_scaled)
#     print("\nTest scores:")
#     print("Min score (most anomalous):", round(np.min(test_scores), 4))
#     print("Max score (least anomalous):", round(np.max(test_scores), 4))
#     print("Mean score:", round(np.mean(test_scores), 4))
#     print("Standard deviation:", round(np.std(test_scores), 4))

# use threshold as the scoring metric (instead of contamination)
thresholds = np.linspace(-4.0, -3.0, 11)  # test from -4.0 to -3.0

best_n = 0
best_threshold = 0
fp_count = np.inf

print(f"\n\nFinding best model using threshold") 
for n in [5, 10, 15, 20, 25, 30, 35, 40]:
    for t in thresholds:
        lof = LocalOutlierFactor(n_neighbors=n, novelty=True)
        lof.fit(X_train_scaled)
        
        train_scores = lof.decision_function(X_train_scaled)
        test_scores = lof.decision_function(X_test_scaled)
        
        binary_train_pred = np.where(train_scores < t, 1, 0)  # 1 = anomaly, 0 = normal
        binary_test_pred = np.where(test_scores < t, 1, 0)    # same for test set
        
        false_pos = np.sum(binary_train_pred == 1)
        num_malicious = np.sum(binary_test_pred == 1)

        # print(f"n: {n} | Threshold: {round(t, 2)} | false pos: {false_pos} | num_malicious: {num_malicious}")
        
        if num_malicious == 2 and false_pos < fp_count:
            fp_count = false_pos
            best_n = n
            best_threshold = t
    # print()

print("Best params for model via threshold:")
print(f"Best n: {best_n}")
print(f"Best threshold: {best_threshold}")
print(f"Best false pos count: {fp_count}")