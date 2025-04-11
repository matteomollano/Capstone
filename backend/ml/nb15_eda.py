import pandas as pd

train = "../datasets/UNSW_NB15_training-set.csv"
test = "../datasets/UNSW_NB15_testing-set.csv"

train_data = pd.read_csv(train)
# print(train_data.head())
# print(train_data.isna().sum())

test_data = pd.read_csv(test)
# print(test_data.head())
# print(test_data.isna().sum())

pd.set_option('display.max_columns', None)
print("\nDescribing train data:")
print(train_data.describe())

print("\nDescribing test data:")
print(test_data.describe())

attack_categories = test_data['attack_cat'].unique()
print(f"\nAttack categories: {attack_categories}")

security_status = test_data['label'].unique()
print(f"Security status: {security_status}")

# can predict whether it is normal (0) or an attack record (1)
# OR
# try to predict the specific attack category

# number of benign records in each dataset
train_benign_records = train_data[train_data['label'] == 0]
num_train_benign_records = train_benign_records.shape[0]

test_benign_records = test_data[test_data['label'] == 0]
num_test_benign_records = test_benign_records.shape[0]

print('\ntrain benign records:', num_train_benign_records)
print('test benign records:', num_test_benign_records)

# number of attack records in each dataset
train_attack_records = train_data[train_data['label'] == 1]
num_train_attack_records = train_attack_records.shape[0]

test_attack_records = test_data[test_data['label'] == 1]
num_test_attack_records = test_attack_records.shape[0]

print(f"\nTrain set attack records: {num_train_attack_records}")
print(f"Test set attack records: {num_test_attack_records}")

print(f"\nFeatures: {train_data.columns}")

# from inspection of the dataset, attack records tend to have higher values in the following columns:
# - 10: sttl,Integer,Source to destination time to live value
# - 11: dttl,Integer,Destination to source time to live value
# - 17: Spkts,integer,Source to destination packet count
# - 18: Dpkts,integer,Destination to source packet count
# - 19: swin,integer,Source TCP window advertisement value
# - 20: dwin,integer,Destination TCP window advertisement value
# - 21: stcpb,integer,Source TCP base sequence number
# - 22: dtcpb,integer,Destination TCP base sequence number

# and larger, random decimal numbers in:
# - 27: Sjit,Float,Source jitter (mSec)
# - 28: Djit,Float,Destination jitter (mSec)
# - 29: Stime,Timestamp,record start time
# - 30: Ltime,Timestamp,record last time
# - 31: Sintpkt,Float,Source interpacket arrival time (mSec)
# - 32: Dintpkt,Float,Destination interpacket arrival time (mSec)
# - 33: tcprtt,Float,"TCP connection setup round-trip time, the sum of synack and ackdat."
# - 34: synack,Float,"TCP connection setup time, the time between the SYN and the SYN_ACK packets."
# - 35: ackdat,Float,"TCP connection setup time, the time between the SYN_ACK and the ACK packets."