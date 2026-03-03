# Деплой GigaBotPresent на Ubuntu 22.04

Инструкция по развёртыванию форка GigaBot Present на сервере Ubuntu 22.04.

---

## Требования

- Ubuntu 22.04
- Python 3.11+
- Рекомендуемые ресурсы: 4 vCPU, 16 GB RAM (для RAG и стабильной работы GigaChat)

## Шаг 1. Системные зависимости

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev libffi-dev tesseract-ocr tesseract-ocr-rus git
```

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
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ> ~/GigaBotPresent
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

## Шаг 4. Конфигурация

```bash
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

```bash
source ~/GigaBotPresent/gigabot/.venv/bin/activate
gigabot agent -m "Привет! Кто ты?"
```

При успехе агент ответит от имени GigaBot. Дальше можно проверить сценарий по [DEMO-PRESET.md](../DEMO-PRESET.md) и [06-Scenarij-demo-CSM.md](06-Scenarij-demo-CSM.md).

## Шаг 6. Systemd-сервис (постоянный запуск)

Подставьте реальные пути (пользователь и каталог). Пример для пользователя `gigabot` и каталога `~/GigaBotPresent/gigabot`:

```bash
sudo tee /etc/systemd/system/gigabot.service > /dev/null << 'EOF'
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
EOF

sudo systemctl daemon-reload
sudo systemctl enable gigabot
sudo systemctl start gigabot
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
