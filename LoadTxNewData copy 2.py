import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from datetime import datetime
import logging
import json
import sys

# Configuração avançada de logging
def setup_logging():
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler('dhis2_integration.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

# Configuração do DHIS2 (considere mover para um arquivo de configuração externo)
DHIS2_CONFIG = {
    "base_url": "http://197.249.4.129:8088/api/29",
    "auth": HTTPBasicAuth("admin", "Chaguala.123"),
    "dataset_id": "bJi2QH24rm5",
    "org_unit": "QSxnM0virqc",
    "timeout": 30,
    "default_period": "202501"  # Pode ser alterado para datetime.now().strftime("%Y%m")
}

# Mapeamento de dados (pode ser externalizado para JSON/Excel)
DATA_ELEMENT_MAPPING = {
    "CT_TX_NEW - Breastfeeding": {
        "id": "VPYqcEW8shs",
        "category_option_combo": "HllvX50cXC0",
        "attribute_option_combo": "HllvX50cXC0"
    },
    # Exemplo de outros mapeamentos:
    # "Novo Indicador": {
    #     "id": "ID_DO_DATAELEMENT",
    #     "category_option_combo": "COC_ID",
    #     "attribute_option_combo": "AOC_ID"
    # }
}

def load_excel_data(file_path):
    """Carrega e valida os dados do Excel"""
    try:
        df = pd.read_excel(file_path)
        if df.empty:
            logging.error("Planilha vazia")
            return None
        
        logging.info("Dados carregados do Excel:")
        logging.info(df.to_markdown(tablefmt="grid"))
        
        return df
    except Exception as e:
        logging.error(f"Falha ao ler arquivo Excel: {str(e)}")
        return None

def prepare_dhis2_payload(df):
    """Prepara o payload para o DHIS2 baseado nos dados do Excel"""
    data_values = []
    
    for col_name, mapping in DATA_ELEMENT_MAPPING.items():
        if col_name in df.columns:
            value = df[col_name].iloc[0]
            
            if pd.isna(value):
                logging.warning(f"Valor ausente para '{col_name}'")
                continue
                
            try:
                data_values.append({
                    "dataElement": mapping["id"],
                    "categoryOptionCombo": mapping["category_option_combo"],
                    "attributeOptionCombo": mapping["attribute_option_combo"],
                    "value": str(int(value))
                })
                logging.info(f"Dado preparado: {col_name} → {value}")
            except (ValueError, TypeError) as e:
                logging.error(f"Valor inválido em '{col_name}': {value} ({str(e)})")
        else:
            logging.warning(f"Coluna não encontrada: '{col_name}'")
    
    if not data_values:
        logging.error("Nenhum dado válido preparado")
        return None
    
    return {
        "dataSet": DHIS2_CONFIG["dataset_id"],
        "completeDate": datetime.now().strftime("%Y-%m-%d"),
        "period": DHIS2_CONFIG["default_period"],
        "orgUnit": DHIS2_CONFIG["org_unit"],
        "dataValues": data_values
    }

def send_to_dhis2(payload):
    """Envia dados para o DHIS2"""
    try:
        url = f"{DHIS2_CONFIG['base_url']}/dataValueSets"
        response = requests.post(
            url,
            json=payload,
            auth=DHIS2_CONFIG["auth"],
            timeout=DHIS2_CONFIG["timeout"]
        )
        
        logging.debug(f"Resposta completa: {response.text}")
        
        if response.status_code in {200, 201, 204}:
            try:
                result = response.json()
                if result.get("status") == "SUCCESS":
                    logging.info("✅ Dados enviados com sucesso!")
                    logging.info(f"Resumo: {result.get('description')}")
                    logging.info(f"Estatísticas: {json.dumps(result.get('importCount'), indent=2)}")
                    return True, result
                else:
                    logging.error("⚠️ Envio completo mas com avisos:")
                    for conflict in result.get("conflicts", []):
                        logging.error(f"Conflito: {conflict.get('value')}")
                    return False, result
            except ValueError:
                return True, response.text
        else:
            logging.error(f"❌ Erro HTTP {response.status_code}")
            logging.error(f"Resposta: {response.text}")
            return False, response.text
            
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Erro de conexão: {str(e)}")
        return False, str(e)

def verify_data_in_dhis2():
    """Verifica se os dados foram armazenados corretamente"""
    try:
        params = {
            "dataSet": DHIS2_CONFIG["dataset_id"],
            "orgUnit": DHIS2_CONFIG["org_unit"],
            "period": DHIS2_CONFIG["default_period"]
        }
        
        response = requests.get(
            f"{DHIS2_CONFIG['base_url']}/dataValueSets",
            params=params,
            auth=DHIS2_CONFIG["auth"],
            timeout=DHIS2_CONFIG["timeout"]
        )
        
        if response.status_code == 200:
            logging.info("Verificação de dados no DHIS2:")
            logging.info(json.dumps(response.json(), indent=2))
            return True
        else:
            logging.error("Falha na verificação")
            return False
    except Exception as e:
        logging.error(f"Erro na verificação: {str(e)}")
        return False

def main():
    setup_logging()
    excel_file = r"C:\Users\Felizardo Chaguala\Desktop\dhis2\data\data.xlsx"
    
    logging.info("=== Iniciando processo de integração ===")
    
    # Passo 1: Carregar dados
    df = load_excel_data(excel_file)
    if df is None:
        sys.exit(1)
    
    # Passo 2: Preparar payload
    payload = prepare_dhis2_payload(df)
    if payload is None:
        sys.exit(1)
    
    logging.info("Payload preparado:")
    logging.info(json.dumps(payload, indent=2))
    
    # Passo 3: Enviar dados
    success, response = send_to_dhis2(payload)
    
    # Passo 4: Verificar (opcional)
    if success:
        verify_data_in_dhis2()
    
    logging.info("=== Processo concluído ===")
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()