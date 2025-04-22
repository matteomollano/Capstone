import pandas as pd, numpy as np
import sys
sys.path.append("../")
from utils.protocols import get_protocol_number

# load test data set (malicious flows)
test = pd.read_csv("../datasets/malicious_flows.csv")
# convert protocol name to protocol number
test['proto'] = test['proto'].apply(get_protocol_number)

# print("\nTest head:")
# print(test.head())

# function to generate new malicious flows
def generate_malicious_flows(df, num_flows):
    new_malicious_flows = []
    last_flow_id = df.iloc[-1]['flow_id']
    for i in range(num_flows):
        # randomly select a row from the original dataset
        row = df.sample(1).iloc[0]

        # create a new flow_id
        new_flow_id = last_flow_id + i + 1
        
        # choose randomly between TCP (6) and UDP (17)
        proto = np.random.choice([6, 17])

        # choose a random port number for sport and dport
        new_port_number = np.random.randint(1024, 65535)

        # set sttl/dttl to 64, therefore ct_state_ttl is 1
        new_sttl = 64
        new_dttl = 64
        new_ct_state_ttl = 1
        
        # randomly generate new sbytes/dbytes and dur
        new_sbytes = row['sbytes'] + np.random.randint(-300, 300)
        new_dbytes = row['dbytes'] + np.random.randint(-300, 300)
        new_dur = row['dur'] + np.random.uniform(-1, 1)
        
        # calculate new sload and dload
        new_sload = (new_sbytes * 8) / new_dur
        new_dload = (new_dbytes * 8) / new_dur
        
        # randomly generate new num_packets
        new_num_packets = row['num_packets'] + np.random.randint(-50, 50)
        
        # calculate new rate from new_num_packets and new_dur
        new_rate = new_num_packets / new_dur
        
        # calculate new smean/dmean from new sbytes/dbytes and new_num_packets
        new_smean = new_sbytes / new_num_packets
        new_dmean = new_dbytes / new_num_packets

        # create a new flow record
        new_flow = {
            'flow_id': int(new_flow_id),
            'sport': new_port_number,
            'dport': new_port_number,
            'proto': proto,
            'sttl': new_sttl,
            'dttl': new_dttl,
            'ct_state_ttl': new_ct_state_ttl,
            'sload': round(new_sload, 2),
            'dload': round(new_dload, 2),
            'sbytes': int(new_sbytes),
            'dbytes': int(new_dbytes),
            'smean': round(new_smean, 5),
            'dmean': round(new_dmean, 5),
            'rate': round(new_rate, 4),
            'dur': new_dur,
            'num_packets': int(new_num_packets),
            'label': 1
        }

        # append the new record to the list of new flows
        new_malicious_flows.append(new_flow)

    # convert the list of new flows to a DataFrame
    new_flows_df = pd.DataFrame(new_malicious_flows)

    # append the new flows to the original DataFrame
    df = pd.concat([df, new_flows_df], ignore_index=True)

    return df


# generate new malicious flows and update the DataFrame
new_test = generate_malicious_flows(test, num_flows=3400)

# # print the updated DataFrame
# print("\nNew test with artificially created flows:")
# print(new_test)

new_test.to_csv("malicious_flows_updated.csv", index=False)