from database.utils import get_db_connection

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
    LIMIT 10'''
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