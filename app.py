#!/usr/bin/env python
# coding: utf-8

# In[1]:


#get_ipython().system('pip install dash')


# ## Call Libraries 

# In[2]:


import pandas as pd
import numpy as np

# Dash packages
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go

from plotly.colors import DEFAULT_PLOTLY_COLORS   # chart default colors


# ## Call the Data 

# In[3]:


# Path of the data's location
path = '../data/'


# In[4]:


# Call the data
df = pd.read_csv(path + 'Revenue_data/Data.csv')


# ## Create and Arrange Data Variables 

# In[5]:


# Create Margin
df['Margin'] = df['Revenue'] - df['Cost']


# In[6]:


# Create variables for the year and month
df['year'] = df['OrderDate'].str.slice(start = 0, stop = 4)
df['month'] = df['OrderDate'].str.slice(start = 5, stop = 7)
# Arrange the data
df = df.sort_values(by = ['Region','Channel','Category','Item Type','year','month','Gender'])


# ## Year Filter

# In[7]:


years = list(df['year'].unique())
years.sort()


# ## App & Layout 

# In[8]:


# App structure
app = dash.Dash(__name__)
app.title = ("Dashboard | Revenue Data")
server = app.server

# App layout
app.layout = html.Div([
    
    # Main Title
    html.H2('Revenue Dashboard with Dash', style={'textAlign': 'center', 'marginBottom':10, 'marginTop':10}),
    
    # Dividing the sections - Left
    html.Div([
        
        ### Pie by Channel, Gender, AgeGroup
        html.Div(className='Pie',
                 children=[
                     html.Div(dcc.Graph(id='channel'), style={'float':'left', 'display':'inline-block', 'width':'33%'}),
                     html.Div(dcc.Graph(id='gender'), style={'float':'left', 'display':'inline-block', 'width':'33%'}),
                     html.Div(dcc.Graph(id='agegroup'), style={'float':'right', 'width':'33%'})
                 ]),
        
        ### Indicater by Region, Bar by Country
        html.Div(className='Indicator & Bar',
                 children=[
                     html.Div(dcc.Graph(id='idc_africa'), style={'float':'left', 'display':'inline-block', 'width':'12%'}),
                     html.Div(dcc.Graph(id='idc_america'), style={'float':'left', 'display':'inline-block', 'width':'12%'}),
                     html.Div(dcc.Graph(id='idc_asia'), style={'float':'left', 'display':'inline-block', 'width':'12%'}),
                     html.Div(dcc.Graph(id='idc_europe'), style={'float':'left', 'display':'inline-block', 'width':'12%'}),
                     html.Div(dcc.Graph(id='idc_oceania'), style={'float':'left', 'display':'inline-block', 'width':'12%'}),
                     html.Div(dcc.Graph(id='country'), style={'float':'right', 'width':'40%'})
                 ]),
                
        ### Line by YM, Radar by Category
        html.Div(className='Line',
                 children=[
                     html.Div(dcc.Graph(id='line'), style={'float':'left', 'display':'inline-block', 'width':'60%'}),
                     html.Div(dcc.Graph(id='radar'), style={'float':'right', 'width':'40%'})
                 ])  
        ], style={'float':'left', 'display':'inline-block', 'width':'65%'}),
    
    # Dividing the Sections - Right
    html.Div([
        html.Div(children=[
                    html.Div(dcc.Dropdown(id = 'id_year',
                                         options=[{'label':i, 'value':i} for i in years],
                                         value = max(years),
                                         style={'width':'50%'})),
                    html.Div(dcc.Graph(id='map')),
                    html.Div(dcc.Graph(id='sankey'))
            ])
    ], style={'float':'right', 'width':'35%'})
])


# ## Pie Chart 

# In[9]:


cols = DEFAULT_PLOTLY_COLORS

### Pie 
@app.callback([Output('channel',  'figure'), 
               Output('gender', 'figure'), 
               Output('agegroup',    'figure')], 
              [Input('id_year', 'value')])

def update_output(val):
        
    # loop values
    pies = ['Channel', 'Gender', 'AgeGroup']
    
    # data by channel, gender, agegroup
    figures = []
    
    for i in range(len(pies)):
        df_fig = df[df['year'] == val]
        df_fig = df_fig.loc[:,[pies[i],'Revenue']].groupby(by = [pies[i]], as_index = False).sum()
        
        # hover text
        df_fig['text'] = round(df_fig['Revenue']/1000000,1).astype(str) + 'M'
        
        
        trace = go.Pie(labels = df_fig[pies[i]],
                       values = df_fig['Revenue'],
                       name = '',
                       text = df_fig['text'],
                       textinfo = 'label+percent',
                       hovertemplate = "[%{label}]<br> Revenue: %{text}<br> Rate: %{percent}",
                       hoverinfo='text',
                       insidetextorientation = 'tangential',   # textinfo type (tangential / auto / horizontal / radial)
                       hole = 0.4, 
                       marker_colors = cols  # pie color
                       )
        data = [trace]
        
        layout = go.Layout(title=pies[i], title_x=0.5, title_xanchor='center', showlegend=False, 
                       height=250, margin=dict(l=50, r=50, b=10, t=50)
                      )
        
        figure = go.Figure(data, layout)
        figures.append(figure)

    return figures[0], figures[1], figures[2]


# ## Indicator 

# In[10]:


### by Region
@app.callback([Output('idc_africa',  'figure'), 
               Output('idc_america', 'figure'), 
               Output('idc_asia',    'figure'), 
               Output('idc_europe',  'figure'), 
               Output('idc_oceania', 'figure')], 
              [Input('id_year', 'value')])

def update_output(val):
        
    # reg - unique values
    reg = df['Region'].unique()
    
    # data by Region
    figures = []
    
    for i in range(len(reg)):
        df_fig = df[(df['year'] == val) & (df['Region'] == reg[i])]
        df_fig = round(df_fig.loc[:,['Revenue','Margin']].sum()/1000000,1) # Milion units
        
        values = df_fig['Revenue']
        deltas = df_fig['Margin']
        
        trace = go.Indicator(mode = 'number+delta',
                             value = values,
                             number = dict(font_size = 35,    # font size fixed (otherwise, the fonts will be different sizes by default)
                                          valueformat = ".1f",
                                          suffix='M'),
                             delta = dict(reference = values - deltas,
                                          font_size = 20,
                                          valueformat = ".1f",
                                          relative = False,
                                          increasing_color = '#3078b4', #increasing_symbol = '',
                                          decreasing_color = '#d13b40', #decreasing_symbol = '',
                                          position = 'top'),
                             title = dict(text = reg[i], font_size = 20)
                            )
        data = [trace]
        
        layout = go.Layout(height=310)
        figure = go.Figure(data, layout)
        figures.append(figure)

    return figures[0], figures[1], figures[2], figures[3], figures[4]


# ## Bar Chart 

# In[11]:


@app.callback(Output('country', 'figure'), [Input('id_year', 'value')])

def update_output(val):
    
    # Revenue by Country
    df_con = df[df['year'] == val]
    df_con = df_con.loc[:,['Country','Revenue']].groupby(by = ['Country'], as_index = False).sum()
    df_con = df_con.sort_values(by = ['Revenue'], ascending=False)
    
    
    # Rank & Top 10
    df_con['rank'] = list(range(1, len(df_con['Country'])+1))
    df_con = df_con[df_con['rank'] <= 10].reset_index(drop = True)
    
        
    # hover_text
    df_con['text'] = df_con['Country'] + ': ' +                      round(df_con['Revenue']/1000000,1).astype(str) + 'M'
    
    trace = go.Bar(x = df_con['Country'],
                   y = df_con['Revenue'],
                   text = df_con['text'],
                   texttemplate = '%{text}', 
                   hoverinfo = 'text'
                   )

    data = [trace]
    
    layout = go.Layout(title = 'Country (Top 10)',
                       # title_x=0,
                       title_y=0.8,
                       height=310
                      )
    
    figure = {'data': data, 'layout': layout}

    return figure


# ## Line Chart 

# In[12]:


### by YearMonth
@app.callback(Output('line', 'figure'), [Input('id_year', 'value')])

def update_output(val):
    
    traces = []
    for yr in years:
        
        df_line = df[df['year'] == yr]
        df_line = df_line.loc[:,['Revenue','year','month']].groupby(by = ['year','month'], as_index = False).sum()
        
        # hover_text
        df_line['text'] = round(df_line['Revenue']/1000000,1).astype(str) + 'M'
        
        traces.append(go.Scatter(x = df_line['month'],
                                 y = df_line['Revenue'],
                                 text = df_line['text'],
                                 hovertemplate = '%{text}',
                                 mode = 'lines+markers',
                                 marker = dict(size = 10),
                                 name = yr))
    data = traces
    
    layout = go.Layout(title = 'Revenue Trend (Monthly)',
                       # tick0 = Set the placement of the first tick mark (use with dtick), dtick = spacing between tick marks
                       xaxis = dict(title='Month', tickmode='linear', tick0=1, dtick=1, showgrid=False),
                       legend = dict(orientation="h",    # option= 'v', 'h'
                                     xanchor="center",   # option= 'auto', 'left', 'center', 'right'
                                     x=0.5,              # x= 0(left), 1 (right)
                                     yanchor="bottom",   # option= 'auto', 'top', 'middle', 'bottom' 
                                     y=-1  #1.1,         # y= 1(top), -1(bottom)
                                    ),
                       height=320, margin=dict(l=50, r=10))
    
    figure = {'data': data, 'layout': layout}

    return figure


# ## Radar Chart

# In[13]:


### by year & category
@app.callback(Output('radar', 'figure'), [Input('id_year', 'value')])

def update_output(val):
    
    df_rad = df.loc[:,['Category','Revenue','year']].groupby(by = ['year','Category'], as_index=False).sum()
    
    # Revenue range categories
    df_rad['Range'] = 0
    df_rad.loc[df_rad['Revenue']<10000000, 'Range'] = 1
    df_rad.loc[(df_rad['Revenue']>=10000000) & (df_rad['Revenue']<30000000), 'Range'] = 2
    df_rad.loc[(df_rad['Revenue']>=30000000) & (df_rad['Revenue']<50000000), 'Range'] = 3
    df_rad.loc[(df_rad['Revenue']>=50000000) & (df_rad['Revenue']<70000000), 'Range'] = 4
    df_rad.loc[(df_rad['Revenue']>=70000000), 'Range'] = 5
    
    # Range labels
    rad_rg=pd.DataFrame([[0, '0'], [1, '< 10M'], [2, '10-30M'], [3, '30-50M'], [4, '50-70M'], [5, '70M <']])
    rad_rg.columns = ['Range', 'Ranges']
    
    # Join
    df_radar = df_rad.merge(rad_rg, on = 'Range', how = 'left')
    
    # Graph
    traces = []
    for yr in years:
        dat = df_radar[df_radar['year'] == yr]   # Extract specific year
        ranges = list(dat['Range'])                # Revenue range Categories
        ranges.append(ranges[0])                   # Append to list
        thetas = list(dat['Category'])           # Item list
        thetas.append(thetas[0])                 # Append to list
        range_R = list(dat['Ranges'])              # Cateogeory info by ranges
        range_R.append(range_R[0])                 # Append to list

        traces.append(go.Scatterpolar(r = ranges,
                                      theta = thetas,
                                      name = yr, 
                                      text = range_R,
                                      hovertemplate = "Revenue:%{text}"))
    
    data = traces
    layout = go.Layout(legend = dict(orientation="h",    # option= 'v', 'h'
                                     xanchor="center",   # option= 'auto', 'left', 'center', 'right'
                                     x=0.5,              # x= 0(left), 1 (right)
                                     yanchor="bottom",   # option= 'auto', 'top', 'middle', 'bottom' 
                                     y=-1                # y= 1(top), -1(bottom)
                                    ),
                       height = 320)    
   
    figure = {'data': data, 'layout': layout}

    return figure


# ## Map Graph 

# In[14]:


### Choropleth Map
@app.callback(Output('map', 'figure'), [Input('id_year', 'value')])

def update_output(val):
    
    # Code3 by Country
    df_code = df.loc[:,['Country','Code3']].drop_duplicates()

    # data
    df_map = df[df['year'] == val]
    df_map = df_map.loc[:,['Country','Revenue']].groupby(by = ['Country'], as_index = False).sum()
    
    # Join map & Code3
    df_m = df_map.merge(df_code, on = 'Country', how = 'left')
    
    # hover_text
    df_m['text'] = df_m['Country'] + ' - Total Revenue : ' +                    round(df_m['Revenue']/1000000,1).astype(str) + 'M'
    
    trace = go.Choropleth(
                    locations = df_m['Code3'],
                    z = df_m['Revenue'],
                    text = df_m['text'],
                    hoverinfo = 'text',          # Activate only the inputted text
                    colorscale = 'Blues',        # color= Greens, Reds, Oranges, ...
                    autocolorscale=False,
                    reversescale=False,
                    marker_line_color='darkgray',
                    marker_line_width=0.5,
                    
                    # colorbar option = legend bar
                    colorbar_title = 'Revenue ($)',
                    colorbar_thickness=15,      # bar width (default=30)
                    colorbar_len=1,             # bar length (default=1)
                    colorbar_x=1.01,            # bar x location (default=1.01, between -2~3)
                    colorbar_ticklen=10         # bar tickline length (default=5)
                                )
    
    data = [trace]
    layout = go.Layout(title = 'Revenue Map',
                       geo = dict(showframe=False,
                                  showcoastlines=False,
                                  projection_type = 'equirectangular'),
                       height=420, margin=dict(l=50, r=50, b=20, t=50))
    
    figure = {'data': data, 'layout': layout}

    return figure


# ## Sankey Graph 

# In[15]:


### Sankey
@app.callback(Output('sankey', 'figure'), [Input('id_year', 'value')])

def update_output(val):
    
    # Arrange in ascending order of revenue for the continent, channel, item in 2020
    df_san = df[df['year'] == val].iloc[:,[13,4,11,9]]
    df_san = df_san.sort_values(by = ['Region','Channel','Category'])
    
    # label
    l_reg = list(df_san['Region'].unique()) # 5 values (order = 0 1 2 3 4)
    l_cha = list(df_san['Channel'].unique()) # 2 values (order = 5 6)
    l_cat = list(df_san['Category'].unique()) # 5 values (order = 7 8 9 10 11)
    labels = l_reg + l_cha + l_cat # 12 values (order = 0 ~ 11)
    
    # source
    source1 = list(np.repeat(range(0, len(l_reg)), len(l_cha)))
    source2 = list(np.repeat(range(len(l_cat), len(l_cat)+len(l_cha)), len(l_cat)))
    sources = source1 + source2
    
    # target
    target1 = list(range(len(l_cat), len(l_cat) + len(l_cha))) * len(l_cat)
    target2 = list(range(len(l_cha) + len(l_cat), len(l_reg) + len(l_cha) + len(l_cat))) * len(l_cha)
    targets = target1 + target2
    
    # value
    value1 = df_san.groupby(by = ['Region','Channel'], as_index = False).sum()
    value2 = df_san.groupby(by = ['Channel','Category'], as_index = False).sum()
    values = list(value1['Revenue']) + list(value2['Revenue'])
    
    trace = go.Sankey(node = dict(label = labels,
                              pad = 15,
                              thickness = 20,
                              line = dict(color = 'black', width = 0.5),
                              color = '#3078b4'),
                  link = dict(source = sources,
                              target = targets,
                              value = values,
                              color = '#EAEAEA'))
    
    data = [trace]
    layout = go.Layout(title = dict(text='Revenue Flow', font_size=16),
                       font_size = 15,
                       height=420, margin=dict(l=50, r=50, b=20, t=50))
    
    figure = {'data': data, 'layout': layout}

    return figure


# In[16]:


# Run App
if __name__=='__main__':
    app.run_server(debug=False)


# In[ ]:




