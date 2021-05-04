
import pandas as pd
import numpy as np

from django.shortcuts import render, redirect
from .models import Stock
from .forms import StockForm
from django.contrib import messages

import requests
#r4vw9kpbibnntQyW3rKW0QsxYKsUYk6b
def home(request):

   import json

   if request.method == 'POST':
      ticker = request.POST['ticker']

      api_request = requests.get("https://api.polygon.io/v1/open-close/"+ticker+"/2021-04-29?unadjusted=true&apiKey=t4Rp6mGojxYHWp3bZDaSL9G3Sm1i9mOO")
      api_request2 = requests.get("https://api.polygon.io/v1/meta/symbols/"+ticker+"/company?&apiKey=t4Rp6mGojxYHWp3bZDaSL9G3Sm1i9mOO")

      try:
         api1 = json.loads(api_request.content)
         api2 = json.loads(api_request2.content)
      except Exception as e:
         api1 = "Error..."
      return render(request, 'home.html', {'api1': api1,'api2': api2})

   else:
      return render(request, 'home.html', {'ticker': "Enter a Ticker Symbol Above..."})

def index(request):


	return render(request,'index.html')
df=pd.read_csv('D:\hackathon may\prediction/BAJFINANCE.csv')

def analyze(request):
	import json
	df.set_index('Date', inplace=True)
	df.dropna(inplace=True)
	df.isna().sum()
	data = df.copy()
	lag_features = ['High', 'Low', 'Volume', 'Turnover', 'Trades']
	window1 = 3
	window2 = 7
	for feature in lag_features:
		data[feature + 'rolling_mean_3'] = data[feature].rolling(window=window1).mean()
		data[feature + 'rolling_mean_7'] = data[feature].rolling(window=window2).mean()
	for feature in lag_features:
		data[feature + 'rolling_std_3'] = data[feature].rolling(window=window1).std()
		data[feature + 'rolling_std_7'] = data[feature].rolling(window=window2).std()
	data.dropna(inplace=True)
	ind_features = ['Highrolling_mean_3', 'Highrolling_mean_7',
					'Lowrolling_mean_3', 'Lowrolling_mean_7', 'Volumerolling_mean_3',
					'Volumerolling_mean_7', 'Turnoverrolling_mean_3',
					'Turnoverrolling_mean_7', 'Tradesrolling_mean_3',
					'Tradesrolling_mean_7', 'Highrolling_std_3', 'Highrolling_std_7',
					'Lowrolling_std_3', 'Lowrolling_std_7', 'Volumerolling_std_3',
					'Volumerolling_std_7', 'Turnoverrolling_std_3', 'Turnoverrolling_std_7',
					'Tradesrolling_std_3', 'Tradesrolling_std_7']
	training_data = data[0:1800]
	test_data = data[1800:]
	#auto arima
	from pmdarima import auto_arima
	import warnings
	warnings.filterwarnings('ignore')
	model = auto_arima(y=training_data['VWAP'], exogenous=training_data[ind_features], trace=True)
	model.fit(training_data['VWAP'], training_data[ind_features])
	forecast = model.predict(n_periods=len(test_data), exogenous=test_data[ind_features])
	test_data['Forecast_ARIMA'] = forecast
	test_data[['VWAP', 'Forecast_ARIMA']].plot(figsize=(14, 7))
	d1 = test_data['VWAP']
	d2 = test_data['Forecast_ARIMA']




	#checking the accuracy of the model
	from sklearn.metrics import mean_absolute_error, mean_squared_error
	error1 = np.sqrt(mean_squared_error(test_data['VWAP'], test_data['Forecast_ARIMA']))
	error2 = mean_absolute_error(test_data['VWAP'], test_data['Forecast_ARIMA'])
	a1 = test_data['VWAP'].to_list()
	a2 = test_data['Forecast_ARIMA'].to_list()

	list2 = []

	i = 0

	for a, b in zip(a1, a2):
		list = []
		list.append(i + 1)
		list.append(a)
		list.append(b)
		list2.append(list)
		i = i + 1

	values_json = json.dumps(list2)


	# , 'valuesarima': values_json
	params = {'purpose': model, 'mean_squared_error': error1, 'mean_absolute_error': error2, 'valuearima': values_json}

	return render(request, 'analyze.html', params)
def add_stock(request):
	import requests 
	import json 

	if request.method == 'POST':
		form = StockForm(request.POST or None)

		if form.is_valid():
			form.save()
			messages.success(request, ("Stock Has Been Added!"))
			return redirect('add_stock')

	else:	
		ticker = Stock.objects.all()
		output = []
		for ticker_item in ticker:
			api_request = requests.get("https://cloud.iexapis.com/stable/stock/" + str(ticker_item) + "/quote?token=pk_062031d20883444f9ea74e2610fe2011")
			try:
				api = json.loads(api_request.content)
				output.append(api)
			except Exception as e:
				api = "Error..."
		
		return render(request, 'add_stock.html', {'ticker': ticker, 'output': output})


def delete(request, stock_id):
	item = Stock.objects.get(pk=stock_id)
	item.delete()
	messages.success(request, ("Stock Has Been Deleted!"))
	return redirect(delete_stock)



def delete_stock(request):
	ticker = Stock.objects.all()
	return render(request, 'delete_stock.html', {'ticker': ticker})
def about(request):
   import json

   text = request.POST.get("entert")
   start = request.POST.get('from')
   end = request.POST.get('to')
   print(text,start,end)
   api_request = requests.get("https://api.polygon.io/v2/aggs/ticker/" + str(text) + "/range/1/day/" + str(start) +'/' + str(end)+ "?unadjusted=true&sort=asc&limit=120&apiKey=t4Rp6mGojxYHWp3bZDaSL9G3Sm1i9mOO")

   try:
      api = json.loads(api_request.content)
      list=[]
      results = api['results']
      i=1
      for x in results:
         list1=[i]
         for y,z in x.items():
            if(y=='o') :
               list1.append(z)
            elif(y=='c') :
               list1.append(z)
            elif(y=='h') :
               list1.append(z)
            elif(y=='l') :
               list1.append(z)

         list.append(list1)
         i=i+1

      values_json = json.dumps(list)


   except Exception as e:
      api = "Error..."
   return render(request, 'about.html', {'stock_name':text})

def chartgraph(request):

   import json

   text = request.POST.get("entert")
   start = request.POST.get('from')
   end = request.POST.get('to')
   print(text, start, end)
   api_request = requests.get(
      "https://api.polygon.io/v2/aggs/ticker/" + str(text) + "/range/1/day/" + str(start) + '/' + str(
         end) + "?unadjusted=true&sort=asc&limit=120&apiKey=t4Rp6mGojxYHWp3bZDaSL9G3Sm1i9mOO")

   api_request1 = requests.get(
       "https://api.polygon.io/v1/open-close/" + str(text) + "/2021-04-29?unadjusted=true&apiKey=t4Rp6mGojxYHWp3bZDaSL9G3Sm1i9mOO")
   api_request2 = requests.get(
       "https://api.polygon.io/v1/meta/symbols/" + str(text) + "/company?&apiKey=t4Rp6mGojxYHWp3bZDaSL9G3Sm1i9mOO")

   try:
      api = json.loads(api_request.content)

      api1 = json.loads(api_request1.content)
      api2 = json.loads(api_request2.content)


      list = []
      results = api['results']
      i = 1
      for x in results:
         list1 = [i]
         for y, z in x.items():
            if (y == 'o'):
               list1.append(z)
            elif (y == 'c'):
               list1.append(z)
            elif (y == 'h'):
               list1.append(z)
            elif (y == 'l'):
               list1.append(z)

         list.append(list1)
         i = i + 1


      values_json = json.dumps(list)


   except Exception as e:
      api = "Error..."
   return render(request, 'chartgraph.html', {'stock_name': text, 'values': values_json ,'api1': api1,'api2' :api2})