# Calculating MEWS score

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

# Get last valid feature value from prediction time
# feature: feature name
# d: dictionary of feature list 
# pred_dt: prediction time
def get_latest_value(feature, d, pred_dt):
    if feature not in d:
        return NO_FEATURE_VALUE

    dt_values = d[feature]
    dt_values = list(filter(lambda x: x[0] <= pred_dt, dt_values))
    dt_values = list(filter(lambda x: is_valid_feature_value(feature, x[1]), dt_values))
    if not dt_values:
        return NO_FEATURE_VALUE

    dt_values = sorted(dt_values, key=lambda x: x[0])
    return dt_values[-1][1]

# calculate sbp score
def calc_sbp(d, pred_dt):
    v = get_latest_value(SBP, d, pred_dt)
    if v == NO_FEATURE_VALUE:
        return 0

    if v <= 70.:
        return 3
    elif v <= 80:
        return 2
    elif v <= 100:
        return 1
    elif v < 200:
        return 0
    else:
        return 2

# calculate heart rate score
def calc_heart_rate(d, pred_dt):
    v = get_latest_value(PULSE, d, pred_dt)
    if v == NO_FEATURE_VALUE:
        return 0

    if v <= 40:
        return 2
    elif v <= 50:
        return 1
    elif v <= 100:
        return 0
    elif v <= 110:
        return 1
    elif v < 130:
        return 2
    else:
        return 3

# calculate respiratory_rate score
def calc_respiratory_rate(d, pred_dt):
    v = get_latest_value(RESP, d, pred_dt)
    if v == NO_FEATURE_VALUE:
        return 0

    if v < 9:
        return 2
    elif v <= 14:
        return 0
    elif v <= 20:
        return 1
    elif v < 30:
        return 2
    else:
        return 3

# calculate temperature score
def calc_temperature(d, pred_dt):
    v = get_latest_value(TEMP, d, pred_dt)
    if v == NO_FEATURE_VALUE:
        return 0

    if v < 35:
        return 2
    elif v < 38.5:
        return 0
    else:
        return 2

# calculate avpu score
def calc_avpu(d, pred_dt):
    v = get_latest_value(GCS, d, pred_dt)
    if v == NO_FEATURE_VALUE:
        return 0

    if v <= 6:
        return 3
    elif v <= 8:
        return 2
    elif v <= 13:
        return 1
    else:
        return 0

# calculate total MEWS score
def calc_medscore(pred_time, features):

    medscore = 0
    medscore += calc_sbp(features, pred_time)
    medscore += calc_heart_rate(features, pred_time)
    medscore += calc_respiratory_rate(features, pred_time)
    medscore += calc_temperature(features, pred_time)
    medscore += calc_avpu(features, pred_time)

    return medscore