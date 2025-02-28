import mysql.connector
from dotenv import load_dotenv
import os
from datetime import datetime
from scapy.all import IP

# establish connection to the database
def get_db_connection():
    # load the environment variables
    load_dotenv()
    DB_HOST = os.getenv('DB_HOST')
    DB_USER = os.getenv('DB_USER')
    DB_PASS = os.getenv('DB_PASS')
    DB_NAME = os.getenv('DB_NAME')

    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )
    return conn


# check if the flow already exists in the database using the 5-tuple flow key
# (ip1, ip2, port1, port2, packet.proto)
def check_flow_exists(flow_key):
    ip1, ip2, port1, port2, protocol = flow_key
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """SELECT flow_id FROM Flows
               WHERE src_ip = ? AND dst_ip = ? 
               AND src_port = ? AND dst_port = ? 
               AND protocol = ?"""
    
    cursor.execute(query, (ip1, ip2, port1, port2, protocol))
    result = cursor.fetchone()
    conn.close()
    return result is not None


# calculate the duration in seconds between two datetime objects
def get_duration(start_time: datetime, end_time: datetime):
    time_difference = end_time - start_time
    return time_difference.total_seconds()


# insert a new flow record into the Flows table
def insert_new_flow(flow_key, is_original_src, packet):
    start_time = datetime.now()
    end_time = datetime.now()
    duration = get_duration(start_time, end_time)
    num_packets = 1
    
    # initialize ttl, bytes, and load metrics as 0
    ttl_src, bytes_src, load_src = 0, 0, 0
    ttl_dst, bytes_dst, load_dst = 0, 0, 0
    
    # get ttl, bytes, and load metrics
    ttl_src, bytes_src, load_src, ttl_dst, bytes_dst, load_dst = get_metrics(is_original_src, packet, ttl_src, bytes_src, load_src, ttl_dst, bytes_dst, load_dst, duration)
    
    # calculate additional metrics
    mean_size_src = bytes_src / max(1, num_packets)
    mean_size_dst = bytes_dst / max(1, num_packets)
    rate = num_packets / max(0.0001, duration)
    
    # ttl_states list
    ttl_states = packet[IP].ttl

    # insert flow into the database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """INSERT INTO Flows 
               (src_ip, dst_ip, src_port, dst_port, protocol, num_packets, ttl_src, ttl_dst, ttl_states, 
                bytes_src, bytes_dst, load_src, load_dst, mean_size_src, mean_size_dst, rate, start_time, end_time, is_malicious) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    
    cursor.execute(query, (flow_key[0], flow_key[1], flow_key[2], flow_key[3], flow_key[4], num_packets, ttl_src, ttl_dst, ttl_states, bytes_src, bytes_dst, load_src, load_dst, mean_size_src, mean_size_dst, rate, start_time, end_time, False))
    conn.commit()
    conn.close()


# update an existing flow record in the Flows table
def update_flow(flow_key, is_original_src, packet):
    ip1, ip2, port1, port2, protocol = flow_key
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """SELECT * FROM Flows WHERE src_ip = ? AND dst_ip = ? 
               AND src_port = ? AND dst_port = ? AND protocol = ?"""
    
    cursor.execute(query, (ip1, ip2, port1, port2, protocol))
    results = cursor.fetchone()
    
    if results:
        start_time = results[16]  # Index for start_time (depends on your table schema)
        end_time = datetime.now()
        duration = get_duration(start_time, end_time)
        
        ttl_src, bytes_src, load_src = 0, 0, 0
        ttl_dst, bytes_dst, load_dst = 0, 0, 0
        
        ttl_src, bytes_src, load_src, ttl_dst, bytes_dst, load_dst = get_metrics(is_original_src, packet, ttl_src, bytes_src, load_src, ttl_dst, bytes_dst, load_dst, duration)

        num_packets = results[6]
        mean_size_src = bytes_src / max(1, num_packets)
        mean_size_dst = bytes_dst / max(1, num_packets)
        rate = num_packets / max(0.0001, duration)
        
        ttl_states = results[9]
        new_ttl_state = str(packet[IP].ttl)
        
        if ttl_states: # if ttl_states has previous ttl values already
            ttl_states_list = ttl_states.split(',')
            if new_ttl_state not in ttl_states_list:
                ttl_states_list.append(new_ttl_state)
            ttl_states = ','.join(ttl_states_list)
        else: # if ttl_states is empty
            ttl_states = new_ttl_state

        # update flow query
        update_query = "UPDATE Flows SET ttl_states = ?, mean_size_src = ?, mean_size_dst = ?, rate = ?, end_time = ?"
                          
        if is_original_src:
            update_query += ", ttl_src = ?, bytes_src = ?, load_src = ? WHERE flow_id = ?"
            cursor.execute(update_query, 
                (ttl_states, mean_size_src, mean_size_dst, rate, end_time, ttl_src, bytes_src, load_src, results[0])
            )
        else:
            update_query += ", ttl_dst = ?, bytes_dst = ?, load_dst = ? WHERE flow_id = ?"
            cursor.execute(update_query, 
                (ttl_states, mean_size_src, mean_size_dst, rate, end_time, ttl_dst, bytes_dst, load_dst, results[0])
            )
        conn.commit()
    conn.close()
  

# helper function to compute ttl, bytes, and load metrics
def get_metrics(is_original_src, packet, ttl_src, bytes_src, load_src, ttl_dst, bytes_dst, load_dst, duration):
    if is_original_src:  # if packet is from src -> dst (request packet)
        ttl_src = packet[IP].ttl
        bytes_src = len(packet)
        load_src = (bytes_src * 8) / max(0.0001, duration) # avoid division by zero
    else:  # if packet is from dst -> src (response packet)
        ttl_dst = packet[IP].ttl
        bytes_dst = len(packet)
        load_dst = (bytes_dst * 8) / max(0.0001, duration)
    return ttl_src, bytes_src, load_src, ttl_dst, bytes_dst, load_dst