from database import get_db_connection

with get_db_connection() as conn:
    with conn.cursor() as cursor:
        # create Flows table
        flows_query = """
        CREATE TABLE Flows (
            flow_id INT AUTO_INCREMENT PRIMARY KEY,
            src_ip VARCHAR(15),
            dst_ip VARCHAR(15),
            src_port INT,
            dst_port INT,
            protocol INT,
            num_packets INT,
            ttl_src INT,
            ttl_dst INT,
            ttl_states TEXT,
            bytes_src INT UNSIGNED,
            bytes_dst INT UNSIGNED,
            load_src FLOAT,
            load_dst FLOAT,
            mean_size_src FLOAT,
            mean_size_dst FLOAT,
            rate FLOAT,
            start_time DATETIME,
            end_time DATETIME,
            is_malicious BOOLEAN
        );
        """
        cursor.execute(flows_query)
        
        # create Packets table
        packets_query = """
        CREATE TABLE Packets (
            packet_id INT AUTO_INCREMENT PRIMARY KEY,
            flow_id INT,
            packet_data JSON,
            timestamp DATETIME,
            FOREIGN KEY (flow_id) REFERENCES Flows(flow_id) ON DELETE CASCADE
        );
        """
        cursor.execute(packets_query)