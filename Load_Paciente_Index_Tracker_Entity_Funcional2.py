import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from datetime import datetime
import logging
import json
import sys
import uuid
import re
import unicodedata
import os
import glob

# Configuração de logging
def setup_logging():
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler('dhis2_tracker_integration.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


def normalize_text(text):
    """Remove acentos e coloca em minúsculas"""
    if not isinstance(text, str):
        return text
    nfkd = unicodedata.normalize('NFKD', text)
    no_accents = ''.join([c for c in nfkd if not unicodedata.combining(c)])
    return no_accents.lower().strip()

# Configuração do DHIS2
DHIS2_CONFIG = {
    "base_url": "http://197.249.4.129:8088/api/29",
    "auth": HTTPBasicAuth("admin", "Chaguala.123"),
    "program_id": "ll4LqMAHvEj",
    "tracked_entity_type": "I1P2bB5OLA9",
    "org_unit": "P3rkRiVWkDI",
    "timeout": 30
}

# Mapeamento de colunas do Excel para data elements
EXCEL_MAPPING = {
    "data_elements": {
        "tzslnQzuJX6": "NID",
        "mCfuxVjtwiS": "Nome do paciente",
        "MMQCeRRvRWt": "Idade",
        "jCdc85LhrtI": "Sexo",
        "JQRlmMxqcDQ": "Data Inicio",
        "MkF7LIFtFVW": "Regime Actual",
        "WWuCIxXXQZZ": "Absoluto",
        "MCw1oDQS5rB": "Percentual",
        "PLpDTb2fqOU": "Data da Proxima Consulta",
        "cnaROiAM1wn": "Ult. Leva",
        "GbGx3hyO2Rq": "Prox. Leva",
        "du5ctoPYFMF": "Dias de Falta",
        "Gn8SvTBWt9K": "Estadio OMS",
        "N3rShDVce0v": "IMC",
        "DzBXLWorexg": "Estado",
        "G1KtcQ0iUbK":"Localidade",
        "yEv5ZJn96UW":"Bairro",
        "TFYug7el9FO":"Referência",
        "tvaZ64Xopsh":"Contacto do Paciente",
        "yDQXG24myq0":"Nome do Confidente",
        "DHYuuFG7EgE":"Contacto do Confidente",
        "phMI3vvzCz6":"Tipo Paciente"
    }
}

# MAPEAMENTO CORRETO BASEADO NO DEBUG
OPTION_SET_MAPPING = {
    "jCdc85LhrtI": {  # Sexo - Option Set: vNW6AlR0bIz
        "M": "Masculino",      # "M" → Código "Masculino"
        "F": "Feminino",       # "F" → Código "Feminino" 
        "Male": "Masculino",   # "Male" → Código "Masculino"
        "Female": "Feminino",  # "Female" → Código "Feminino"
        "Masculino": "Masculino",  # "Masculino" → Código "Masculino"
        "Feminino": "Feminino",    # "Feminino" → Código "Feminino"
        "m": "Masculino",      # "m" → Código "Masculino"
        "f": "Feminino"        # "f" → Código "Feminino"
    },
    "Gn8SvTBWt9K": {  # Estadio OMS - Option Set: YNBMqVtrSvi
        "Estadio OMS I": "i",      # "Estadio OMS I" → Código "i"
        "Estadio OMS II": "ii",    # "Estadio OMS II" → Código "ii"
        "Estadio OMS III": "iii",  # "Estadio OMS III" → Código "iii"
        "Estadio OMS IV": "iv",    # "Estadio OMS IV" → Código "iv"
        "OMS I": "i",              # "OMS I" → Código "i"
        "OMS II": "ii",            # "OMS II" → Código "ii"
        "OMS III": "iii",          # "OMS III" → Código "iii"
        "OMS IV": "iv",            # "OMS IV" → Código "iv"
        "I": "i",                  # "I" → Código "i"
        "II": "ii",                # "II" → Código "ii"
        "III": "iii",              # "III" → Código "iii"
        "IV": "iv",                # "IV" → Código "iv"
        "i": "i",                  # "i" → Código "i"
        "ii": "ii",                # "ii" → Código "ii"
        "iii": "iii",              # "iii" → Código "iii"
        "iv": "iv"                 # "iv" → Código "iv"
    },
    "DzBXLWorexg":{
        "yyUuaBrXlAZ":"Abandononaonotificado",
        "d7b7j9SNwaf":"Abandononaonotificado",
        "vdOc3pNXu2O": "ABANDONO",
        "kTWUGlA949C": "TRANSFERIDO PARA",
        "Ri42R0ht3DD": "TRANSFERIDO DE",
        "bcRzjwqiIx6":"abandonoutratamento",
        "N0nFExgghmv":"obito",
        "A8xl20xCA6d":"AutoTransferenciaPara",
        "k0U2yJfFkeA":"EfeitosSecundarios",
        "maPHhCdVZyX":"EncaminhadoParaUS",
        "etLnTRoIu6v":"EncaminhadoGrupoApoio",
        "uDlWltVacp4":"EsqueceuData",
        "SP5ujfjv97i":"EstaDoente",
        "CAID4EurlDX":"MauAtendimento",
        "BFl6zeL2C0k":"FamiliarReferidoUS",
        "fcg1HvVenPB":"MedoProvedorSaude",
        "XrQkyqxv0YN":"NaoAceitouRegressarUS",
        "B1G89zToudV":"NaoEncontrado",
        "TOYiyaapN8o":"ProblemaTransporte",
        "DWfkmNEceZe":"RetornouUnidadeSanitaria",
        "jMGh7bsJU9m":"Trabalho",
        "hOfTmKTYWFJ":"EstavaMachamba",
        "S9E5Ru0KG87":"SenteBem",
        "YjsIyb5wpMQ":"NaoSenteBem",
        "a21U7WtTmcL":"TransferidoParaOutraUS",
        "Mti9DO3n3rL":"TratamentoTradicional",
    }
}

def load_excel_data(file_path):
    """Carrega dados do Excel"""
    try:
        df = pd.read_excel(file_path, header=5)
        if df.empty:
            logging.error("Planilha vazia")
            return None
        logging.info(f"Encontradas {len(df)} linhas de dados")
        logging.info(f"Colunas: {df.columns.tolist()}")
        return df
    except Exception as e:
        logging.error(f"Falha ao ler arquivo Excel: {str(e)}")
        return None

def clean_date_value(value):
    """Limpa e formata valores de data para YYYY-MM-DD"""
    if pd.isna(value):
        return None
    
    try:
        if isinstance(value, (pd.Timestamp, datetime)):
            return value.strftime("%Y-%m-%d")
        elif isinstance(value, str):
            if ' ' in value:
                value = value.split(' ')[0]
            if re.match(r'\d{4}-\d{2}-\d{2}', value):
                return value
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%m-%d-%Y"]:
                try:
                    dt = datetime.strptime(value, fmt)
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
            return value.strip()
        elif isinstance(value, (int, float)):
            try:
                base_date = datetime(1899, 12, 30)
                delta = pd.Timedelta(days=float(value))
                result_date = base_date + delta
                return result_date.strftime("%Y-%m-%d")
            except:
                return str(value)
        else:
            return str(value).strip()
    except Exception as e:
        logging.warning(f"Erro ao limpar valor {value}: {str(e)}")
        return str(value).strip()

def map_option_value(attribute_id, value):
    """Mapeia valores para os códigos corretos do DHIS2"""
    if pd.isna(value) or value == "":
        return None
        
    value_str = str(value).strip()
    
    # Verifica se há mapeamento para este atributo
    if attribute_id in OPTION_SET_MAPPING:
        mapping = OPTION_SET_MAPPING[attribute_id]
        
        # Procura correspondência exata
        if value_str in mapping:
            return mapping[value_str]
        
        # Procura correspondência case insensitive
        for key, mapped_value in mapping.items():
            if key.lower() == value_str.lower():
                return mapped_value
        
        logging.warning(f"Valor '{value_str}' não mapeado para atributo {attribute_id}")
    
    return value_str

def validate_dhis2_config():
    """Valida a configuração do DHIS2"""
    endpoints_to_check = [
        f"trackedEntityTypes/{DHIS2_CONFIG['tracked_entity_type']}",
        f"programs/{DHIS2_CONFIG['program_id']}",
        f"organisationUnits/{DHIS2_CONFIG['org_unit']}"
    ]
    
    for endpoint in endpoints_to_check:
        try:
            url = f"{DHIS2_CONFIG['base_url']}/{endpoint}"
            response = requests.get(url, auth=DHIS2_CONFIG["auth"], timeout=10)
            if response.status_code != 200:
                logging.error(f"❌ Recurso não encontrado: {endpoint}")
                logging.error(f"Resposta: {response.text}")
                return False
            else:
                logging.info(f"✅ Recurso válido: {endpoint}")
        except Exception as e:
            logging.error(f"❌ Erro ao validar {endpoint}: {str(e)}")
            return False
    return True

def prepare_tracker_payload(df):
    """Prepara payload para programa tracker"""
    tracked_entities = []
    
    for idx, row in df.iterrows():
        nid_value = row.get("NID")
        if pd.isna(nid_value) or str(nid_value).strip() == "":
            logging.warning(f"Linha {idx+7}: NID vazio, pulando...")
            continue
            
        tracked_entity_data = {
            "trackedEntityInstance": str(uuid.uuid4()),
            "trackedEntityType": DHIS2_CONFIG["tracked_entity_type"],
            "orgUnit": DHIS2_CONFIG["org_unit"],
            "attributes": [],
            "enrollments": [{
                "enrollment": str(uuid.uuid4()),
                "program": DHIS2_CONFIG["program_id"],
                "orgUnit": DHIS2_CONFIG["org_unit"],
                "enrollmentDate": datetime.now().strftime("%Y-%m-%d"),
                "incidentDate": datetime.now().strftime("%Y-%m-%d"),
                "status": "ACTIVE",
                "events": []
            }]
        }
        
        # Adicionar atributos
        for de_id, col_name in EXCEL_MAPPING["data_elements"].items():
            if col_name not in df.columns:
                continue

            value = row[col_name]
            if pd.isna(value):
                continue

            # Processa valores especiais
            if any(keyword in col_name.lower() for keyword in ['data', 'date', 'leva', 'inicio', 'proxima', 'ultimo']):
                value_str = clean_date_value(value)
            else:
                # Mapeia valores para option sets
                value_str = map_option_value(de_id, value)
                
                # Se ainda for string, limpa
                if isinstance(value_str, str):
                    value_str = value_str.strip()

            tracked_entity_data["attributes"].append({
                "attribute": de_id,
                "value": value_str
            })
            
            logging.info(f"Linha {idx+7}: {col_name} → '{value}' → '{value_str}'")
        
        tracked_entities.append(tracked_entity_data)
        # if len(tracked_entities) >= 2:  # Limita a 2 registros para teste
        #     break
    
    return {"trackedEntityInstances": tracked_entities}

def send_to_dhis2_tracker(payload):
    """Envia dados para DHIS2"""
    try:
        url = f"{DHIS2_CONFIG['base_url']}/trackedEntityInstances"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        logging.info(f"Enviando {len(payload['trackedEntityInstances'])} registros para DHIS2")
        
        response = requests.post(
            url,
            json=payload,
            auth=DHIS2_CONFIG["auth"],
            timeout=DHIS2_CONFIG["timeout"],
            headers=headers,
            params={"async": "false"}
        )
        
        logging.info(f"Status Code: {response.status_code}")
        
        if response.status_code in {200, 201}:
            logging.info("✅ Sucesso!")
            try:
                result = response.json()
                logging.info(f"Importados: {result['response']['imported']}")
                logging.info(f"Atualizados: {result['response']['updated']}")
                logging.info(f"Ignorados: {result['response']['ignored']}")
            except:
                pass
            return True, response.text
        else:
            logging.error(f"❌ Erro HTTP {response.status_code}")
            logging.error(f"Resposta: {response.text}")
            
            # Tenta obter mais detalhes do erro
            try:
                error_data = response.json()
                if "response" in error_data and "importSummaries" in error_data["response"]:
                    for summary in error_data["response"]["importSummaries"]:
                        if "conflicts" in summary:
                            for conflict in summary["conflicts"]:
                                logging.error(f"Conflito: {conflict}")
            except:
                pass
                
            return False, response.text
            
    except Exception as e:
        logging.error(f"❌ Erro: {str(e)}")
        return False, str(e)

def main():
    setup_logging()
    # excel_file = r"C:\Users\Felizardo Chaguala\Desktop\dhis2\data\paciente_atualmente_tarv.xls"
    # ======
    data_directory = r"C:\Users\Felizardo Chaguala\Desktop\dhis2\data"
    excel_files = glob.glob(os.path.join(data_directory, "*.xls*"))  # pega .xls e .xlsx
    excel_files += glob.glob(os.path.join(data_directory, "*.csv"))   # adiciona .csv
    
    if not excel_files:
        logging.warning("⚠️ Nenhum ficheiro Excel encontrado no diretório.")
        sys.exit(0)

    for excel_file in excel_files:
        logging.info(f"📄 Processando ficheiro: {excel_file}")

        # Carregar dados
        df = load_excel_data(excel_file)
        if df is None:
            logging.warning(f"❌ Falha ao carregar: {excel_file}")
            continue

        # Preparar e enviar
        payload = prepare_tracker_payload(df)
        if not payload or "trackedEntityInstances" not in payload or not payload["trackedEntityInstances"]:
            logging.warning(f"⚠️ Nenhum dado válido para enviar: {excel_file}")
            continue

        logging.info(f"Preparados {len(payload['trackedEntityInstances'])} registros")
        success, response = send_to_dhis2_tracker(payload)

        if success:
            logging.info("✅ Enviado com sucesso!")
        else:
            logging.error("❌ Falha ao enviar dados")

        # Após processamento, apagar o ficheiro
        try:
            os.remove(excel_file)
            logging.info(f"🗑️ Ficheiro apagado: {excel_file}")
        except Exception as e:
            logging.warning(f"⚠️ Não foi possível apagar o ficheiro {excel_file}: {e}")

    # ======

    logging.info("=== Iniciando processo de integração TRACKER ===")

    # 1. Validar configuração do DHIS2
    logging.info("Validando configuração do DHIS2...")
    if not validate_dhis2_config():
        logging.error("Configuração do DHIS2 inválida")
        sys.exit(1)

    # 2. Carregar dados do Excel
    df = load_excel_data(excel_file)
    if df is None:
        sys.exit(1)

    # 3. Processar e enviar dados
    payload = prepare_tracker_payload(df)
    if not payload or "trackedEntityInstances" not in payload or not payload["trackedEntityInstances"]:
        logging.error("Nenhum dado válido para enviar")
        sys.exit(1)

    logging.info(f"Preparados {len(payload['trackedEntityInstances'])} registros")
    success, response = send_to_dhis2_tracker(payload)
    
    if success:
        logging.info("✅ Processo concluído com sucesso!")
    else:
        logging.error("❌ Falha no processo de integração")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()