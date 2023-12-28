#===================================================================================================================================
#Bibliotecas necessarias:
#===================================================================================================================================
import pandas as pd
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import folium
import streamlit as st
import numpy as np
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static

#===================================================================================================================================
#Funções:
#===================================================================================================================================
def clean_code( df1 ):
    '''
    Esta função tem a responsabilidade de limpar o Data Frame
    1. Remoção dos dados NaN
    2. Mudança do tipo de colina de dados (float, int, data, etc.)
    3. Remoção dos espaços das variaveis de texto
    4. Formatação das colunas de datas
    5. Limpeza da coluna de tempo - remoção do texto da variável numérica

    input: Dataframe
    output: Dataframe
    
    '''
    # 1. tirando os espaços das colunas:
    df1['ID'] = df1.loc[ : , 'ID'].str.strip()
    df1['Weatherconditions'] = df1.loc[ : , 'Weatherconditions'].str.strip()
    df1['Road_traffic_density'] = df1.loc[ : , 'Road_traffic_density'].str.strip()
    df1['Festival'] = df1.loc[ : , 'Festival'].str.strip()
    df1['City'] = df1.loc[ : , 'City'].str.strip()
    
    #2. Alterando colunas para int/float/datetime:
    
    #Delivery_person_Age
    linhas_selecionadas = df1.loc[ : , 'Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas , :]
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )
    
    #multiple_deliveries
    linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas , : ]
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )
    
    #Road_traffic_density
    df1 = df1.loc[df1['Road_traffic_density'] != 'NaN' , :]
    
    #Weatherconditions
    df1 = df1.loc[df1['Weatherconditions'] != 'conditions NaN' , :]
    
    #City
    df1 = df1.loc[df1['City'] != 'NaN' , :]
    
    #Delivery_person_Ratings
    df1['Delivery_person_Ratings'] = df1.loc[: , 'Delivery_person_Ratings'].astype( float )
    
    #Order_Date
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'] , format='%d-%m-%Y')
    
    
    #3. Removendo o '(min) ' da coluna 'Time_taken(min)':
    
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )
    df1 = df1.reset_index(drop=True)
    return df1

def distance( df1 ):
    df1['distance'] = (df1.loc[ : , ['Restaurant_latitude' , 'Restaurant_longitude' , 'Delivery_location_latitude' , 'Delivery_location_longitude']]
                          .apply( lambda x: haversine(                                                                                                                                                        (x['Restaurant_latitude'] , x['Restaurant_longitude']),                                                                                                                     (x['Delivery_location_latitude'] , x['Delivery_location_longitude'])), axis=1))
    
    avg_distance = np.round(df1['distance'].mean() , 2)
    col2.metric('Distancia Média' , avg_distance)
    return avg_distance

def avg_std_time_delivery( df1 , festival , op):
    '''
    Esta função calcula o tempo médio e desvio padrão das entregas.
        Parâmetros:
            Input: Dataframe com os dados necessários para o calculo
            op: tipo de operação que precisa ser calculada
                'avg_time' : calcula o tempo médio
                'std_time' : calcula o desvio padrão do tempo
            festival:
                'Yes': calcula com base nas entregas realizadas durante festivais
                'No': calcula com base na entregas realizadas fora dos festivais
            Output: Dataframe com2 colunas e 1 linha.
    '''
    df_aux = (df1.loc[ : , ['Festival' , 'Time_taken(min)']].groupby(['Festival'])
                                                            .agg({'Time_taken(min)' : ['mean' , 'std']}))
                                                                                
    df_aux.columns = ['avg_time' , 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes' , op] , 2)
    
    return df_aux

def avg_std_timegraph( df1 ):
    st.title('Tempo Médio de Entrega por Cidade')
    df1['distance'] = (df1.loc[ : , ['Restaurant_latitude' , 'Restaurant_longitude' , 'Delivery_location_latitude' , 'Delivery_location_longitude']]
                          .apply( lambda x: haversine((x['Restaurant_latitude'] , x['Restaurant_longitude']),                                                                                                                     (x['Delivery_location_latitude'] , x['Delivery_location_longitude'])), axis=1))
    avg_distance = df1.loc[ : ,['City' , 'distance']].groupby(['City']).mean().reset_index()

    fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0,0.1,0])])
    return fig

def avg_std_delivery_time( df1 ):
                
    time_taken_avg_std = (df1.loc[ : , ['Time_taken(min)' , 'City']]
                             .groupby(['City'])
                             .agg({'Time_taken(min)' : ['mean' , 'std']}))
                                                                
    time_taken_avg_std.columns = ['Time_taken_avg' , 'Time_taken_std']
    time_taken_avg_std = time_taken_avg_std.reset_index()
    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control',
                           x=time_taken_avg_std['City'],
                           y=time_taken_avg_std['Time_taken_avg'],
                           error_y=dict(type='data' , array=time_taken_avg_std['Time_taken_std'])))
    fig.update_layout(barmode='group')
    return fig

def avg_std_time_on_traffic( df1 ):
    time_taken_city_traffic_density_avg_std = (df1.loc[ : , ['Time_taken(min)' , 'City' , 'Road_traffic_density']]
                                                  .groupby(['City' , 'Road_traffic_density'])
                                                  .agg({'Time_taken(min)' : ['mean' , 'std']}))
    time_taken_city_traffic_density_avg_std.columns = ['Time_taken_avg' , 'Time_taken_std']
    time_taken_city_traffic_density_avg_std = time_taken_city_traffic_density_avg_std.reset_index()
    fig = px.sunburst(time_taken_city_traffic_density_avg_std, path=['City' , 'Road_traffic_density'] , values='Time_taken_avg',
                      color='Time_taken_avg' , color_continuous_scale='RdBu',
                      color_continuous_midpoint=np.average(time_taken_city_traffic_density_avg_std['Time_taken_avg']))
    return fig
#===================================================================================================================================
#Importando arquivo:
#===================================================================================================================================

df = pd.read_csv('dataset/train.csv')
df1 = df.copy()

#===================================================================================================================================
#Tratamento de dados:
#===================================================================================================================================
df1 = clean_code( df )


#===================================================================================================================================
#Layout Sidebar
#===================================================================================================================================
st.set_page_config(page_title='Visao Restaurantes' , layout='wide')

st.header('Marketplace - Visão Restaurantes')

#image_path = r'C:\Users\User\FTC\curry_company_logo.jpg'
image = Image.open('curry_company_logo.jpg')
st.sidebar.image( image , width=120 )

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('### The Fastest Delivery in Town')
st.sidebar.markdown('''---''')
st.sidebar.markdown('Select limit Date')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime( 2022 , 4 , 13 ),
    min_value=datetime( 2022 , 2 , 22 ),
    max_value=datetime( 2022 , 4 , 6 ),
    format='DD-MM-YYYY')
traffic_condition = st.sidebar.multiselect(
    'Selecione uma condição de trânsito' ,['High' , 'Medium' , 'Low' , 'Jam'] ,
    default='Low')
weathercondition = st.sidebar.multiselect(
    'Selecione uma condição de tempo' ,['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms',
       'conditions Cloudy', 'conditions Fog', 'conditions Windy'] ,
    default='conditions Sunny')

st.sidebar.markdown('''---''')
st.sidebar.markdown('Powered by PsA')

#Filtro de Data:
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas , :]

#Filtro de transito:
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_condition)
df1 = df1.loc[linhas_selecionadas , : ]

#Filtro de weatherconditions:
linhas_selecionadas = df1['Weatherconditions'].isin(weathercondition)
df1 = df1.loc[linhas_selecionadas , : ]

#===================================================================================================================================
#Layout Main Page
#===================================================================================================================================
tab1 , tab2 , tab3 = st.tabs(['Visão Gerencial' , '_' , '_'])

#===================================================================================================================================
#Container Superior
#===================================================================================================================================
with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1 , col2 , col3 , col4 , col5 , col6 = st.columns(6)
        with col1:
            delivery_unique = (df1['Delivery_person_ID'].nunique())
            col1.metric('Entregadores Únicos' , delivery_unique)
        with col2:
            avg_distance = distance( df1 )
        with col3:
            df_aux = avg_std_time_delivery( df1 , 'Yes' , 'avg_time')
            col3.metric('AVGT de Entrega em Festival' , df_aux)
        with col4:
            df_aux = avg_std_time_delivery( df1 , 'Yes' , 'std_time')
            col4.metric('AVGT de Entrega em Festival' , df_aux)
        with col5:
            df_aux = avg_std_time_delivery( df1 , 'No' , 'avg_time')
            col5.metric('AVGT de Entrega s/ Festival' , df_aux)
        with col6:
            df_aux = avg_std_time_delivery( df1 , 'No' , 'std_time')
            col6.metric('STD de Entrega s/ Festival' , df_aux)
            
        st.markdown('''---''')
        
    with st.container():
        fig = avg_std_timegraph( df1 )
        st.plotly_chart( fig, use_container_width=True )
        
        st.markdown('''---''')
        
    with st.container():
        st.title('Distribuição do Tempo')
        
        col1 , col2 = st.columns(2)
        with col1:
            fig = avg_std_delivery_time( df1 )
            st.plotly_chart( fig , use_container_width=True )
                        
        with col2:
            
            fig = avg_std_time_on_traffic( df1 )
            st.plotly_chart( fig )
        
    with st.container():
        st.title('Distribuição da Distância')
        
        with st.container():
            time_city_Order_type_avg_std = (df1.loc[ : , ['Time_taken(min)' , 'City' , 'Type_of_order']]
                                                     .groupby(['City' , 'Type_of_order'])
                                                     .agg({'Time_taken(min)' : ['mean' , 'std']}))
        
            time_city_Order_type_avg_std.columns = ['Time_taken_mean' , 'Time_taken_std']
            time_city_Order_type_avg_std = time_city_Order_type_avg_std.reset_index()
            st.dataframe( time_city_Order_type_avg_std , use_container_width=True )


        