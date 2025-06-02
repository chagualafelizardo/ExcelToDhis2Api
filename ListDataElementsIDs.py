import requests
from requests.auth import HTTPBasicAuth

# Configurações de acesso
BASE_URL = "http://197.249.4.129:8088/api/29"
USERNAME = "admin"
PASSWORD = "Chaguala.123"
DATASET_ID = "bJi2QH24rm5"  # Ex: TX_NEW

# Autenticação
auth = HTTPBasicAuth(USERNAME, PASSWORD)

def get_dataset_elements():
    """Obtém todos os dataElements do dataset específico, incluindo categorias"""
    try:
        response = requests.get(
            f"{BASE_URL}/dataSets/{DATASET_ID}",
            params={
                "fields": "id,name,dataSetElements[dataElement[id,name,categoryCombo[categoryOptionCombos[id,name,categoryOptions[id,name]]]]]"
            },
            auth=auth
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter dataset: {str(e)}")
        return None

def main():
    dataset = get_dataset_elements()
    if not dataset:
        return

    dataset_name = dataset.get("name", "NomeDesconhecido")

    print(f"\nDataSet: {dataset_name}")

    data_elements = dataset.get("dataSetElements", [])

    if not data_elements:
        print("Nenhum dataElement encontrado no dataset.")
        return

    for dse in data_elements:
        data_element = dse["dataElement"]
        element_name = data_element.get("name", "SemNome")
        element_id = data_element.get("id")

        print(f"\nIndicador: {element_name} (ID: {element_id})")

        combos = data_element["categoryCombo"].get("categoryOptionCombos", [])
        if not combos:
            print("  Nenhum combo encontrado.")
            continue

        # Filtrar apenas combos com 1 categoria (ex: uma única faixa etária)
        single_category_combos = [
            combo for combo in combos if len(combo.get("categoryOptions", [])) == 1
        ]

        if not single_category_combos:
            print("  Nenhum combo individual encontrado.")
            continue

        for combo in single_category_combos:
            category_option = combo["categoryOptions"][0]
            readable_name = category_option["name"]
            combo_id = combo["id"]
            print(f"{dataset_name} | {readable_name} => ID: {combo_id}")

if __name__ == "__main__":
    main()
