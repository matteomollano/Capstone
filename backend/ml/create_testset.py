import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.utils import get_db_connection
import pandas as pd

with get_db_connection() as conn:
    with conn.cursor() as cursor:
        query = '''
        SELECT
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
            is_malicious as label
        FROM Flows
        '''
        cursor.execute(query)
        results = cursor.fetchall()
        column_names = ['sttl', 'dttl', 'ct_state_ttl', 'sload', 'dload', 'sbytes', 'dbytes', 'smean', 'dmean', 'rate', 'dur', 'label']

        # load results into a dataframe
        data = pd.DataFrame(results, columns=column_names)
        
        # convert duration to float
        data['dur'] = data['dur'].astype(float)
        
        # convert ct_state_ttl list to its length
        data['ct_state_ttl'] = data['ct_state_ttl'].str.split(",").apply(lambda x: len(x) if x is not None else 0)
        
        # fill NaN values in sttl and dttl with 0 (from ARP and ICMP flows)
        data[['sttl', 'dttl']] = data[['sttl', 'dttl']].fillna(0)
        
        # save data to csv file
        data.to_csv('real_data_test.csv', index=False) 