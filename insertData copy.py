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

# Configurações DHIS2
DHIS2_CONFIG = {
    "base_url": "http://197.249.4.129:8088/api/29",
    "auth": HTTPBasicAuth("admin", "Chaguala.123"),
    "dataset_id": "bJi2QH24rm5",  # Dataset TX_NEW (CT_TX_NEW CD4<200)
    "org_unit": "QSxnM0virqc"
}

# IDs dos dataElements para faixas etárias específicas
DATA_ELEMENT_MAPPING = {
    "5-9": {
        "dataElement": "rZtFk3z5o9X",
        "combo": "ZY2f7vnLoiw"
    },
    "10-14": {
        "dataElement": "rZtFk3z5o9X",
        "combo": "OZvd6zClIQV"
    },
    "15-19": {
        "dataElement": "rZtFk3z5o9X",
        "combo": "B32kr1PRiNS"
    }
    # ... adicione outras faixas etárias conforme necessário
}

def send_data_to_dhis2(data_values):
    """Envia os dados para o DHIS2 via API"""
    # Ajuste period para o mês atual no formato YYYYMM
    # period = datetime.now().strftime("%Y%m") # Ele vai buscar a data atual, vamos colocar uma data pre-definida
    period = "202501" # Ele vai buscar a data atual, vamos colocar uma data pre-definida
    
    payload = {
        "dataSet": DHIS2_CONFIG["dataset_id"],
        "completeDate": datetime.now().strftime("%Y-%m-%d"),
        "period": period,
        "orgUnit": DHIS2_CONFIG["org_unit"],
        "dataValues": data_values
    }
    
    logging.info(f"Payload para envio:\n{json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{DHIS2_CONFIG['base_url']}/dataValueSets",
            json=payload,
            auth=DHIS2_CONFIG["auth"],
            timeout=10
        )
        if response.status_code in [200, 201, 204]:
            logging.info(f"Dados enviados com sucesso. Status: {response.status_code}")
            logging.info(f"Resposta da API: {response.text}")
            return True, response.text
        else:
            logging.error(f"Erro no envio. Status: {response.status_code}, Response: {response.text}")
            return False, response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao enviar dados: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logging.error(f"Resposta do servidor: {e.response.text}")
        return False, None

def prepare_data_from_excel(file_path):
    """Extrai os dados do Excel com base nas colunas definidas no mapeamento"""
    try:
        df = pd.read_excel(file_path)
        data_values = []

        for age_group, de_info in DATA_ELEMENT_MAPPING.items():
            if age_group in df.columns:
                value = df[age_group].iloc[0]
                if pd.notna(value):
                    try:
                        val = int(value)
                        data_values.append({
                            "dataElement": de_info["dataElement"],
                            "categoryOptionCombo": de_info["combo"],
                            "value": str(val)
                        })
                    except ValueError:
                        logging.warning(f"Valor inválido para '{age_group}': {value}")
        
        return data_values
    except Exception as e:
        logging.error(f"Erro ao processar arquivo Excel: {str(e)}")
        return None


if __name__ == "__main__":
    excel_file = r"C:\Users\Felizardo Chaguala\Desktop\dhis2\dados.xlsx"
    
    data_values = prepare_data_from_excel(excel_file)
    
    if data_values:
        logging.info(f"Preparando para enviar {len(data_values)} valores para o DHIS2...")
        success, response = send_data_to_dhis2(data_values)
        
        if success:
            logging.info("Dados enviados com sucesso!")
            logging.debug(f"Resposta do DHIS2: {response}")
        else:
            logging.error("Falha ao enviar dados para o DHIS2.")
    else:
        logging.error("Nenhum dado válido encontrado para envio.")
