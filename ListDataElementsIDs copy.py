import requests
from requests.auth import HTTPBasicAuth

# Configurações de acesso
BASE_URL = "http://197.249.4.129:8088/api/29" # Servidor DHIS2 DOD
# BASE_URL = "http://196.22.54.214:8088/api/29" # Servidor eLOS
USERNAME = "admin"
PASSWORD = "Chaguala.123" # Senha Servidor DHIS2 
# PASSWORD = "Abalate.123" # Senha Servidor DHIS2 
DATASET_ID = "bJi2QH24rm5"  # Ex: TX_NEW


# Autenticação básica
auth = HTTPBasicAuth(USERNAME, PASSWORD)

def get_dataset_elements():
    """Obtém os dataElements e suas categorias a partir de um dataset"""
    try:
        response = requests.get(
            f"{BASE_URL}/dataSets/{DATASET_ID}",
            params={
                "fields": "id,name,dataSetElements[dataElement[id,name,"
                          "categoryCombo[categoryOptionCombos[id,name,"
                          "categoryOptions[id,name]]]]]"
            },
            auth=auth,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha ao obter dados do dataset: {e}")
        return None

def extract_combinations(dataset):
    """Extrai todas as combinações de categorias de todos os dataElements"""
    combinations = []
    unique_combo_ids = set()

    for dse in dataset.get("dataSetElements", []):
        data_element = dse.get("dataElement", {})
        element_name = data_element.get("name", "SemNome")
        element_id = data_element.get("id")

        combos = data_element.get("categoryCombo", {}).get("categoryOptionCombos", [])
        for combo in combos:
            combo_id = combo["id"]
            combo_name = combo.get("name", "SemNome")

            if combo_id in unique_combo_ids:
                continue  # Ignora combos repetidos

            unique_combo_ids.add(combo_id)

            category_options = combo.get("categoryOptions", [])
            option_names = [opt["name"] for opt in category_options]

            combinations.append({
                "combo_id": combo_id,
                "combo_name": combo_name,
                "category_options": option_names,
                "data_element_name": element_name,
                "data_element_id": element_id
            })

    return combinations

def main():
    print(f"Conectando ao servidor para buscar combinações de categorias do dataset '{DATASET_ID}'...\n")

    dataset = get_dataset_elements()
    if not dataset:
        print("Não foi possível recuperar o dataset.")
        return

    dataset_name = dataset.get("name", "Desconhecido")
    print(f"=== Dataset: {dataset_name} ===\n")

    combos = extract_combinations(dataset)

    if not combos:
        print("Nenhuma combinação de categorias encontrada.")
        return

    for combo in combos:
        print(f"● DataElement: {combo['data_element_name']} (ID: {combo['data_element_id']})")
        print(f"  ↳ Combo: {combo['combo_name']} (ID: {combo['combo_id']})")
        print(f"     - Categorias: {', '.join(combo['category_options'])}\n")

if __name__ == "__main__":
    main()
