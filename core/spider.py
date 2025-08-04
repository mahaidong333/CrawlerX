class Spider:
    """所有爬虫插件的基类"""
    name = "base_spider"  # 添加默认名称属性
    
    def __init__(self, config):
        self.config = config
    
    def run(self):
        raise NotImplementedError("子类必须实现run方法")
    
    

    def save_results(self, results):
        """保存爬取结果并更新计数"""
        task_id = self.config.get("task_id", "unknown")
        output_dir = os.path.join("data", "tasks", task_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # 确保结果计数是整数
        if not isinstance(results, (int, float)):
            result_count = len(results) if hasattr(results, '__len__') else 0
        else:
            result_count = results
        
        # 保存结果文件
        output_file = os.path.join(output_dir, "results.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "count": result_count,
                "items": results if not isinstance(results, (int, float)) else []
            }, f, ensure_ascii=False, indent=2)
        
        # 更新任务状态文件
        status_file = os.path.join(output_dir, "status.json")
        with open(status_file, "r+") as f:
            status_data = json.load(f)
            status_data["result_count"] = result_count
            status_data["status"] = "COMPLETED"
            f.seek(0)
            json.dump(status_data, f)
            f.truncate()
        
        print(f"已保存 {result_count} 条结果到 {output_file}")
        return result_count