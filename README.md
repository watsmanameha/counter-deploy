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