import streamlit as st
from PIL import Image

st.set_page_config(page_title='Home' , layout='wide')


#image_path = r'C:\Users\User\FTC\curry_company_logo.jpg'
image = Image.open('curry_company_logo.jpg')
st.sidebar.image( image , width=120 )


st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('### The Fastest Delivery in Town')
st.sidebar.markdown('''---''')
st.sidebar.markdown('Select limit Date')
st.write('# Cury Company Growth Dashboard')

st.markdown(
    '''
    Grouwth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar este Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregadores:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes.
    ### Ask for Help
        - Time de Datascience no Discord
            - Philippe Almeida
    ''')