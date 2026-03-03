# GigaBotPresent — пакет документации и форк для презентации CSM в Сбере

Пакет предназначен для проведения презентации перед CSM (Customer Success Manager) в Сбере: показать, как LLM встраивается в контур (аналогия Cloud.ru + GigaChat), продемонстрировать работу RAG и задач, дать язык метрик и снять «туман» перед GigaEnterprise.

**Итоговая цель презентации:** CSM понимают, как работает LLM в контуре, и при общении или планировании общения с клиентом могут опираться на продукты Сбера (в т.ч. GigaEnterprise).

---

## Структура пакета

| Путь | Назначение |
|------|------------|
| **docs/** | Документация по темам презентации и сценарий демо |
| **tech-spec/** | Техническое задание на форк GigaBot |
| **gigabot/** | Форк кода GigaBot с доработками под демо |
| **DEMO-PRESET.md** | Инструкция по подготовке демо-окружения |

---

## Документация (docs/)

| Документ | Содержание |
|----------|-------------|
| [01-Vnedrenie-LLM-v-kontur.md](docs/01-Vnedrenie-LLM-v-kontur.md) | Тема 1: внедрение LLM в контур (аналогия Cloud.ru, бизнес-процессы, боли) |
| [02-Demo-LLM-v-kliente.md](docs/02-Demo-LLM-v-kliente.md) | Тема 2: демо RAG, задач, приоритизация; пошаговые сценарии |
| [03-Metriki-vnedreniya.md](docs/03-Metriki-vnedreniya.md) | Тема 3: метрики для CSM (финансовые, операционные, стратегические) |
| [04-GigaEnterprise.md](docs/04-GigaEnterprise.md) | Тема 4: GigaEnterprise, снятие «тумана» |
| [05-Slajdy-10-priznakov.md](docs/05-Slajdy-10-priznakov.md) | Анализ слайдов: 10 признаков хорошего/плохого кейса, примитивы LLM |
| [06-Scenarij-demo-CSM.md](docs/06-Scenarij-demo-CSM.md) | Сценарий демо по шагам (тайминг 15–25 мин, ключевые фразы) |
| [07-Analitika-i-boli.md](docs/07-Analitika-i-boli.md) | Аналитика диалогов и боли (мониторинг задач, навигация по RAG) |

---

## Техзадание и форк

- **Техзадание:** [tech-spec/TZ-Fork-GigaBot-Present.md](tech-spec/TZ-Fork-GigaBot-Present.md) — критичные функции, архитектура, зависимости, доработки (отчёт по задачам, сводка аналитики, демо-пресет).
- **Форк кода:** [gigabot/](gigabot/) — копия GigaBot с добавленным tool `summary`, навыком `task_report` и обновлённым списком инструментов в контексте. Установка и запуск — как у базового GigaBot (см. [gigabot/README.md](gigabot/README.md)).

---

## Быстрый старт

1. Прочитай сценарий демо: [docs/06-Scenarij-demo-CSM.md](docs/06-Scenarij-demo-CSM.md).
2. Подготовь демо-пресет по [DEMO-PRESET.md](DEMO-PRESET.md).
3. Установи и настрой форк из папки `gigabot/` (pip install -e ., gigabot onboard, конфиг GigaChat/Telegram).
4. Проведи демо по таймингу и блокам из документа 06.

Папку GigaBotPresent можно целиком копировать в другой путь — всё необходимое для презентации и форка внутри неё.
