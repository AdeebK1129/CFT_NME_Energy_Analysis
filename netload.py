import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#Note to others: CHANGE THE FILE DIRECTORY OF THE FOLLOWING DATA FILES WHEN DOWNLOADED
power_generation_file_path = '/Users/jasonchen/Desktop/generation_by_source.csv'
historical_power_file_path = '/Users/jasonchen/Desktop/historical_power_load.csv'

generation_data = pd.read_csv(power_generation_file_path)
load_data = pd.read_csv(historical_power_file_path)

# We display rows of each dataset to understand their structure
generation_data.head(), load_data.head()

# Now convert the datetime columns to objects for them to align and merge
generation_data['datetime_beginning_utc'] = pd.to_datetime(generation_data['datetime_beginning_utc']) 
load_data['forecast_hour_beginning_utc'] = pd.to_datetime(load_data['forecast_hour_beginning_utc'])

# Filter the generation data to only include renewable sources (is_renewable == True)
renewable_generation = generation_data[generation_data['is_renewable']]
renewable_generation_agg = renewable_generation.groupby('datetime_beginning_utc')['mw'].sum().reset_index() # by hour
clean_data = pd.merge(load_data, renewable_generation_agg, left_on='forecast_hour_beginning_utc', right_on='datetime_beginning_utc', how='left') # Merge the renewable generation data with the load data
clean_data['mw'].fillna(0, inplace=True)

clean_data['net_load_mw'] = clean_data['forecast_load_mw'] - clean_data['mw'] # Calculate the net load as total load minus renewable generation

#Note to others, CHANGE THE OUTPUT PATH WHEN DOWNLOADED
net_load_data = clean_data[['forecast_hour_beginning_utc', 'forecast_load_mw', 'mw', 'net_load_mw']]
output_path = '/Users/jasonchen/Desktop/net_load_data.csv'
net_load_data.to_csv(output_path, index=False)
print(net_load_data.head())

# Plot net load
plt.figure(figsize=(30, 6))
plt.plot(net_load_data['forecast_hour_beginning_utc'], net_load_data['net_load_mw'], label='Net Load (MW)', color='red')

#details
plt.title('Net Load over time')
plt.xlabel('Time (hours)')
plt.ylabel('Net Load of Power (MegaW)')
plt.xticks(rotation=45)
plt.grid(True)
plt.legend()
plt.tight_layout()

# #Note to others, CHANGE THE OUTPUT PATH WHEN DOWNLOADED
output_image_path = '/Users/jasonchen/Desktop/net_load_plot.png'
plt.savefig(output_image_path, dpi=300)  

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# PART (2) ANALYSING THE CYCLICALITY OF THIS METRIC
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

#Note to others, CHANGE THE OUTPUT PATH WHEN DOWNLOADED
net_load_file_path = '/Users/jasonchen/Desktop/net_load_data.csv'
net_load_data = pd.read_csv(net_load_file_path)

# Convert datetime column to object
net_load_data['forecast_hour_beginning_utc'] = pd.to_datetime(net_load_data['forecast_hour_beginning_utc'])
net_load_data.set_index('forecast_hour_beginning_utc', inplace=True)
daily_net_load = net_load_data['net_load_mw'].resample('D').mean()

#autocorrelation part to analyze cyclicality
def autocorrelation(x, lag):
    return np.corrcoef(x[:-lag], x[lag:])[0, 1]
lags = np.arange(1, 31)
autocorrelations = [autocorrelation(daily_net_load.values, lag) for lag in lags]

# We plot the values
plt.figure(figsize=(10, 6))
plt.stem(lags, autocorrelations)
plt.title('Autocorrelation of Daily Net Load (Cyclicality Analysis)')
plt.xlabel('Lag (days)')
plt.ylabel('Autocorrelation')
plt.grid(True)

#Note to others, CHANGE THE OUTPUT PATH WHEN DOWNLOADED
autocorrelation_plot_path = '/Users/jasonchen/Desktop/cyclic_plot.png'
plt.savefig(autocorrelation_plot_path, dpi=300) 