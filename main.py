from sqlite3 import Date
from dash import dash, dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
#import dash_table as dt
from datetime import date
import datetime
import plotly.express as px


app = dash.Dash()


today = date.today().strftime('%d-%m-%Y')

df = pd.read_csv('catastro.csv', sep=';', encoding='UTF-8', on_bad_lines='skip')
#df['TERMINO'] = pd.to_datetime(df['TERMINO'], dayfirst=True)    
df['FINALIZA'] = df['TERMINO']
df['FECHA RECEPCION'] = pd.to_datetime(df['FECHA RECEPCION'], dayfirst=True)    

dfl = df
df = df[['NOMBRE','Cargo','Area','TIPO','DIAS','INICIO','FINALIZA','GlosaLocalidad','GLugar_Pago','Area_Pertenencia','TERMINO']]
dfcl = df[['Cargo','TERMINO','GlosaLocalidad','Area']][['Cargo','TERMINO','GlosaLocalidad','Area']].value_counts().reset_index()
dfc = pd.DataFrame(data=dfcl)
dfc.rename(columns={'GlosaLocalidad':'Localidad',0:'Total'},inplace=True)


#fecha = dfl[(dfl['FECHA RECEPCION'] >= '01-01-2022') &(dfl['FECHA RECEPCION'] <= select_date) & (dfl['GlosaLocalidad'] == 'HOSPITAL VIÑA')].groupby(['FECHA RECEPCION']).count().reset_index()
  

features = df['GlosaLocalidad'].unique()

app.layout = html.Div([

        html.Div(['Fecha',        
            html.Div([
                dcc.DatePickerSingle(
                    id='datepicker',
                    month_format = ('Do-MMM-YYYY'),
                    placeholder='01/03/2022',
                    display_format= "DD/MM/YYYY"
                )
            ]),
            html.Div(['Selector localidad',
                dcc.Dropdown(
                    options=[i for i in features],
                    value= 'HOSPITAL VIÑA', 
                    id= 'localidad'

                    )

                ])
                  ]),
        
    dcc.Tabs([

#tab1
    dcc.Tab(
        label='Tabla', children=[
        dash_table.DataTable(id='tbl', 
        columns=[{'name':i,'id':i} for i in df.columns if i != 'TERMINO'] ,
        filter_action='native',
        sort_action='native',
        sort_mode='multi',
    #filter_action='native',
    style_table={
    'height':'auto',
    'overflow':'scroll'
    },
    style_data={
    # 'width':'auto',
    # 'minWidth':'150px',
    # 'maxWidth':'150px',
    'whiteSpace':'normal',
    'overflow':'hidden',
    'textOverflow':'ellipsis'
    },
    style_cell_conditional=[
    {'if':{'column_id':'DIAS'},
    'width':'-20%'},
    {'if':{'column_id':'TIPO'},
    'width':'20%'},
    {'if':{'column_id':'NOMBRE'},
    'width':'20%'},
    ],
    export_format='csv')]

        ),

#tab2
    dcc.Tab(label='Consolidado', children=[
        # dcc.Dropdown(
        #     id='filter',
        #     options=['Cargo','Area'],
        #     placeholder='Cargo',
        #     multi=False,
        #     value='Cargo'),

       dash_table.DataTable(id='tblv',
        columns=[{'name':i,'id':i} for i in dfc.columns if i != 'Localidad'],
        
        style_table={
        'height':'auto',
        'overflow':'scroll'
        },
        style_data_conditional=[
            {'if':{'column_id':'TERMINO'},
             'display':'None'}],
        style_header_conditional=[
            {'if':{'column_id':'TERMINO'},
             'display':'None'}
        ],
        style_cell_conditional=[
        {'if':{'column_id':'Cargo'},
        'width':'40%'}])
        ]),
    
#tab3
    dcc.Tab(label='Grafico',children=[
     html.H4('Evolucion licencias'),
     dcc.Graph(id='timeseries'), 
    ])
    
    ]),

])

@app.callback(
    Output('tbl', 'data'),
    [Input('datepicker','date'),
    Input('localidad','value')]
)

def update_row(select_date, select_location):

   
    data = df[(df['TERMINO'] >= select_date) & (df['GlosaLocalidad'] == select_location)].sort_values(by=['TERMINO']) 
    
    return data.to_dict('records')

@app.callback(
    Output('tblv','data'),
    [Input('datepicker','date')],
    [Input('localidad','value')]
)

def update_rows(select_date, select_location):
    data = dfc[(dfc['TERMINO'] >= select_date) & (dfc['Localidad'] == select_location)].groupby(['Cargo','Area']).count().reset_index()
    data.sort_values(by=['Cargo','Total'],inplace=True, ascending=False)
    return data.to_dict('records')


@app.callback(
    Output('timeseries','figure'),
    [Input('datepicker','date')]
)

def display_timeseries(select_date):
    fecha = dfl[(dfl['FECHA RECEPCION'] >= '01-01-2022') &(dfl['FECHA RECEPCION'] <= select_date)].groupby(['FECHA RECEPCION']).count().reset_index()  
    fig = px.line(fecha , x='FECHA RECEPCION', y= 'TRAMITE')
    return fig

if __name__ =='__main__':
    app.run_server()
