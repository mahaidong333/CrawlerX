import os
import json
import threading
from datetime import datetime

class TaskManager:
    def __init__(self, data_dir="data/tasks"):
        self.data_dir = data_dir
        self.lock = threading.Lock()
        self.task_counter = self._load_task_counter()
        
    def _load_task_counter(self):
        """从文件加载任务计数器"""
        counter_file = os.path.join(self.data_dir, "task_counter.json")
        try:
            if os.path.exists(counter_file):
                with open(counter_file, "r") as f:
                    return int(json.load(f).get("counter", 0))
        except Exception:
            pass
        return 0  # 默认从0开始

    def _save_task_counter(self):
        """保存任务计数器到文件"""
        os.makedirs(self.data_dir, exist_ok=True)
        counter_file = os.path.join(self.data_dir, "task_counter.json")
        with open(counter_file, "w") as f:
            json.dump({"counter": self.task_counter}, f)

    def create_task(self, config):
        """创建新任务并生成唯一ID"""
        with self.lock:
            self.task_counter += 1
            task_id = f"task_{self.task_counter}"
            self._save_task_counter()
        
        # 创建任务目录
        task_dir = os.path.join(self.data_dir, task_id)
        os.makedirs(task_dir, exist_ok=True)
        
        # 保存任务配置
        config_path = os.path.join(task_dir, "config.json")
        with open(config_path, "w") as f:
            json.dump(config, f)
            
        return task_id

    def get_task_summary(self):
        """获取任务摘要信息（确保结果为数字）"""
        summary = {
            "total": 0,
            "completed": 0,
            "running": 0,
            "failed": 0,
            "results": 0  # 确保这是数字
        }
        
        for task_id in os.listdir(self.data_dir):
            task_path = os.path.join(self.data_dir, task_id)
            if not os.path.isdir(task_path):
                continue
                
            status_file = os.path.join(task_path, "status.json")
            if os.path.exists(status_file):
                with open(status_file, "r") as f:
                    task_status = json.load(f)
                    
                # 确保结果计数是整数
                result_count = task_status.get("result_count", 0)
                if not isinstance(result_count, (int, float)):
                    # 如果结果计数不是数字，尝试转换或设为0
                    try:
                        result_count = int(result_count)
                    except (TypeError, ValueError):
                        result_count = 0
                
                summary["results"] += result_count
                summary[task_status["status"].lower()] += 1
                summary["total"] += 1
        
        return summary

    def get_tasks_by_status(self, status):
        """获取指定状态的任务ID列表"""
        tasks = []
        for task_id in os.listdir(self.data_dir):
            task_dir = os.path.join(self.data_dir, task_id)
            if not os.path.isdir(task_dir):
                continue
                
            status_file = os.path.join(task_dir, "status.json")
            if os.path.exists(status_file):
                with open(status_file, "r") as f:
                    task_status = json.load(f)
                    if task_status.get("status") == status:
                        tasks.append(task_id)
        return tasks
    
    def get_task_info(self, task_id):
        """获取任务详细信息"""
        task_dir = os.path.join(self.data_dir, task_id)
        if not os.path.isdir(task_dir):
            return None
            
        info = {}
        
        # 加载状态
        status_file = os.path.join(task_dir, "status.json")
        if os.path.exists(status_file):
            with open(status_file, "r") as f:
                info.update(json.load(f))
        
        # 加载配置
        config_file = os.path.join(task_dir, "config.json")
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                info["config"] = json.load(f)
        
        # 加载结果
        results_file = os.path.join(task_dir, "results.json")
        if os.path.exists(results_file):
            with open(results_file, "r") as f:
                info["results"] = json.load(f)
        
        return info