import streamlit as st
import pandas as pd
import re

# --- FONCTIONS DE CALCUL ET EXTRACTION ---

def extract_matricule_ia(df_raw):
    """Cherche le mot 'MATRICULE' et extrait le nombre qui suit (ex: 00941)."""
    for row in df_raw.values:
        for cell in row:
            cell_str = str(cell).upper()
            if "MATRICULE" in cell_str:
                match = re.search(r'(\d+)', cell_str)
                if match:
                    return match.group(1)
    return "Inconnu"

def decimal_to_time(decimal_val):
    """Convertit 9.45 en '09:27'."""
    if pd.isna(decimal_val) or decimal_val == "" or decimal_val == 0:
        return "00:00"
    try:
        # On utilise le calcul exact pour éviter les décalages de secondes
        total_minutes = int(round(float(decimal_val) * 60))
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours:02d}:{minutes:02d}"
    except:
        return "00:00"

# --- CONFIGURATION DE L'INTERFACE ---

st.set_page_config(page_title="IA Pointage Alami", layout="wide")

st.title("📊 Générateur de Pointage Automatique")
st.markdown("Uploadez votre fichier Excel pour générer le tableau au format de la capture.")

file = st.file_uploader("Choisir le fichier Excel de pointage", type=['xlsx'])

if file:
    # 1. Extraction du matricule dans les premières lignes
    header_info = pd.read_excel(file, header=None).head(15)
    matricule_detecte = extract_matricule_ia(header_data=header_info)
    
    # 2. Lecture des données (Le tableau commence après l'en-tête)
    df = pd.read_excel(file, skiprows=11)
    
    # Nettoyage : on ne garde que les lignes où il y a une date
    df = df.dropna(subset=[df.columns[1]]) 

    # 3. Création du tableau final
    final_df = pd.DataFrame()
    final_df['matricule'] = [matricule_detecte] * len(df)
    final_df['nom'] = "ALAMI"
    final_df['prenom'] = "SAID"
    final_df['date'] = pd.to_datetime(df.iloc[:, 1]).dt.strftime('%d/%m/%Y')
    final_df["heure d'entrée"] = df.iloc[:, 2]
    final_df["heure de sortie"] = df.iloc[:, 3]
    
    # Calcul du temps effectué (Colonne index 7 dans votre fichier source)
    final_df["N° heures effectuées"] = df.iloc[:, 7].apply(decimal_to_time)

    # --- AFFICHAGE ---
    st.success(f"✅ Matricule détecté : **{matricule_detecte}**")
    
    # Affichage du tableau stylisé
    st.dataframe(final_df, use_container_width=True)

    # Bouton de téléchargement Excel
    csv = final_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Télécharger le résultat (CSV)",
        data=csv,
        file_name=f"Pointage_{matricule_detecte}.csv",
        mime="text/csv"
    )