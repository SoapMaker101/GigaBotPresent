"""Summary tool — сводка по проектам, задачам и базам знаний для демо CSM."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gigabot.agent.tools.base import Tool
from gigabot.config.schema import RAGConfig


class SummaryTool(Tool):
    """Сводка: проекты (папки), задачи, базы знаний RAG. Для аналитики и демо."""

    def __init__(self, workspace: Path, rag_config: RAGConfig) -> None:
        self._workspace = Path(workspace).expanduser().resolve()
        self._rag_config = rag_config
        self._tasks_file = self._workspace.parent / "tasks" / "tasks.json"

    @property
    def name(self) -> str:
        return "summary"

    @property
    def description(self) -> str:
        return "Сводка по контуру: список проектов (папок), задачи (краткая статистика), базы знаний RAG (проекты и объёмы). Используй для ответа на запросы «что загружено», «какие задачи», «что в базах знаний», «аналитика»."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }

    async def execute(self, **kwargs: Any) -> str:
        parts: list[str] = []

        # Проекты (папки в workspace/projects)
        projects_root = self._workspace / "projects"
        if projects_root.exists():
            dirs = [d.name for d in projects_root.iterdir() if d.is_dir()]
            if dirs:
                parts.append("## Проекты (папки)\n" + "\n".join(f"  • {d}" for d in sorted(dirs)))
            else:
                parts.append("## Проекты (папки)\n  Нет проектов.")
        else:
            parts.append("## Проекты (папки)\n  Папка projects не найдена.")

        # Задачи
        tasks_summary = self._tasks_summary()
        parts.append("## Задачи\n" + tasks_summary)

        # Базы знаний RAG
        rag_summary = self._rag_summary()
        parts.append("## Базы знаний (RAG)\n" + rag_summary)

        return "\n\n".join(parts)

    def _tasks_summary(self) -> str:
        if not self._tasks_file.exists():
            return "  Нет файла задач (tasks.json)."
        try:
            data = json.loads(self._tasks_file.read_text(encoding="utf-8"))
            tasks = data.get("tasks", [])
        except Exception:
            return "  Ошибка чтения tasks.json."
        if not tasks:
            return "  Задач нет."
        by_status: dict[str, int] = {}
        for t in tasks:
            s = t.get("status", "todo")
            by_status[s] = by_status.get(s, 0) + 1
        lines = [f"  Всего задач: {len(tasks)}"]
        for status, count in sorted(by_status.items()):
            lines.append(f"  — {status}: {count}")
        return "\n".join(lines)

    def _rag_summary(self) -> str:
        try:
            import chromadb
        except ImportError:
            return "  ChromaDB недоступен."
        chroma_dir = str(Path(self._rag_config.chroma_dir).expanduser())
        try:
            client = chromadb.PersistentClient(path=chroma_dir)
            raw = client.list_collections()
        except Exception as e:
            return f"  Ошибка RAG: {e}"
        if not raw:
            return "  Нет созданных баз знаний."
        names = [c.name if isinstance(c, str) else c.name for c in raw]
        lines: list[str] = []
        for name in sorted(names):
            try:
                col = client.get_collection(name)
                display = (col.metadata or {}).get("display_name", name)
                lines.append(f"  • {display}: {col.count()} фрагментов")
            except Exception:
                lines.append(f"  • {name}: ?")
        return "\n".join(lines) if lines else "  Нет данных."
