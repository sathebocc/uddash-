#!/usr/bin/env python
# coding: utf-8

# In[1]:


import dash
import json
from dash import dcc
from dash import html 
from dash import dash_table

import plotly.graph_objects as go
import pandas as pd
import numpy as np
# import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, ALL, State, MATCH, ALLSMALLER
import plotly.express as px
import dash_daq as daq

pd.set_option('display.max_rows', 500)

df = pd.read_csv("bills_bkly.csv", parse_dates =["bill_start_date"], low_memory=False)
sqft_df = pd.read_csv("sqft.csv")
df.columns.to_list()
df1 = df.iloc[:,:19]
df1["month_year"] = df["bill_start_date"].dt.strftime("%y %b")
df1["year"] = df["bill_start_date"].dt.year
df1["month"] = df["bill_start_date"].dt.month
df1["month_year"] = pd.to_datetime(df1[['year', 'month']].assign(Day=1)).dt.strftime('%b %y')

df_use = df1.groupby(["year","month","utility_meter_number","location","type","bill_total_unit"])["bill_total","bill_volume"].sum().sort_values(by=["utility_meter_number","year","month"],ascending = False).reset_index()
df_use["month_year"] = pd.to_datetime(df_use[['year', 'month']].assign(Day=1)).dt.strftime('%b %y')
df_use["sqft"] = df_use["location"].map(sqft_df.set_index("location")["sqft"])
df_use["sqft"] = [float(str(i).replace(",", "")) for i in df_use["sqft"]]                                                                                      
 
df_use['electric_kbtu'] = df_use[df_use["bill_total_unit"] == "kwh"]["bill_volume"]*3.412
df_use['electric_kbtu'] = df_use['electric_kbtu'].replace(np.nan, 0)

df_use['gas_kbtu'] = df_use[df_use["bill_total_unit"] == "therms"]["bill_volume"]*100
df_use['gas_kbtu'] = df_use['gas_kbtu'].replace(np.nan, 0)

df_use['total_kbtu'] = df_use['electric_kbtu'] + df_use['gas_kbtu']
df_use['date']=df_use['year'].astype(str) + df_use['month'].astype(str).str.zfill(2)
df_use['date'] = pd.to_datetime(df_use['date'], format='%Y%m')


# In[2]:


df1_therms  = df1[df1["bill_total_unit"] == "therms"]
therms_df=df1_therms.groupby(['year','month'])["bill_volume","bill_total"].sum().reset_index().sort_values(by = ['year','month'],ascending = False)
therms_df["month_year"] = pd.to_datetime(therms_df[['year', 'month']].assign(Day=1)).dt.strftime('%b %y')


# In[3]:


lat_long = {"lat" :[37.89463424682617,37.861439,37.8577799,37.85232162475586,37.8588012,37.8924229,37.86616516113281,37.8682847,
                   37.8824185,37.8592703,37.8593864440918,37.876548767089844,37.85436248779297
                   
                   ],
            "long":[-122.26585388183594,-122.251019,-122.2457449,-122.27220916748047,-122.2619369,-122.2810054,-122.27240753173828,-122.270756,
                   -122.2777089,-122.2758049,-122.26033020019531,-122.26927947998047,-122.27103424072266
                   
                   ]}
df2 =pd.DataFrame(lat_long)
sqft_df =pd.concat([sqft_df,df2], axis =1)
sqft_df.dropna(how="all",axis=1,inplace=True)
# sqft_df.reset_index(inplace=True)
sqft_df
df_use.dtypes


df_use1 = df_use.copy()



uiui = df_use[df_use["month_year"] == "Jun 21"]
start_date_np = uiui["date"].unique()[0]

start_date_pd = pd.to_datetime(start_date_np, format='%Y%m')   
end_date_pd = pd.to_datetime(start_date_np, format='%Y%m') - pd.offsets.DateOffset(months=12)    
end_date_np = end_date_pd.to_numpy()

sliced_df = df_use[(df_use['date'] <= start_date_np) & (df_use['date'] > end_date_np )]

type(end_date_np)
sliced_df  = sliced_df.groupby("type")["total_kbtu"].sum()
sliced_df = pd.DataFrame(sliced_df)
sliced_df.reset_index(inplace = True)
sliced_df


# In[ ]:





# In[4]:


sqft_df["sqft"] = pd.to_numeric(sqft_df["sqft"].str.replace(",", ""), errors='coerce')
sqft_df["sqft"].astype(float)
sqft_only = sqft_df[["location","sqft"]]
names = sqft_df["type"].unique()
values =sqft_df.groupby('type')["sqft"].sum()

dicton = {"typename" : names , "typesqft" : values}
df_dict = pd.DataFrame(dicton).reset_index()
sqft_df


# In[5]:





fig_pie = px.pie(sqft_df, values=values, names=names, hole =.5,
                
                
                )
fig_pie.update_traces(textinfo='label+percent',
                hovertemplate = "School type : %{label} <br>Square foot : %{value}"
)

fig_pie.update_layout(
    {"showlegend":False,
        "margin":{"l":0,"r":0,"t":0,"b":0}},
     annotations=[dict(text='Sqft', x=0.5, y=0.5, font_size=12, showarrow=False)]
 
        )



# donut_top = go.Figure()
# # donut_top.layout.template = CHART_THEME
# donut_top.add_trace(go.Pie(labels=sqft_df, values=values))
# donut_top.update_traces(hole=.4, hoverinfo="label+value+percent")
# donut_top.update_traces(textposition='outside', textinfo='label+value')
# donut_top.update_layout(showlegend=False)
# # donut_top.update_layout(margin = dict(t=50, b=50, l=25, r=25))
# donut_top.show()




# dicton
new = pd.concat([df_dict,sliced_df], axis =1)
# new.drop(columns=["type"], inplace = True)
# new["EUI"] = new["total_kbtu"] / new["typesqft"]
# new
# new = df_dict.join(sliced_df, how ="outer")
new
sqft_df
# color dictonary #

type_color = { 
 "Elementary School" : "Blue",
    "High School" : "Green",
    "Middle School" : "Brown",
    "Other" : "Indigo",
  
}

sqft_df["color"] = sqft_df["type"].map(type_color)
sqft_df


# In[6]:


df_use_eui_location = df_use.groupby(["location","type"])["total_kbtu"].sum().reset_index().sort_values(by = "type" , ascending = True)
df_use_eui_location = pd.merge(df_use_eui_location, 
                      sqft_only, 
                      on ='location', 
                      how ='inner')

df_use_eui_location["EUI"] = df_use_eui_location["total_kbtu"] / df_use_eui_location ["sqft"]
df_use_eui_location


### National EUI dataframe #### 
national_eui_dic = {'type': ["High School","Elementary School","Middle School","Other" ], 
     'National_EUI': [48.5,48.5,48.5,55.10 ]}

national_eui_df = pd.DataFrame(national_eui_dic)
national_eui_df


# In[7]:


app= dash.Dash()
server = app.server

app.layout = html.Div([    
                        
                            html.Div([
                            html.Div([
        html.Div([ 
        html.Img(src = app.get_asset_url('district_logo.png'), style ={"display":"inline-block"}),
        html.P("Sample School District")], 
        style ={"display":"flex","height":"auto","max-width":"100%"}), 
                                
        html.P("Utilities Dashboard"),
                                
        html.Img(src = app.get_asset_url('logo.png'))
                                                                                  
                                                       
                        ],className="inside-c1")
                        ], className ="container1"),
    
                      
                    
        html.Div([                  
        html.Div(
        dcc.Graph(id = "pie-chart", figure = fig_pie , config={'displayModeBar': False}
                  , style ={"width":"300px","height":"100px", "padding":"5px 5px"}
                 )
            , style = {"display":"inline-block","max-width":"100%"})
            
        ],className="container2 shadow-sm p-3 mb-5 bg-white rounded"),
    
                        
                    
        html.Div([                  
        html.Div(
        dcc.Graph(id = "indicator", figure = {},config={'displayModeBar': False},
                  style ={"width":"300px","height":"600px"})
            , style = {"display":"inline-block","max-width":"100%"})
            
        ],className="container3"),
    

 
    
            html.Div(dcc.Graph(id = "graph1", figure = {}, config={'displayModeBar': False},
                                            style = {"display":"inline-block","max-width":"100%"}),                                
                                 className="container6"),
    
            html.Div(dcc.Graph(id="map",figure={}, config={'displayModeBar': False, 'scrollZoom': True},
                               style ={"display":"inline-block","max-width":"100%"}),
                                                             
                                 className="container7"),
    
                            
                       html.Div([
                               html.Div([
                              dcc.RadioItems(options = ["kwh","therms"], value ="kwh", id="rb",className = "box1"),
                                        
                              dcc.Dropdown(options = df_use["month_year"].unique(), value =df_use["month_year"].unique()[0],
    id= "dd",className = "box2"), 
                                   
                                   daq.BooleanSwitch(id ="switch",
                                                      on=True,
                                                      label="Location - - - - - District",color = 'rgb(230, 230, 230)',
                                                      labelPosition="top", className ="box4"
),
                         
              dcc.Dropdown(options = df_use["location"].unique(), placeholder = "Select a Location",
                           
             id= "dd_loc",className ="box3") ],className="wrapper"),
                                                
            dcc.Graph(id="graph",figure= {},config={'displayModeBar': False},
                      className = "box4")]
                     
                                ,className="container8"),
  
    html.Div( html.Div(id="data-table", style ={"display":"inline-block","max-width":"100%", "padding" : "10px"})
             
             
             ,className="container9"),
    dcc.Store(id='memory-output'),
    dcc.Store(id='memory-output1'),
    dcc.Store(id='memory-output2')

],className="main-container")


# In[8]:



@app.callback(
        Output('dd_loc','clearable'),
        Output('dd_loc','disabled'),
        Output('dd_loc','value'),
        Input('switch','on')
)

def initial_start(switch):
    
    if switch == True:
        disabled = True
        clearable = True
        value = ""
               
    else: 
        disabled = False
        clearable = False
        value = ""
       
        
        
    return clearable, disabled , value


@app.callback(
    [Output('memory-output','data'),
     Output("memory-output1",'value'),
     Output("memory-output2",'value')
        ],
     [Input('map','clickData'),
     Input('dd_loc','value'),
        Input('switch','on')]
   
)
def select_location(map_loc,dd_loc,switch):
    
    if switch == True:
                     
            location = "District wide"
            return df_use.to_dict('records'), str(location), df_use1.to_dict('records')
      
    else:
        
            ctx = dash.callback_context
            component_triggered = ctx.triggered[0]["prop_id"].split(".")[0]

            if component_triggered == 'dd_loc':
                   
                    location = dd_loc            
                    dff = df_use[df_use["location"] == location]              
                    return dff.to_dict('records'), str(location),df_use1.to_dict('records')

            else:
                    
                    location = map_loc["points"][0]["customdata"][0]        
                    dff = df_use[df_use["location"] == location] 
                    return dff.to_dict('records'), str(location),df_use1.to_dict('records')
    


# In[ ]:


# @app.callback(
#      Output('memory-output','value'),
#      Input('map','clickData'),
#      Input('dd_loc','value'),
     
# )
# def select_location(map_loc, dd_loc):
#     ctx = dash.callback_context
#     component_triggered = ctx.triggered[0]["prop_id"].split(".")[0]
    
#     if component_triggered == 'dd_loc':
#         location = dd_loc
#     else:
#         location = map_loc["points"][0]["customdata"][0]

#     return location


# In[ ]:


@app.callback(
    [Output('graph', 'figure'),
     Output('map','figure'),
     Output('graph1','figure'),
     Output('indicator','figure'),
     Output('data-table','children')
   ],
    [Input('rb','value'),
     Input('dd','value'),
     Input('memory-output','data'),
     Input('memory-output1','value'),
     Input("memory-output2",'value'),
    
]
       
)
def update_graph(radio, dropdown, data, location, data_eui):
    
    dff1 = pd.DataFrame.from_records(data)    
    dff1['date'] = pd.to_datetime(dff1['month_year'], format='%b %y') 
    
    #### copy for Indicator calcs and graphs - before dropdown selector ####
    dff_indicator = dff1.copy()
    dff_indicator1 = dff1.copy()
#     print(dff_indicator)
    
    dff1 = dff1[(dff1["bill_total_unit"] == radio)]   

    dff1 = dff1.groupby(["date","month_year"])["bill_total","bill_volume"].sum().reset_index().sort_values(by=["date"], ascending = True)
    index_1st = dff1.index[dff1["month_year"] == dropdown].values.astype(int)[0]
    idx_1st  = index_1st + 1
    idx_last = idx_1st - 12
    idx_previousyear = idx_last -12
    
    dff1_current = dff1.iloc[idx_last:idx_1st]
    dff1_previous = dff1.iloc[idx_previousyear:idx_last]
    
   

    total_sum_current = dff1_current["bill_volume"].sum()
    total_sum_previous = dff1_previous["bill_volume"].sum()
    
  #### Electric Indicator calcs ####
    
    dff_indicator = dff_indicator[dff_indicator["bill_total_unit"] == "kwh"]
    dff_indicator = dff_indicator.groupby(["date","month_year"])["bill_total","bill_volume"].sum().reset_index().sort_values(by=["date"], ascending = True)
    index_1st_indi = dff_indicator.index[dff_indicator["month_year"] == dropdown].values.astype(int)[0]
    idx_1st_indi  = index_1st_indi + 1
    idx_last_indi = idx_1st_indi - 12
    idx_previousyear_indi = idx_last_indi -12
    
    dff_indicator_current = dff_indicator.iloc[idx_last_indi:idx_1st_indi]
    dff_indicator_previous = dff_indicator.iloc[idx_previousyear_indi:idx_last_indi]
    
    
    total_sum_current_elec_use = dff_indicator_current["bill_volume"].sum()
    total_sum_previous_elec_use = dff_indicator_previous["bill_volume"].sum()
    
    total_sum_current_elec_cost = dff_indicator_current["bill_total"].sum()
    total_sum_previous_elec_cost = dff_indicator_previous["bill_total"].sum()
    
    #### Gas indicator calcs ####
    
    dff_indicator_gas = dff_indicator1[dff_indicator1["bill_total_unit"] == "therms"]
    dff_indicator_gas = dff_indicator_gas.groupby(["date","month_year"])["bill_total","bill_volume"].sum().reset_index().sort_values(by=["date"], ascending = True)
    index_1st_indi_gas = dff_indicator_gas.index[dff_indicator_gas["month_year"] == dropdown].values.astype(int)[0]
    idx_1st_indi_gas  = index_1st_indi_gas + 1
    idx_last_indi_gas = idx_1st_indi_gas - 12
    idx_previousyear_indi_gas = idx_last_indi_gas -12
    
    dff_indicator_gas_current = dff_indicator_gas.iloc[idx_last_indi_gas:idx_1st_indi_gas]
    dff_indicator_gas_previous = dff_indicator_gas.iloc[idx_previousyear_indi_gas:idx_last_indi_gas]
    
    
    total_sum_current_gas_use = dff_indicator_gas_current["bill_volume"].sum()
    total_sum_previous_gas_use = dff_indicator_gas_previous["bill_volume"].sum()
    
    total_sum_current_gas_cost = dff_indicator_gas_current["bill_total"].sum()
    total_sum_previous_gas_cost = dff_indicator_gas_previous["bill_total"].sum()
    
    ### Emissions Indicator Calcs ###
    
    total_sum_current_emissions = (total_sum_current_elec_use * 0.0005) + (total_sum_current_gas_use * 0.006)
    total_sum_previous_emissions = (total_sum_previous_elec_use * 0.0005) + (total_sum_previous_gas_use * 0.006)
    
    ### Indicator Figure construction  ###
    
    indicators_ptf = go.Figure()
    
    
    indicators_ptf.add_trace(go.Indicator(
    mode = "number+delta",
    value = int(total_sum_current_elec_use),
    number = {'valueformat': '.2s'},
    title = {"text": "<br><span style='font-size:0.7em;color:gray'>kWh Usage</span>"},
    delta = {'position': "bottom", 'reference': int(total_sum_previous_elec_use), 'relative': False},
    domain = {'row': 0, 'column': 0}))
    
    indicators_ptf.add_trace(go.Indicator(
    mode = "number+delta",
    value = int(total_sum_current_elec_cost),
    number = {'valueformat': '.2s'},
    title = {"text": "<br><span style='font-size:0.7em;color:gray'>kWh Cost</span>"},
    delta = {'position': "bottom", 'reference': int(total_sum_previous_elec_cost), 'relative': False},
    domain = {'row': 1, 'column': 0}))
    
    indicators_ptf.add_trace(go.Indicator(
    mode = "number+delta",
    value = int(total_sum_current_gas_use),
    number = {'valueformat': '.2s'},
    title = {"text": "<br><span style='font-size:0.7em;color:gray'>Therms Usage</span>"},
    delta = {'position': "bottom", 'reference': int(total_sum_previous_gas_use), 'relative': False},
    domain = {'row': 2, 'column': 0}))
    
    indicators_ptf.add_trace(go.Indicator(
    mode = "number+delta",
    value = int(total_sum_current_gas_cost),
    number = {'valueformat': '.2s'},
    title = {"text": "<br><span style='font-size:0.7em;color:gray'>Therms Cost</span>"},
    delta = {'position': "bottom", 'reference': int(total_sum_previous_gas_cost), 'relative': False},
    domain = {'row': 3, 'column': 0}))
   
  
    indicators_ptf.add_trace(go.Indicator(
    mode = "number+delta",
    value = total_sum_current_emissions,
    number = {'valueformat': '.2s'},
    title = {"text": "<br><span style='font-size:0.7em;color:gray'>Emissions CO2</span>"},
    delta = {'position': "bottom", 'reference': total_sum_previous_emissions, 'relative': False},
    domain = {'row': 4, 'column': 0}))
 
    indicators_ptf.update_layout(
    grid = {'rows': 5, 'columns': 1, 'pattern': "independent"},
#     margin=dict(l=0, r=0, t=0, b=0, pad =5),
    
    )

   #### EUI calcs ####
    
    dff2 = pd.DataFrame.from_records(data_eui)  
    
    uiui = df_use[df_use["month_year"] == dropdown]
    start_date_np = uiui["date"].unique()[0]

    start_date_pd = pd.to_datetime(start_date_np, format='%Y%m')   
    end_date_pd = pd.to_datetime(start_date_np, format='%Y%m') - pd.offsets.DateOffset(months=12)    
    end_date_np = end_date_pd.to_numpy()
    
    end_date_pd_2yrs = pd.to_datetime(end_date_np, format='%Y%m') - pd.offsets.DateOffset(months=12)
    end_date_np_2yrs = end_date_pd_2yrs.to_numpy()

    sliced_df = df_use[(df_use['date'] <= start_date_np) & (df_use['date'] > end_date_np )]
    sliced_df_datatable_first_year = sliced_df.copy()
    
    sliced_df_datatable_previous_year = df_use[(df_use['date'] <= end_date_np) & (df_use['date'] > end_date_np_2yrs )]
    
    
    sliced_df  = sliced_df.groupby("type")["total_kbtu"].sum()
    sliced_df = pd.DataFrame(sliced_df)
    sliced_df.reset_index(inplace = True)
   

    new = pd.concat([df_dict,sliced_df], axis = 1)
    new.drop(columns=["type"], inplace = True)
    new["EUI"] = new["total_kbtu"] / new["typesqft"]
#     print(new)
    
    fig_eui = go.Figure()
   
    trace1_eui = go.Bar(
        x=new['typename'], # NOC stands for National Olympic Committee
        y=new["EUI"],
        name = 'EUI',
        marker=dict(color='#FFD700') # set the marker color to gold
        )
    
    
    trace2_eui = go.Scatter(
        x=national_eui_df['type'], # NOC stands for National Olympic Committee
        y=national_eui_df["National_EUI"],
        name = 'National_EUI',
        mode = "lines+markers",
        # set the marker color to gold
        )
    
    
    data1 = [trace1_eui,trace2_eui]
    layout1 = go.Layout(
     {
        "margin":{"l":5,"r":5,"t":5,"b":5, "pad" :10}},
        legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1,
    title = "Energy Use Index"
        ),
        plot_bgcolor  = '#FFFFFF'
        )
  
    fig_eui = go.Figure(data=data1, layout=layout1)
    

    fig = go.Figure()
    trace1 = go.Bar(
        x=dff1_current['month_year'], # NOC stands for National Olympic Committee
        y=dff1_current["bill_volume"],
        name = 'Current consumption',
        marker=dict(color='#FFD700') # set the marker color to gold
        )
 
    trace2 = go.Bar(
        x=dff1_current['month_year'], # NOC stands for National Olympic Committee
        y=dff1_previous["bill_volume"],
        name = 'Previous consumption',
        marker=dict(color='#9EA0A1') # set the marker color to gold
        )
    data = [trace1, trace2]
    layout = go.Layout(
     {
        "margin":{"l":5,"r":5,"t":5,"b":5,"pad":10}},
        legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1,
    title = location),
    plot_bgcolor  = '#FFFFFF'
      

        )
   
    fig = go.Figure(data=data, layout=layout)
    
    ##### Map ####
    
    if location == "District wide":
        lon = sqft_df["long"]
        lat = sqft_df["lat"]
        center = {"lat": 37.854362, "lon" : -122.271034}
        zoom = 11
        color = sqft_df["color"]
        customdata = sqft_df[["location","sqft","type"]]
    else:
        lon = sqft_df[sqft_df['location'] == location]['long']
        lat = sqft_df[sqft_df['location'] == location]['lat']
        zoom = 12
        center = {"lat": float(lat), "lon" : float(lon)}
        color = sqft_df[sqft_df['location'] == location]['color']
        customdata = sqft_df[sqft_df['location'] == location][["location","sqft","type"]]
    
    mapbox_access_token ='pk.eyJ1Ijoic2F0aGVib2NjIiwiYSI6ImNsM202bnljZzAwazczYm9lMHd3bHZtZm0ifQ.HRaTxGQxuDBQyyKRpYPZuA'
    
    m_fig = go.Figure()
    
    data_map=[go.Scattermapbox(
                        lon = lon,
                        lat = lat,
                        mode='markers',
                        marker={'color' : color, 'size' :12, 'opacity' : 0.8},
                        unselected={'marker' : {'opacity':0.5, 'size':12}},
                        selected={'marker' : {'opacity':0.7, 'size':12}},
                        hoverinfo= ['text'],
                        customdata = customdata,
#                         customdata = sqft_df[["location","sqft","type"]],

        hovertemplate = 'Location : %{customdata[0]}<br>sqft : %{customdata[1]}<br>Facility type : %{customdata[2]}<extra></extra>',
              )
        ]

   
    layout_map = go.Layout(
                uirevision= 'foo', #preserves state of figure/map after callback activated
                clickmode= 'event+select',
                hovermode='closest',
                hoverdistance=2,
                mapbox=dict(
                accesstoken=mapbox_access_token,
                style='light',
                bearing = 25,
#                 center = {"lat": 37.854362, "lon" : -122.271034},
                center = center,
                zoom= zoom
                ),
                margin = dict(l=5,r=5,t=5,b=5,pad =0)
    )
                
    m_fig = go.Figure(data=data_map, layout=layout_map)
#     m_fig.update_layout(autosize = True)
    
    
    #### Data table calcs for EUI ####
    
    df_use_eui_current = sliced_df_datatable_first_year.groupby(["location","type"])["total_kbtu"].sum().reset_index().sort_values(by = "type" , ascending = True)
    df_use_eui_current = pd.merge(df_use_eui_current, 
                      sqft_only, 
                      on ='location', 
                      how ='inner')

    df_use_eui_current["Current EUI"] = df_use_eui_current["total_kbtu"] / df_use_eui_current ["sqft"]
    df_use_eui_current
    
    
    df_use_eui_previous = sliced_df_datatable_previous_year.groupby(["location","type"])["total_kbtu"].sum().reset_index().sort_values(by = "type" , ascending = True)
    df_use_eui_previous = pd.merge(df_use_eui_previous, 
                      sqft_only, 
                      on ='location', 
                      how ='inner')

    df_use_eui_previous["Previous EUI"] = df_use_eui_previous["total_kbtu"] / df_use_eui_previous ["sqft"]
    df_use_eui_previous.rename({'total_kbtu': 'total_kbtu_previous'}, axis=1, inplace=True)
    
    display_df = pd.merge(df_use_eui_previous, 
                      df_use_eui_current, 
                      on ='location', 
                      how ='inner')
    
    display_df = display_df[["location","type_x","sqft_x","Previous EUI","Current EUI"]]
    display_df.rename(columns = {'location':'Site Name', 
                                 'type_x':'Type',
                                 'sqft_x':'Sqft'
                                
                                
                                }, inplace = True)

    
#     print(df_use_eui_current)
    
    if location == "District wide":
            display_df1 =display_df
    else:
            display_df1 = display_df[display_df["Site Name"] == location]
    
    my_table = dash_table.DataTable(
        
        columns=[{"name": i, "id": i} for i in display_df1.columns],
        data =display_df1.to_dict('records'),
        
        style_cell={'textAlign': 'left'},
        
        page_action='none',
        style_table={'height': '320px', 'overflowY': 'auto'},
        export_format = 'csv'
    )
    
    print(location)
            
    return fig, m_fig , fig_eui, indicators_ptf, my_table


@app.callback (
    Output('details','children'),
    Input('map','clickData')
)
def new_try(cData):
        if cData is None:
            raise PreventUpdate
        else:
            name = cData["points"][0]["customdata"][0]
            print(cData,name)
        return name, print(name)  


# In[ ]:





# In[ ]:


if __name__ == "__main__":
    app.run_server()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




