import requests
import pandas as pd
from datetime import datetime
import logging
from typing import Dict, List

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='dhis2_integration.log'
)
logger = logging.getLogger(__name__)

class DHIS2Integrator:
    def __init__(self, config: Dict):
        """
        Inicializa o integrador com as configurações do DHIS2
        
        Args:
            config (dict): Dicionário com:
                - url: URL base do DHIS2
                - username: Nome de usuário
                - password: Senha
                - org_unit: ID da unidade organizacional
                - dataset_id: ID do conjunto de dados
        """
        self.config = config
        self.session = requests.Session()
        self.session.auth = (config['username'], config['password'])
        self.session.headers.update({'Content-Type': 'application/json'})
        
        # Verificar conexão
        self._test_connection()

    def _test_connection(self):
        """Testa a conexão com o DHIS2"""
        try:
            response = self.session.get(f"{self.config['url']}/api/system/info")
            response.raise_for_status()
            logger.info("Conexão com DHIS2 estabelecida com sucesso")
        except Exception as e:
            logger.error(f"Falha ao conectar ao DHIS2: {str(e)}")
            raise

    def load_data_from_excel(self, file_path: str) -> pd.DataFrame:
        """
        Carrega dados de um arquivo Excel
        
        Args:
            file_path (str): Caminho para o arquivo Excel
            
        Returns:
            pd.DataFrame: DataFrame com os dados
        """
        try:
            df = pd.read_excel(file_path)
            logger.info(f"Dados carregados do arquivo {file_path}")
            return df
        except Exception as e:
            logger.error(f"Erro ao carregar arquivo Excel: {str(e)}")
            raise

    def prepare_payload(self, row: pd.Series, data_element_mapping: Dict) -> Dict:
        """
        Prepara o payload para envio ao DHIS2
        
        Args:
            row (pd.Series): Linha do DataFrame com os dados

            data_element_mapping (dict): Mapeamento coluna -> elemento de dados
            
        Returns:
            dict: Payload no formato esperado pelo DHIS2
        """
        data_values = []
        
        for col_name, de_id in data_element_mapping.items():
            if col_name in row and pd.notna(row[col_name]):
                data_values.append({
                    "dataElement": rZtFk3z5o9X,
                    "value": str("15")  # Convertendo para string para garantir
                })
        
        return {
            "dataSet": self.config['bJi2QH24rm5'], # dataset_id = bJi2QH24rm5
            "completeDate": datetime.now().strftime("%Y-%m-%d"),
            "period": str(row['202501']),  # Garantindo que é string
            "orgUnit": self.config['QSxnM0virqc'], # org_unit = QSxnM0virqc
            "dataValues": data_values
        }

    def send_data(self, df: pd.DataFrame, data_element_mapping: Dict) -> None:
        """
        Envia dados para o DHIS2
        
        Args:
            df (pd.DataFrame): DataFrame com os dados
            data_element_mapping (dict): Mapeamento coluna -> elemento de dados
        """
        success_count = 0
        error_count = 0
        
        for _, row in df.iterrows():
            try:
                payload = self.prepare_payload(row, data_element_mapping)
                response = self.session.post(
                    f"{self.config['url']}/api/dataValueSets",
                    json=payload
                )
                
                if response.status_code == 200:
                    success_count += 1
                    logger.info(f"Dados enviados para período 202501.") # {row['periodo']} este periodo vira de uma fonte como excel 
                else:
                    error_count += 1
                    logger.error(
                        f"Erro ao enviar dados para período 202501. "
                        f"Status: {response.status_code}. Resposta: {response.text}"
                    )
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Erro ao processar período 202501: {str(e)}")
        
        logger.info(
            f"Processamento concluído. Sucessos: {success_count}, "
            f"Erros: {error_count}, Total: {len(df)}"
        )

if __name__ == "__main__":
    # Configurações - SUBSTITUA COM SEUS DADOS REAIS
    config = {
        "url": "http://197.249.4.129:8088/api/29",
        "username": "admin",
        "password": "Chaguala.123",
        "org_unit": "QSxnM0virqc",
        "dataset_id": "bJi2QH24rm5"
    }
    
    # Mapeamento colunas -> elementos de dados - SUBSTITUA COM SEUS DADOS
    data_element_mapping = {
        "coluna5_9": "ofim8WPTvLg",
        "coluna10_14": "bgxXDloWVji",
        # Adicione mais mapeamentos conforme necessário
    }
    
    # Caminho do arquivo Excel
    excel_file = "C:\Users\Felizardo Chaguala\Desktop\dhis2\dados.xlsx"
    
    try:
        integrator = DHIS2Integrator(config)
        df = integrator.load_data_from_excel(excel_file)
        integrator.send_data(df, data_element_mapping)
    except Exception as e:
        logger.error(f"Erro fatal no processo: {str(e)}")