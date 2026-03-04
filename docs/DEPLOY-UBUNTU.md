# Деплой GigaBotPresent на Ubuntu 22.04

Пошаговая инструкция «с нуля»: зашли на сервер — делаете шаги по порядку. Все команды приведены для одного пользователя с правами sudo (далее в примерах — `giga`). Если будете использовать отдельного пользователя `gigabot`, в конце есть примечание.

---

## Требования

- Ubuntu 22.04
- Python 3.11+
- Рекомендуемые ресурсы: 4 vCPU, 16 GB RAM (для RAG и GigaChat)

---

## Шаг 1. Системные зависимости

**Где вы находитесь:** любой каталог (например домашний `~`).

На Ubuntu 22.04 Python 3.11 часто нет в стандартных репозиториях. Добавляем PPA [deadsnakes](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa) и ставим пакеты:

```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev libffi-dev tesseract-ocr tesseract-ocr-rus git
```

---

## Шаг 2. Клонирование репозитория

**Где вы находитесь:** домашний каталог `~` (например `/home/giga`).

Клонируем проект в каталог `~/GigaBotPresent`:

```bash
cd ~
git clone https://github.com/SoapMaker101/GigaBotPresent ~/GigaBotPresent
```

Проверьте, что появилась папка:

```bash
ls ~/GigaBotPresent
```

Должны быть папки `gigabot`, `docs`, `tech-spec` и файлы в корне.

---

## Шаг 3. Виртуальное окружение и установка пакета

**Важно:** виртуальное окружение (venv) и команда `gigabot` должны находиться **внутри каталога проекта** `~/GigaBotPresent/gigabot`, а не в домашней папке. Иначе после перезахода или смены каталога команда `gigabot` не будет найдена.

**Где вы должны быть:** каталог `~/GigaBotPresent/gigabot`. Сначала перейдите в него, затем создайте venv и установите пакет.

```bash
cd ~/GigaBotPresent/gigabot
```

Убедитесь, что вы в нужном месте (должен быть файл `pyproject.toml`):

```bash
pwd
ls pyproject.toml
```

Создаём виртуальное окружение **в этом каталоге** и ставим проект:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install hatchling
pip install -e .
```

В приглашении должно появиться `(.venv)` — окружение активно. Проверьте, что команда есть:

```bash
which gigabot
```

Должно вывести путь вида `/home/giga/GigaBotPresent/gigabot/.venv/bin/gigabot`.

---

## Как потом снова попасть в окружение

После нового подключения к серверу или смены каталога команда `gigabot` снова будет недоступна, пока вы не активируете venv. Делайте так:

```bash
cd ~/GigaBotPresent/gigabot
source .venv/bin/activate
```

После этого в приглашении будет `(.venv)` и команды `gigabot onboard`, `gigabot agent` и т.д. заработают.

**Конфиг** лежит в домашнем каталоге пользователя: `~/.gigabot/config.json` (у пользователя `giga` — это `/home/giga/.gigabot/config.json`). Редактировать его можно в любой момент, без активации venv: `nano ~/.gigabot/config.json`.

---

## Шаг 4. Конфигурация

**Где вы должны быть:** каталог `~/GigaBotPresent/gigabot`, окружение активировано (`(.venv)` в приглашении). Если только что зашли на сервер — выполните блок из раздела «Как потом снова попасть в окружение», затем команды ниже.

```bash
cd ~/GigaBotPresent/gigabot
source .venv/bin/activate
gigabot onboard
nano ~/.gigabot/config.json
```

Заполните минимум:

- **gigachat**: credentials (base64), scope, model (например GigaChat-2-Max).
- **telegram** (если нужен бот): enabled: true, token, allowFrom (список Telegram ID).

Для **режима презентации** в config.json добавьте в секцию `agent`:

```json
"agent": {
  "workspace": "~/.gigabot/workspace",
  "presentationMode": true
}
```

Сохраните файл (в nano: Ctrl+O, Enter, Ctrl+X).

---

## Шаг 5. Проверка

**Где вы должны быть:** окружение активировано (вы в `~/GigaBotPresent/gigabot` и выполнили `source .venv/bin/activate`). Либо из любого каталога:

```bash
source ~/GigaBotPresent/gigabot/.venv/bin/activate
gigabot agent -m "Привет! Кто ты?"
```

При успехе агент ответит от имени GigaBot. Дальше можно проверить сценарий по [DEMO-PRESET.md](../DEMO-PRESET.md) и [06-Scenarij-demo-CSM.md](06-Scenarij-demo-CSM.md).

---

## Шаг 6. Systemd-сервис (постоянный запуск)

**Кто выполняет:** пользователь с правами sudo (в нашем примере — `giga`). Не выполняйте эти команды от имени пользователя без sudo (например от `gigabot`, если у него нет sudo) — пароль не примется.

В репозитории есть готовый файл юнита. Скопируйте его в systemd и включите сервис. **Путь к проекту подставьте свой:** если проект в домашней папке пользователя `giga`, то каталог — `~/GigaBotPresent` (т.е. `/home/giga/GigaBotPresent`).

Команды по одной:

```bash
sudo cp ~/GigaBotPresent/docs/gigabot.service /etc/systemd/system/
```

Если появится «No such file or directory» — проект может лежать в другом месте (например у пользователя `gigabot`). Тогда используйте полный путь к файлу, например:

```bash
sudo cp /home/gigabot/GigaBotPresent/docs/gigabot.service /etc/systemd/system/
```

Либо создайте файл вручную: `sudo nano /etc/systemd/system/gigabot.service` и вставьте содержимое из файла [docs/gigabot.service](gigabot.service) (в путях замените `gigabot` на своего пользователя, если проект развёрнут под ним).

Файл юнита в репозитории настроен на пользователя `gigabot` и пути `/home/gigabot/...`. **Если вы разворачивали всё под пользователем `giga`**, после копирования отредактируйте юнит:

```bash
sudo nano /etc/systemd/system/gigabot.service
```

Замените во всём файле `gigabot` на `giga` (User=, WorkingDirectory=, ExecStart=, Environment=HOME=). Сохраните (Ctrl+O, Enter, Ctrl+X).

Затем выполните:

```bash
sudo systemctl daemon-reload
sudo systemctl enable gigabot
sudo systemctl start gigabot
```

Проверка:

```bash
sudo systemctl status gigabot
sudo journalctl -u gigabot -f
```

---

## Шаг 7. Обновление после изменений кода

**Где вы должны быть:** каталог проекта, окружение активировано.

```bash
cd ~/GigaBotPresent/gigabot
source .venv/bin/activate
git pull origin main
pip install -e .
sudo systemctl restart gigabot
```

---

## Логи и откат

- **Логи:** `sudo journalctl -u gigabot -n 100 --no-pager` или `sudo journalctl -u gigabot -f`.
- **Откат:** откатить код (git checkout / восстановить копию), снова `pip install -e .` в каталоге `~/GigaBotPresent/gigabot` с активированным venv, затем `sudo systemctl restart gigabot`.

---

## Если используете отдельного пользователя `gigabot`

- После шага 1 выполните: `sudo useradd -m -s /bin/bash gigabot`, затем войдите под ним: `su - gigabot`.
- Шаги 2–5 делайте от имени `gigabot` (проект будет в `/home/gigabot/GigaBotPresent`).
- В шаге 6 выполняйте команды с sudo от пользователя с правами админа (например снова зайдите как `giga`). Файл юнита из репозитория уже рассчитан на пользователя `gigabot` и пути `/home/gigabot/...` — менять ничего не нужно, только скопировать и выполнить `daemon-reload`, `enable`, `start`.
