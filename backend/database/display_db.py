from utils import get_db_connection, get_duration
import json

def is_valid_table_name(table_name):
    return table_name.isidentifier()


def display_table(table_name):
    if not is_valid_table_name(table_name):
        print(f"{table_name} is invalid")
        return
    
    print("--------------------------------------------------------------------------------------------")
    print(f"{table_name} Table")
    print("--------------------------------------------------------------------------------------------\n")
    
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table_name}")
    column_names = [desc[0] for desc in cursor.description]
    results = cursor.fetchall()

    for row in results:
        for i, column_value in enumerate(row):
            print(f"{column_names[i]}: {column_value}")
        print("\n--------------------------------------------------------------------------------------------\n")
    
    print("--------------------------------------------------------------------------------------------")
    print(f"{table_name} Table End")
    print("--------------------------------------------------------------------------------------------")
    
    cursor.close()
    conn.close()
   
 
def display_flow_by_id(flow_id):
    query = 'SELECT * FROM Flows WHERE flow_id = %s'
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (flow_id, ))
            result = cursor.fetchone()
            if result:
                column_names = [desc[0] for desc in cursor.description]
                for i, column_value in enumerate(result):
                    print(f"{column_names[i]}: {column_value}")
            else:
                print(f"No flow found with flow_id {flow_id}") 

               
def aggregate_packets_by_flow_id(flow_id):
    query = 'SELECT packet_data, timestamp FROM Packets WHERE flow_id = %s ORDER BY timestamp ASC'
    agg_bytes_src = 0
    agg_bytes_dst = 0
    num_packets = 0
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (flow_id, ))
            packets = cursor.fetchall()
            
            for i, packet in enumerate(packets):
                num_packets += 1
                packet_data = json.loads(packet[0])
                ip_layer = packet_data.get("IP", {})
                
                # on the first packet, identify the src_ip, dst_ip, src_port, dst_port, and protocol for the flow
                if i == 0:
                    src_ip = ip_layer.get("src")
                    dst_ip = ip_layer.get("dst")
                    tcp_layer = packet_data.get("TCP", {})
                    src_port = tcp_layer.get("sport")
                    dst_port = tcp_layer.get("dport")
                    protocol = ip_layer.get("proto")
                    
                # determine direction and sum up fields accordingly
                if ip_layer.get("src") == src_ip and ip_layer.get("dst") == dst_ip:
                    # src -> dst packet
                    agg_bytes_src += int(ip_layer.get("len", 0))
                elif ip_layer.get("src") == dst_ip and ip_layer.get("dst") == src_ip:
                    # dst -> src packet
                    agg_bytes_dst += int(ip_layer.get("len", 0))
            
            first_packet_time = packets[0][1]
            last_packet_time = packets[len(packets) - 1][1]
            duration = get_duration(first_packet_time, last_packet_time)
            
            load_src = (agg_bytes_src * 8) / max(0.0001, duration)
            load_dst = (agg_bytes_dst * 8) / max(0.0001, duration)
            mean_size_src = agg_bytes_src / max(1, num_packets)
            mean_size_dst = agg_bytes_dst / max(1, num_packets)
            rate = num_packets / max(0.0001, duration)
            
    # print all variables here
    print(f"flow_id: {flow_id}")
    print(f"src_ip: {src_ip}")
    print(f"dest_ip: {dst_ip}")
    print(f"src_port: {src_port}")
    print(f"dst_port: {dst_port}")
    print(f"protocol: {protocol}")
    print(f"num_packets: {num_packets}")
    print(f"bytes_src: {agg_bytes_src}")
    print(f"bytes_dst: {agg_bytes_dst}")
    print(f"load_src: {load_src}")
    print(f"load_dst: {load_dst}")
    print(f"mean_size_src: {mean_size_src}")
    print(f"mean_size_dest: {mean_size_dst}")
    print(f"rate: {rate}")
    print(f"start_time: {first_packet_time}")
    print(f"end_time: {last_packet_time}")

                
if __name__ == "__main__":
    display_table("Flows")
    # display_flow_by_id(111)
    # print("\n--------------------------------------------------------------------------------------------\n")
    # aggregate_packets_by_flow_id(111)