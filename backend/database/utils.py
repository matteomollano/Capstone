import mysql.connector, os
from mysql.connector import Error
from dotenv import load_dotenv
from datetime import datetime, timedelta
from database.model_stuff import format_features, predict

# 60 second timeout to align with UNSW-NB15 dataset
FLOW_TIMEOUT = timedelta(minutes = 1)

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


# check if the flow is expired (i.e. it elapses the FLOW_TIMEOUT)
def is_flow_expired(start_time):
    current_time = datetime.now()
    return (current_time - start_time) > FLOW_TIMEOUT


# check if the flow already exists in the database using the 5-tuple flow key
# (ip1, ip2, port1, port2, protocol)
def check_flow_exists(flow_key):
    ip1, ip2, port1, port2, protocol = flow_key
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # if the packet doesn't use ports, we need a different query
    if port1 == None and port2 == None:
        query = """SELECT start_time FROM Flows
                   WHERE src_ip = %s AND dst_ip = %s
                   AND src_port IS NULL AND dst_port IS NULL
                   AND protocol = %s"""
        params = (ip1, ip2, protocol)
    else:
        query = """SELECT start_time FROM Flows
                   WHERE src_ip = %s AND dst_ip = %s 
                   AND src_port = %s AND dst_port = %s 
                   AND protocol = %s"""
        params = (ip1, ip2, port1, port2, protocol)
    
    cursor.execute(query, params)
    result = cursor.fetchone()
    conn.close()
    
    # if the flow doesn't exist
    if result is None:
        return False
    
    # if the flow exists, check if it has expired
    start_time = result[0]
    if is_flow_expired(start_time):
        return False
    
    # the flow exists and has not expired
    return True


# calculate the duration in seconds between two datetime objects
def get_duration(start_time: datetime, end_time: datetime):
    time_difference = end_time - start_time
    return time_difference.total_seconds()


# insert a new flow record into the Flows table
def insert_new_flow(flow_key, is_original_src, packet_layer, packet_json, frame_layer, debug=True):
    ip1, ip2, port1, port2, protocol = flow_key
    
    start_time = datetime.now()
    end_time = datetime.now()
    duration = get_duration(start_time, end_time)
    num_packets = 1
    
    # initialize bytes and load values to 0
    bytes_src, bytes_dst, load_src, load_dst = 0, 0, 0, 0
    
    # if the packet does not have an IP layer (and hence no TTL), set TTLs to None
    if packet_layer["ttl"] == None:
        ttl_src, ttl_dst, ttl_states = None, None, None
        
        if is_original_src:  # if packet is from src -> dst (request packet)
            bytes_src = packet_layer["packet_length"]
            load_src = (bytes_src * 8) / max(0.0001, duration)
        else:  # if packet is from dst -> src (response packet)
            bytes_dst = packet_layer["packet_length"]
            load_dst = (bytes_dst * 8) / max(0.0001, duration)
        
    # if it does have an IP layer and TTLs, initialize them to 0
    else:
        ttl_src, ttl_dst = 0, 0
        ttl_states = str(packet_layer["ttl"])
    
        if is_original_src:  # if packet is from src -> dst (request packet)
            ttl_src = packet_layer["ttl"]
            bytes_src = packet_layer["packet_length"]
            load_src = (bytes_src * 8) / max(0.0001, duration) # avoid division by zero
        else:  # if packet is from dst -> src (response packet)
            ttl_dst = packet_layer["ttl"]
            bytes_dst = packet_layer["packet_length"]
            load_dst = (bytes_dst * 8) / max(0.0001, duration)
    
    # calculate additional metrics
    mean_size_src = bytes_src / max(1, num_packets)
    mean_size_dst = bytes_dst / max(1, num_packets)
    rate = num_packets / max(0.0001, duration)
    
    
    # === Machine Learning Predictions === #
    print("For inserting flow:")
    data = format_features(
        src_port=port1, dst_port=port2, protocol=protocol, ttl_src=ttl_src, ttl_dst=ttl_dst,
        ct_state_ttl=ttl_states, load_src=load_src, load_dst=load_dst, bytes_src=bytes_src, bytes_dst=bytes_dst,
        mean_size_src=mean_size_src, mean_size_dst=mean_size_dst, rate=rate, duration=duration, num_packets=num_packets
    )
    print("Data:")
    print(data)
    is_malicious = predict(data)
    print(f"is_malicious: {is_malicious}")
    print()
    

    # insert flow into the database
    query = """INSERT INTO Flows 
               (src_ip, dst_ip, src_port, dst_port, protocol, num_packets, ttl_src, ttl_dst, ttl_states, 
                bytes_src, bytes_dst, load_src, load_dst, mean_size_src, mean_size_dst, rate, start_time, end_time, is_malicious) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (ip1, ip2, port1, port2, protocol, num_packets, ttl_src, ttl_dst, ttl_states, bytes_src, bytes_dst, load_src, load_dst, mean_size_src, mean_size_dst, rate, start_time, end_time, False))
                conn.commit()
                
                # get the flow_id of the newly inserted flow
                flow_id = cursor.lastrowid
                
                # for debugging
                if debug:
                    print(f"Inserting new flow with flow_id: {flow_id}")
                    print(f"src ip: {ip1}, dst ip: {ip2}")
                    print(f"src port: {port1}, dst port: {port2}, protocol: {protocol}")
                    print(f"start time: {start_time}, end time: {end_time}")
                
                # add the new flow's corresponding packet json to the Packets table,
                # using flow_id as the foreign key
                packet_id = insert_packet(flow_id, packet_json, start_time, debug)
                
                # add the new flow's corresponding frame data to the Frames table
                insert_frame(flow_id, packet_id, frame_layer, debug)
                
                # print("\n--------------------------------------------------------------------------------------------\n")
    except Error as e:
        print(f"Error inserting new flow: {e}")


# update an existing non-IP layer flow in the Flows table
def update_non_ip_flow(flow_key, is_original_src, packet_layer, debug=True):
    ip1, ip2, port1, port2, protocol = flow_key
    
    query = """SELECT * FROM Flows WHERE src_ip = %s AND dst_ip = %s
               AND src_port IS NULL AND dst_port IS NULL AND protocol = %s
               ORDER BY end_time DESC LIMIT 1"""
    params = (ip1, ip2, protocol)
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchone()
                
                if results:
                    start_time, old_end_time = results[17], results[18]
                    
                    # # check again if flow is expired
                    # if is_flow_expired(old_end_time):
                    #     if debug:
                    #         print(f"Flow expired (flow_id: {results[0]}) - starting new flow instead")
                    #     return None, None  # signal to create a new flow instead of updating 
                    
                    
                    new_end_time = datetime.now()
                    duration = get_duration(start_time, new_end_time)
                    
                    bytes_src, bytes_dst = results[10], results[11]
                    load_src, load_dst = results[12], results[13]
                    
                    if is_original_src:  # if packet is from src -> dst (request packet)
                        bytes_src += packet_layer["packet_length"]
                    else:  # if packet is from dst -> src (response packet)
                        bytes_dst += packet_layer["packet_length"]
                        
                    # get num_packets and increase by 1
                    num_packets = results[6]
                    num_packets += 1
                    
                    # update src and dst load
                    load_src = (bytes_src * 8) / max(0.0001, duration)
                    load_dst = (bytes_dst * 8) / max(0.0001, duration)
                    
                    # calculate mean_size_src, mean_size_dst, and rate
                    mean_size_src = bytes_src / max(1, num_packets)
                    mean_size_dst = bytes_dst / max(1, num_packets)
                    rate = num_packets / max(0.0001, duration)
                    
                    # get the flow id
                    flow_id = results[0]
                    
                    # get label from query
                    is_malicious = results[19]
                    print(f"is_malicious before: {is_malicious}")
                    
                    # === Machine Learning Predictions === #
                    # only run the models if the flow is not malicious (is_malicious == 0)
                    # if it's already malicious (is_malicious == 1), there is no need to check again
                    if is_malicious == 0:
                        print("For update non-ip flow:")
                        data = format_features(
                            src_port=port1, dst_port=port2, protocol=protocol, ttl_src=None, ttl_dst=None,
                            ct_state_ttl=None, load_src=load_src, load_dst=load_dst, bytes_src=bytes_src, bytes_dst=bytes_dst,
                            mean_size_src=mean_size_src, mean_size_dst=mean_size_dst, rate=rate, duration=duration, num_packets=num_packets
                        )
                        print("Data:")
                        print(data)
                        is_malicious = predict(data)
                        print(f"is_malicious: {is_malicious}")
                        print()

        
                    # update flow query
                    update_query = """
                    UPDATE Flows SET num_packets = %s, load_src = %s, load_dst = %s, 
                    mean_size_src = %s, mean_size_dst = %s, rate = %s, end_time = %s, is_malicious = %s
                    """
                    
                    if is_original_src:
                        update_query += ", bytes_src = %s WHERE flow_id = %s"
                        update_params = (num_packets, load_src, load_dst, mean_size_src, mean_size_dst, rate, new_end_time, is_malicious, bytes_src, flow_id)
                    else:
                        update_query += ", bytes_dst = %s WHERE flow_id = %s"
                        update_params = (num_packets, load_src, load_dst, mean_size_src, mean_size_dst, rate, new_end_time, is_malicious, bytes_dst, flow_id)
                    
                    cursor.execute(update_query, update_params)
                    conn.commit()
                    
                    # for debugging
                    if debug:
                        print("Non IP layer flow:")
                        print(f"Updating flow_id {flow_id} with src ip: {ip1}, dst ip: {ip2}")
                        print(f"src port: {port1}, dst port: {port2}, protocol: {protocol}")
                        print("num packets", num_packets)
                        print(f"start time: {start_time}, old end time: {old_end_time}, new end time: {new_end_time}")
                        
                    return flow_id, new_end_time
                                    
    except Error as e:
        print(f"Error updating existing flow: {e}")
        
      
# update an existing IP layer flow in the Flows table  
def update_ip_flow(flow_key, is_original_src, packet_layer, debug=True):
    ip1, ip2, port1, port2, protocol = flow_key
    
    query = """SELECT * FROM Flows WHERE src_ip = %s AND dst_ip = %s 
               AND src_port = %s AND dst_port = %s AND protocol = %s
               ORDER BY end_time DESC LIMIT 1"""
    params = (ip1, ip2, port1, port2, protocol)
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchone()

                if results:
                    start_time, old_end_time = results[17], results[18]
                    
                    # if is_flow_expired(old_end_time):
                    #     if debug:
                    #         print(f"Flow expired (flow_id: {results[0]}) - starting new flow instead")
                    #     return None, None
                    
                    new_end_time = datetime.now()
                    duration = get_duration(start_time, new_end_time)
                    
                    ttl_src, ttl_dst = results[7], results[8]
                    bytes_src, bytes_dst = results[10], results[11]
                    load_src, load_dst = results[12], results[13]
                    
                    if is_original_src:  # if packet is from src -> dst (request packet)
                        ttl_src = packet_layer["ttl"]
                        bytes_src += packet_layer["packet_length"]
                    else:  # if packet is from dst -> src (response packet)
                        ttl_dst = packet_layer["ttl"]
                        bytes_dst += packet_layer["packet_length"]
                        
                    # update src and dst load
                    load_src = (bytes_src * 8) / max(0.0001, duration)
                    load_dst = (bytes_dst * 8) / max(0.0001, duration)
                    
                    # get num_packets and increase by 1
                    num_packets = results[6]
                    num_packets += 1
                    
                    # calculate mean_size_src, mean_size_dst, and rate
                    mean_size_src = bytes_src / max(1, num_packets)
                    mean_size_dst = bytes_dst / max(1, num_packets)
                    rate = num_packets / max(0.0001, duration)
                    
                    # update ttl_states list
                    ttl_states = results[9]
                    new_ttl_state = str(packet_layer["ttl"])
                    
                    if ttl_states: # if ttl_states has previous ttl values already
                        ttl_states_list = ttl_states.split(',')
                        if new_ttl_state not in ttl_states_list:
                            ttl_states_list.append(new_ttl_state)
                        ttl_states = ','.join(ttl_states_list)
                    else: # if ttl_states is empty
                        ttl_states = new_ttl_state
                        
                    # get flow id
                    flow_id = results[0]
                    
                    # get the label from the query
                    is_malicious = results[19]
                    print(f"is_malicious before: {is_malicious}")
                    
                    # === Machine Learning Predictions === #
                    if is_malicious == 0:
                        print("For update ip flow:")
                        data = format_features(
                            src_port=port1, dst_port=port2, protocol=protocol, ttl_src=ttl_src, ttl_dst=ttl_dst,
                            ct_state_ttl=ttl_states, load_src=load_src, load_dst=load_dst, bytes_src=bytes_src, bytes_dst=bytes_dst,
                            mean_size_src=mean_size_src, mean_size_dst=mean_size_dst, rate=rate, duration=duration, num_packets=num_packets
                        )
                        print("Data:")
                        print(data)
                        is_malicious = predict(data)
                        print(f"is_malicious: {is_malicious}")
                        print()
                    

                    # update flow query
                    update_query = """UPDATE Flows SET num_packets = %s, ttl_states = %s, load_src = %s, load_dst = %s, 
                    mean_size_src = %s, mean_size_dst = %s, rate = %s, end_time = %s, is_malicious = %s"""
                                    
                    if is_original_src:
                        update_query += ", ttl_src = %s, bytes_src = %s WHERE flow_id = %s"
                        update_params = (num_packets, ttl_states, load_src, load_dst, mean_size_src, mean_size_dst, rate, new_end_time, is_malicious, ttl_src, bytes_src, flow_id)
                    else:
                        update_query += ", ttl_dst = %s, bytes_dst = %s WHERE flow_id = %s"
                        update_params = (num_packets, ttl_states, load_src, load_dst, mean_size_src, mean_size_dst, rate, new_end_time, is_malicious, ttl_dst, bytes_dst, flow_id)
                    
                    cursor.execute(update_query, update_params)
                    conn.commit()
                    
                    # for debugging
                    if debug:
                        print("IP layer flow")
                        print(f"Updating flow_id {flow_id} with src ip: {ip1}, dst ip: {ip2}")
                        print(f"src port: {port1}, dst port: {port2}, protocol: {protocol}")
                        print("num packets", num_packets)
                        print(f"start time: {start_time}, old end time: {old_end_time}, new end time: {new_end_time}")
                    
                    return flow_id, new_end_time
                
    except Error as e:
        print(f"Error updating existing flow: {e}")
    

# update an existing flow record in the Flows table
def update_flow(flow_key, is_original_src, packet_layer, packet_json, frame_layer, debug=True):
    try:
        # if the packet doesn't have a TTL value, it doesn't have an IP layer (non-IP flow)
        if packet_layer["ttl"] == None:
            flow_id, new_end_time = update_non_ip_flow(flow_key, is_original_src, packet_layer, debug)
        # if it does have a TTL value, it has an IP layer (IP flow)
        else:
            flow_id, new_end_time = update_ip_flow(flow_key, is_original_src, packet_layer, debug)  
            
        # # if the original flow is expired, insert a new flow instead
        # if flow_id == None:
        #     insert_new_flow(flow_key, is_original_src, packet_layer, packet_json, frame_layer, debug)
        #     return  
                        
        # add packet json to the Packets table, using flow_id as the foreign key
        packet_id = insert_packet(flow_id, packet_json, new_end_time, debug)
        
        # add frame data to the Frames table, using flow_id as the foreign key
        insert_frame(flow_id, packet_id, frame_layer, debug)
        
        # print("\n--------------------------------------------------------------------------------------------------\n")
    except Error as e:
        print(f"Error updating existing flow: {e}")
    
    
# function to insert a flow's corresponding packet into the Packets table
def insert_packet(flow_id, packet_json, timestamp, debug):  
    insert_query = "INSERT INTO Packets (flow_id, packet_data, timestamp) VALUES (%s, %s, %s)"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor: 
                cursor.execute(insert_query, (flow_id, packet_json, timestamp))
                conn.commit()
                packet_id = cursor.lastrowid
        if debug:
            print(f"\nInserting packet for flow_id {flow_id}")
            print(f"timestamp: {timestamp}")
        return packet_id
    except Error as e:
        print(f"Error inserting packet for flow_id {flow_id}: {e}")
  
  
# function to insert a flow's corresponding frame into the Frames table
def insert_frame(flow_id, packet_id, frame_layer, debug):
    src_mac, dst_mac, ether_type, protocol = frame_layer["src_mac_address"], frame_layer["dst_mac_address"], frame_layer["ether_type"], frame_layer["protocol"]
    insert_query = "INSERT INTO Frames (flow_id, packet_id, src_mac, dst_mac, ether_type, protocol) VALUES (%s, %s, %s, %s, %s, %s)"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(insert_query, (flow_id, packet_id, src_mac, dst_mac, ether_type, protocol))
                conn.commit()
        if debug:
            print(f"\nInserting frame for flow_id {flow_id} and packet_id {packet_id}")
            print(f"src mac: {src_mac}, dst mac: {dst_mac}, ether type: {ether_type}, protocol: {protocol}")
            print("\n--------------------------------------------------------------------------------------------\n")
    except Error as e:
        print(f"Error inserting frame for flow_id {flow_id}: {e}")
        print("\n--------------------------------------------------------------------------------------------\n")