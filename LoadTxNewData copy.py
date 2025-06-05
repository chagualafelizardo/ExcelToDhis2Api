import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from datetime import datetime
import logging
import json

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dhis2_integration.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Configuração do DHIS2
DHIS2_CONFIG = {
    "base_url": "http://197.249.4.129:8088/api/29",
    "auth": HTTPBasicAuth("admin", "Chaguala.123"),
    "dataset_id": "bJi2QH24rm5",
    "org_unit": "QSxnM0virqc"
}

# Mapeamento completo e corrigido
COLUMN_MAPPING = {
    "CT_TX_NEW - Breastfeeding": "VPYqcEW8shs",
    # "Men who have sex with men (MSM)": "M4p3BYCSG4x",
    # "Female sex workers (FSW)": "SCibQDr9Tb1",
    # "People in prison and other closed settings": "ypwYDGkwYiR"  # ATENÇÃO: Mesmo ID que MSM - confirmar se está correto
}

CATEGORY_COMBO_ID = "HllvX50cXC0"
ATTRIBUTE_COMBO_ID = "HllvX50cXC0"

def prepare_data_from_excel(file_path):
    try:
        # Lê o Excel (cabeçalho na primeira linha, dados na segunda)
        df = pd.read_excel(file_path)
        
        logging.info("Dados lidos do Excel:")
        logging.info(df.to_string())
        
        data_values = []
        
        for excel_col, data_element in COLUMN_MAPPING.items():
            if excel_col in df.columns:
                value = df[excel_col].iloc[0]  # Pega o valor da primeira linha de dados
                if pd.notna(value):
                    try:
                        data_values.append({
                            "dataElement": data_element,
                            "categoryOptionCombo": CATEGORY_COMBO_ID,
                            "attributeOptionCombo": ATTRIBUTE_COMBO_ID,
                            "value": str(int(value))
                        })
                        logging.info(f"Processado: {excel_col} = {value}")
                    except (ValueError, TypeError) as e:
                        logging.error(f"Valor não numérico em '{excel_col}': {value}")
                else:
                    logging.warning(f"Valor vazio/NAN em '{excel_col}'")
            else:
                logging.error(f"Coluna não encontrada: '{excel_col}'")
        
        if not data_values:
            logging.error("Nenhum dado válido encontrado na planilha")
            return None
            
        return data_values
    
    except Exception as e:
        logging.error(f"Erro fatal ao ler Excel: {str(e)}", exc_info=True)
        return None

def send_data_to_dhis2(data_values):
    if not data_values:
        return False, "No data to send"
    
    period = '202501'
    # period = datetime.now().strftime("%Y%m")  # Formato YYYYMM
    
    payload = {
        "dataSet": DHIS2_CONFIG["dataset_id"],
        "completeDate": datetime.now().strftime("%Y-%m-%d"),
        "period": period,
        "orgUnit": DHIS2_CONFIG["org_unit"],
        "dataValues": data_values
    }
    
    logging.info("Enviando payload para DHIS2:")
    logging.info(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(
            f"{DHIS2_CONFIG['base_url']}/dataValueSets",
            json=payload,
            auth=DHIS2_CONFIG["auth"],
            timeout=30
        )
        
        if response.status_code in [200, 201, 204]:
            logging.info(f"Sucesso! Status: {response.status_code}")
            return True, response.text
        else:
            logging.error(f"Erro na API. Status: {response.status_code}\nResposta: {response.text}")
            return False, response.text
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Falha na conexão: {str(e)}")
        return False, str(e)

if __name__ == "__main__":
    excel_file = r"C:\Users\Felizardo Chaguala\Desktop\dhis2\data\data.xlsx"
    
    logging.info(f"Iniciando processamento do arquivo: {excel_file}")
    data_values = prepare_data_from_excel(excel_file)
    
    if data_values:
        logging.info(f"Enviando {len(data_values)} valores para DHIS2...")
        success, response = send_data_to_dhis2(data_values)
        
        if success:
            logging.info("✅ Dados enviados com sucesso!")
            logging.info(f"Resposta do DHIS2: {response}")
        else:
            logging.error("❌ Falha no envio!")
            logging.error(f"Detalhes do erro: {response}")
    else:
        logging.error("❌ Nenhum dado válido para enviar")