import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://197.249.4.129:8088/api/29"
USERNAME = "admin"
PASSWORD = "Chaguala.123"
DATASET_ID = "bJi2QH24rm5"

auth = HTTPBasicAuth(USERNAME, PASSWORD)

def get_dataset_elements():
    try:
        response = requests.get(
            f"{BASE_URL}/dataSets/{DATASET_ID}",
            params={
                "fields": "id,name,dataSetElements[dataElement[id,name,categoryCombo[categoryOptionCombos[id,name,categoryOptions[id,name]]]]]"
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
    result = {}

    for dse in dataset.get("dataSetElements", []):
        data_element = dse.get("dataElement", {})
        element_name = data_element.get("name", "SemNome")
        element_id = data_element.get("id")

        key = f"{element_name} (ID: {element_id})"
        result[key] = []

        combos = data_element.get("categoryCombo", {}).get("categoryOptionCombos", [])
        for combo in combos:
            combo_id = combo.get("id")
            category_options = combo.get("categoryOptions", [])
            option_names = [opt["name"] for opt in category_options]

            # Junta as opções como: "Male 10-14"
            option_names_sorted = sorted(option_names)
            combined_name = " ".join(option_names_sorted)

            result[key].append({
                "name": combined_name,
                "id": combo_id
            })

    return result

def main():
    print(f"Conectando ao servidor para buscar combinações de categorias do dataset '{DATASET_ID}'...\n")

    dataset = get_dataset_elements()
    if not dataset:
        print("Não foi possível recuperar o dataset.")
        return

    dataset_name = dataset.get("name", "Desconhecido")
    print(f"=== Dataset: {dataset_name} ===\n")

    combos_dict = extract_combinations(dataset)

    for indicator, combos in combos_dict.items():
        print(f"Indicador: {indicator}")
        for combo in combos:
            print(f"  - {combo['name']} (ID: {combo['id']})")
        print()

if __name__ == "__main__":
    main()
