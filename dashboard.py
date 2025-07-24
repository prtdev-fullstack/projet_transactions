import streamlit as st
import pandas as pd
import plotly.express as px

# Titre et description
st.set_page_config(page_title="Dashboard Transactions", layout="wide")
st.title("📊 Dashboard Transactions - Analyse complète")
st.markdown("""
Ce dashboard présente une analyse interactive et visuelle des transactions.
Utilisez les filtres pour explorer les données.
""")

@st.cache_data
def load_data():
    df = pd.read_csv("/Users/mac/Desktop/Transactions_data_complet.csv", parse_dates=['TransactionStartTime'])
    return df

df = load_data()

# Filtres colonne latérale
st.sidebar.header("Filtres")
product_filter = st.sidebar.multiselect(
    "Catégories produits",
    options=df['ProductCategory'].unique(),
    default=df['ProductCategory'].unique()
)

provider_filter = st.sidebar.multiselect(
    "Fournisseurs",
    options=df['ProviderId'].unique(),
    default=df['ProviderId'].unique()
)

fraud_filter = st.sidebar.radio(
    "Filtrer par fraude",
    options=["Tous", "Fraudes uniquement", "Non fraudes uniquement"]
)

# Appliquer filtres
df_filtered = df[
    (df['ProductCategory'].isin(product_filter)) &
    (df['ProviderId'].isin(provider_filter))
]

if fraud_filter == "Fraudes uniquement":
    df_filtered = df_filtered[df_filtered['FraudResult'] == 1]
elif fraud_filter == "Non fraudes uniquement":
    df_filtered = df_filtered[df_filtered['FraudResult'] == 0]

st.markdown(f"### Données filtrées : {len(df_filtered)} transactions")

# 1. Distribution des montants
st.subheader("Distribution des montants (Amount)")
fig_amount = px.histogram(df_filtered, x="Amount", nbins=50, marginal="box",
                          title="Répartition des montants des transactions",
                          color='FraudResult', color_discrete_map={0:"green",1:"red"},
                          labels={"Amount": "Montant", "FraudResult": "Fraude"})
st.plotly_chart(fig_amount, use_container_width=True)

# 2. Proportion des fraudes
st.subheader("Proportion des fraudes")
fraud_counts = df_filtered['FraudResult'].value_counts().rename({0:'Non Fraude', 1:'Fraude'})
fraud_counts = fraud_counts.reset_index()
fraud_counts.columns = ['Statut', 'Nombre']

fig_pie = px.pie(fraud_counts, values='Nombre', names='Statut',
                 color='Statut',
                 color_discrete_map={'Fraude':'red', 'Non Fraude':'green'},
                 title="Proportion des transactions frauduleuses")
st.plotly_chart(fig_pie, use_container_width=True)

# 3. Transactions par catégorie de produit
st.subheader("Transactions par catégorie de produit")
cat_counts = df_filtered['ProductCategory'].value_counts().reset_index()
cat_counts.columns = ['Catégorie', 'Nombre']
fig_bar_cat = px.bar(cat_counts, x='Catégorie', y='Nombre',
                     title="Nombre de transactions par catégorie",
                     text='Nombre')
st.plotly_chart(fig_bar_cat, use_container_width=True)

# 4. Transactions par fournisseur
st.subheader("Transactions par fournisseur")
prov_counts = df_filtered['ProviderId'].value_counts().reset_index()
prov_counts.columns = ['Fournisseur', 'Nombre']
fig_bar_prov = px.bar(prov_counts, x='Fournisseur', y='Nombre',
                      title="Nombre de transactions par fournisseur",
                      text='Nombre')
st.plotly_chart(fig_bar_prov, use_container_width=True)

# 5. Analyse temporelle : transactions par mois
st.subheader("Transactions par mois")
df_filtered['Month'] = df_filtered['TransactionStartTime'].dt.to_period('M').astype(str)
month_counts = df_filtered['Month'].value_counts().sort_index().reset_index()
month_counts.columns = ['Mois', 'Nombre']
fig_line_month = px.line(month_counts, x='Mois', y='Nombre',
                         title="Nombre de transactions par mois")
st.plotly_chart(fig_line_month, use_container_width=True)

# 6. Heatmap jours/heures
st.subheader("Heatmap des transactions par jour et heure")
df_filtered['DayOfWeek'] = df_filtered['TransactionStartTime'].dt.day_name()
df_filtered['Hour'] = df_filtered['TransactionStartTime'].dt.hour

heatmap_data = df_filtered.groupby(['DayOfWeek', 'Hour']).size().reset_index(name='count')
# Ordre des jours pour plus de lisibilité
days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
heatmap_data['DayOfWeek'] = pd.Categorical(heatmap_data['DayOfWeek'], categories=days_order, ordered=True)
heatmap_data = heatmap_data.sort_values(['DayOfWeek', 'Hour'])

heatmap_pivot = heatmap_data.pivot(index='DayOfWeek', columns='Hour', values='count')

import seaborn as sns
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(15,6))
sns.heatmap(heatmap_pivot, cmap="YlGnBu", ax=ax)
plt.title("Transactions par jour de la semaine et heure")
st.pyplot(fig)

# 7. Montant moyen par catégorie
st.subheader("Montant moyen par catégorie de produit")
mean_amount_cat = df_filtered.groupby('ProductCategory')['Amount'].mean().reset_index()
fig_bar_mean = px.bar(mean_amount_cat, x='ProductCategory', y='Amount',
                      title="Montant moyen par catégorie",
                      labels={"Amount": "Montant moyen"})
st.plotly_chart(fig_bar_mean, use_container_width=True)

# 8. Montant total par canal
st.subheader("Montant total par canal")
amount_by_channel = df_filtered.groupby('ChannelId')['Amount'].sum().reset_index()
fig_bar_channel = px.bar(amount_by_channel, x='ChannelId', y='Amount',
                         title="Montant total par canal")
st.plotly_chart(fig_bar_channel, use_container_width=True)

# Footer / crédits
st.markdown("---")
st.markdown("Dashboard créé par **Marc Obanga** - Powered by Streamlit & Plotly")

