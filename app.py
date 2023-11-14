import streamlit as st
import pandas as pd
import requests
import os
import zipfile
import shutil

def cargar_excel(uploaded_file):
    return pd.read_excel(uploaded_file)

def descargar_archivo(url, index, total, errores, progreso_texto, folder='descargas'):
    if not os.path.exists(folder):
        os.makedirs(folder)

    enlaces = url.split(', ')
    descargado = False
    for enlace in enlaces:
        response = requests.get(enlace)
        if response.status_code == 200:
            nombre_archivo = enlace.split('/')[-1]
            ruta_completa = os.path.join(folder, nombre_archivo)
            with open(ruta_completa, 'wb') as f:
                f.write(response.content)
            descargado = True
        else:
            errores.append((index+1, enlace))

    if descargado:
        progreso_texto.text(f'Descargado: {index+1} de {total}')

def crear_zip(folder):
    zip_filename = f"{folder}.zip"
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for root, dirs, files in os.walk(folder):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(folder, '..')))
    return zip_filename

def main():
    st.title("Descargador de Archivos desde Excel")
    
    uploaded_file = st.file_uploader("Elige un archivo Excel", type=['xlsx'])

    if uploaded_file is not None:
        df = cargar_excel(uploaded_file)
        campo_links = st.text_input("Nombre de la columna que contiene los links:")
        
        if campo_links:
            if campo_links not in df.columns:
                st.error("La columna especificada no existe en el archivo Excel.")
            else:
                total = len(df)
                errores = []
                progreso_texto = st.empty()
                folder = 'descargas'

                for index, link in enumerate(df[campo_links].dropna()):
                    descargar_archivo(link, index, total, errores, progreso_texto, folder)

                progreso_texto.empty()
                st.success(f'Descargas completadas. Total de errores: {len(errores)}')

                # Crear archivo zip
                zip_filename = crear_zip(folder)
                with open(zip_filename, "rb") as file:
                    btn = st.download_button(
                        label="Descargar archivo ZIP",
                        data=file,
                        file_name=zip_filename,
                        mime="application/zip"
                    )

                if errores:
                    st.error("Errores encontrados en las siguientes líneas y enlaces:")
                    for error in errores:
                        st.write(f'Línea {error[0]}: {error[1]}')

if __name__ == '__main__':
    main()