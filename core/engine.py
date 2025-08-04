from .plugin_manager import PluginManager
import time
from datetime import datetime
from collections import deque
import logging
import threading
from .task_manager import TaskManager



class CrawlerEngine:
    def __init__(self):
        self.active_tasks = {}
        self.completed_tasks = deque(maxlen=100)
        self.task_queue = deque()
        self.task_id_counter = 0
        self.task_history = {}
        self.task_lock = threading.Lock()
        self.plugin_manager = PluginManager()
        self.task_manager = TaskManager()
        
        # 初始化插件管理器
        self.plugin_manager = PluginManager()
        self.plugin_manager.load_plugins()
        
        # 启动任务处理线程
        self.worker_thread = threading.Thread(target=self._task_worker, daemon=True)
        self.worker_thread.start()
        logging.getLogger("engine").info("任务处理线程已启动")

    def _schedule_tasks(self):
        """任务调度循环"""
        while True:
            # 检查新任务并加入队列
            self._check_pending_tasks()
            time.sleep(1)  # 每秒检查一次

    def _task_worker(self):
        """后台任务处理线程"""
        while True:
            try:
                if self.task_queue:
                    task_id = self.task_queue.popleft()
                    self.run_task(task_id)
                time.sleep(1)
            except Exception as e:
                logging.getLogger("engine").error(f"任务处理错误: {str(e)}")
        
    def create_task(self, spider_name, urls, config=None):
        """创建新爬虫任务"""
        with self.task_lock:
            task_id = f"task_{self.task_id_counter}"
            self.task_id_counter += 1
            
            task = {
                "id": task_id,
                "spider": spider_name,
                "urls": urls,
                "config": config or {},
                "status": "queued",
                "created_at": datetime.now().isoformat(),
                "start_time": None,
                "end_time": None,
                "results": [],
                "progress": 0,
                "error": None
            }
            self.task_queue.append(task_id)
            self.active_tasks[task_id] = task
            self.task_history[task_id] = task
            return task_id
    def run_task(self, task_id):
        """执行爬虫任务"""
        task = self.active_tasks.get(task_id)
        if not task:
            return
    
        try:
            # 更新任务状态
            task["status"] = "running"
            task["start_time"] = datetime.now().isoformat()
        
            # 获取爬虫实例
            spider = self.plugin_manager.get_spider(task["spider"])
            if not spider:
                raise ValueError(f"爬虫 '{task['spider']}' 未找到")
        
            # 初始化爬虫
            spider.setup(task.get("config", {}))
        
            # 执行爬取任务
            total_urls = len(task["urls"])
            for i, url in enumerate(task["urls"]):
                # 更新进度
                progress = int((i + 1) / total_urls * 100)
                task["progress"] = progress
            
                # 执行爬取
                try:
                    result = spider.crawl(url)
                    task["results"].append(result)
                    logging.getLogger("engine").info(f"已爬取: {url} - 状态: {result.get('status', 'unknown')}")
                except Exception as e:
                    error_result = {
                        "url": url,
                        "status": "error",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                    task["results"].append(error_result)
                    logging.getLogger("engine").error(f"爬取失败: {url} - {str(e)}")
            
                # 避免过快请求
                time.sleep(0.5)
        
            # 任务完成
            task["status"] = "completed"
            task["progress"] = 100
    
        except Exception as e:
            task["status"] = "failed"
            task["error"] = str(e)
            logging.getLogger("engine").error(f"任务失败: {task_id} - {str(e)}")
    
        finally:
            # 清理资源
            if spider:
                try:
                    spider.teardown()
                except Exception as e:
                    logging.getLogger("engine").error(f"清理资源失败: {str(e)}")
        
            # 更新结束时间
            task["end_time"] = datetime.now().isoformat()
        
            # 移动到已完成
            self.completed_tasks.append(task)
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]


    
    def get_task_status(self, task_id):
        """获取任务状态"""
        # 先在活动任务中查找
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
        
        # 在已完成任务中查找
        for task in self.completed_tasks:
            if task["id"] == task_id:
                return task
        
        # 在历史记录中查找
        if task_id in self.task_history:
            return self.task_history[task_id]
        
        return {"error": "Task not found"}
    
    def get_all_tasks(self):
        """获取所有任务状态"""
        return {
            "active": list(self.active_tasks.values()),
            "completed": list(self.completed_tasks),
            "queued": list(self.task_queue)
        }
    
    def run_next_task(self):
        """执行队列中的下一个任务"""
        if not self.task_queue:
            return
        
        task_id = self.task_queue.popleft()
        task = self.active_tasks[task_id]
        
        # 更新任务状态
        task["status"] = "running"
        task["start_time"] = datetime.now().isoformat()
        
        # 这里应该是实际爬虫执行逻辑
        # 示例：模拟任务执行
        for i in range(1, 11):
            time.sleep(0.5)  # 模拟处理延迟
            task["progress"] = i * 10
            
            # 模拟结果生成
            if i % 2 == 0:
                task["results"].append({
                    "url": f"https://example.com/page/{i}",
                    "data": f"Sample data {i}",
                    "timestamp": datetime.now().isoformat()
                })
        
        # 任务完成
        task["status"] = "completed"
        task["end_time"] = datetime.now().isoformat()
        task["progress"] = 100
        
        # 移动到已完成
        self.completed_tasks.append(task)
        del self.active_tasks[task_id]
        
    def get_task_history(self):
        """获取所有任务历史记录"""
        return list(self.task_history.values())

    def execute_task(self, task_id):
        try:
            logger.info(f"开始执行任务: {task_id}")
        
            # 加载任务配置
            task_config = self._load_task_config(task_id)
            logger.debug(f"任务配置: {task_config}")
        
            # 获取爬虫类
            spider_name = task_config.get("spider", "basic").strip().lower()
            spider_cls = self.plugin_manager.get_spider(spider_name)
        
            if not spider_cls:
                error_msg = f"爬虫 '{spider_name}' 未找到"
                logger.error(error_msg)
                raise ValueError(error_msg)
        
            # 实例化并运行爬虫
            spider = spider_cls(task_config)
            result_count = spider.run()
            logger.info(f"任务完成: {task_id}, 结果数: {result_count}")
        
            # 更新任务状态
            self._update_task_status(task_id, "COMPLETED", result_count=result_count)
        
        except Exception as e:
            logger.error(f"任务失败: {task_id}\n{str(e)}\n{traceback.format_exc()}")
            self._update_task_status(task_id, "FAILED", str(e))

    def _update_task_status(self, task_id, status, message=None):
        """更新任务状态"""
        task_dir = os.path.join(self.task_manager.data_dir, task_id)
        os.makedirs(task_dir, exist_ok=True)
        
        status_file = os.path.join(task_dir, "status.json")
        status_data = {
            "task_id": task_id,
            "status": status,
            "update_time": datetime.now().isoformat()
        }
        
        if message:
            status_data["message"] = message
            
        with open(status_file, "w") as f:
            json.dump(status_data, f)