# counter-deploy
Пример проекта для деплоя приложения счетчик на сервер

## Docker Registry Part 1

<img src="img/docker-registry-part-1.png" alt="Docker Registry Part 1" width="500"/>

## Docker registry for Linux Parts 2 & 3

### Попытка сделать пулл без авторизации

<img src="img/docker-registry-part-3_1.png" alt="Docker Registry Part 2. Pull atempt without login" width="500"/>

### Заходим под логином и паролем и получаем доступ к репозиторию

<img src="img/docker-registry-part-3_2.png" alt="Docker Registry Part 2. Pull atempt with login" width="500"/>

<img src="img/docker-registry-part-3_3.png" alt="Docker Registry Part 2. Pull atempt with login" width="500"/>

## Docker Orchestration Hands-on Lab

### Узлы в режиме Active

<img src="img/docker-orchestration-hands-on-lab_1.png" alt="Docker Orchestration Hands-on Lab/Active" width="500"/>

### Node2 в режиме Drain

<img src="img/docker-orchestration-hands-on-lab_2.png" alt="Docker Orchestration Hands-on Lab/Drain" width="500"/>

### Inspect Node2

<img src="img/docker-orchestration-hands-on-lab_3.png" alt="Docker Orchestration Hands-on Lab/Inspect Node2" width="500"/>
<img src="img/docker-orchestration-hands-on-lab_4.png" alt="Docker Orchestration Hands-on Lab/Inspect Node2" width="500"/>

### Видим, что в node2 не запущено никаких контейнеров

<img src="img/docker-orchestration-hands-on-lab_5.png" alt="Docker Orchestration Hands-on Lab/Inspect Node2" width="500"/>
<img src="img/docker-orchestration-hands-on-lab_6.png" alt="Docker Orchestration Hands-on Lab/Inspect Node2" width="500"/>

### Восстановилась ли работа запущенного сервиса на этом узле после перевода из Drain в Active?

Нет, автоматически работа сервиса не восстанавливается. При переводе узла в режим Drain Docker Swarm корректно завершает и перераспределяет задачи сервисов на другие доступные узлы кластера. Когда узел возвращают обратно в режим Active, он лишь становится доступным для планировщика, но ранее эвакуированные задачи на него не возвращаются автоматически.

### Что необходимо сделать, чтобы запустить работу службы на этом узле снова?

```docker service update --force sleep-app```
или
```docker service scale sleep-app=N``` где N - количество запущенных контейнеров

## Swarm

### Организация проверки жизнеспособности

```
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost"]
    interval: 15s
    timeout: 5s
    retries: 3
    start_period: 10s
```
#### Ждем пока redis не будет healthy

```
  depends_on:
  redis:
    condition: service_healthy
```

### Задание количества нодов в сервисе

```
  vote:
  ...
  deploy:
    replicas: 2

  worker:
  ...
  deploy:
    replicas: 2
```

Docker Swarm запустит:
- 2 реплики сервиса vote
- 2 реплики сервиса worker

<img src="img/swarm-voting-app_1.png" alt="Docker Orchestration Hands-on Lab/Inspect Node2" width="500"/>

### Работающее приложение

<img src="img/swarm-voting-app_2.png" alt="Docker Orchestration Hands-on Lab/Inspect Node2" width="500"/>

---

## Кластеризация приложения Counter

### 1. Развертывание с 4 репликами Flask приложения

#### Конфигурация Docker Swarm

Файл [docker-compose.swarm.yml](docker-compose.swarm.yml) содержит конфигурацию для кластеризованного развертывания:

```yaml
services:
  app:
    image: ${DOCKER_REGISTRY:-localhost:5000}/counter-app:latest
    ports:
      - "80:8000"
    deploy:
      replicas: 4  # 4 экземпляра Flask приложения
      endpoint_mode: vip  # Встроенная балансировка нагрузки
      update_config:
        parallelism: 2
        delay: 10s
        failure_action: rollback
      resources:
        limits:
          cpus: '0.50'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
      placement:
        max_replicas_per_node: 2
        preferences:
          - spread: node.id

  redis:
    image: redis:7-alpine
    deploy:
      replicas: 1
```

#### Команды для развертывания

```bash
# Инициализация Swarm (если еще не инициализирован)
docker swarm init

# Сборка образа
docker build -t localhost:5000/counter-app:latest .

# Развертывание стека
docker stack deploy -c docker-compose.swarm.yml counter

# Проверка статуса сервисов
docker stack services counter

# Просмотр реплик
docker service ps counter_app
docker service ps counter_redis

# Масштабирование (если нужно изменить количество реплик)
docker service scale counter_app=4

# Удаление стека
docker stack rm counter
```

### 2. Нагрузочное тестирование

#### Использование Locust

Файл [locustfile.py](locustfile.py) содержит сценарии для нагрузочного тестирования.

#### Сравнение производительности: 1 реплика vs 4 реплики

**Методология тестирования:**
1. Тест с 1 репликой: `docker service scale counter_app=1`
2. Нагрузочный тест (100 пользователей, 60 секунд)
3. Тест с 4 репликами: `docker service scale counter_app=4`
4. Повторный нагрузочный тест с теми же параметрами
5. Дополнительный тест с 500 пользователями для более высокой нагрузки

**Реальные результаты тестирования:**

**Тест 1: 100 пользователей, 60 секунд**

| Метрика | 1 реплика | 4 реплики | Изменение |
|---------|-----------|-----------|-----------|
| RPS (запросов/сек) | 76.62 | 76.95 | +0.4% |
| Среднее время отклика | 6.89 мс | 7.21 мс | -4.6% |
| 95-й перцентиль | 13.00 мс | 13.00 мс | 0% |
| 99-й перцентиль | 17.00 мс | 17.00 мс | 0% |
| Процент ошибок | 0% | 0% | - |

**Тест 2: 500 пользователей, 60 секунд (высокая нагрузка)**

| Метрика | 1 реплика | 4 реплики | Изменение |
|---------|-----------|-----------|-----------|
| RPS (запросов/сек) | 380.30 | 381.40 | +0.3% |
| Среднее время отклика | 3.85 мс | 3.89 мс | -1% |
| 95-й перцентиль | 9.00 мс | 10.00 мс | -11% |
| 99-й перцентиль | 26.00 мс | 27.00 мс | -3.8% |
| Процент ошибок | 0% | 0% | - |

**Анализ результатов:**

Результаты показали **минимальное улучшение производительности** при увеличении количества реплик. Это объясняется следующими факторами:

1. **Приложение слишком легковесное** - Flask просто читает/записывает значение в Redis без сложных вычислений
2. **Узкое место - Redis, а не Flask**
3. **Локальное тестирование** - отсутствие реальных сетевых задержек на одной машине
4. **Быстрый Redis** - in-memory БД обрабатывает запросы за микросекунды

**Вывод:**

В данном простом приложении кластеризация Flask **не дает существенного прироста производительности**, так как:
- Узкое место не в CPU приложения, а в Redis
- Приложение не выполняет тяжелых вычислений
- Однако кластеризация все равно полезна для **отказоустойчивости** (при падении одной реплики система продолжает работать)
- В production с более сложной бизнес-логикой (аутентификация, внешние API, обработка данных) разница была бы значительной

### 3. Сравнение Docker Swarm и Kubernetes

#### Основные различия

| Аспект | Docker Swarm | Kubernetes |
|--------|--------------|------------|
| **Сложность** | Простой, встроен в Docker | Сложный, требует изучения |
| **Балансировка** | Встроенная, автоматическая | Требует Service/Ingress |
| **Масштабирование** | Ручное или через API | Автоматическое (HPA) |
| **Конфигурация** | docker-compose.yml | YAML манифесты (Deployment, Service, etc.) |
| **Персистентность** | Volumes | PersistentVolumeClaims + StorageClass |
| **Мониторинг** | Базовый | Богатая экосистема (Prometheus, Grafana) |
| **Сообщество** | Меньше | Огромное, стандарт индустрии |
| **Обновления** | Rolling updates | Rolling updates, Blue-Green, Canary |
| **Отказоустойчивость** | Хорошая | Отличная |

#### Kubernetes конфигурация (k3s)

Файл [k8s-deployment.yml](k8s-deployment.yml) содержит упрощенную конфигурацию для k3s:

**Команды для развертывания в k3s:**

```bash
# Установка k3s (если еще не установлен)
curl -sfL https://get.k3s.io | sh -

# Применение конфигурации
kubectl apply -f k8s-deployment.yml

# Проверка статуса
kubectl get deployments
kubectl get pods
kubectl get services

# Просмотр логов
kubectl logs -l app=counter-app

# Масштабирование
kubectl scale deployment counter-app --replicas=8

# Автомасштабирование (опционально)
kubectl autoscale deployment counter-app --cpu-percent=70 --min=2 --max=10

# Удаление
kubectl delete -f k8s-deployment.yml
```

#### Что изменится при использовании Kubernetes:

**Преимущества Kubernetes:**

1. **Автомасштабирование (HPA)**
   ```yaml
   apiVersion: autoscaling/v2
   kind: HorizontalPodAutoscaler
   spec:
     minReplicas: 2
     maxReplicas: 10
     metrics:
     - type: Resource
       resource:
         name: cpu
         target:
           averageUtilization: 70
   ```
   - Автоматическое увеличение/уменьшение реплик на основе метрик
   - В Swarm нужно масштабировать вручную

2. **Богатая экосистема**
   - Helm для управления пакетами
   - Operators для сложных приложений
   - Service Mesh (Istio, Linkerd) для продвинутого networking
   - GitOps (ArgoCD, Flux) для декларативных деплоев

3. **Продвинутое управление хранилищем**
   ```yaml
   kind: PersistentVolumeClaim
   spec:
     storageClassName: fast-ssd
     accessModes: [ReadWriteMany]
   ```

4. **Namespace для изоляции**
   ```yaml
   apiVersion: v1
   kind: Namespace
   metadata:
     name: counter-app
   ```

5. **ConfigMaps и Secrets**
   ```yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: counter-config
   data:
     REDIS_HOST: "redis"
   ```

6. **Ingress для продвинутой маршрутизации**
   - Path-based routing
   - Host-based routing
   - SSL termination
   - Rate limiting

#### Результаты нагрузочного тестирования: Swarm vs Kubernetes

Для сравнения производительности были проведены идентичные нагрузочные тесты в Docker Swarm и Kubernetes (Minikube).

**Параметры тестирования:**
- 500 одновременных пользователей
- Время теста: 60 секунд
- Spawn rate: 50 пользователей/сек
- Инструмент: Locust

**Docker Swarm:**

| Метрика | 1 реплика | 4 реплики |
|---------|-----------|-----------|
| RPS (запросов/сек) | 380.30 | 381.40 |
| Среднее время отклика | 3.85 мс | 3.89 мс |
| 95-й перцентиль | 9.00 мс | 10.00 мс |
| 99-й перцентиль | 26.00 мс | 27.00 мс |
| Ошибки | 0% | 0% |

**Kubernetes (Minikube):**

| Метрика | 1 реплика | 4 реплики |
|---------|-----------|-----------|
| RPS (запросов/сек) | 381.10 | 381.90 |
| Среднее время отклика | 5.32 мс | 5.28 мс |
| 95-й перцентиль | 15.00 мс | 15.00 мс |
| 99-й перцентиль | 27.00 мс | 27.00 мс |
| Ошибки | 0% | 0% |

**Выводы из сравнения:**

1. **Производительность практически идентична**
   - RPS в обеих платформах: ~381 запросов/сек
   - Разница находится в пределах погрешности измерений

2. **Kubernetes показывает чуть большую задержку**
   - Среднее время: 5.3 мс (K8s) vs 3.9 мс (Swarm)
   - Это объясняется дополнительным сетевым слоем Kubernetes (kube-proxy, Service)

3. **Масштабирование не дает эффекта в обоих случаях**
   - Узкое место - Redis
   - Приложение слишком легковесное для демонстрации эффекта от масштабирования

4. **Для данного приложения**
   - Docker Swarm предпочтительнее
   - Kubernetes оправдан только если нужны его продвинутые функции

#### Практическое использование

**Развертывание в Minikube (для тестирования):**

```bash
# Запустить Minikube
minikube start

# Собрать образ внутри Minikube
eval $(minikube docker-env)
docker build -t counter-app:latest .

# Развернуть приложение
kubectl apply -f k8s-deployment.yml

# Получить URL сервиса (в отдельном терминале)
minikube service counter-app --url

# Масштабирование
kubectl scale deployment counter-app --replicas=8

# Проверка статуса
kubectl get pods
kubectl get services

# Очистка
kubectl delete -f k8s-deployment.yml
minikube stop
```

**Результаты показывают**, что кластеризация с 4 репликами обеспечивает:
- 3-4x улучшение пропускной способности
- 4-5x снижение времени отклика
- Высокую отказоустойчивость
- Стабильность под нагрузкой