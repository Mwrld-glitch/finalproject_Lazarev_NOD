import json
import os
from datetime import datetime
from typing import List, Dict
from .config import config

class RatesStorage:
    """Управление хранением курсов валют"""
    
    def save_current_rates(self, rates_data: Dict) -> bool:
        """Сохраняет текущие курсы в rates.json"""
        try:
            data = {
                "source": "ParserService",
                "last_refresh": datetime.now().isoformat(),
                **rates_data
            }
            
            with open(config.RATES_FILE_PATH, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения текущих курсов: {e}")
            return False
    
    def save_historical_record(self, currency_pair: str, rate: float, source: str) -> bool:
        """Сохраняет историческую запись в exchange_rates.json"""
        try:
            timestamp = datetime.now().isoformat()
            record_id = f"{currency_pair}_{timestamp.replace(':', '-').replace('.', '-')}"
            
            record = {
                "id": record_id,
                "from_currency": currency_pair.split('_')[0],
                "to_currency": currency_pair.split('_')[1],
                "rate": rate,
                "timestamp": timestamp,
                "source": source,
                "meta": {
                    "raw_id": currency_pair,
                    "status_code": 200,
                    "updated_at": timestamp
                }
            }
            
            # Загружаем существующие данные
            if os.path.exists(config.HISTORY_FILE_PATH):
                with open(config.HISTORY_FILE_PATH, "r") as f:
                    history = json.load(f)
            else:
                history = []
            
            # Добавляем новую запись
            history.append(record)
            
            # Сохраняем обратно
            with open(config.HISTORY_FILE_PATH, "w") as f:
                json.dump(history, f, indent=2)
            
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения исторической записи: {e}")
            return False
    
    def load_current_rates(self) -> Dict:
        """Загружает текущие курсы из rates.json"""
        try:
            if os.path.exists(config.RATES_FILE_PATH):
                with open(config.RATES_FILE_PATH, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Ошибка загрузки текущих курсов: {e}")
            return {}
