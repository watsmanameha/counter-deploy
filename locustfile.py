from locust import HttpUser, task, between, events
import random


class CounterUser(HttpUser):
    """
    Пользователь, который взаимодействует со счетчиком
    """
    wait_time = between(0.5, 2)

    def on_start(self):
        """Вызывается при запуске каждого пользователя"""
        # Загрузка главной страницы при старте
        self.client.get("/")

    @task(10)
    def get_counter(self):
        """
        Получение текущего значения счетчика
        Вес: 10 (выполняется чаще других)
        """
        with self.client.get("/api/counter", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    if "value" in json_data:
                        response.success()
                    else:
                        response.failure("Отсутствует поле 'value' в ответе")
                except Exception as e:
                    response.failure(f"Ошибка парсинга JSON: {str(e)}")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(5)
    def increment_counter(self):
        """
        Увеличение счетчика
        Вес: 5
        """
        with self.client.post("/api/counter/increment", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    if "value" in json_data:
                        response.success()
                    else:
                        response.failure("Отсутствует поле 'value' в ответе")
                except Exception as e:
                    response.failure(f"Ошибка парсинга JSON: {str(e)}")

    @task(3)
    def decrement_counter(self):
        """
        Уменьшение счетчика
        Вес: 3
        """
        with self.client.post("/api/counter/decrement", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    if "value" in json_data:
                        response.success()
                    else:
                        response.failure("Отсутствует поле 'value' в ответе")
                except Exception as e:
                    response.failure(f"Ошибка парсинга JSON: {str(e)}")

    @task(1)
    def reset_counter(self):
        """
        Сброс счетчика
        Вес: 1 (выполняется реже всего)
        """
        self.client.post("/api/counter/reset")

    @task(2)
    def load_main_page(self):
        """
        Загрузка главной страницы
        Вес: 2
        """
        self.client.get("/")


# Event listeners для сбора дополнительной статистики
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Вызывается при начале теста"""
    print("\n" + "="*60)
    print("НАЧАЛО НАГРУЗОЧНОГО ТЕСТИРОВАНИЯ")
    print("="*60 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Вызывается при завершении теста"""
    print("\n" + "="*60)
    print("ЗАВЕРШЕНИЕ НАГРУЗОЧНОГО ТЕСТИРОВАНИЯ")
    print("="*60 + "\n")

    # Вывод общей статистики
    stats = environment.stats
    print(f"Общее количество запросов: {stats.total.num_requests}")
    print(f"Общее количество ошибок: {stats.total.num_failures}")
    print(f"Среднее время отклика: {stats.total.avg_response_time:.2f} мс")
    print(f"Медианное время отклика: {stats.total.median_response_time:.2f} мс")
    print(f"95-й перцентиль: {stats.total.get_response_time_percentile(0.95):.2f} мс")
    print(f"99-й перцентиль: {stats.total.get_response_time_percentile(0.99):.2f} мс")
    print(f"RPS (запросов в секунду): {stats.total.total_rps:.2f}")
    print("\n" + "="*60 + "\n")
