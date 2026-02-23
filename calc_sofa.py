# Calculating SOFA score

import numpy as np
from datetime import timedelta


NO_FEATURE_VALUE = 'NO_FEATURE_VALUE'

# Feature validity check function
def is_valid_feature_value(feature_key, v):
    if feature_key == 'PULSE':
        return 0 <= v <= 300
    elif feature_key == 'RESP':
        return 0 <= v <= 120
    elif feature_key == 'SBP':
        return 0 <= v <= 300
    elif feature_key == 'DBP':
        return 0 <= v <= 300
    elif feature_key == 'TEMP':
        return 25 <= v <= 50
    elif feature_key == 'GCS':
        return 3 <= v <= 15
    elif feature_key == 'FiO2':
        return 0 <= v <= 1
    elif feature_key == 'O2':
        return 1 <= v <= 10
    elif feature_key == 'SpO2':
        return 0 <= v <= 100
    elif feature_key == 'pO2':
        return True
    elif feature_key == 'PLATELET':
        return 0 <= v <= 1000
    elif feature_key == 'BILIRUBIN':
        return 0 <= v <= 75
    elif feature_key == 'MBP':
        return True
    elif feature_key == 'NORP':
        return True
    elif feature_key == 'DOPA':
        return True
    elif feature_key == 'DOBU':
        return True
    elif feature_key == 'VASO':
        return True
    elif feature_key == 'EPIN':
        return True
    elif feature_key == 'URINE':
        return True
    elif feature_key == 'CREATININE':
        return 0 <= v <= 20
    elif feature_key == 'SaO2':
        return True
    elif feature_key == 'GCS_EYE':
        return True
    elif feature_key == 'GCS_MOT':
        return True
    elif feature_key == 'GCS_VER':
        return True
    elif feature_key == 'GCS_TOTAL':
        return 3 <= v <= 15
    elif feature_key == 'SODIUM':
        return 0 <= v <= 500
    elif feature_key == 'pH':
        return 0 <= v <= 14
    elif feature_key == 'POTASSIUM':
        return 0 <= v <= 15
    elif feature_key == 'WBC':
        return 0 <= v <= 100
    elif feature_key == 'HCO3':
        return 0 <= v <= 100
    elif feature_key == 'HEMATOCRIT':
        return 0 <= v <= 100

    else:
        raise AssertionError('{} {}'.format(feature_key, v))

# Get last valid feature value within 24 hours from prediction time
# feature: feature name
# d: dictionary of feature list 
# pred_dt: prediction time
def get_last24_values(feature, d, pred_dt):
    if feature not in d:
        return NO_FEATURE_VALUE

    time_window = pred_dt - timedelta(hours=24)

    dt_values = d[feature]
    dt_values = list(filter(lambda x: pred_dt >= x[0] >= time_window, dt_values))
    dt_values = list(filter(lambda x: is_valid_feature_value(feature, x[1]), dt_values))
    if not dt_values:
        return NO_FEATURE_VALUE

    dt_values = sorted(dt_values, key=lambda x: x[0])
    return list(np.array(dt_values)[:,1])

# Get last valid feature time and value within 24 hours from prediction time
# feature: feature name
# d: dictionary of feature list 
# pred_dt: prediction time
def get_last24_features(feature, d, pred_dt):
    if feature not in d:
        return NO_FEATURE_VALUE

    time_window = pred_dt - timedelta(hours=24)

    dt_values = d[feature]
    dt_values = list(filter(lambda x: pred_dt >= x[0] >= time_window, dt_values))
    dt_values = list(filter(lambda x: is_valid_feature_value(feature, x[1]), dt_values))
    if not dt_values:
        return NO_FEATURE_VALUE

    dt_values = sorted(dt_values, key=lambda x: x[0])
    return list(np.array(dt_values))

# calculate respiratory rate score
def calc_respiratory_rate(d, pred_dt):
    fio2_values = get_last24_values(FiO2, d, pred_dt)
    if isinstance(fio2_values, str):
        return 0
    
    fio2_values = list(filter(lambda x: 0. <= x <= 1., fio2_values))

    o2_values = get_last24_values(O2, d, pred_dt)
    if isinstance(o2_values, str):
        o2 = None
        o2_values = list()
    else:
        o2 = True


    if o2:
        _o2_values = [0.21]
        for v in o2_values:
            if v == 1:
                _o2_values.append(0.23)
            elif v == 2:
                _o2_values.append(0.25)
            elif v == 3:
                _o2_values.append(0.27)
            elif v == 4:
                _o2_values.append(0.30)
            elif v == 5:
                _o2_values.append(0.35)
            elif v == 6:
                _o2_values.append(0.40)
            elif v == 7:
                _o2_values.append(0.40)
            elif v == 8:
                _o2_values.append(0.49)
            elif v == 9:
                _o2_values.append(0.49)
            elif v == 10:
                _o2_values.append(0.49)
            else:
                continue
        o2_values = _o2_values

    po2_values = get_last24_values(pO2, d, pred_dt)
    if isinstance(po2_values, str):
        return 0

    fio2_worst = max(fio2_values) if fio2_values else 0
    o2_worst = max(o2_values) if o2_values else 0

    po2_worst = min(po2_values)

    fio2_worst = max([fio2_worst, o2_worst])

    if fio2_worst == 0:
        return 0

    value = po2_worst / fio2_worst
    if value < 100:
        return 4
    elif value < 200:
        return 3
    elif value < 300:
        return 2
    elif value < 400:
        return 1
    else:
        return 0

# calculate coagulation score
def calc_coagulation(d, pred_dt):
    values = get_last24_values(PLATELET, d, pred_dt)
    if isinstance(values, str):
        return 0

    value = min(values)
    if value < 20:
        return 4
    elif value < 50:
        return 3
    elif value < 100:
        return 2
    elif value < 150:
        return 1
    else:
        return 0

# calculate liver score
def calc_liver(d, pred_dt):
    values = get_last24_values(BILIRUBIN, d, pred_dt)
    if isinstance(values, str):
        return 0

    value = max(values)
    if value > 12.0:
        return 4
    elif value > 6.0:
        return 3
    elif value > 2.0:
        return 2
    elif value > 1.2:
        return 1
    else:
        return 0

# calculate cardiovascular score
def calc_cardiovascular(d, pred_dt):
    
    mbp_values = get_last24_values(MBP, d, pred_dt)
    sbp_values = get_last24_features(SBP, d, pred_dt)
    dbp_values = get_last24_features(DBP, d, pred_dt)
    
    if isinstance(mbp_values, str) and isinstance(sbp_values, str) and isinstance(dbp_values, str):
        return 0
    
    if isinstance(mbp_values, str):
        mbp_values = list()
    
    if isinstance(sbp_values, str) or isinstance(dbp_values, str):
        pass
    elif len(sbp_values) > 0 and len(dbp_values) > 0:
        for sbp in sbp_values:
            sbp_t, sbp_v = sbp
            dbp_matched = list(filter(lambda x: x[0] == sbp_t, dbp_values))
            if len(dbp_matched) > 0:
                dbp_t,dbp_v = dbp_matched[0]
            else:
                continue
                
            mbp_values.append((sbp_v + (2 * dbp_v)) / 3.)
    

    norp = get_last24_values(NORP, d, pred_dt)
    if isinstance(norp, str):
        norp = 0
    else:
        norp = 1

    dopa = get_last24_values(DOPA, d, pred_dt)
    if isinstance(dopa, str):
        dopa = 0
    else:
        dopa = 1

    dobu = get_last24_values(DOBU, d, pred_dt)
    if isinstance(dobu, str):
        dobu = 0
    else:
        dobu = 1

    if len(mbp_values) == 0:
        return 0
    
    mbp = min(mbp_values)
    nvdu = norp + dopa + dobu 
    if mbp < 70. and nvdu >= 3:
        return 4
    elif mbp < 70. and nvdu == 2:
        return 3
    elif mbp < 70. and nvdu == 1:
        return 2
    elif mbp < 70. and nvdu == 0:
        return 1
    else:
        return 0

# calculate gcs score
def calc_gcs(d, pred_dt):
    v = get_last24_values(GCS, d, pred_dt)
    if isinstance(v, str):
        return 0
    
    v = min(v)
    # alert
    if v == 15:
        return 0
    
    # drowsy
    elif v == 13:
        return 1
    
    # stupor
    elif v == 10:
        return 2
    
    # semicoma
    elif v == 6:
        return 3
    
    # coma
    elif v == 3:
        return 4
    
    else:
        return 0

# calculate renal score
def calc_renal(d, pred_dt):
    urine_values = get_last24_values(URINE, d, pred_dt)
    if isinstance(urine_values, str):
        urine = None
    else:
        urine = True

    creatinine_values = get_last24_values(CREATININE, d, pred_dt)
    if isinstance(creatinine_values, str):
        creatinine = None
    else:
        creatinine = True

    scores = set([0])
    if urine:
        urine = sum(urine_values)
        if urine < 200:
            scores.add(4)
        elif urine < 500:
            scores.add(3)
        else:
            scores.add(0)
    if creatinine:
        creatinine = max(creatinine_values)
        if creatinine > 5.0:
            scores.add(4)
        elif creatinine >= 3.5:
            scores.add(3)
        elif creatinine >= 2.0:
            scores.add(2)
        elif creatinine >= 1.2:
            scores.add(1)
        else:
            scores.add(0)

    if not (urine and creatinine):
        scores.add(4)

    return max(list(scores))

# calculate total sofa score
def calc_medscore(pred_time, features):

    medscore = 0
    medscore += calc_respiratory_rate(features, pred_time)
    medscore += calc_coagulation(features, pred_time)
    medscore += calc_liver(features, pred_time)
    medscore += calc_cardiovascular(features, pred_time)
    medscore += calc_gcs(features, pred_time)
    medscore += calc_renal(features, pred_time)

    return medscore