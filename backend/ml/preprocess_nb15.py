# function to preprocess the UNSW-NB15 dataset, and return the resulting dataframe
def preprocess_nb15(train, test):
    # get the scaling factors between UNSW-NB15 dataset and pi network data
    sbytes_factor = test['sbytes'].mean() / train['sbytes'].mean()
    dbytes_factor = test['dbytes'].mean() / train['dbytes'].mean()
    rate_factor = test['rate'].mean() / train['rate'].mean()
    sttl_factor = test['sttl'].mean() / train['sttl'].mean()
    dttl_factor = test['dttl'].mean() / train['dttl'].mean()

    # scale down UNSW-NB15 dataset to be more like pi network data
    train_adjusted = train.copy()
    train_adjusted['sbytes'] *= sbytes_factor
    train_adjusted['dbytes'] *= dbytes_factor
    train_adjusted['rate'] *= rate_factor
    train_adjusted['sttl'] *= sttl_factor
    train_adjusted['dttl'] *= dttl_factor
    
    # recalculate sload and sload from updated sbytes and dbytes statistics
    train_adjusted['sload'] = (train_adjusted['sbytes'] * 8) / train_adjusted['dur'].replace(0, 1e-6)
    train_adjusted['dload'] = (train_adjusted['dbytes'] * 8) / train_adjusted['dur'].replace(0, 1e-6)
    
    return train_adjusted