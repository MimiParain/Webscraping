import streamlit as st
import folium
import pandas as pd
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import matplotlib.pyplot as plt
import seaborn as sns

# Initialiser le géocodeur Nominatim avec un user_agent spécifique
geolocator = Nominatim(user_agent="my_coworking_app")

# Fonction pour géocoder une adresse
def geocode_address(address, retries=3):
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            return (location.latitude, location.longitude)
        else:
            return None
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        if retries > 0:
            return geocode_address(address, retries - 1)
        else:
            return None

# Charger les données nettoyées
df = pd.read_excel("coworking_paris_cleaned.xlsx")

# Créer une carte Folium
m = folium.Map(location=[48.8566, 2.3522], zoom_start=12)

# Ajouter des marqueurs pour chaque espace de coworking
non_trouvees = []
for _, row in df.iterrows():
    if row['adresse'] != "Non disponible":
        coordinates = geocode_address(row['adresse'])
        if coordinates:
            folium.Marker(
                location=coordinates,
                popup=f"<b>{row['Nom']}</b><br>{row['description']}",
                tooltip=row['Nom']
            ).add_to(m)
        else:
            non_trouvees.append(row['adresse'])

# Afficher la carte avec Streamlit
st.title("Carte des espaces de coworking à Paris")
folium_static(m)

# Visualisations supplémentaires
st.subheader("Visualisations des Données")

# Répartition des coworking par arrondissement
st.write("### Répartition des coworking par arrondissement")
df['arrondissement'] = df['adresse'].apply(lambda x: x.split(',')[-1].strip() if ',' in x else 'Autre')
fig, ax = plt.subplots()
sns.countplot(data=df, x='arrondissement', order=df['arrondissement'].value_counts().index, ax=ax)
plt.xticks(rotation=90)
st.pyplot(fig)

# Distribution des types d'accès
st.write("### Distribution des types d'accès")
fig, ax = plt.subplots()
sns.countplot(data=df, x='acces', order=df['acces'].value_counts().index, ax=ax)
plt.xticks(rotation=90)
st.pyplot(fig)

# Analyse des présences en ligne
st.write("### Présence sur les réseaux sociaux")
presence_sociale = {
    'Twitter': df['twitter'].apply(lambda x: x != "Non disponible").sum(),
    'Facebook': df['facebook'].apply(lambda x: x != "Non disponible").sum(),
    'LinkedIn': df['linkedin'].apply(lambda x: x != "Non disponible").sum()
}
fig, ax = plt.subplots()
sns.barplot(x=list(presence_sociale.keys()), y=list(presence_sociale.values()), ax=ax)
st.pyplot(fig)

# Afficher les adresses non trouvées
if non_trouvees:
    st.subheader("Adresses non trouvées lors du géocodage")
    for adresse in non_trouvees:
        st.write(adresse)

# Afficher les informations détaillées
st.subheader("Détails des espaces de coworking")
for _, row in df.iterrows():
    st.write(f"### {row['Nom']}")
    st.write(f"**Adresse :** {row['adresse']}")
    st.write(f"**Téléphone :** {row['telephone']}")
    st.write(f"**Accès :** {row['acces']}")
    st.write(f"**Site :** {row['site']}")
    st.write(f"**Twitter :** {row['twitter']}")
    st.write(f"**Facebook :** {row['facebook']}")
    st.write(f"**LinkedIn :** {row['linkedin']}")
    st.write(f"**Description :** {row['description']}")
    st.write(f"**Meta Title inférieur à 150 caractères :** {row['meta_title_inferieur_a_150']}")
    st.write("---")
