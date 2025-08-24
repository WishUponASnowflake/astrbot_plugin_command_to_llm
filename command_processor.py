import asyncio
from astrbot.api.event import AstrMessageEvent
from astrbot.api import logger
from astrbot.api.message_components import Plain
from .data_manager import DataManager
from .utils import CommandUtils
from .command_executor import CommandExecutor

class CommandProcessor:
    def __init__(self, star_instance):
        self.star = star_instance
        self.context = star_instance.context
        self.data_manager = star_instance.data_manager
        self.command_executor = CommandExecutor(self.context)

    async def execute_command(self, event, command_text: str, args: str = "") -> str:
        """执行指令"""
        try:
            # 查找指令映射
            mapping = self.data_manager.get_mapping(command_text)
            if not mapping:
                return f"错误：未找到指令 '{command_text}' 的映射。请先使用 add_command_mapping 添加映射。"
            
            llm_function = mapping.get("llm_function")
            description = mapping.get("description", "")
            
            logger.info(f"执行指令映射: {command_text} -> {llm_function}")
            
            # 构建完整指令
            full_command = f"/{command_text}"
            if args:
                full_command += f" {args}"
            
            # 获取用户信息
            creator_id = event.get_sender_id() if hasattr(event, 'get_sender_id') else "user"
            creator_name = None
            if hasattr(event, 'message_obj') and hasattr(event.message_obj, 'sender'):
                creator_name = event.message_obj.sender.nickname
            
            # 使用指令执行器执行指令
            success, captured_messages = await self.command_executor.execute_command(
                event.unified_msg_origin, full_command, creator_id, creator_name
            )
            
            if success and captured_messages:
                # 主动发送转发消息（类似旧插件的机制）
                logger.info(f"[command_processor] 开始主动发送转发消息")
                
                for i, captured_msg in enumerate(captured_messages):
                    if captured_msg is not None:
                        logger.info(f"[command_processor] 发送第 {i+1} 条转发消息")
                        
                        # 构建转发消息
                        from astrbot.core.message.message_event_result import MessageChain
                        from astrbot.api.message_components import Plain
                        
                        forward_msg = MessageChain()
                        forward_msg.chain.append(Plain(f"[指令执行] {command_text}\n"))
                        
                        # 添加捕获到的消息内容
                        if hasattr(captured_msg, 'chain') and captured_msg.chain:
                            for component in captured_msg.chain:
                                forward_msg.chain.append(component)
                        
                        # 发送转发消息
                        await self.context.send_message(event.unified_msg_origin, forward_msg)
                        
                        # 如果有多条消息，添加间隔
                        if len(captured_messages) > 1 and i < len(captured_messages) - 1:
                            await asyncio.sleep(0.5)
                
                # 提取响应文本用于返回给LLM函数
                response_texts = []
                for msg_chain in captured_messages:
                    if msg_chain is not None:
                        # 尝试不同的方法获取文本
                        text = None
                        if hasattr(msg_chain, 'get_plain_text'):
                            text = msg_chain.get_plain_text()
                        elif hasattr(msg_chain, 'to_plain_text'):
                            text = msg_chain.to_plain_text()
                        elif hasattr(msg_chain, 'chain') and msg_chain.chain:
                            # 手动提取文本
                            text_parts = []
                            for component in msg_chain.chain:
                                if hasattr(component, 'text'):
                                    text_parts.append(component.text)
                                elif hasattr(component, 'content'):
                                    text_parts.append(component.content)
                            text = ''.join(text_parts) if text_parts else None
                        
                        if text:
                            response_texts.append(text)
                
                if response_texts:
                    return f"指令 '{command_text}' 执行结果：\n" + "\n".join(response_texts)
                else:
                    return f"指令 '{command_text}' 执行成功，但未返回文本内容"
            else:
                return f"指令 '{command_text}' 执行失败或超时"
                
        except Exception as e:
            logger.error(f"执行指令失败: {e}")
            return f"执行指令时发生错误：{str(e)}"





    async def add_mapping(self, event, command_name: str, llm_function: str, description: str = ""):
        """添加指令映射"""
        logger.info(f"[command_processor] add_mapping 被调用 - 指令: '{command_name}', 函数: '{llm_function}', 描述: '{description}'")
        
        try:
            success, message = self.data_manager.add_mapping(command_name, llm_function, description)
            logger.info(f"[command_processor] data_manager.add_mapping 返回: success={success}, message='{message}'")
            
            if success:
                logger.info(f"[command_processor] 开始刷新动态LLM函数")
                # 刷新动态LLM函数
                self.star.dynamic_llm_manager.refresh_functions()
                logger.info(f"[command_processor] 动态LLM函数刷新完成")
            
            yield event.plain_result(message)
            
        except Exception as e:
            logger.error(f"[command_processor] 添加指令映射失败: {e}")
            import traceback
            logger.error(f"[command_processor] 错误堆栈:\n{traceback.format_exc()}")
            yield event.plain_result(f"添加指令映射时发生错误：{str(e)}")

    async def list_mappings(self, event):
        """列出所有指令映射"""
        try:
            mappings = self.data_manager.list_mappings()
            if not mappings:
                yield event.plain_result("当前没有配置任何指令映射")
                return
            
            result = "当前配置的指令映射：\n"
            for i, (cmd, mapping) in enumerate(mappings.items(), 1):
                llm_func = mapping.get("llm_function", "")
                desc = mapping.get("description", "")
                result += f"{i}. {cmd} -> {llm_func}"
                if desc:
                    result += f" ({desc})"
                result += "\n"
            
            yield event.plain_result(result)
        except Exception as e:
            logger.error(f"列出指令映射失败: {e}")
            yield event.plain_result(f"列出指令映射时发生错误：{str(e)}")

    async def remove_mapping(self, event, command_name: str):
        """删除指令映射"""
        try:
            success = self.data_manager.remove_mapping(command_name)
            if success:
                # 刷新动态LLM函数
                self.star.dynamic_llm_manager.refresh_functions()
                yield event.plain_result(f"成功删除指令映射：'{command_name}'")
            else:
                yield event.plain_result(f"错误：指令 '{command_name}' 不存在映射")
        except Exception as e:
            logger.error(f"删除指令映射失败: {e}")
            yield event.plain_result(f"删除指令映射时发生错误：{str(e)}") 