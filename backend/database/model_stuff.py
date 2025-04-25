from scapy.all import ETHER_TYPES, IP_PROTOS
from database.common_ports import COMMON_PORTS
import pandas as pd, numpy as np
import os, joblib
from concurrent.futures import ThreadPoolExecutor

# function to convert a protocol name to its corresponding protocol number
def get_protocol_number(proto_name):
    proto_name = str(proto_name).lower()
    
    # check COMMON_PORTS first (reverse the mapping)
    common_ports_map = {str(v).lower(): k for k, v in COMMON_PORTS.items()}
    if proto_name in common_ports_map:
        return common_ports_map[proto_name]
    
    # check IP_PROTOS second
    ip_proto_map = {str(IP_PROTOS[i]).lower(): i for i in IP_PROTOS}
    if proto_name in ip_proto_map:
        return ip_proto_map[proto_name]
    
    # check ETHER_TYPES last
    ether_map = {str(ETHER_TYPES[i]).lower(): i for i in ETHER_TYPES}
    if proto_name in ether_map:
        return ether_map[proto_name]
    
    return None


# function to format features for machine learning models before making predictions
def format_features(src_port, dst_port, protocol, ttl_src, ttl_dst, ct_state_ttl, 
    load_src, load_dst, bytes_src, bytes_dst, mean_size_src, mean_size_dst, 
    rate, duration, num_packets
):
    # ensure it matches your model training columns exactly
    features = pd.DataFrame([{
        "sport": src_port if src_port is not None else 0, # fill sport, dport, sttl, and dttl with 0 for ARP and ICMP packets
        "dport": dst_port if src_port is not None else 0,
        "proto": protocol,
        "sttl": ttl_src if ttl_src is not None else 0,
        "dttl": ttl_dst if ttl_dst is not None else 0,
        "ct_state_ttl": ct_state_ttl,
        "sload": load_src,
        "dload": load_dst,
        "sbytes": bytes_src,
        "dbytes": bytes_dst,
        "smean": mean_size_src,
        "dmean": mean_size_dst,
        "rate": rate,
        "dur": duration,
        "num_packets": num_packets
    }])
    
    # convert ct_state_ttl list to its length
    features['ct_state_ttl'] = features['ct_state_ttl'].str.split(",").apply(lambda x: len(x) if x is not None else 0)
    
    # convert protocol name to number
    features['proto'] = features['proto'].apply(get_protocol_number)

    return features


# === PREDICTIONS === #

# get the absolute path to the ml/final_models directory
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
models_dir = os.path.join(base_dir, "ml", "final_models")

# load forest models
random_forest_model = joblib.load(os.path.join(models_dir, "random_forest_model.joblib"))
iso_forest_model = joblib.load(os.path.join(models_dir, "iso_forest_model.joblib"))

# load knn model, scaler, and threshold
knn_model_data = joblib.load(os.path.join(models_dir, "knn_model_with_scaler.joblib"))
knn_model = knn_model_data["model"]
knn_scaler = knn_model_data["scaler"]
knn_threshold = knn_model_data["threshold"]

# predict using random forest model
def random_forest_predict(data, model):
    pred = model.predict(data)
    return pred


# predict using isolation forest model
def iso_forest_predict(data, model):
    pred = model.predict(data)
    binary_pred = np.where(pred == -1, 1, 0)
    return binary_pred


# predict using knn model
def knn_predict(data, model, scaler, threshold):
    # scale the incoming data
    data_scaled = scaler.transform(data)
    
    # get distances to the nearest neighbors
    distances, _ = model.kneighbors(data_scaled)
    
    # use mean distance as anomaly score
    anomaly_score = distances.mean(axis=1)
    
    pred = (anomaly_score > threshold).astype(int)
    
    return pred


# run all three model predictions using separate threads
# classify prediction as 1 if at least 2/3 (majority) return 1
# else, classifiy prediction as 0
def predict(data):
    # === run predictions concurrently ===
    with ThreadPoolExecutor(max_workers=3) as executor:
        rf_future = executor.submit(random_forest_predict, data, random_forest_model)
        if_future = executor.submit(iso_forest_predict, data, iso_forest_model)
        knn_future = executor.submit(knn_predict, data, knn_model, knn_scaler, knn_threshold)

        rf_pred = rf_future.result()[0]
        if_pred = if_future.result()[0]
        knn_pred = knn_future.result()[0]

    # combine predictions (e.g., majority vote)
    preds = [rf_pred, if_pred, knn_pred]
    is_malicious = 1 if sum(preds) >= 2 else 0
    
    return is_malicious