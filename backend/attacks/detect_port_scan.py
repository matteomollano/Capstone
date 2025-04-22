import sys
sys.path.append("../")
from database.utils import get_db_connection

def detect_port_scan():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            query = '''
            WITH targeted_ips AS (
                SELECT dst_ip
                FROM Flows
                GROUP BY dst_ip
                HAVING COUNT(DISTINCT dst_port) >= 50
            )
            SELECT f.* FROM Flows f
            JOIN targeted_ips t ON f.dst_ip = t.dst_ip
            WHERE f.end_time >= NOW() - INTERVAL 1 MINUTE
            AND protocol NOT IN ('ARP', 'ICMP')
            AND (f.dst_port = 20 OR f.src_port = 20);
            '''
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            cursor.close()
            conn.close()

            # display results
            for i, row in enumerate(results):
                print(f"{i}. src_ip: {row[1]} | dst_ip: {row[2]} | sport: {row[3]} | dport: {row[4]} | proto: {row[5]}")

# run detection
detect_port_scan()

# time periods for port scan test attacks
'''
WHERE f.end_time BETWEEN '2025-04-22 12:32:00' AND '2025-04-22 12:32:30'
WHERE f.end_time BETWEEN '2025-04-22 13:59:00.00' AND '2025-04-22 13:59:22.00'
WHERE f.end_time BETWEEN '2025-04-22 18:03:49.00' AND '2025-04-22 18:03:53.00'
WHERE f.end_time BETWEEN '2025-04-22 18:42:41.900140' AND '2025-04-22 18:42:45.599598'
'''

# MariaDB Event Scheduler
'''
CREATE EVENT mark_malicious_flows
ON SCHEDULE EVERY 30 SECOND
DO
BEGIN
    -- Step 1: Create a temporary table to store targeted_ips
    CREATE TEMPORARY TABLE targeted_ips AS
    SELECT dst_ip
    FROM Flows
    GROUP BY dst_ip
    HAVING COUNT(DISTINCT dst_port) >= 50;

    -- Step 2: Update flows based on targeted_ips
    UPDATE Flows f
    JOIN targeted_ips t ON f.dst_ip = t.dst_ip
    SET f.is_malicious = 1
    WHERE f.end_time >= NOW() - INTERVAL 1 MINUTE
    AND (f.dst_port = 20 OR f.src_port = 20);
END;
'''