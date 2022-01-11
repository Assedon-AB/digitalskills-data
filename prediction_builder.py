import time
import pandas as pd
import numpy as np
from darts import TimeSeries
from darts.models import ExponentialSmoothing
from darts.metrics import mape
from darts.utils.statistics import check_seasonality
import numbers
import math
import datetime as dt
import statsmodels.api as sm
from scipy.stats import normaltest

def eval_model(model, train, val):
    t_start = time.perf_counter()
    print("> Starting evaluation of model {}...".format(model))
    
    #fit model and compute forecast
    res = model.fit(train)
    forecast = model.predict(len(val))

    #compute accuracy and processing time
    res_mape = mape(val,forecast)
    res_time = time.perf_counter() - t_start
    res_accuracy = {"MAPE": res_mape, "time": res_time}
    results = [forecast, res_accuracy]
    print("> Completed: " + str(model) + ": " + str(res_time) + "sec")
    return results


def create_predictions(skill_time_series):
    t_start_script = time.perf_counter()
    print(f"> Creating prediction from time series...")
    MSEAS = 12                   # seasonality periodicity default
    ALPHA = 0.05                  # significance level default

    ## load data
    skill_data = skill_time_series.resample('M').sum()

    #find first month where skill is demanded
    date_keys = skill_data.keys()
    date_counter = 0
    for d in date_keys:
        date_interval_keys = date_keys[date_counter:date_counter+13]
        
        count_sum = 0
        for dik in date_interval_keys:
            count_sum+= skill_data[dik]
        if count_sum > 10:
            break
        else: date_counter += 1
    print(date_keys[date_counter])
    skill_data = skill_data[date_counter:-1] #remove all leading zer-values aswell as last value (which gets a weird value due to monthly resample and not having all days for that month)

    cut_off_index = round(len(skill_data)*0.2)  #80/20 rule for train/test
    cut_off_date = skill_data.keys()[len(skill_data)-cut_off_index] #get date where to split between train and test based on cut_off_index

    TRAIN = dt.datetime(cut_off_date.year,cut_off_date.month,cut_off_date.day).date() #a bit unnecessary converting timestamp to date this way, but good to have if input changes

    skill_ts = TimeSeries.from_series(skill_data)
    skill_df = skill_ts.pd_dataframe()
    skill_pd_series = skill_ts.pd_series()
    skill_pd_series.replace(0.0, np.nan, inplace=True)
    skill_pd_series = skill_pd_series.fillna(method="bfill")
    skill_series = skill_ts.from_series(skill_pd_series)  #Is this really correct? TODO: check if necessary step
    print(f"> Description of time series")
    print(skill_series.describe())  

    #check for seasonality
    print(f"> Checking seasonality...")
    for m in range(2,25):
        is_seasonal, mseas = check_seasonality(skill_series, m=m, alpha=ALPHA)
        if is_seasonal:
            print(f"> The times series is seasonal.")
            print("> Seasonality of order {} detected.".format(mseas))
            break

    #split train and test data base on TRAIN variable
    print(f"> Splitting data into traing and validation...")
    if isinstance(TRAIN, numbers.Number):
        split_at = TRAIN
    else:
        split_at = pd.Timestamp(TRAIN)
    
    train, val = skill_series.split_before(split_at)
    print("> train is {} month long".format(len(train)))
    print("> val is {} month long".format(len(val)))

    #fit and ocompute prediction
    
    #prepare exponential smoothing forecaster
    if is_seasonal:
        m_expon = ExponentialSmoothing(seasonal_periods=mseas)
    else:
        m_expon = ExponentialSmoothing()

    models = [m_expon]

    #call eval_model for each of the models  
    model_predictions  = [eval_model(m_expon, train, val)]

    # RUN the forecasters and tabulate their prediction accuracy and processing time
    print(f"> Creating table of prediction accuracy and processing time...")
    df_acc = pd.DataFrame.from_dict(model_predictions[0][1], orient="index")
    df_acc.columns = [str(models[0])]

    for i, m in enumerate(models):
        if i > 0: 
            df = pd.DataFrame.from_dict(model_predictions[i][1], orient="index")
            df.columns = [str(m)]
            df_acc = pd.concat([df_acc, df], axis=1)
        i +=1

    pd.set_option("display.precision",3)
    df_acc.style.highlight_min(color="lightgreen", axis=1).highlight_max(color="yellow", axis=1)
    #show df_acc table
    print(df_acc)

    act = val

    resL = {}
    resN = {}
    for i,m in enumerate(models):
        pred = model_predictions[i][0]
        resid = pred - act
        sr = resid.pd_series()
        resL[str(m)] = sm.stats.acorr_ljungbox(sr, lags=[5], return_df = False)[1][0]
        resN[str(m)] = normaltest(sr)[1]
    
    print("> Ljung-Box test for white-noise residuals: p-value > alpha?")
    [print(key,":",value) for key,value in resL.items()]

    print("> Test for normality of residuals: p-value > alpha?")
    [print(key,":",value) for key,value in resN.items()]
    script_res_time = time.perf_counter() - t_start_script
    print(f"> Script took " + str(script_res_time) + " sec")
    return model_predictions[0]
 
 
 
 
#TEST TODO: Remove   
dataset = "/Users/andreassamuelsson/Projects/Jobtechdev/UKA-Sandbox/time series/react_regex_time_series.json"
input_data = pd.read_json(dataset, typ="series")

create_predictions(input_data)

