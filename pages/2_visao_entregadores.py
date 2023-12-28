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


def top_delivery_person ( df1 , top_asc=True):
    fastest_delivery_person = (df1.loc[ : , ['Delivery_person_ID' , 'City' , 'Time_taken(min)' ]]
                                  .groupby(['City' , 'Delivery_person_ID'])
                                  .mean()
                                  .sort_values(['City' , 'Time_taken(min)'] , ascending=top_asc)
                                  .reset_index())

    fastest_delivery_person_Metropolitian = fastest_delivery_person.loc[fastest_delivery_person['City']== 'Metropolitian' , : ].head(10)
    fastest_delivery_person_Urban = fastest_delivery_person.loc[fastest_delivery_person['City']== 'Urban' , : ].head(10)
    fastest_delivery_person_Semi_Urban = fastest_delivery_person.loc[fastest_delivery_person['City']== 'Semi-Urban' , : ].head(10)


    fastest_delivery_person_per_city = pd.concat( [fastest_delivery_person_Metropolitian , fastest_delivery_person_Urban , fastest_delivery_person_Semi_Urban])
    return fastest_delivery_person_per_city
#===================================================================================================================================
#Importando arquivo:
#===================================================================================================================================

df = pd.read_csv('dataset/train.csv')
df1 = df.copy()

#===================================================================================================================================
#Limpeza de dados:
#===================================================================================================================================
df1 = clean_code( df )

#===================================================================================================================================
#Layout Sidebar
#===================================================================================================================================
st.set_page_config(page_title='Visão Entregadores' , layout='wide')

st.header('Marketplace - Visão Entregadores')

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
        col1, col2, col3 , col4 = st.columns(4, gap='large')
        
        #Maior Idade dos Entregadores
        with col1:
            maior_idade = (df1.loc[ : ,'Delivery_person_Age'].max())
            col1.metric('Maior Idade' , maior_idade)
        
        #Menor Idade dos Entregadores
        with col2:
            menor_idade = (df1.loc[ : ,'Delivery_person_Age'].min())
            col2.metric('Menor Idade', menor_idade)
        
        #Melhor condição de veículos:
        with col3:
            melhor_condicao = (df1.loc[ : ,'Vehicle_condition'].max())
            col3.metric('Melhor Condição de Veículos', melhor_condicao)
            

        #Pior condição de veículos:
        with col4:
            pior_condicao = (df1.loc[ : ,'Vehicle_condition'].min())
            col4.metric('Pior Condição de Veículos', pior_condicao)

#===================================================================================================================================
#Container do meio
#===================================================================================================================================
    with st.container():
        st.markdown('''---''')
        st.title('Avaliações')
        with st.container():
            col1 , col2 = st.columns(2)
            with col1:
                st.markdown('##### Avaliação Média por Entregador')
                avg_rating_per_delivery_person = (df1.loc[ : , ['Delivery_person_ID' , 'Delivery_person_Ratings']]
                                                  .groupby(['Delivery_person_ID'])
                                                  .mean().reset_index())
                
                st.dataframe(avg_rating_per_delivery_person)
                

            with col2:
                st.markdown('##### Avaliação Média por Trânsito')
                traffic_density_avg_std = (df1.loc[ : , ['Delivery_person_Ratings' , 'Road_traffic_density']]
                                           .groupby(['Road_traffic_density'])
                                           .agg({'Delivery_person_Ratings' : ['mean' , 'std']}))
                
                #Renomeando as Colunas:
                traffic_density_avg_std.columns = ['Delivery_person_Ratings_mean' , 'Delivery_person_Ratings_std']
                traffic_density_avg_std = traffic_density_avg_std.reset_index()
                st.dataframe(traffic_density_avg_std)

                
                st.markdown('##### Avaliação Média por Clima')
                weatherconditions_rate_avg_std = (df1.loc[ : , ['Delivery_person_Ratings' , 'Weatherconditions']]
                                                  .groupby(['Weatherconditions'])
                                                  .agg({'Delivery_person_Ratings' : ['mean' , 'std']}))
                #Renomeando as Colunas:
                weatherconditions_rate_avg_std.columns = ['Delivery_person_Ratings_mean' , 'Delivery_person_Ratings_std']
                weatherconditions_rate_avg_std = weatherconditions_rate_avg_std.reset_index()
                st.dataframe(weatherconditions_rate_avg_std)

#===================================================================================================================================
#Container inferior
#===================================================================================================================================
    with st.container():
        st.markdown('''---''')
        st.title('Velocidade de Entrega')

        col1 , col2 = st.columns(2)
        with col1:
            st.markdown('##### Top Entregadores mais Rápidos')
            fastest_delivery_person_per_city = top_delivery_person ( df1 , top_asc=True )
            st.dataframe(fastest_delivery_person_per_city)
            
        with col2:
            st.markdown('##### Top Entregadores mais Lentos')
            fastest_delivery_person_per_city = top_delivery_person ( df1 , top_asc=False )
            st.dataframe(fastest_delivery_person_per_city)
        