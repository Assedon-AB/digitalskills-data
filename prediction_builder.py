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
    horizons = [3,6,12]
    backtests = []

    res_backtest = {}
    print("> Starting backtest evaluation of model {}...".format(model))
    for horizon in horizons:
        if len(series) - (len(series)*bt_start) > horizon:
            temp_backtest = model.historical_forecasts(series, start=bt_start, forecast_horizon = horizon)
            err = mape(temp_backtest, series)
            res_backtest[str(horizon)] = {'mape': float(err), 'backtest': temp_backtest} 
        else:
            res_backtest[str(horizon)] = None 

    bt_res_time = time.perf_counter() - bt_t_start
    print(f"> Backtest script took " + str(bt_res_time) + " sec")
    res_backtest['time'] = float(bt_res_time)
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
    res_accuracy = {"MAPE": float(res_mape), "time": float(res_time)}
    results = [forecast, res_accuracy]
    print("> Completed: " + str(model) + ": " + str(res_time) + "sec")
    return results

def check_trend(series, ld, mld, qld, hyld, yld):
    trend_obj = {}
    #trend_obj['month_trend'] = ld/mld
    if qld is not None:
        trend_obj['month_3'] = float(((ld/qld)*100)-100)
    else: 
         trend_obj['month_3'] = None
    if hyld is not None:
        trend_obj['month_6'] = float(((ld/hyld)*100)-100)
    else: 
         trend_obj['month_6'] = None
    if yld is not None:
        trend_obj['month_12'] = float(((ld/yld)*100)-100)
    else: 
         trend_obj['month_12'] = None
    return trend_obj

#TODO: Add function to check forecast
def check_forecast(series, model, last_measured_data):
    t_start = time.perf_counter()
    print("> Starting evaluation of model {}...".format(model))
    
    #fit model and compute forecast
    model.fit(series)
    horizons = [3,6,12]
    forecasts = {}
    prediction_series = {}
    prediction_percentages = {}
    prediction_values = {}
    for horizon in horizons:

        forecast = model.predict(horizon)
        
        forecast_json = json.loads(forecast.to_json())
        labels_raw = forecast_json['index']
        data_raw = forecast_json['data']
        labels_clean = []
        data_clean = []
        for label in labels_raw:
            label_clean = label.split('T')[0]
            labels_clean.append(label_clean)
        for d in data_raw:
            data_clean.append(int(round(d[0])))
      
        horizon_key = "month_"+str(horizon)
        prediction_series[horizon_key] = {'labels': labels_clean, 'values': data_clean}
        prediction_values[horizon_key] = data_clean[-1]
        prediction_percentages[horizon_key] = float((((data_clean[-1]/last_measured_data)*100)-100).item())
        
        

    forecasts['prediction_series'] = prediction_series
    forecasts['prediction_values'] = prediction_values
    forecasts['prediction_percentages'] = prediction_percentages
    print("> Completed: " + str(model))
    return forecasts

def create_predictions(skill_time_series):
    final_forecast = {}
    t_start_script = time.perf_counter()
    print(f"> Creating prediction from time series...")
    MSEAS = 12                   # seasonality periodicity default
    ALPHA = 0.05                  # significance level default
    BT_START = 0.3             #from where to start backtesting
    #BT_HORIZON = 36 not used             #how many months ahead to forecast in backtest
    #FORECAST_HORIZON = 6  not used    #how many months to forecast
    ## load data
    skill_data = skill_time_series.resample('M').sum()
    print(skill_data)

    #find first month where skill is demanded
    date_keys = skill_data.keys()
    date_counter = 0
    for d in date_keys:
        date_interval_keys = date_keys[date_counter:date_counter+13]
        
        count_sum = 0
        for intervalKey in date_interval_keys:
            count_sum+= skill_data[intervalKey]
        if count_sum > 10:
            break
        else: date_counter += 1
    print(date_keys[date_counter])
    skill_data = skill_data[date_counter:-1] #remove all leading zero-values aswell as last value (which gets a weird value due to monthly resample and not having all days for that month)
    print(skill_data)
    last_data = skill_data[-1]
    month_trend_data = skill_data[-2] #TODO: remove later if we choose to not use monthly
    if len(skill_data) > 3:
        quarterly_trend_data = skill_data[-4]
    else: quarterly_trend_data = None
    if len(skill_data) > 6:
        half_year_trend_data = skill_data[-7]
    else: half_year_trend_data = None
    if len(skill_data) > 12:
        yearly_trend_data = skill_data[-13]
    else: yearly_trend_data = None
    print(last_data, month_trend_data, quarterly_trend_data, half_year_trend_data, yearly_trend_data)
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
    final_forecast['eval_mape'] = float(model_predictions[1]['MAPE'])
    final_forecast['eval_mape'] = float(model_predictions[1]['time'])

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
        final_forecast['eval_ljung_box'] = float(sm.stats.acorr_ljungbox(sr, lags=[5], return_df = False)[1][0])
        try:
            final_forecast['eval_normaltest'] = float(normaltest(sr)[1])
        except:
            final_forecast['eval_normaltest'] = None
  
   
    script_res_time = time.perf_counter() - t_start_script
    final_forecast['eval_time'] = float(script_res_time)
    print(f"> Eval script took " + str(script_res_time) + " sec")

    #backtesting
    try:
        res_backtest = eval_backtest(models[0], skill_series, BT_START)
        
        final_forecast['backtest'] = res_backtest
    except:
        final_forecast['backtest'] = None
   
    trend = check_trend(skill_series, last_data, month_trend_data, quarterly_trend_data, half_year_trend_data, yearly_trend_data)
    forecast = check_forecast(skill_series, models[0], last_data)
    final_forecast['trend_percentages'] = trend
    final_forecast['trend'] = {'month_3': int(quarterly_trend_data),'month_6': int(half_year_trend_data),'month_12': int(yearly_trend_data)}
    final_forecast['prediction_series'] = forecast['prediction_series']
    final_forecast['prediction_values'] = forecast['prediction_values']
    final_forecast['prediction_percentages'] = forecast['prediction_percentages']
    final_forecast['series'] = skill_series
    skills_series_json = json.loads(skill_series.to_json())
    skill_labels_raw = skills_series_json['index']
    skill_data_raw = skills_series_json['data']
    skill_labels_clean = []
    skill_data_clean = []
    for label in skill_labels_raw:
        label_clean = label.split('T')[0]
        skill_labels_clean.append(label_clean)
    for d in skill_data_raw:
        skill_data_clean.append(int(round(d[0])))
    
  
    final_forecast['series'] = {'labels': skill_labels_clean, 'values': skill_data_clean}
    return final_forecast
 
 
 
 


if __name__ == "__main__":
    dataset = json.load(open("./enriched/enriched-jobs.json"))
    #for occupation in dataset.keys():
    input_data = pd.read_json(dataset["frontendutvecklare"]["series"], typ="series")
    pred = create_predictions(input_data)
    print(pred.values())
    pred['eval_forecast'] = pred['eval_forecast'].to_json()
    with open("data/skills_predicted.json", "w", encoding="utf-8") as fd:
        json.dump(pred, fd, ensure_ascii=False, indent=4)
