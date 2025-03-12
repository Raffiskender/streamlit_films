import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ast

def accueil():
    st.title("Accueil")
    st.write("Bienvenue sur la présentation Streamlit")
    st.write("Voici quelques graphiques concernant les films de la db tmdb")

def load_data():
    if 'df' not in st.session_state:
        st.session_state.df = pd.read_csv('https://nextcloud.raffiskender.duckdns.org/s/BYgFQ2rejAJwR9N', parse_dates=['Date'])

def details():
    st.title("Détails d'un film")
    st.write("Recherchez un film par son titre.")
    title = st.selectbox("Titre du film", st.session_state.df['Title'].unique())

    df_details = st.session_state.df[st.session_state.df['Title'] == title]
    st.markdown(f""" ## Film : {df_details['Title'].iloc[0]}
    ![image du film]({df_details['Poster'].iloc[0]})
                
    Note : {df_details['Note'].iloc[0]}/10

    Date de sortie : {df_details['Date'].iloc[0]} 
    Durée : {df_details['Runtime'].iloc[0]} minutes""")
    
    formatted_budget = f"{int(df_details['Budget'].iloc[0]):,}".replace(',', ' ')
    formatted_recette = f"{int(df_details['Revenue'].iloc[0]):,}".replace(',', ' ')
    formated_profit = f"{int(df_details['Revenue'].iloc[0] - df_details['Budget'].iloc[0]):,}".replace(',', ' ')
    

    # Affichage du texte avec couleur conditionnelle
    if df_details['Revenue'].iloc[0] - df_details['Budget'].iloc[0] >= 0:
        st.markdown(f"<p>Budjet : $ {formatted_budget} - Recette : $ {formatted_recette} - <span style='color:green;'>Profit : $ {formated_profit}</span></p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p>Budjet : $ {formatted_budget} - Recette : $ {formatted_recette} - <span style='color:red;'>Profit : $ {formated_profit}</span></p>", unsafe_allow_html=True)

    st.markdown("""
    ---
    ### Casting """)

    # Convertir la chaîne en liste
    cast_list = ast.literal_eval(df_details['Cast'].iloc[0])
    cols = st.columns(3)  # Crée 3 colonnes (ajuste le nombre selon tes besoins)

    for i, actor in enumerate(cast_list):
        with cols[i % 3]:
            st.markdown(f"#### **{actor['name']}**")
            st.markdown(f"*Rôle : {actor['character']}*")
            st.image(f"https://image.tmdb.org/t/p/w185/{actor['profile_path']}", caption=f"{actor['name']} - {actor['character']}")
            
def averages():
    st.title('Des moyennes sur les films')
    df_temp = st.session_state.df[['Country_lisible', 'Note', 'Popularity', 'Budget', 'Revenue']]

    df_temp = df_temp.drop(df_temp.loc[df_temp['Country_lisible'] == 'Inconnu'].index)
    df_temp['Profit'] = df_temp['Revenue'] - df_temp['Budget']
    # 1- Mettre en forme la data
    # selectionner le budjet des films par country
    country_choice = st.multiselect('Country', sorted(df_temp['Country_lisible'].unique()), max_selections=5)
    # 2- Afficher le budjet moyen par pays
    st.write('Valeur moyenne à observer :')
    value_choice = st.selectbox('Valeur à observer', ['Budget', 'Revenue', 'Profit', 'Note', 'Popularity'])
    st.write(value_choice)
    df_graphique = df_temp[df_temp['Country_lisible'].isin(country_choice)]
    df_graphique = df_graphique.groupby('Country_lisible').mean().reset_index()

    # 3- Afficher le graphique
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Country_lisible', y=value_choice, data=df_graphique)
    plt.title(f'{value_choice} moyen par pays')
    plt.xticks(rotation=45)
    st.pyplot(plt)


def budget_evolution():
    st.title('Évolution du budget par années')
    # 1- Préparation de la data :
    df = st.session_state.df[['Budget', 'Revenue', 'Country_lisible', 'Date']]
    df['Profit'] = df['Revenue'] - df['Budget']
    df['Year'] = df['Date'].dt.year
    df['Country_lisible'] = df['Country_lisible'].str.normalize('NFKD').str.encode('ASCII', errors='ignore').str.decode('ASCII')
    years = sorted(df['Year'].unique())

    #Sélection plage des dates
    plage = st.select_slider('Année', options=years, value=(years[0], years[-1]))

    #Selection des pays
    country_choice = st.multiselect('Quels pays vous intéressent ?', sorted(df['Country_lisible'].unique()), default=['Allemagne', 'France', 'Etats-Unis'], max_selections=5)
    df_graph = df[df['Country_lisible'].isin(country_choice)]

    #selection de la donnée
    data_choice = st.selectbox('Quelles données vous intéressent ?', ['Budget', 'Revenue','Profit'])

    df_graph = df[df['Country_lisible'].isin(country_choice)][['Country_lisible', 'Year', data_choice]]

    df_graph = df_graph[(df['Year'] >= plage[0]) & (df_graph['Year'] <= plage[1])]
    df_graph = df_graph.groupby(['Country_lisible', 'Year'])[data_choice].mean().reset_index()
    
    df_graph = df_graph.sort_values(by=['Country_lisible', 'Year'])

    with st.expander("Afficher les données"):
        st.dataframe(df_graph, hide_index=True)

    # 2- Affichage du graph
    plt.figure(figsize=(10, 6))
    sns.lineplot(x='Year', y=data_choice, data=df_graph, hue='Country_lisible', ci=None)
    plt.title(f'Évolution {data_choice} moyen par années pour les pays choisis')
    plt.legend(sorted(country_choice), title="Pays", loc="center left", bbox_to_anchor=(1, 0.5))
    st.pyplot(plt)


def side_menu():
    st.sidebar.title("Menu")

    # Création de variables dans la session pour gérer la navigation
    if "page" not in st.session_state:
        st.session_state.page = 0

    # Affichage des boutons de navigation
    if st.sidebar.button("🏠 Accueil"):
        st.session_state.page = 0
    if st.sidebar.button("Chercher un film"):
        st.session_state.page = 1
    if st.sidebar.button("Des moyennes par pays"):
        st.session_state.page = 2
    if st.sidebar.button("Évolution du budget par années"):
        st.session_state.page = 3

    # Affichage de la page
    if st.session_state.page == 0:
        accueil()
    elif st.session_state.page == 1:
        details()
    elif st.session_state.page == 2:
        averages()
    elif st.session_state.page == 3:
        budget_evolution()


if __name__ == '__main__':
    load_data()
    side_menu()

