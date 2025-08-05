import logging
from flask import Flask, render_template, jsonify, request
import threading
import time
from datetime import datetime, timedelta
import json
from markupsafe import Markup
from flask import Flask, render_template, request, jsonify
from core.task_manager import TaskManager  # 导入 TaskManager
from core.engine import CrawlerEngine
import os
from flask import g


# 初始化应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# 初始化爬虫引擎
engine = CrawlerEngine()

# 创建日志记录器
logger = logging.getLogger("web.app")
task_manager = TaskManager(data_dir="data/tasks")

# ===============================================
# 模板过滤器函数
# ===============================================

def _schedule_tasks(self):
    """任务调度循环"""
    while True:
        # 检查新任务并加入队列
        self._check_pending_tasks()
        time.sleep(1)  # 每秒检查一次

def _check_pending_tasks(self):
    """检查待处理任务"""
    pending_tasks = self.task_manager.get_tasks_by_status("PENDING")
    for task_id in pending_tasks:
        self.logger.info(f"发现待处理任务: {task_id}")
        self.task_queue.put(task_id)
        self._update_task_status(task_id, "QUEUED", "等待执行")

# 在现有过滤器后添加
def tojson_filter(value):
    """将对象转换为JSON字符串"""
    return Markup(json.dumps(value, ensure_ascii=False))

def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
    """格式化日期时间"""
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value)
            return dt.strftime(format)
        except ValueError:
            return value
    elif isinstance(value, datetime):
        return value.strftime(format)
    return value

def to_datetime(value):
    """转换为 datetime 对象"""
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
    return value

def format_duration(duration):
    """格式化时间间隔"""
    if not isinstance(duration, timedelta):
        return "N/A"

    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if hours:
        parts.append(f"{hours}小时")
    if minutes:
        parts.append(f"{minutes}分钟")
    if seconds or not parts:
        parts.append(f"{seconds}秒")

    return " ".join(parts)

# 注册模板过滤器
app.jinja_env.filters['format_datetime'] = format_datetime
app.jinja_env.filters['to_datetime'] = to_datetime
app.jinja_env.filters['format_duration'] = format_duration
# ===============================================

# 注册新的模板过滤器
app.jinja_env.filters['tojson'] = tojson_filter


def initialize_web(engine_instance):
    """初始化 Web 界面"""
    global engine
    engine = engine_instance
    logger.info("Web 界面已初始化")

    # 确保任务处理线程正确启动
def task_worker():
    """任务处理工作线程"""
    logger.info("任务工作线程已启动")
    while True:
        try:
            # 从引擎队列获取任务
            task_id = engine.task_queue.get()
            if task_id is None:  # 安全退出机制
                break

            logger.info(f"开始处理任务: {task_id}")

            # 更新任务状态为运行中
            engine._update_task_status(task_id, "RUNNING", "正在执行")

            # 执行任务
            engine.execute_task(task_id)

            logger.info(f"任务完成: {task_id}")

        except Exception as e:
            logger.error(f"任务处理异常: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

        finally:
            engine.task_queue.task_done()


@app.before_request
def before_request():
    if 'engine' not in g:
        g.engine = CrawlerEngine()

@app.route('/run_task', methods=['POST'])
def run_task():
    task_config = request.json
    try:
        result = g.engine.execute_task(task_config)
        return jsonify({"status": "running", "task_id": "task_123"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def check_engine_initialized():
    """确保引擎已初始化"""
    if engine is None and request.endpoint not in ['static', 'health']:
        return "引擎未初始化。请稍候或重启应用。", 500

@app.route('/')
def dashboard():
    """仪表盘视图"""
    # 获取任务摘要
    summary = task_manager.get_task_summary()

    # 获取已完成和运行中的任务详情
    completed_tasks = []
    running_tasks = []

    # 遍历所有任务目录
    for task_id in os.listdir(task_manager.data_dir):
        task_dir = os.path.join(task_manager.data_dir, task_id)
        if not os.path.isdir(task_dir):
            continue

        # 加载任务状态
        status_file = os.path.join(task_dir, "status.json")
        if os.path.exists(status_file):
            with open(status_file, "r") as f:
                task_status = json.load(f)

            # 确保结果计数是整数
            result_count = task_status.get("result_count", 0)
            if not isinstance(result_count, (int, float)):
                try:
                    result_count = int(result_count)
                except (TypeError, ValueError):
                    result_count = 0

            task_info = {
                "id": task_id,
                "name": task_status.get("name", "未命名任务"),
                "status": task_status["status"],
                "results": result_count,
                "created": task_status.get("created_time", ""),
                "updated": task_status.get("update_time", "")
            }

            if task_status["status"] == "COMPLETED":
                completed_tasks.append(task_info)
            elif task_status["status"] == "RUNNING":
                running_tasks.append(task_info)

    return render_template('dashboard.html',
                           summary=summary,
                           completed_tasks=completed_tasks,
                           running_tasks=running_tasks)



@app.route('/create_task', methods=['GET', 'POST'])
def create_task():
    try:
        headers_json = request.form.get('headers', '{}')
        # 空值处理
        if not headers_json.strip():
            headers = {}
        else:
            headers = json.loads(headers_json)
            # 类型验证
            if not isinstance(headers, dict):
                raise ValueError("请求头必须是字典对象")

            # 值类型验证
            for key, value in headers.items():
                if not isinstance(value, str):
                    raise ValueError(
                        f"请求头值类型错误: 键 '{key}' 的值必须是字符串类型"
                    )

        """创建新爬虫任务"""
        if request.method == 'GET':
            return render_template('create_task.html')

        # 处理表单提交
        spider_name = request.form['spider']
        urls = [url.strip() for url in request.form['urls'].split('\n') if url.strip()]

        # 构建配置
        config = {}
        headers_value = request.form.get('headers', '').strip()
        if headers_value:
            try:
                config['headers'] = json.loads(headers_value)
            except json.JSONDecodeError as e:
                return jsonify({
                    "status": "error",
                    "message": f"无效的请求头JSON格式: {str(e)}"
                }), 400

        if request.form.get('timeout'):
            try:
                config['timeout'] = int(request.form['timeout'])
            except ValueError:
                pass

        # 创建任务
        task_id = engine.create_task(spider_name, urls, config)
        return jsonify({
            "status": "success",
            "task_id": task_id,
            "message": f"任务已创建，正在处理 {len(urls)} 个URL"
        })

    except json.JSONDecodeError as e:
            # 精准定位错误位置
            error_line = e.doc.splitlines()[e.lineno - 1]
            pointer = ' ' * (e.colno - 1) + '^'
            return jsonify({
                'status': 'error',
                'message': f'JSON格式错误: {e.msg}',
                'detail': f"{error_line}\n{pointer}"
            }), 400
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/task/<task_id>')
def task_detail(task_id):
    """任务详情页面"""
    task = engine.get_task_status(task_id)
    return render_template('task_detail.html', task=task)

@app.route('/api/tasks')
def get_tasks_api():
    """获取所有任务的API接口"""
    tasks = engine.get_all_tasks()
    return jsonify(tasks)

@app.route('/api/task/<task_id>')
def get_task_api(task_id):
    """获取单个任务详情的API接口"""
    task = engine.get_task_status(task_id)
    return jsonify(task)

@app.route('/download/<task_id>')
def download_results(task_id):
    """下载任务结果"""
    task = engine.get_task_status(task_id)
    if "error" in task:
        return jsonify({"error": "任务未找到"}), 404

    if task["status"] != "completed":
        return jsonify({"error": "任务未完成"}), 400

    # 在实际应用中，这里应该生成文件
    return jsonify({
        "status": "success",
        "task_id": task_id,
        "results": task["results"]
    })

@app.route('/health')
def health_check():
    """健康检查端点"""
    return jsonify({
        "status": "ok",
        "engine_initialized": engine is not None
    })

def execute_task(self, task_id):
        """执行爬虫任务"""
        try:
            self.logger.info(f"开始执行任务: {task_id}")

            # 加载任务配置
            task_config = self._load_task_config(task_id)
            self.logger.debug(f"任务配置: {task_config}")

            # 获取爬虫类
            spider_name = task_config.get("spider", "basic").strip().lower()
            spider_cls = self.plugin_manager.get_spider(spider_name)

            if not spider_cls:
                error_msg = f"爬虫 '{spider_name}' 未找到"
                self.logger.error(error_msg)
                raise ValueError(error_msg)

            # 添加任务ID到配置
            task_config["task_id"] = task_id

            # 实例化并运行爬虫
            spider = spider_cls(task_config)
            result_count = spider.run()

            self.logger.info(f"任务完成: {task_id}, 结果数: {result_count}")

            # 更新任务状态
            self._update_task_status(task_id, "COMPLETED", f"抓取完成，共 {result_count} 条结果")

        except Exception as e:
            self.logger.error(f"任务失败: {task_id}\n{str(e)}\n{traceback.format_exc()}")
            self._update_task_status(task_id, "FAILED", str(e))


if __name__ == '__main__':
    app.run(debug=True)