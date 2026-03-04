# Деплой GigaBotPresent на Ubuntu 22.04

Инструкция по развёртыванию форка GigaBot Present на сервере Ubuntu 22.04.

---

## Требования

- Ubuntu 22.04
- Python 3.11+
- Рекомендуемые ресурсы: 4 vCPU, 16 GB RAM (для RAG и стабильной работы GigaChat)

## Шаг 1. Системные зависимости

На Ubuntu 22.04 пакеты Python 3.11 часто отсутствуют в стандартных репозиториях. Добавьте PPA [deadsnakes](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa) и установите зависимости:

```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev libffi-dev tesseract-ocr tesseract-ocr-rus git
```

> **Примечание:** На Ubuntu 24.04 и новее Python 3.12 может быть в стандартных репозиториях; при желании использовать его замените `3.11` на `3.12` в командах (и проверьте совместимость проекта).

`libffi-dev` и `python3.11-dev` нужны для зависимостей чтения PDF (cffi → pdfplumber). Для **режима презентации** (без OCR) tesseract можно не использовать, но оставить его безопасно.

## Шаг 2. Пользователь и каталог (опционально)

```bash
sudo useradd -m -s /bin/bash gigabot
sudo su - gigabot
```

Далее команды — от имени пользователя, в домашнем каталоге которого будет разложен проект.

## Шаг 3. Размещение кода и venv

Если проект уже в репозитории:

```bash
git clone https://github.com/SoapMaker101/GigaBotPresent ~/GigaBotPresent
cd ~/GigaBotPresent/gigabot
```

Если копируете папку вручную (без git):

```bash
# На своей машине: скопировать GigaBotPresent на сервер (scp/rsync)
# На сервере, например:
mkdir -p ~/GigaBotPresent
# положить содержимое GigaBotPresent (в т.ч. gigabot/, docs/, tech-spec/) в ~/GigaBotPresent
cd ~/GigaBotPresent/gigabot
```

Создание виртуального окружения и установка пакета:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install hatchling
pip install -e .
```

### Виртуальное окружение и как в него попадать

- **Виртуальное окружение (venv)** — это папка `.venv` внутри каталога проекта: `~/GigaBotPresent/gigabot/.venv`. В ней установлены Python и команда `gigabot`; без активации окружения команда `gigabot` в системе не найдена.
- **Конфиг** лежит в **домашнем каталоге пользователя**, под которым вы работаете: `~/.gigabot/config.json`. Например, для пользователя `giga` это `/home/giga/.gigabot/config.json`; для `gigabot` — `/home/gigabot/.gigabot/config.json`. Редактировать конфиг можно в любой момент (даже без активированного venv): `nano ~/.gigabot/config.json`.

**После нового подключения к серверу** нужно снова войти в каталог проекта и активировать окружение — тогда заработает команда `gigabot`:

```bash
cd ~/GigaBotPresent/gigabot
source .venv/bin/activate
```

В приглашении появится `(.venv)` — значит окружение активно. Дальше можно вызывать `gigabot onboard`, `gigabot agent`, и т.д.

## Шаг 4. Конфигурация

Перейдите в каталог проекта и активируйте venv (см. выше), затем создайте конфиг и отредактируйте его:

```bash
cd ~/GigaBotPresent/gigabot
source .venv/bin/activate
gigabot onboard
nano ~/.gigabot/config.json
```

Заполнить минимум:

- **gigachat**: credentials (base64), scope, model (например GigaChat-2-Max).
- **telegram** (если нужен бот): enabled: true, token, allowFrom (список Telegram ID).

Для **режима презентации** (только нужные для демо инструменты) в config.json добавить в секцию `agent`:

```json
"agent": {
  "workspace": "~/.gigabot/workspace",
  "presentationMode": true
}
```

Либо при отсутствии config.json можно задать переменную окружения перед запуском: `export GIGABOT_AGENT__PRESENTATION_MODE=true`.

## Шаг 5. Проверка

Сначала активируйте виртуальное окружение (из любого каталога можно так, либо `cd ~/GigaBotPresent/gigabot` и `source .venv/bin/activate`):

```bash
source ~/GigaBotPresent/gigabot/.venv/bin/activate
gigabot agent -m "Привет! Кто ты?"
```

При успехе агент ответит от имени GigaBot. Дальше можно проверить сценарий по [DEMO-PRESET.md](../DEMO-PRESET.md) и [06-Scenarij-demo-CSM.md](06-Scenarij-demo-CSM.md).

## Шаг 6. Systemd-сервис (постоянный запуск)

Выполнять **от пользователя с sudo** (например `giga`), не от `gigabot`.

В репозитории лежит готовый файл юнита `docs/gigabot.service`. Скопируйте его в systemd и включите сервис — **четыре команды по одной строке**:

```bash
sudo cp ~/GigaBotPresent/docs/gigabot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gigabot
sudo systemctl start gigabot
```

**Если выдаёт «No such file or directory»:**

1. Проект может лежать в домашней папке пользователя `gigabot`. Тогда (под пользователем `giga`):
   ```bash
   sudo cp /home/gigabot/GigaBotPresent/docs/gigabot.service /etc/systemd/system/
   ```
2. Либо на сервере старая копия репозитория без этого файла. Обновите код и снова скопируйте:
   ```bash
   cd ~/GigaBotPresent && git pull
   sudo cp ~/GigaBotPresent/docs/gigabot.service /etc/systemd/system/
   ```
3. Либо создайте файл вручную. Команда:
   ```bash
   sudo nano /etc/systemd/system/gigabot.service
   ```
   Вставьте содержимое ниже (замените `gigabot` на `giga` в путях и в `User`/`Environment`, если проект под пользователем `giga`), сохраните (Ctrl+O, Enter, Ctrl+X):

   ```
   [Unit]
   Description=GigaBot Present (CSM demo)
   After=network.target

   [Service]
   Type=simple
   User=gigabot
   WorkingDirectory=/home/gigabot/GigaBotPresent/gigabot
   ExecStart=/home/gigabot/GigaBotPresent/gigabot/.venv/bin/gigabot gateway
   Restart=always
   RestartSec=5
   Environment=HOME=/home/gigabot

   [Install]
   WantedBy=multi-user.target
   ```

После того как файл юнита появился в `/etc/systemd/system/gigabot.service`, выполните:
```bash
sudo systemctl daemon-reload
sudo systemctl enable gigabot
sudo systemctl start gigabot
```

Если проект развёрнут под пользователем **giga** (а не `gigabot`), отредактируйте файл и замените все `gigabot` на `giga` в путях и в `User`/`Environment`:

```bash
sudo nano /etc/systemd/system/gigabot.service
```

Проверка:

```bash
sudo systemctl status gigabot
sudo journalctl -u gigabot -f
```

## Шаг 7. Обновление после изменений кода

```bash
cd ~/GigaBotPresent/gigabot
source .venv/bin/activate
git pull origin main   # если используете git
pip install -e .
sudo systemctl restart gigabot
```

## Логи и откат

- **Логи:** `sudo journalctl -u gigabot -n 100 --no-pager` или `sudo journalctl -u gigabot -f`.
- **Откат:** откатить код (git checkout / восстановить копию), снова `pip install -e .`, `sudo systemctl restart gigabot`.

