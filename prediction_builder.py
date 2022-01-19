from pyexpat import model
import time
from typing import final
import pandas as pd
import numpy as np
from darts import TimeSeries
from darts.models import ExponentialSmoothing
from darts.metrics import mape
from darts.utils.statistics import check_seasonality
import numbers
import math
import json
import matplotlib.pyplot as plt
import datetime as dt
import statsmodels.api as sm
from scipy.stats import normaltest
import warnings
warnings.filterwarnings("ignore")
import logging
logging.disable(logging.CRITICAL)

def eval_backtest(model, series, bt_start):
    bt_t_start = time.perf_counter()
    print("> Starting backtests...")
    horizons = [3,6,12,24,36]
    backtests = []

    res_backtest = {}
    print("> Starting backtest evaluation of model {}...".format(model))
    for horizon in horizons:
        if len(series) - (len(series)*bt_start) > horizon:
            temp_backtest = model.historical_forecasts(series, start=bt_start, forecast_horizon = horizon)
            err = mape(temp_backtest, series)
            res_backtest[str(horizon)] = {'mape': err, 'backtest': temp_backtest} 
        else:
            res_backtest[str(horizon)] = None 

    bt_res_time = time.perf_counter() - bt_t_start
    print(f"> Backtest script took " + str(bt_res_time) + " sec")
    res_backtest['time'] = bt_res_time
    return res_backtest

def eval_model(model, train, val):
    t_start = time.perf_counter()
    print("> Starting evaluation of model {}...".format(model))
    
    #fit model and compute forecast
    model.fit(train)
    
    forecast = model.predict(len(val))

    #compute accuracy and processing time
    res_mape = mape(val,forecast)
    res_time = time.perf_counter() - t_start
    res_accuracy = {"MAPE": res_mape, "time": res_time}
    results = [forecast, res_accuracy]
    print("> Completed: " + str(model) + ": " + str(res_time) + "sec")
    return results

def check_trend(series, ld, mld, yld):
    trend_obj = {}
    trend_obj['month_trend'] = ld/mld
    if yld is not None:
        trend_obj['year_trend'] = ld/yld
    else: 
         trend_obj['year_trend'] = None
    return trend_obj

#TODO: Add function to check forecast
def check_forecast(series, model):
    t_start = time.perf_counter()
    print("> Starting evaluation of model {}...".format(model))
    
    #fit model and compute forecast
    model.fit(series)
    horizons = [3,6,12,24]
    forecasts =[]
    for horizon in horizons:

        forecast = model.predict(horizon)
        forecasts.append(forecast)

    #compute accuracy and processing time

    res_time = time.perf_counter() - t_start
    res_accuracy = {"time": res_time}
    results = [forecasts, res_accuracy]
    print("> Completed: " + str(model) + ": " + str(res_time) + "sec")
    return results

def create_predictions(skill_time_series):
    final_forecast = {}
    t_start_script = time.perf_counter()
    print(f"> Creating prediction from time series...")
    MSEAS = 12                   # seasonality periodicity default
    ALPHA = 0.05                  # significance level default
    BT_START = 0.3             #from where to start backtesting
    BT_HORIZON = 36             #how many months ahead to forecast in backtest
    FORECAST_HORIZON = 6        #how many months to forecast
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
    skill_data = skill_data[date_counter:-1] #remove all leading zero-values aswell as last value (which gets a weird value due to monthly resample and not having all days for that month)
    print(skill_data)
    last_data = skill_data[-1]
    month_trend_data = skill_data[-2]
    if len(skill_data) > 12:
        yearly_trend_data = skill_data[-13]
    else: yearly_trend_data = None
    print(last_data, month_trend_data, yearly_trend_data)
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
    final_forecast['model'] = str(models[0])
    #call eval_model for each of the models  
    model_predictions  = eval_model(m_expon, train, val)
    final_forecast['eval_forecast'] = model_predictions[0]
    final_forecast['eval_mape'] = model_predictions[1]['MAPE']
    final_forecast['eval_mape'] = model_predictions[1]['time']

    # RUN the forecasters and tabulate their prediction accuracy and processing time
    print(f"> Creating table of prediction accuracy and processing time...")
    df_acc = pd.DataFrame.from_dict(model_predictions[1], orient="index")
    df_acc.columns = [str(models[0])]

    for m in enumerate(models): 
        df = pd.DataFrame.from_dict(model_predictions[1], orient="index")
        df.columns = [str(m)]
        df_acc = pd.concat([df_acc, df], axis=1)
    

    #show df_acc table
    print(df_acc)

    act = val
    for m in enumerate(models):
        pred = model_predictions[0]
        resid = pred - act
        sr = resid.pd_series()
        final_forecast['eval_ljung_box'] = sm.stats.acorr_ljungbox(sr, lags=[5], return_df = False)[1][0]
        try:
            final_forecast['eval_normaltest'] = normaltest(sr)[1]
        except:
            final_forecast['eval_normaltest'] = None
  
   
    script_res_time = time.perf_counter() - t_start_script
    final_forecast['eval_time'] = script_res_time
    print(f"> Eval script took " + str(script_res_time) + " sec")

    #backtesting
    try:
        res_backtest = eval_backtest(models[0], skill_series, BT_START)
        
        final_forecast['backtest'] = res_backtest
    except:
        final_forecast['backtest'] = None
   
    trend = check_trend(skill_series, last_data, month_trend_data, yearly_trend_data)
    forecast = check_forecast(skill_series, models[0])
    final_forecast['trend'] = trend
    final_forecast['forecast'] = forecast
    print(forecast)
    print(trend)
    return final_forecast
 
 
 
 


if __name__ == "__main__":
    dataset = json.load(open("./enriched/enriched-jobs.json"))
    for occupation in dataset.keys():
        input_data = pd.read_json(dataset[occupation]["series"], typ="series")
        pred = create_predictions(input_data)
        dataset[occupation]["prediction"] = pred
