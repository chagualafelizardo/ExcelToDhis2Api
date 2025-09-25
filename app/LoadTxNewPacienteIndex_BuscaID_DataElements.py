import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from datetime import datetime
import logging
import json
import sys
import uuid
import re

# Configuração de logging
def setup_logging():
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler('dhis2_debug.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

# Configuração do DHIS2
DHIS2_CONFIG = {
    "base_url": "http://197.249.4.129:8088/api/29",
    "auth": HTTPBasicAuth("admin", "Chaguala.123"),
    "program_id": "ll4LqMAHvEj",
    "tracked_entity_type": "I1P2bB5OLA9",
    "org_unit": "P3rkRiVWkDI",
    "timeout": 30
}

def debug_option_set_values():
    """Debug completo dos option sets e seus valores"""
    logging.info("=== DEBUG COMPLETO DOS OPTION SETS ===")
    
    # Option Set Sexo
    sex_option_set = get_option_set_details("vNW6AlR0bIz")
    if sex_option_set:
        logging.info(f"\n🔍 OPTION SET SEXO ({sex_option_set['name']}):")
        for option_name, option_code in sex_option_set['options'].items():
            logging.info(f"   '{option_name}' → '{option_code}'")
    else:
        logging.error("❌ Option Set Sexo não encontrado!")
    
    # Option Set Estadio OMS
    oms_option_set = get_option_set_details("YNBMqVtrSvi")
    if oms_option_set:
        logging.info(f"\n🔍 OPTION SET ESTADIO OMS ({oms_option_set['name']}):")
        for option_name, option_code in oms_option_set['options'].items():
            logging.info(f"   '{option_name}' → '{option_code}'")
    else:
        logging.error("❌ Option Set Estadio OMS não encontrado!")

    # Option Set Estado
    estado_option_set = get_option_set_details("dzgX0THTnVc")
    if estado_option_set:
        logging.info(f"\n🔍 OPTION SET ESTADO ({estado_option_set['name']}):")
        for option_name, option_code in estado_option_set['options'].items():
            logging.info(f"   '{option_name}' → '{option_code}'")
    else:
        logging.error("❌ Option Set Estado não encontrado!")

def get_option_set_details(option_set_id):
    """Obtém detalhes completos de um option set"""
    try:
        url = f"{DHIS2_CONFIG['base_url']}/optionSets/{option_set_id}?fields=id,name,options[code,name,id]"
        response = requests.get(url, auth=DHIS2_CONFIG["auth"], timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            options = {}
            for option in data.get('options', []):
                # Mapeia tanto por nome quanto por código para ambos os valores
                options[option['name']] = option['code']  # Nome → Código
                options[option['code']] = option['code']  # Código → Código
                options[str(option['id'])] = option['code']  # ID → Código
            
            return {
                'id': data['id'],
                'name': data['name'],
                'options': options
            }
        else:
            logging.error(f"Erro ao obter option set {option_set_id}: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Erro ao obter option set {option_set_id}: {str(e)}")
        return None

def test_single_value(attribute_id, value_to_test, option_set_id):
    """Testa um valor específico contra o option set"""
    option_set = get_option_set_details(option_set_id)
    if not option_set:
        return False, "Option set não encontrado"
    
    value_str = str(value_to_test).strip()
    options = option_set['options']
    
    logging.info(f"\n🧪 TESTANDO: '{value_str}' no option set {option_set['name']}")
    
    # Verifica todas as possibilidades
    if value_str in options:
        logging.info(f"✅ ENCONTRADO: '{value_str}' → '{options[value_str]}'")
        return True, options[value_str]
    
    # Verifica case insensitive
    for option_name, option_code in options.items():
        if option_name.lower() == value_str.lower():
            logging.info(f"✅ ENCONTRADO (case insensitive): '{value_str}' → '{option_code}'")
            return True, option_code
    
    logging.info(f"❌ NÃO ENCONTRADO: '{value_str}'")
    logging.info(f"   Opções disponíveis: {list(options.keys())}")
    return False, None

def test_all_possible_values():
    """Testa todos os valores possíveis"""
    logging.info("\n=== TESTANDO TODOS OS VALORES POSSÍVEIS ===")
    
    # Testar valores para Sexo
    sex_values_to_test = ["M", "F", "Male", "Female", "Masculino", "Feminino", "m", "f"]
    for value in sex_values_to_test:
        success, mapped_value = test_single_value("jCdc85LhrtI", value, "vNW6AlR0bIz")
    
    # Testar valores para Estadio OMS
    oms_values_to_test = ["Estadio OMS I", "Estadio OMS II", "Estadio OMS III", "Estadio OMS IV", 
                         "OMS I", "OMS II", "OMS III", "OMS IV", "I", "II", "III", "IV",
                         "i", "ii", "iii", "iv"]
    for value in oms_values_to_test:
        success, mapped_value = test_single_value("Gn8SvTBWt9K", value, "YNBMqVtrSvi")

def get_tracked_entity_attribute_details(attribute_id):
    """Obtém detalhes específicos de um atributo da entidade rastreada"""
    try:
        url = f"{DHIS2_CONFIG['base_url']}/attributes/{attribute_id}"
        response = requests.get(url, auth=DHIS2_CONFIG["auth"], timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logging.info(f"\n📋 DETALHES DO ATRIBUTO {attribute_id}:")
            logging.info(f"   Nome: {data.get('name', 'N/A')}")
            logging.info(f"   Value Type: {data.get('valueType', 'N/A')}")
            
            if 'optionSet' in data:
                option_set = data['optionSet']
                logging.info(f"   Option Set: {option_set.get('name', 'N/A')} (ID: {option_set.get('id', 'N/A')})")
            else:
                logging.info("   ❌ SEM OPTION SET VINCULADO")
            
            return data
        else:
            logging.error(f"Erro ao obter atributo {attribute_id}: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Erro ao obter atributo {attribute_id}: {str(e)}")
        return None

def main():
    setup_logging()
    logging.info("=== DEBUG COMPLETO DO PROBLEMA DHIS2 ===")
    
    # 1. Debug dos option sets
    debug_option_set_values()
    
    # 2. Testar todos os valores possíveis
    test_all_possible_values()
    
    # 3. Verificar detalhes dos atributos problemáticos
    logging.info("\n=== VERIFICANDO VINCULO DOS ATRIBUTOS COM OPTION SETS ===")
    get_tracked_entity_attribute_details("jCdc85LhrtI")  # Sexo
    get_tracked_entity_attribute_details("Gn8SvTBWt9K")  # Estadio OMS
    
    # 4. Teste manual com curl
    logging.info("\n=== COMANDO CURL PARA TESTE MANUAL ===")
    logging.info("Execute este comando para testar manualmente:")
    logging.info(f"curl -X POST '{DHIS2_CONFIG['base_url']}/trackedEntityInstances' \\")
    logging.info("  -H 'Content-Type: application/json' \\")
    logging.info(f"  -u 'admin:Chaguala.123' \\")
    logging.info("  -d '{\"trackedEntityInstances\":[{\"trackedEntityInstance\":\"test-001\",\"trackedEntityType\":\"I1P2bB5OLA9\",\"orgUnit\":\"P3rkRiVWkDI\",\"attributes\":[{\"attribute\":\"jCdc85LhrtI\",\"value\":\"M\"},{\"attribute\":\"Gn8SvTBWt9K\",\"value\":\"Estadio OMS I\"}],\"enrollments\":[{\"enrollment\":\"test-enroll-001\",\"program\":\"ll4LqMAHvEj\",\"orgUnit\":\"P3rkRiVWkDI\",\"enrollmentDate\":\"2025-09-09\",\"incidentDate\":\"2025-09-09\",\"status\":\"ACTIVE\"}]}]}'")

if __name__ == "__main__":
    main()