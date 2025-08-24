import os
import json
import datetime
from typing import Dict, Tuple
from astrbot.api.star import Context
from astrbot.api import logger
from .utils import CommandUtils

class DataManager:
    def __init__(self, context: Context):
        self.context = context
        
        # 使用data目录下的数据文件
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
        os.makedirs(os.path.join(data_dir, "command_to_llm"), exist_ok=True)
        self.data_file = os.path.join(data_dir, "command_to_llm", "command_mappings.json")
        
        # 加载指令映射配置
        self.command_mappings = self.load_command_mappings()

    def load_command_mappings(self) -> Dict[str, Dict]:
        """加载指令映射配置"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载指令映射配置失败: {e}")
                return {}
        return {}

    def save_command_mappings(self):
        """保存指令映射配置"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.command_mappings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存指令映射配置失败: {e}")

    def add_mapping(self, command_name: str, llm_function: str, description: str = "") -> Tuple[bool, str]:
        """添加指令映射
        
        Returns:
            (success, message): 成功状态和消息
        """
        logger.info(f"[data_manager] add_mapping 被调用 - 指令: '{command_name}', 函数: '{llm_function}', 描述: '{description}'")
        
        # 验证参数
        errors = CommandUtils.validate_mapping(command_name, llm_function)
        if errors:
            logger.warning(f"[data_manager] 参数验证失败: {errors}")
            return False, f"参数验证失败: {'; '.join(errors)}"
        
        if command_name in self.command_mappings:
            logger.warning(f"[data_manager] 指令已存在: {command_name}")
            return False, f"指令 '{command_name}' 已存在映射"
        
        logger.info(f"[data_manager] 开始添加映射")
        self.command_mappings[command_name] = {
            "llm_function": llm_function,
            "description": description,
            "created_at": str(datetime.datetime.now())
        }
        
        logger.info(f"[data_manager] 保存映射配置")
        self.save_command_mappings()
        logger.info(f"[data_manager] 映射添加完成")
        return True, f"成功添加指令映射：'{command_name}' -> '{llm_function}'"

    def remove_mapping(self, command_name: str) -> bool:
        """删除指令映射"""
        if command_name not in self.command_mappings:
            return False
        
        del self.command_mappings[command_name]
        self.save_command_mappings()
        return True

    def get_mapping(self, command_name: str) -> Dict:
        """获取指令映射"""
        return self.command_mappings.get(command_name, {})

    def list_mappings(self) -> Dict[str, Dict]:
        """列出所有指令映射"""
        return self.command_mappings.copy() 