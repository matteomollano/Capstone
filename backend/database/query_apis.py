from database.utils import get_db_connection
from database.ip_protocol_dict import ip_protocol_dict
from utils.ip_addr import is_public_ip, get_domain_name

# get the last 50 flows to display on the tables page
def get_flow_table():
    query = '''
    SELECT 
        flow_id, 
        end_time as timestamp, 
        src_ip, dst_ip, 
        src_port, dst_port, 
        protocol, 
        num_packets, 
        bytes_src, bytes_dst, 
        is_malicious 
    FROM Flows 
    ORDER BY flow_id DESC
    LIMIT 50'''
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            
            flow_list = []
            for row in results:
                flow = {
                    'flow_id': row[0],
                    'timestamp': str(row[1]),
                    'src_ip': row[2],
                    'dst_ip': row[3],
                    'src_port': row[4],
                    'dst_port': row[5],
                    'protocol': row[6],
                    'num_packets': row[7],
                    'bytes_src': row[8],
                    'bytes_dst': row[9],
                    'is_malicious': row[10]
                }
                flow_list.append(flow)
            return flow_list
 

# get the volume data over time for VolumeGraph
def get_volume_data():
    query = '''
    SELECT
        DATE_FORMAT(end_time, '%Y-%m-%d %H:00:00') as time_interval,
        SUM(bytes_src) as bytes_sent,
        SUM(bytes_dst) as bytes_received
    FROM Flows
    GROUP BY time_interval
    ORDER BY time_interval
    '''
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            
            volume_data = []
            for row in results:
                data = {
                    'time_interval': row[0],
                    'bytes_sent': int(row[1]),
                    'bytes_received': int(row[2])
                }
                volume_data.append(data)
            return volume_data[len(volume_data)-5:] # return last 5 time intervals
        
        
# get packet types distribution for donut pie chart
def get_packet_types():
    query = '''
    SELECT
        protocol,
        SUM(num_packets) as total_num_packets
    FROM Flows
    GROUP BY protocol
    ORDER BY protocol
    '''
    
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            
            packet_types = [
                ["Protocol", "Number of packets"],
            ]
            
            for row in results:
                protocol_name = ip_protocol_dict[row[0]]
                num_packets = int(row[1])
                packet_types.append([protocol_name, num_packets])
            
            return packet_types
        
        
# get domains that have been visited the most
def get_top_domains():
    query = '''
    SELECT ip, SUM(num_packets) AS total_packets
    FROM (
        SELECT src_ip AS ip, num_packets FROM Flows
        UNION ALL
        SELECT dst_ip AS ip, num_packets FROM Flows
    ) AS combined_ips
    GROUP BY ip
    ORDER BY total_packets DESC;
    '''
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            
            top_domains = []
            for row in results:
                
                # only want top 5 domains
                if len(top_domains) == 5:
                    break
                
                ip, num_packets = row[0], int(row[1])
                
                # check if the ip is a public ip
                if is_public_ip(ip):
                    
                    # # get the public ip's domain name
                    # domain_name = get_domain_name(ip)
                    # if domain_name is not None:
                    #     host = domain_name
                    # else:
                    #     host = ip
                    
                    data = {'domain': ip, 'hits': num_packets}
                    top_domains.append(data)
                    
            return top_domains