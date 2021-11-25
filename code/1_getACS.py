"""
Author: Jameson Carter
File Description:
This file gets shapefiles for the ACS at the tract level, using the 
autocensus package: https://github.com/socrata/autocensus, which can be
installed using pip install autocensus and works for python 3.7 and higher.
Downloading this file may fail. Apparently the process for downloading these
files is a bit complicated. See getACS_readMe if you encounter issues.

File Input: Your census API key and 'ACS Variable Documentation.csv.' The
file contains a list of variables to be queried in the queryCensus function.

File Output: A pandas dataframe containing every Census Tract in Cook County, with a 
'geometry' field, readable by the geopandas package. Tracking 100 variables.
"""
from autocensus import Query
import pandas as pd
from pyprojroot import here

def queryCensus(apiKey):
    ACSVars = pd.read_csv(here('./documents/ACS Variable Documentation.csv')) # read variables
    
    '''
    Initialize query object for autocensus. 
    estimate = 5 establishes 5-year averages
    years = 2019 sets the final year for the 5 year average
    variables = list(ACSVars['Key']) calls the variables of interest
    for_geo = 'tract:*' selects all tracts
    in_geo=['state:17','county:031'] selects Cook County, in Illinois
    geometry='polygons' establishes that we want polygon data
    census_api_key= apiKey your API key!
    '''
    query = Query(
        estimate=5,
        years=2019,
        variables=list(ACSVars['Key']),
        for_geo='tract:*',
        in_geo=['state:17','county:031'],
        # Optional arg to add geometry: 'points', 'polygons', or None (default)
        geometry='polygons',
        census_api_key= apiKey )
    
    initial = query.run() # run the query and get initial DataFrame
    
    # Initial DataFrame is long, and we want wide. So I find all of the unique
    # polygon data by dropping duplicates. Initial is preserved.
    polygons = initial[['geo_id','geometry']].drop_duplicates() 
    
    # Reshape to wide, losing polygon data in the process
    reshaped = initial.pivot(index = ['geo_id', 'name'], 
                             columns = 'variable_code', 
                             values = 'value')
    
    # Merge polygon data back onto the reshaped file using geo_id
    result = pd.merge(reshaped,polygons,
                      left_on = 'geo_id', right_on = 'geo_id', 
                      how = 'left')
    
    return result


if __name__ == '__main__':
    apikey = input('Enter your Census API Key: ')
    err = 1
    while err != 0:
        try:
            frame = queryCensus(apikey)
            frame.to_csv(here('./data/raw/ACSFile.csv'), 
                         encoding='utf-8', index=False)
            err = 0
        except:
            print('Try again! Error.')
            apikey = input('Enter your Census API Key: ')