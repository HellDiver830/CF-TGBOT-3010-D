# Crypto P2P API (Tatum-ready)

Бэкенд для криптокошелька и P2P-платформы без хранения приватных ключей.

Проект рассчитан на развёртывание в виде отдельного API-сервиса. Для работы с реальными
блокчейнами используется внешний RPC-провайдер (например, [Tatum](https://tatum.io/)).


## Возможности

- Регистрация и авторизация пользователей (JWT, `Bearer`-токен)
- Справочник поддерживаемых сетей:
  - BTC, ETH, USDT (ERC20), TRX, USDT (TRC20), LTC, BNB, TON
- Получение актуальных курсов (CoinGecko, с кэшем)
- Валидация адресов кошельков по сети
- Оценка комиссии (простая модель)
- Отправка подписанных транзакций в сеть через Tatum
- Проверка статуса транзакций (pending / confirmed / failed)
- P2P-эскроу:
  - Создание ордеров (buy/sell)
  - Принятие ордеров второй стороной
  - Подтверждение сделки обеими сторонами
  - Отмена ордера создателем
  - История сделок по пользователю


## Запуск под Ubuntu / WSL (без Docker)

### 1. Подготовка PostgreSQL

```bash
sudo apt update
sudo apt install -y postgresql postgresql-contrib libpq-dev python3-venv python3-pip
sudo service postgresql start

sudo -u postgres psql
```

В psql выполнить (если уже создавали пользователя/БД — ошибки о существовании можно игнорировать):

```sql
CREATE USER crypto WITH PASSWORD 'crypto';
CREATE DATABASE crypto_p2p OWNER crypto;
GRANT ALL PRIVILEGES ON DATABASE crypto_p2p TO crypto;
\q
```

### 2. Клонирование / распаковка проекта

```bash
cd /mnt/c/projects
unzip crypto_p2p_api_ready_tatum.zip -d crypto_p2p_api_ready
cd crypto_p2p_api_ready
```

### 3. Настройка окружения

Создайте `.env`:

```env
DB_URL=postgresql+psycopg2://crypto:crypto@127.0.0.1:5432/crypto_p2p

# Ключ и базовый URL Tatum (пример)
TATUM_API_KEY=ВАШ_КЛЮЧ_TATUM
TATUM_BASE_URL=https://api.tatum.io

# JWT (можно оставить по умолчанию)
SECRET_KEY=CHANGE_ME_SECRET
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 4. Установка зависимостей и инициализация БД

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

python init_db.py
```

Ожидаемый вывод: `DB initialized.`

### 5. Запуск API

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Swagger-документация: `http://localhost:8000/docs`


## Мини-сценарий проверки

1. **Сети**  
   `GET /api/v1/networks` – вернёт:
   BTC, ETH, USDT_ERC20, TRX, USDT_TRC20, LTC, BNB, TON.

2. **Регистрация и логин**  
   - `POST /api/v1/auth/register` – создать пользователя.  
   - `POST /api/v1/auth/login` – получить `access_token`.  
   - Нажать **Authorize** в Swagger и ввести `Bearer <access_token>`.

3. **P2P**  
   - Пользователь A создаёт ордер `POST /api/v1/p2p/orders`.  
   - Пользователь B видит его в `GET /api/v1/p2p/orders` и принимает через  
     `POST /api/v1/p2p/orders/{id}/accept`.  
   - Оба по очереди подтверждают `POST /api/v1/p2p/orders/{id}/confirm` до статуса `completed`.  
   - `GET /api/v1/p2p/history` показывает историю сделок.

4. **Транзакции через Tatum**  
   При наличии `TATUM_API_KEY` и корректно подписанной транзакции:

   - `POST /api/v1/tx/broadcast` отправляет транзакцию через Tatum и возвращает `tx_hash`.  
   - `GET /api/v1/tx/{network}/{tx_hash}` синхронизирует статус с сетью через Tatum.  

   Без Tatum API ключа поведение остаётся тестовым: хеш считается как SHA256 от `signed_tx`,
   а статус хранится только в БД.


## Замечание по боевой эксплуатации

Код ориентирован на простую интеграцию с внешним RPC-провайдером и демонстрацию всех
бизнес-процессов по ТЗ. Для «жёсткого» продакшена рекомендуется:

- завести отдельные RPC-ключи/ноды под каждую сеть;
- детализировать обработку ответов Tatum для разных сетей (EVM, UTXO, Tron, TON);
- добавить логирование, мониторинг, rate limiting, retries и т.д.
