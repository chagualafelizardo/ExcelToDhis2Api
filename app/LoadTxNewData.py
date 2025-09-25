import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from datetime import datetime
import logging
import json
import sys

# Configuração de logging (mantida)
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

# Configuração do DHIS2 (mantida)
DHIS2_CONFIG = {
    "base_url": "http://197.249.4.129:8088/api/29",
    "auth": HTTPBasicAuth("admin", "Chaguala.123"),
    "dataset_id": "bJi2QH24rm5",
    "org_unit": "QSxnM0virqc",
    "timeout": 30
}

# Mapeamento ajustado para sua estrutura (agora usando nomes de colunas)
EXCEL_MAPPING = {
    "period_col": "Reporting_Period",  # Nome da coluna do período
    "org_unit_code_col": "DHIS2 Organization Unit. CODE",  # Nome da coluna da unidade organizacional
    "data_elements": {
        # Indicador: CT_TX_NEW Unknown CD4 (ID: JLS7gzuchtM)
        # Male
        "ZY2f7vnLoiw": {
            "excel_col": "<1",
            "category_option_combo": "HllvX50cXC0",
            "attribute_option_combo": "HllvX50cXC0"
        }
        # ,"gQkhTd0IU8C": {
        #     "excel_col": "1-4",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"dMN8MXwN1Ue": {
        #     "excel_col": "5-9",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"RDukOhwPcd5": {
        #     "excel_col": "10-14",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"paI8UMgu8Dc": {
        #     "excel_col": "15-19",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"Z3rjANi4vnx": {
        #     "excel_col": "20-24",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"DTyNTfND4d3": {
        #     "excel_col": "25-29",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"mZwS5pdEsWR": {
        #     "excel_col": "30-34",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"zkgLpu4rYLt": {
        #     "excel_col": "35-39",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"x3aCdOTHlJX": {
        #     "excel_col": "40-44",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"a99LnnfNOhU": {
        #     "excel_col": "45-49",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"Ou2VmGYrWh5": {
        #     "excel_col": "50-54",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"HJZA3asMJNd": {
        #     "excel_col": "55-59",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"I1klmlLg6IF": {
        #     "excel_col": "60-64",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"yMoj8TQcscD": {
        #     "excel_col": ">=65",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"zJ4rbwr8Tff": {
        #     "excel_col": "unknown age",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # }
        ,
        # Indicador: CT_TX_NEW Unknown CD4 (ID: JLS7gzuchtM)
        # Female
        "ZY2f7vnLoiw": {
            "excel_col": "<1",
            "category_option_combo": "HllvX50cXC0",
            "attribute_option_combo": "HllvX50cXC0"
        }
        # ,"SvC379cWcbY": {
        #     "excel_col": "1-4",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"mJcDyx94OPv": {
        #     "excel_col": "5-9",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"NuasfnIWt79": {
        #     "excel_col": "10-14",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"YTCBeGd4gt5": {
        #     "excel_col": "15-19",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"fWcgmXfWddJ": {
        #     "excel_col": "20-24",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"T3wy1NMDAvT": {
        #     "excel_col": "25-29",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"PY2AMs1iAmr": {
        #     "excel_col": "30-34",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"lqHRZ1wflXF": {
        #     "excel_col": "35-39",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"uiqEPuCZLhb": {
        #     "excel_col": "40-44",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"LzOHrf1nbX3": {
        #     "excel_col": "45-49",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"a81Ipg9bIkQ": {
        #     "excel_col": "50-54",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"nnQEiziFLtG": {
        #     "excel_col": "55-59",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"T73PEkJIa53": {
        #     "excel_col": "60-64",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"lNtsXh4BcrU": {
        #     "excel_col": ">=65",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # },"K5hr1MZvK0L": {
        #     "excel_col": "unknown age",
        #     "category_option_combo": "HllvX50cXC0",
        #     "attribute_option_combo": "HllvX50cXC0"
        # }
        ,
        #
        "VPYqcEW8shs": {
            "excel_col": "Breastfeeding",
            "category_option_combo": "HllvX50cXC0",
            "attribute_option_combo": "HllvX50cXC0"
        },
        "ZY2f7vnLoiw": {
            "excel_col": "People who inject drugs (PWID)",
            "category_option_combo": "HllvX50cXC0",
            "attribute_option_combo": "HllvX50cXC0"
        },
        "ZY2f7vnLoiw": {
            "excel_col": "Men who have sex with men (MSM)",
            "category_option_combo": "HllvX50cXC0",
            "attribute_option_combo": "HllvX50cXC0"
        },
        "ZY2f7vnLoiw": {
            "excel_col": "Female sex workers (FSW)",
            "category_option_combo": "HllvX50cXC0",
            "attribute_option_combo": "HllvX50cXC0"
        },
        "ZY2f7vnLoiw": {
            "excel_col": "People in prison and other closed settings",
            "category_option_combo": "HllvX50cXC0",
            "attribute_option_combo": "HllvX50cXC0"
        },
        "dmwUvF8zj6L": {
            "excel_col": "Data Check",
            "category_option_combo": "HllvX50cXC0",
            "attribute_option_combo": "HllvX50cXC0"
        }
    }
}

def load_excel_data(file_path):
    """Carrega dados do Excel usando a primeira linha como cabeçalho"""
    try:
        # Lê o Excel usando a primeira linha como cabeçalho
        df = pd.read_excel(file_path, header=0)
        
        if df.empty:
            logging.error("Planilha vazia")
            return None
        
        logging.info("Cabeçalhos encontrados:")
        logging.info(df.columns.tolist())
        
        return df
    except Exception as e:
        logging.error(f"Falha ao ler arquivo Excel: {str(e)}")
        return None

def prepare_dhis2_payload(df):
    """Prepara payload baseado na estrutura do Excel"""
    data_values = []
    
    # Verifica se temos dados
    if len(df) < 1:
        logging.error("Nenhuma linha de dados encontrada")
        return None
    
    # Pega o período da coluna especificada (usando o nome da coluna agora)
    period = str(df.iloc[0][EXCEL_MAPPING["period_col"]]) if pd.notna(df.iloc[0][EXCEL_MAPPING["period_col"]]) else datetime.now().strftime("%Y%m")
    
    # Processa cada dataElement configurado
    for de_id, mapping in EXCEL_MAPPING["data_elements"].items():
        col_name = mapping["excel_col"]
        
        if col_name not in df.columns:
            logging.warning(f"Coluna '{col_name}' não encontrada no DataFrame")
            continue
            
        value = df.iloc[0][col_name]
        
        if pd.isna(value):
            logging.warning(f"Valor ausente para dataElement {de_id} (coluna: {col_name})")
            continue
            
        try:
            # Converte para inteiro (remove decimais se for float)
            int_value = int(float(value)) if '.' in str(value) else int(value)
            
            data_values.append({
                "dataElement": de_id,
                "categoryOptionCombo": mapping["category_option_combo"],
                "attributeOptionCombo": mapping["attribute_option_combo"],
                "value": str(int_value)
            })
            logging.info(f"Processado: {col_name} → {de_id} = {int_value}")
        except (ValueError, TypeError) as e:
            logging.error(f"Valor inválido na coluna {col_name}: {value} ({str(e)})")
    
    if not data_values:
        logging.error("Nenhum dado válido preparado")
        return None
    
    return {
        "dataSet": DHIS2_CONFIG["dataset_id"],
        "completeDate": datetime.now().strftime("%Y-%m-%d"),
        "period": period,
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
        
        if response.status_code in {200, 201, 204}:
            try:
                result = response.json()
                if result.get("status") == "SUCCESS":
                    logging.info("✅ Dados enviados com sucesso!")
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
            "period": datetime.now().strftime("%Y%m")
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