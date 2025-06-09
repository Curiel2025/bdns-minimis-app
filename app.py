import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

st.set_page_config(page_title="Buscador Minimis BDNS", layout="centered")
st.title("🔍 Buscador de Ayudas de Minimis - BDNS")

# Campo de entrada para CIFs
cifs_input = st.text_area("Pega aquí los CIFs (uno por línea):", height=200)

if st.button("Buscar ayudas de minimis") and cifs_input:
    with st.spinner("Consultando BDNS..."):

        def get_driver():
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--start-maximized")
            options.add_argument("--window-size=1920,1080")
            service = Service()
            return webdriver.Chrome(service=service, options=options)

        def buscar_cif_bdns(cif):
            driver = get_driver()
            url = "https://www.infosubvenciones.es/bdnstrans/GE/es/convBusqByCIF"
            driver.get(url)
            time.sleep(2)
            resultados = []
            try:
                input_cif = driver.find_element(By.ID, "cif")
                input_cif.send_keys(cif)
                driver.find_element(By.ID, "btnBuscar").click()
                time.sleep(2)
                filas = driver.find_elements(By.CSS_SELECTOR, "#resultadosBusqueda tbody tr")
                for fila in filas:
                    cols = fila.find_elements(By.TAG_NAME, "td")
                    if len(cols) >= 5:
                        resultados.append({
                            "CIF": cif,
                            "Nombre": cols[0].text,
                            "Importe": cols[2].text,
                            "Fecha": cols[3].text,
                            "Convocatoria": cols[1].text,
                            "Concedente": cols[4].text,
                            "Minimis": "minimis" in cols[1].text.lower()
                        })
            except Exception as e:
                resultados.append({
                    "CIF": cif,
                    "Nombre": "ERROR",
                    "Importe": "-",
                    "Fecha": "-",
                    "Convocatoria": str(e),
                    "Concedente": "-",
                    "Minimis": False
                })
            driver.quit()
            return resultados

        lista_cifs = [c.strip() for c in cifs_input.strip().splitlines() if c.strip()]
        datos = []
        for cif in lista_cifs:
            datos.extend(buscar_cif_bdns(cif))

        df = pd.DataFrame(datos)
        st.success("Consulta finalizada ✅")
        st.dataframe(df)

        st.download_button(
            label="📥 Descargar Excel",
            data=df.to_excel(index=False, engine='openpyxl'),
            file_name="ayudas_minimis.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
