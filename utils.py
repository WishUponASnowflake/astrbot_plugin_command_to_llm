from typing import Dict, List

class CommandUtils:
    @staticmethod
    def parse_command_args(args_str: str) -> Dict[str, str]:
        """解析命令参数
        
        Args:
            args_str: 参数字符串，如 "text=hello time=08:00"
            
        Returns:
            解析后的参数字典
        """
        if not args_str:
            return {}
        
        parsed_args = {}
        parts = args_str.split()
        
        for part in parts:
            if '=' in part:
                key, value = part.split('=', 1)
                parsed_args[key.strip()] = value.strip()
            else:
                # 如果没有key=value格式，作为text参数
                if 'text' not in parsed_args:
                    parsed_args['text'] = part
                else:
                    parsed_args['text'] += ' ' + part
        
        return parsed_args

    @staticmethod
    def build_command_string(command_name: str, args: Dict[str, str]) -> str:
        """构建命令字符串
        
        Args:
            command_name: 命令名称
            args: 参数字典
            
        Returns:
            构建的命令字符串
        """
        if not args:
            return command_name
        
        args_str = ' '.join([f"{k}={v}" for k, v in args.items()])
        return f"{command_name} {args_str}"

    @staticmethod
    def validate_mapping(command_name: str, llm_function: str) -> List[str]:
        """验证映射参数
        
        Args:
            command_name: 命令名称（支持多级指令，如 "rmd ls"）
            llm_function: LLM函数名称
            
        Returns:
            错误信息列表，空列表表示验证通过
        """
        errors = []
        
        if not command_name or not command_name.strip():
            errors.append("命令名称不能为空")
        
        if not llm_function or not llm_function.strip():
            errors.append("LLM函数名称不能为空")
        
        # 移除空格验证，因为多级指令名可以包含空格
        # if command_name and ' ' in command_name:
        #     errors.append("命令名称不能包含空格")
        
        return errors 