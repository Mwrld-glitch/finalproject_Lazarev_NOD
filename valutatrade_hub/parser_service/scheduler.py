import threading
import time

import schedule

from .updater import rates_updater


class RatesScheduler:
    """Планировщик периодического обновления курсов"""
    
    def __init__(self):
        self.updater = rates_updater
        self._stop_event = threading.Event()
    
    def start_background_scheduler(self):
        """Запускает планировщик в фоновом потоке"""
        def run_scheduler():
            # Обновление каждые 5 минут
            schedule.every(5).minutes.do(self._run_update)
            
            while not self._stop_event.is_set():
                schedule.run_pending()
                time.sleep(1)
        
        thread = threading.Thread(target=run_scheduler, daemon=True)
        thread.start()
        print("INFO: Rates scheduler started in background (updates every 5 minutes)")
    
    def _run_update(self):
        """Запускает обновление курсов"""
        print("INFO: Scheduled rates update started...")
        success = self.updater.run_update()
        if success:
            print("INFO: Scheduled update completed successfully")
        else:
            print("WARNING: Scheduled update completed with errors")
    
    def stop(self):
        """Останавливает планировщик"""
        self._stop_event.set()


# Автоматический запуск при импорте
rates_scheduler = RatesScheduler()
rates_scheduler.start_background_scheduler()