
#===================================================================================================================================
#Bibliotecas necessarias:
#===================================================================================================================================
import pandas as pd
from haversine import haversine
import plotly.express as px
import folium
import streamlit as st
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

def order_metric( df1 ):
    df_aux = df1.loc[: , ['ID' , 'Order_Date']].groupby(['Order_Date']).count().reset_index()
    fig = px.bar(df_aux , x='Order_Date' , y='ID')
    return fig

def traffic_order_share( df1 ):
    df_aux = (df1.loc[ : , ['ID' , 'Road_traffic_density']]
                 .groupby(['Road_traffic_density'])
                 .count()
                 .reset_index())
    fig = px.pie(df_aux , names='Road_traffic_density' , values='ID' , color='Road_traffic_density')
    return fig

def traffic_order_city( df1 ):
    df_aux = (df1.loc[ : , ['ID' , 'Road_traffic_density' , 'City']]
                 .groupby(['Road_traffic_density' , 'City'])
                 .count()
                 .reset_index())
    fig = px.scatter( df_aux , x='City' , y='Road_traffic_density' , size='ID' , color='City')
    return fig

def order_by_week( df1 ):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )
    df_aux = (df1.loc[ : , ['ID' , 'week_of_year']]
                 .groupby('week_of_year')
                 .count()
                 .reset_index())
    fig = px.line( df_aux , x='week_of_year' , y='ID')
    return fig

def order_share_by_week( df1 ):
    df_aux01 = (df1.loc[ : , ['week_of_year' , 'Delivery_person_ID']]
                   .groupby(['week_of_year'])
                   .nunique()
                   .reset_index())
    df_aux02 = (df1.loc[ : , ['ID' , 'week_of_year']]
                   .groupby(['week_of_year'])
                   .count()
                   .reset_index())

    df_aux = pd.merge(df_aux01 , df_aux02 , how='inner')
    df_aux['order_per_delivery_person'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux , x='week_of_year' , y='order_per_delivery_person')
    return fig

def country_maps( df1 ):
    
    df_aux = (df1.loc[ : , ['City' , 'Road_traffic_density' , 'Delivery_location_latitude' , 'Delivery_location_longitude']]
                .groupby(['City' , 'Road_traffic_density'])
                .median()
                .reset_index())
    map = folium.Map()
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'] , 
                       location_info['Delivery_location_longitude']] , 
                       popup=location_info[['City' , 'Road_traffic_density']]).add_to( map )
    folium_static(map , width=1024 , height=600)
    return None
#===================================================================================================================================
#Importando arquivo:
#===================================================================================================================================

df = pd.read_csv('dataset/train.csv')
df1 = df.copy()

#===================================================================================================================================
#Limpeza de dados:
#===================================================================================================================================
df1 = clean_code (df)


#===================================================================================================================================
#Layout Sidebar
#===================================================================================================================================
st.set_page_config(page_title='Visão Empresa' , layout='wide')

st.header('Marketplace - Visão Empresa')

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
tab1, tab2, tab3 = st.tabs(['Visão Gerencial' , 'Visão Tatica' , 'Visão Geográfica'])

#Visão Gerencial
#===================================================================================================================================
with tab1:
    with st.container():
        #Order Metric
        st.markdown('# Orders by Day')
        fig = order_metric( df1 )
        st.plotly_chart(fig, use_container_width=True)
 

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('Traffic Order Share')
            fig = traffic_order_share( df1 )
            st.plotly_chart(fig , use_container_width=True)
  
        with col2:
            st.markdown('Traffic Order City')
            fig = traffic_order_city( df1 )
            st.plotly_chart(fig , use_container_width=True)

#Visão Tatica
#===================================================================================================================================
with tab2:
    with st.container():
        st.markdown('Order by Week')
        fig = order_by_week( df1 )
        st.plotly_chart(fig , use_container_width=True)
  
    with st.container():
        st.markdown('Order Share by Week')
        fig = order_share_by_week( df1 )
        st.plotly_chart(fig , use_container_width=True)
                               
#Visão Geografica
#===================================================================================================================================
with tab3:
    st.markdown('Country Maps')
    country_maps( df1 )
