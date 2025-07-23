import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(page_title="Dashboard Transactions Complet", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("Transactions_data_complet.csv") 
    df['TransactionStartTime'] = pd.to_datetime(df['TransactionStartTime'], utc=True)
    df['Année'] = df['TransactionStartTime'].dt.year
    df['Mois'] = df['TransactionStartTime'].dt.month
    df['Jour'] = df['TransactionStartTime'].dt.day
    df['Heure'] = df['TransactionStartTime'].dt.hour
    df['AnneeMois'] = df['TransactionStartTime'].dt.to_period('M').astype(str)
    return df

df = load_data()

st.title("📊 Dashboard Transactions Complet")

# Sidebar filtres
st.sidebar.header("Filtres")

years = sorted(df['Année'].unique())
year_filter = st.sidebar.multiselect("Année", years, default=years)

categories = sorted(df['ProductCategory'].unique())
category_filter = st.sidebar.multiselect("Catégorie produit", categories, default=categories)

providers = sorted(df['ProviderId'].unique())
provider_filter = st.sidebar.multiselect("Fournisseur", providers, default=providers)

country_filter = st.sidebar.multiselect("Pays (CountryCode)", sorted(df['CountryCode'].unique()), default=sorted(df['CountryCode'].unique()))

channel_filter = st.sidebar.multiselect("Canal (ChannelId)", sorted(df['ChannelId'].unique()), default=sorted(df['ChannelId'].unique()))

filtered_df = df[
    (df['Année'].isin(year_filter)) &
    (df['ProductCategory'].isin(category_filter)) &
    (df['ProviderId'].isin(provider_filter)) &
    (df['CountryCode'].isin(country_filter)) &
    (df['ChannelId'].isin(channel_filter))
]

# Stats clés
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Nombre Transactions", filtered_df.shape[0])
col2.metric("Montant Total", f"{filtered_df['Amount'].sum():,.2f}")
col3.metric("Montant Moyen", f"{filtered_df['Amount'].mean():,.2f}")
col4.metric("Transactions Fraude", filtered_df['FraudResult'].sum())
col5.metric("Transactions Négatives", (filtered_df['Amount'] < 0).sum())

st.markdown("---")

# 1. Répartition transactions par catégorie (barplot seaborn)
st.subheader("Répartition des transactions par catégorie")
fig1, ax1 = plt.subplots(figsize=(10,5))
sns.countplot(data=filtered_df, x='ProductCategory', order=filtered_df['ProductCategory'].value_counts().index, ax=ax1)
plt.xticks(rotation=45)
st.pyplot(fig1)

# 2. Montant total par année (barplot plotly)
st.subheader("Montant total par année")
df_year = filtered_df.groupby('Année')['Amount'].sum().reset_index()
fig2 = px.bar(df_year, x='Année', y='Amount', labels={"Amount":"Montant total", "Année":"Année"})
st.plotly_chart(fig2, use_container_width=True)

# 3. Distribution des montants par heure (boxplot seaborn)
st.subheader("Distribution des montants par heure")
fig3, ax3 = plt.subplots(figsize=(10,5))
sns.boxplot(data=filtered_df, x='Heure', y='Amount', ax=ax3)
st.pyplot(fig3)

# 4. Heatmap corrélations (seaborn)
st.subheader("Heatmap des corrélations")
num_cols = ['Amount', 'Value', 'PricingStrategy', 'FraudResult']
fig4, ax4 = plt.subplots(figsize=(8,6))
sns.heatmap(filtered_df[num_cols].corr(), annot=True, cmap="coolwarm", ax=ax4)
st.pyplot(fig4)

# 5. Montant total par mois (ligne plotly)
st.subheader("Montant total par mois")
df_month = filtered_df.groupby('AnneeMois')['Amount'].sum().reset_index()
fig5 = px.line(df_month, x='AnneeMois', y='Amount', markers=True,
               labels={"AnneeMois": "Année-Mois", "Amount": "Montant total"})
fig5.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig5, use_container_width=True)

# 6. Répartition catégories en pourcentage (pie plotly)
st.subheader("Répartition des catégories en pourcentage")
cat_sum = filtered_df.groupby('ProductCategory')['Amount'].sum().reset_index()
fig6 = px.pie(cat_sum, values='Amount', names='ProductCategory', title="Part des catégories")
st.plotly_chart(fig6, use_container_width=True)

# 7. Montants par fournisseur (boxplot seaborn)
st.subheader("Montants par fournisseur")
fig7, ax7 = plt.subplots(figsize=(12,6))
sns.boxplot(data=filtered_df, x='ProviderId', y='Amount', ax=ax7)
plt.xticks(rotation=45)
st.pyplot(fig7)

# 8. Histogramme des montants
st.subheader("Histogramme des montants")
fig8, ax8 = plt.subplots(figsize=(10,5))
ax8.hist(filtered_df['Amount'], bins=50, color='skyblue', edgecolor='black')
ax8.set_xlabel("Montant")
ax8.set_ylabel("Nombre de transactions")
st.pyplot(fig8)

# 9. Evolution des fraudes dans le temps
st.subheader("Evolution des fraudes dans le temps")
df_fraud = filtered_df.groupby('AnneeMois')['FraudResult'].sum().reset_index()
fig9 = px.line(df_fraud, x='AnneeMois', y='FraudResult', markers=True,
               labels={"AnneeMois": "Année-Mois", "FraudResult": "Nombre fraudes"})
fig9.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig9, use_container_width=True)

# 10. Répartition des pays (barplot plotly)
st.subheader("Répartition des transactions par pays")
df_country = filtered_df['CountryCode'].value_counts().reset_index()
df_country.columns = ['CountryCode', 'Count']
fig10 = px.bar(df_country, x='CountryCode', y='Count', labels={"Count": "Nombre de transactions"})
st.plotly_chart(fig10, use_container_width=True)

# 11. Scatter Amount vs Value
st.subheader("Scatter plot Montant vs Valeur")
fig11 = px.scatter(filtered_df, x='Amount', y='Value', color='FraudResult',
                   labels={"Amount": "Montant", "Value": "Valeur", "FraudResult": "Fraude"},
                   title="Montant vs Valeur coloré par fraude")
st.plotly_chart(fig11, use_container_width=True)

# 12. Barplot des canaux
st.subheader("Transactions par canal (ChannelId)")
df_channel = filtered_df['ChannelId'].value_counts().reset_index()
df_channel.columns = ['ChannelId', 'Count']
fig12 = px.bar(df_channel, x='ChannelId', y='Count', labels={"Count": "Nombre de transactions"})
st.plotly_chart(fig12, use_container_width=True)

# 13. Transactions positives vs négatives
st.subheader("Transactions positives vs négatives")
pos_count = (filtered_df['Amount'] >= 0).sum()
neg_count = (filtered_df['Amount'] < 0).sum()
df_pos_neg = pd.DataFrame({
    'Type': ['Positives', 'Négatives'],
    'Count': [pos_count, neg_count]
})
fig13 = px.pie(df_pos_neg, values='Count', names='Type', title="Répartition des transactions positives et négatives")
st.plotly_chart(fig13, use_container_width=True)

# Afficher un extrait des données filtrées
st.subheader("Extrait des données filtrées")
st.dataframe(filtered_df.head(50))
