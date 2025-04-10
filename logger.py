

import os
import json
from datetime import datetime
from pathlib import Path

class RunLogger:
    def __init__(self, base_dir="logs/runs", run_id=None):
        timestamp = run_id or datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.run_id = timestamp
        self.run_path = Path(base_dir) / timestamp
        self.run_path.mkdir(parents=True, exist_ok=True)
        self.meta = {
            "run_id": self.run_id,
            "timestamp": datetime.now().isoformat(),
            "status": "in_progress",
            "input_query": None,
            "total_tasks": 0,
            "output_report_path": None
        }

    def log_task(self, task_index, query, urls, removed_matches, cleaned_preview):
        data = {
            "task_id": f"task_{task_index}",
            "query": query,
            "url_sources": urls,
            "removed_matches": removed_matches,
            "cleaned_content_preview": cleaned_preview[:1500] + ("..." if len(cleaned_preview) > 1500 else "")
        }
        with open(self.run_path / f"task_{task_index}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def log_report(self, report_md: str):
        report_path = self.run_path / "final_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_md)
        self.meta["output_report_path"] = str(report_path)

    def finalize(self, query: str, total_tasks: int, status="completed"):
        self.meta["input_query"] = query
        self.meta["total_tasks"] = total_tasks
        self.meta["status"] = status
        with open(self.run_path / "run_meta.json", "w", encoding="utf-8") as f:
            json.dump(self.meta, f, indent=2, ensure_ascii=False)

    def get_run_path(self):
        return str(self.run_path)