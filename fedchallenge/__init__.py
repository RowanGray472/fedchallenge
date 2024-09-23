"""
This file is used to generate the graphs for the project. It contains all of
the functions that go from an input that looks something like this:

datalist = ["GDPC1", "GDPPOT"]
chart_title = "GDP vs. Potential GDP, 2006-2010 + 2018-2024"
fig = create_line_graph(datalist, chart_title = chart_title,
                                         legend_titles = ['Real GDP', 
                                                          'Real Potential GDP'],
                                         start_date = '2006-01-01',
                                         end_date = '2012-09-01',
                                         y_axis_title = "Billions of Dollars",
                                         y_axis_range = [15000, 24000],
                                         two_time_periods = True,
                                         second_start_date = '2018-01-01',
                                         second_end_date = '2024-09-01',
                                         fomc = False,
                                         recessions = False,
                                        )   

fig.show() 

to an graph that's outputted as a .png file.

Full input instructions can be found in the README.md file.
"""

# Libraries
from fredapi import Fred
import config
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from IPython.display import Image
from plotly.subplots import make_subplots
import datetime
from datetime import datetime
import warnings
warnings.filterwarnings("ignore", category=FutureWarning) #stfu pandas
from dotenv import load_dotenv
load_dotenv()

######################
## HELPER FUNCTIONS ##
######################

# Wrapper function for using FRED API
def fred_api(data_series, units = 'lin'):
    fred = Fred(api_key=FRED_API_KEY)
    data = fred.get_series(data_series, units = units)
    info = fred.get_series_info(data_series)
    return data, info

# Wrapper function for getting just info data
def fred_api_info(data_series):
    fred = Fred(api_key=FRED_API_KEY)
    info = fred.get_series_info(data_series)
    return info

# Retreiving Dataframes
def get_datasets(datalist, units):
  # create data structures to return
  dataframes = []
  datanames = []

  for series_id in datalist:
    # get data from fred
    data, info = fred_api(series_id, units)

    # get data into good df format
    df = pd.DataFrame(data)
    df = df.rename(columns={df.columns[0]: 'values'})
    df['index'] = df.index
    df = df[['index', 'values']]

    # add df and name to lists
    dataframes.append(df)
    datanames.append(info['title'])

  return dataframes, datanames

########################
## PLOTTING FUNCTIONS ##
########################

def create_line_graph(
    datalist,
    chart_title = None,
    legend_titles = 'Default',
    start_date = '2021-01-01',
    end_date = 'Default', # Present
    units = 'lin',
    y_axis_range = 'Default',
    x_axis_title = None,
    y_axis_title = 'Default',
    x_gridlines = False,
    y_gridlines = False,
    x_axis_line = True,
    zero_line = False,
    y_axis_line = False,
    split_y_axis = False,
    num_lines_split_axis = None,
    split_y_axis_title = 'Default',
    split_y_axis_range = 'Default',
    two_time_periods = False,
    second_start_date = '2021-01-01',
    second_end_date = '2023-12-31',
    hor_line = 'Default',
    recessions = True,
    fomc = True,
    num_ticks = 24,
    tick_format = '%b-%y',
    font_family = 'Georgia',
    font_size = 15,
    line_colors = ['darkblue', 'darkgoldenrod', 'green', '#9cb6f5', 'grey'],
    second_line_colors = ['green', '#9cb6f5', 'grey', 'darkblue', 'darkgoldenrod'],
    line_width = 3,
    width=1400,
    height=500
    ):
  """
  This function creates all of the plots. THe defaults are set in the function
  definition, but can be overridden by the user.
  """

  # get data
  dataframes, datanames = get_datasets(datalist, units)

  # if passed in, rename lines
  if legend_titles != 'Default':
      datanames = legend_titles

  # determine primary y-axis title
  if y_axis_title == 'Default':
      y_axis_title = fred_api_info(datalist[0])['units']

  #determine x-axis stopping point
  if end_date == 'Default':
      latest_date = pd.Timestamp("1900-01-01")  # Set to a very old date
      for df in dataframes:
          if not df.empty:
              max_date_in_df = df.iloc[:, 0].max()
          if max_date_in_df > latest_date:
              latest_date = max_date_in_df

      end_date = latest_date

  ## Split Y Axis Case ##
  if split_y_axis:
      # create Plotly figure with subplots
      fig = make_subplots(specs=[[{"secondary_y": True}]])

      # find which data series should be in y1 or y2
      index_split = len(dataframes)-num_lines_split_axis

      # add lines to y-axis 1
      for i, (df, line_color) in enumerate(zip(dataframes[:index_split], line_colors[:index_split])):
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=df.iloc[:, 1], mode='lines', name=f'{datanames[i]}', line=dict(width=line_width, color=line_color)), secondary_y=False)

      # add lines to y-axis 2
      for i, (df, line_color) in enumerate(zip(dataframes[index_split:], line_colors[index_split:])):
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=df.iloc[:, 1], mode='lines', name=f'{datanames[i+index_split]}', line=dict(width=line_width, color=line_color)), secondary_y = True)

      # get y-axis 2 title
      if split_y_axis_title == "Default":
        split_y_axis_title = fred_api_info(datalist[index_split])['units']

      # y-axes formatting
      fig.update_yaxes(title_text=y_axis_title, showgrid=y_gridlines, gridcolor='grey', showline=y_axis_line, linecolor='black', secondary_y=False)
      fig.update_yaxes(title_text=split_y_axis_title, showgrid=y_gridlines, gridcolor='grey', showline=y_axis_line, linecolor='black', secondary_y=True)

      # y-axis 2 range, else use default
      if split_y_axis_range != "Default":
        fig.update_yaxes(range=split_y_axis_range, secondary_y = True)



  ## No Split Y Axis ##
  # create Plotly figure
  else:
      fig = go.Figure()

      # Else no split axis, add lines for all dataframes
      for i, (df, line_color) in enumerate(zip(dataframes, line_colors)):
          fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=df.iloc[:, 1], mode='lines', name=f'{datanames[i]}', line=dict(width=line_width, color=line_color)))
      # Name y-axis
      fig.update_layout(yaxis_title=y_axis_title)
      fig.update_layout(yaxis=dict(showgrid=y_gridlines, gridcolor='grey', showline=y_axis_line, linecolor='black'))



  ## Add horizontal line
  if hor_line != 'Default':

    # Add a horizontal line at the desired y-value
    fig.add_shape(
    go.layout.Shape(
        type="line",
        x0=start_date,
        x1=end_date,
        y0=hor_line,
        y1=hor_line,
        line=dict(color="red", width=5, dash = 'dash'),
    )
    )


  if zero_line:
    # Add a horizontal line at zero to get it to show up
    fig.add_shape(
    go.layout.Shape(
        type="line",
        x0=start_date,
        x1=end_date,
        y0=0,
        y1=0,
        line=dict(color="black", width=1)
    )
    )


  rec_list = [('1857-06-01', '1858-12-01'),
              ('1860-10-01', '1861-06-01'),
              ('1865-04-01', '1867-12-01'),
              ('1869-06-01', '1870-12-01'),
              ('1873-10-01', '1879-03-01'),
              ('1882-03-01', '1885-05-01'),
              ('1887-03-01', '1888-04-01'),
              ('1890-07-01', '1891-05-01'),
              ('1893-01-01', '1894-06-01'),
              ('1895-12-01', '1897-06-01'),
              ('1899-06-01', '1900-12-01'),
              ('1902-09-01', '1904-08-01'),
              ('1907-05-01', '1908-06-01'),
              ('1910-01-01', '1912-01-01'),
              ('1913-01-01', '1914-12-01'),
              ('1918-08-01', '1919-03-01'),
              ('1920-01-01', '1921-07-01'),
              ('1923-05-01', '1924-07-01'),
              ('1926-10-01', '1927-11-01'),
              ('1929-08-01', '1933-03-01'),
              ('1937-05-01', '1938-06-01'),
              ('1945-02-01', '1945-10-01'),
              ('1948-11-01', '1949-10-01'),
              ('1953-07-01', '1954-05-01'),
              ('1957-08-01', '1958-04-01'),
              ('1960-04-01', '1961-02-01'),
              ('1969-12-01', '1970-11-01'),
              ('1973-11-01', '1975-03-01'),
              ('1980-01-01', '1980-07-01'),
              ('1981-07-01', '1982-11-01'),
              ('1990-07-01', '1991-03-01'),
              ('2001-03-01', '2001-11-01'),
              ('2007-12-01', '2009-06-01'),
              ('2020-02-01', '2020-04-01')]
  if recessions:

    for (rec0, rec1) in rec_list:
        fig.add_shape(
            go.layout.Shape(
                type="rect",
                fillcolor = "grey",
                line = dict(color = "grey"),
                opacity = 0.3,
                x0 = rec0,
                x1 = rec1,
                xref = "x",
                y0 = 0,
                y1 = 1,
                yref = "paper"
            )
        )
  fomc_dates = ["01-30", "03-19", "04-30", "06-11", "07-30", "09-17", "11-06", "12-17"]
  fomc_list = []
  for year in range(2005, datetime.now().year + 1):
      for date in fomc_dates:
          fomc_list.append(f"{year}-{date}")
  if fomc:
      for fomc in fomc_list:
          fig.add_shape(
              go.layout.Shape(
                  type="line",
                  line=dict(
                      color="rgba(255, 0, 0, 0.5)",  # semi-transparent red
                      width=1,
                      dash="dash"  # dashed line
                  ),
                  x0=fomc,
                  x1=fomc,
                  y0=0,
                  y1=1,
                  xref="x",
                  yref="paper"
              )
          )
  ## Graph Layouts (Split and Nonsplit Cases)##

  # Non-parameterized layout
  fig.update_layout(
      paper_bgcolor='white',  # Set background color to white
      plot_bgcolor='white',   # Set plot background color to white
  )

  # Default value custom layout
  fig.update_layout(
      title=chart_title,
      xaxis_title = x_axis_title,
      #yaxis=dict(showgrid=y_gridlines, gridcolor='grey', showline=y_axis_line, linecolor='black'),
      xaxis=dict(
          showgrid=x_gridlines,
          gridcolor='grey',
          showline=x_axis_line,
          linecolor='black',
          showticklabels=True,
          ticks='outside',
          tickmode='auto',  # Automatically calculate the date ticks
          nticks=num_ticks,  # Adjust the number of ticks as needed
          tickformat= tick_format,  # Format of the date ticks
          tickfont=dict(family=font_family, size=font_size), # Set the font family and size
          range=[start_date, end_date]),
      xaxis2=dict(
        showgrid=x_gridlines,
        gridcolor='grey',
        showline=x_axis_line,
        linecolor='black',
        showticklabels=True,
        ticks='outside',
        tickmode='auto',  # Automatically calculate the date ticks
        nticks=num_ticks,  # Adjust the number of ticks as needed
        tickformat= tick_format,  # Format of the date ticks
        tickfont=dict(family=font_family, size=font_size), # Set the font family and size
        range=[second_start_date, second_end_date],
        side='top',
        overlaying='x',
    ),
      font=dict(family=font_family, size=font_size), # Set the font family and size for all non-tick text on graph
      legend = dict(orientation = "h",   # show entries horizontally
                     xanchor = "center",  # use center of legend as anchor
                     x = 0.5,  # put legend in center of x-axis
                     y = -0.2 # buffer space between legend and x-axis
                    ),
  )

  # Check if two_time_periods is True
  if two_time_periods:
      # Fetch the data for the second time period
      second_dataframes, second_datanames = get_datasets(datalist, units)
      second_dataframes = [df[(df.iloc[:, 0] >= second_start_date) & (df.iloc[:, 0] <= second_end_date)] for df in second_dataframes]

      # Add a new line to the graph for each dataset on the secondary x-axis
      for i, (df, line_color) in enumerate(zip(second_dataframes, second_line_colors)):
          fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=df.iloc[:, 1], mode='lines', name=f'{second_datanames[i]} (2nd period)', line=dict(width=line_width, color=line_color), xaxis='x2'))
          
  # Auto Populate Cases
  if y_axis_range != "Default":
    fig.update_layout(yaxis=dict(range=y_axis_range))
    # else graph will use defaults

  # Show the plot
  # fig.show() not using basic show() because of resolution issues
  return fig


###############
## PLOT CODE ##
###############


"""
This code serves as a repository for the code that creates all the graphs. 
Running this code will generate all of these graphs and save them to local 
memory where they can be referenced. Once you're satisfied with all of
the graphs, you can save them with code below this.
"""


##############
### SET-UP ###
##############

figures_list = []
chart_titles = []

########################
### 2006-2010 GRAPHS ###
########################

datalist = ["GDPC1", "GDPPOT"]
chart_title = "GDP vs. Potential GDP, 2006-2010"
fig1_1 = create_line_graph(datalist, chart_title = chart_title,
                                         legend_titles = ['Real GDP', 
                                                          'Real Potential GDP'],
                                         start_date = '2006-01-01',
                                         end_date = '2010-09-01',
                                         y_axis_title = "Billions of Dollars",
                                         y_axis_range = [15000, 20000]                                         
                                        )
figures_list.append(fig1_1)
chart_titles.append(chart_title)

datalist = ["MEDLISPRIUS", "MEDLISPRIPERSQUFEEUS"]
chart_title = "Home List Price vs. Home List Price per Square Foot, 2006-2010"
fig1_2 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2006-01-01',
                                         end_date = '2010-09-01',
                                         y_axis_title = "U.S. Dollars",
                                         split_y_axis_title = "U.S. Dollars",
                                         split_y_axis = True,
                                         num_lines_split_axis = 1
                                        )
figures_list.append(fig1_2)
chart_titles.append(chart_title)


datalist = ["MSPUS"]
chart_title = "Home Sale Price, 2006-2010"
fig1_3 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2006-01-01',
                                         end_date = '2010-09-01',
                                         y_axis_title = "U.S. Dollars",
                                         y_axis_range = [200000, 300000]
                                        )
figures_list.append(fig1_3)
chart_titles.append(chart_title)

datalist = ["MORTGAGE30US"]
chart_title = "30 Year Fixed Rate Mortage Average, 2006-2010"
fig1_4 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2006-01-01',
                                         end_date = '2010-09-01',
                                         y_axis_title = "Percent",
                                         y_axis_range = [4, 8]
                                        )
figures_list.append(fig1_4)
chart_titles.append(chart_title)


datalist = ["DPCCRV1Q225SBEA", "FEDFUNDS", "IORB"]
chart_title = """Core PCE, Federal Funds Rate, vs. Interest on Reserved Balances
                  , 2006-2010"""
fig1_5 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2006-01-01',
                                         end_date = '2010-09-01',
                                         y_axis_title = "Percent",
                                         split_y_axis = True,
                                         num_lines_split_axis = 2,
                                         split_y_axis_title = 'Percent',
                                         y_axis_range = [-1, 10],
                                         split_y_axis_range = [0, 6]
                                        )
figures_list.append(fig1_5)
chart_titles.append(chart_title)


datalist = ["NFCI"]
chart_title = "Chicago Fed National Financial Conditions Index, 2006-2010"
fig1_6 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2006-01-01',
                                         end_date = '2010-09-01',
                                         y_axis_title = "Index",
                                         y_axis_range = [-1, 3]
                                        )
figures_list.append(fig1_6)
chart_titles.append(chart_title)


datalist = ["DJIA", "SP500"]
chart_title = "DJIA & S&P500, 2006-2010"
fig1_7 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2006-01-01',
                                         end_date = '2010-09-01',
                                         y_axis_title = "Index",
                                         split_y_axis = True,
                                         num_lines_split_axis = 1,
                                         split_y_axis_title= "Index",
                                         y_axis_range = [0, 15000],
                                         split_y_axis_range = [1000, 2000]
                                        )
figures_list.append(fig1_7)
chart_titles.append(chart_title)

datalist = ["T10Y2Y"]
chart_title = """10-Year Treasury Constant Maturity Minus 2-Year Treasury 
                Constant Maturity, 2006-2010"""
fig1_8 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2006-01-01',
                                         end_date = '2010-09-01',
                                         y_axis_title = "Percent"
                                        )
figures_list.append(fig1_8)
chart_titles.append(chart_title)

datalist = ["UMCSENT"]
chart_title = "University of Michigan Consumer Sentiment, 2006-2010"
fig1_9 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2006-01-01',
                                         end_date = '2010-09-01',
                                         y_axis_title = "Index: 1996"
                                        )
figures_list.append(fig1_9)
chart_titles.append(chart_title)

datalist = ["VIXCLS"]
chart_title = "CBOE Volatility Index, 2006-2010"
fig1_10 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2006-01-01',
                                         end_date = '2010-09-01',
                                         y_axis_title = "Index"
                                        )
figures_list.append(fig1_10)
chart_titles.append(chart_title)

datalist = ['WLEMUINDXD']
chart_title = "Equity Market-related Economic Uncertainty Index, 2006-2010"
fig1_101 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2006-01-01',
                                         end_date = '2010-09-01',
                                         y_axis_title = "Index",
                                         y_axis_range = [0, 1500]
                                        )
figures_list.append(fig1_101)
chart_titles.append(chart_title)


########################
### 2018-2024 GRAPHS ###
########################

datalist = ["GDPC1", "GDPPOT"]
chart_title = "GDP vs. Potential GDP, 2018-2024"
fig1_11 = create_line_graph(datalist, chart_title = chart_title,
                                         legend_titles = ['Real GDP', 
                                                          'Real Potential GDP'],
                                         start_date = '2018-01-01',
                                         end_date = '2024-09-01',
                                         y_axis_title = "Billions of Dollars",
                                         y_axis_range = [18500, 24000]                                         
                                        )
figures_list.append(fig1_11)
chart_titles.append(chart_title)

datalist = ["MEDLISPRIUS", "MEDLISPRIPERSQUFEEUS"]
chart_title = "Home List Price vs. Home List Price per Square Foot, 2018-2024"
fig1_12 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2018-01-01',
                                         end_date = '2024-09-01',
                                         y_axis_title = "U.S. Dollars",
                                         split_y_axis_title = "U.S. Dollars",
                                         split_y_axis = True,
                                         num_lines_split_axis = 1
                                        )
figures_list.append(fig1_12)
chart_titles.append(chart_title)


datalist = ["MSPUS"]
chart_title = "Home Sale Price, 2018-2024"
fig1_13 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2018-01-01',
                                         end_date = '2024-09-01',
                                         y_axis_title = "U.S. Dollars",
                                         y_axis_range = [300000, 450000]
                                        )
figures_list.append(fig1_13)
chart_titles.append(chart_title)

datalist = ["MORTGAGE30US"]
chart_title = "30 Year Fixed Rate Mortage Average, 2018-2024"
fig1_14 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2018-01-01',
                                         end_date = '2024-09-01',
                                         y_axis_title = "Percent",
                                         y_axis_range = [1, 8]
                                        )
figures_list.append(fig1_14)
chart_titles.append(chart_title)


datalist = ["DPCCRV1Q225SBEA", "FEDFUNDS", "IORB"]
chart_title = """Core PCE, Federal Funds Rate, vs. Interest on Reserved 
                  Balances, 2018-2024"""
fig1_15 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2018-01-01',
                                         end_date = '2024-09-01',
                                         y_axis_title = "Percent",
                                         split_y_axis = True,
                                         num_lines_split_axis = 2,
                                         split_y_axis_title = 'Percent',
                                         y_axis_range = [-1, 10],
                                         split_y_axis_range = [0, 6]
                                        )
figures_list.append(fig1_15)
chart_titles.append(chart_title)


datalist = ["NFCI"]
chart_title = "Chicago Fed National Financial Conditions Index, 2018-2024"
fig1_16 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2018-01-01',
                                         end_date = '2024-09-01',
                                         y_axis_title = "Index",
                                         y_axis_range = [-1, 1]
                                        )
figures_list.append(fig1_16)
chart_titles.append(chart_title)


datalist = ["DJIA", "SP500"]
chart_title = "DJIA & S&P500, 2018-2024"
fig1_16 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2018-01-01',
                                         end_date = '2024-09-01',
                                         y_axis_title = "Index",
                                         split_y_axis = True,
                                         num_lines_split_axis = 1,
                                         split_y_axis_title= "Index",
                                         y_axis_range = [20000, 45000],
                                         split_y_axis_range = [2000, 6000]
                                        )
figures_list.append(fig1_16)
chart_titles.append(chart_title)

datalist = ["T10Y2Y"]
chart_title = """10-Year Treasury Constant Maturity Minus 2-Year Treasury 
                  Constant Maturity, 2018-2024"""
fig1_17 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2018-01-01',
                                         end_date = '2024-09-01',
                                         y_axis_title = "Percent"
                                        )
figures_list.append(fig1_17)
chart_titles.append(chart_title)

datalist = ["UMCSENT"]
chart_title = "University of Michigan Consumer Sentiment, 2018-2024"
fig1_18 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2018-01-01',
                                         end_date = '2024-09-01',
                                         y_axis_title = "Index: 1996"
                                        )
figures_list.append(fig1_18)
chart_titles.append(chart_title)

datalist = ["VIXCLS"]
chart_title = "CBOE Volatility Index, 2018-2024"
fig1_19 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2018-01-01',
                                         end_date = '2024-09-01',
                                         y_axis_title = "Index"
                                        )
figures_list.append(fig1_19)
chart_titles.append(chart_title)

datalist = ['WLEMUINDXD']
chart_title = "Equity Market-related Economic Uncertainty Index, 2018-2024"
fig1_21 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2018-01-01',
                                         end_date = '2024-09-01',
                                         y_axis_title = "Index",
                                         y_axis_range = [0, 1500]
                                        )
figures_list.append(fig1_21)
chart_titles.append(chart_title)

########################
### 2006-2024 GRAPHS ###
########################

datalist = ["GDPC1", "GDPPOT"]
chart_title = "GDP vs. Potential GDP, 2006-2024"
fig1_22 = create_line_graph(datalist, chart_title = chart_title,
                                         legend_titles = ['Real GDP', 
                                                          'Real Potential GDP'],
                                         start_date = '2006-01-01',
                                         end_date = '2024-09-01',
                                         fomc = False,
                                         y_axis_title = "Billions of Dollars",
                                         y_axis_range = [15000, 24000]                                         
                                        )
figures_list.append(fig1_22)
chart_titles.append(chart_title)

datalist = ["MEDLISPRIUS", "MEDLISPRIPERSQUFEEUS"]
chart_title = "Home List Price vs. Home List Price per Square Foot, 2006-2024"
fig1_23 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2006-01-01',
                                         end_date = '2024-09-01',
                                         fomc = False,
                                         y_axis_title = "U.S. Dollars",
                                         split_y_axis_title = "U.S. Dollars",
                                         split_y_axis = True,
                                         num_lines_split_axis = 1
                                        )
figures_list.append(fig1_23)
chart_titles.append(chart_title)


datalist = ["MSPUS"]
chart_title = "Home Sale Price, 2006-2024"
fig1_24 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2006-01-01',
                                         end_date = '2024-09-01',
                                         fomc = False,
                                         y_axis_title = "U.S. Dollars",
                                         y_axis_range = [200000, 450000]
                                        )
figures_list.append(fig1_24)
chart_titles.append(chart_title)

datalist = ["MORTGAGE30US"]
chart_title = "30 Year Fixed Rate Mortage Average, 2006-2024"
fig1_25 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2006-01-01',
                                         end_date = '2024-09-01',
                                         fomc = False,
                                         y_axis_title = "Percent",
                                         y_axis_range = [1, 8]
                                        )
figures_list.append(fig1_25)
chart_titles.append(chart_title)


datalist = ["DPCCRV1Q225SBEA", "FEDFUNDS", "IORB"]
chart_title = """Core PCE, Federal Funds Rate, vs. Interest on Reserved 
                  Balances, 2006-2024"""
fig1_26 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2006-01-01',
                                         end_date = '2024-09-01',
                                         fomc = False,
                                         y_axis_title = "Percent",
                                         split_y_axis = True,
                                         num_lines_split_axis = 2,
                                         split_y_axis_title = 'Percent',
                                         y_axis_range = [-1, 10],
                                         split_y_axis_range = [0, 6]
                                        )
figures_list.append(fig1_26)
chart_titles.append(chart_title)


datalist = ["NFCI"]
chart_title = "Chicago Fed National Financial Conditions Index, 2006-2024"
fig1_27 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2006-01-01',
                                         end_date = '2024-09-01',
                                         fomc = False,
                                         y_axis_title = "Index",
                                         y_axis_range = [-1, 3]
                                        )
figures_list.append(fig1_27)
chart_titles.append(chart_title)


datalist = ["DJIA", "SP500"]
chart_title = "DJIA & S&P500, 2006-2024"
fig1_28 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2006-01-01',
                                         end_date = '2024-09-01',
                                         fomc = False,
                                         y_axis_title = "Index",
                                         split_y_axis = True,
                                         num_lines_split_axis = 1,
                                         split_y_axis_title= "Index",
                                         y_axis_range = [0, 45000],
                                         split_y_axis_range = [1000, 6000]
                                        )
figures_list.append(fig1_28)
chart_titles.append(chart_title)

datalist = ["T10Y2Y"]
chart_title = """10-Year Treasury Constant Maturity Minus 2-Year Treasury 
                  Constant Maturity, 2006-2024"""
fig1_29 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2006-01-01',
                                         end_date = '2024-09-01',
                                         fomc = False,
                                         y_axis_title = "Percent"
                                        )
figures_list.append(fig1_29)
chart_titles.append(chart_title)

datalist = ["UMCSENT"]
chart_title = "University of Michigan Consumer Sentiment, 2006-2024"
fig1_18 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2006-01-01',
                                         end_date = '2024-09-01',
                                         fomc = False,
                                         y_axis_title = "Index: 1996"
                                        )
figures_list.append(fig1_29)
chart_titles.append(chart_title)

datalist = ["VIXCLS"]
chart_title = "CBOE Volatility Index, 2006-2024"
fig1_31 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2006-01-01',
                                         end_date = '2024-09-01',
                                         fomc = False,
                                         y_axis_title = "Index"
                                        )
figures_list.append(fig1_31)
chart_titles.append(chart_title)

datalist = ['WLEMUINDXD']
chart_title = "Equity Market-related Economic Uncertainty Index, 2006-2024"
fig1_32 = create_line_graph(datalist, chart_title = chart_title,
                                         start_date = '2006-01-01',
                                         end_date = '2024-09-01',
                                         fomc = False,
                                         y_axis_title = "Index",
                                         y_axis_range = [0, 1500]
                                        )
figures_list.append(fig1_32)
chart_titles.append(chart_title)


########################
### 2006+2024 GRAPHS ###
########################

# TODO: Add this lol

# TODO: Change output functions to save files to downloads folder.