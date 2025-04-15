import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.utils import get_db_connection
import pandas as pd
# pd.set_option('display.max_columns', None)

with get_db_connection() as conn:
    with conn.cursor() as cursor:
        query = '''
        SELECT
            flow_id,
            src_port as sport,
            dst_port as dport,
            protocol as proto,
            ttl_src as sttl,
            ttl_dst as dttl,
            ttl_states as ct_state_ttl,
            load_src as sload,
            load_dst as dload,
            bytes_src as sbytes,
            bytes_dst as dbytes,
            mean_size_src as smean,
            mean_size_dst as dmean,
            rate,
            end_time - start_time as dur,
            num_packets,
            is_malicious as label
        FROM Flows
        '''
        cursor.execute(query)
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]

        # load results into a dataframe
        data = pd.DataFrame(results, columns=column_names)
        data = data[data.dur <= 60]
        
        # convert duration to float
        data['dur'] = data['dur'].astype(float)
        
        # convert ct_state_ttl list to its length
        data['ct_state_ttl'] = data['ct_state_ttl'].str.split(",").apply(lambda x: len(x) if x is not None else 0)
        
        # fill NaN values in sport, dport, sttl, and dttl with 0 (from ARP and ICMP flows)
        data[['sport', 'dport', 'sttl', 'dttl']] = data[['sport', 'dport', 'sttl', 'dttl']].fillna(0)
        
        benign_data = data[data.label == 0]
        malicious_data = data[data.label == 1]
        
        # save benign data to a train set csv file
        benign_data.to_csv('real_pi_data.csv', index=False)
        
        # save malicious data to a test set csv file
        malicious_data.to_csv('malicious_flows.csv', index=False)