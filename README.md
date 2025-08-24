# 指令转LLM插件

这个插件允许你将各种指令转换为LLM函数调用，让AI能够在对话中主动执行指令并获取响应。拆分自隔壁插件[ai-reminder](https://github.com/kjqwer/astrbot_plugin_sy)独立出来作为一个功能。

## 功能特性

- 🔄 将指令映射为LLM函数调用
- 📝 支持动态添加和管理指令映射
- 🎯 支持指令参数传递
- 💾 持久化存储指令映射配置
- 🛠️ 提供完整的命令行管理工具

## 快速开始

### 1. 添加指令映射

首先，你需要将现有的指令映射为LLM函数：

```
/cmd2llm add rmd--ls list_reminders 列出所有提醒
```

![添加指令映射](https://sywb.top/Staticfiles/pic/command1.png)

### 2. AI调用指令

映射完成后，AI就可以通过LLM函数调用这些指令：

![AI调用指令](https://sywb.top/Staticfiles/pic/command2.png)

## 使用方法

### 命令行操作

#### 添加指令映射
```
/cmd2llm add <指令名> <LLM函数名> [描述]
```

指令名格式：
- 单个指令：`rmd`
- 多级指令：`rmd--ls`, `rmd--add`, `rmd--help`
- 支持任意数量的 `--` 连接

示例：
```
/cmd2llm add rmd--ls list_reminders 列出所有提醒
/cmd2llm add rmd--help show_help 显示提醒帮助
/cmd2llm add weather get_weather 获取天气信息
```

#### 列出所有映射
```
/cmd2llm ls
```

输出示例：
```
当前配置的指令映射：
1. rmd ls -> list_reminders (列出所有提醒)
2. rmd help -> show_help (显示提醒帮助)
3. weather -> get_weather (获取天气信息)
```

#### 删除映射
```
/cmd2llm rm <指令名>
```

注意：删除时需要使用完整的指令名，例如：
- 删除 `rmd--ls` 映射：`/cmd2llm rm rmd--ls`
- 删除 `weather` 映射：`/cmd2llm rm weather`

#### 执行指令
```
/cmd2llm exec <指令名> [参数]
```

示例：
```
/cmd2llm exec rmd--ls
/cmd2llm exec rmd--add text=喝水 time=10:00
```

#### 显示帮助
```
/cmd2llm help
```

### LLM函数调用

插件提供了以下LLM函数供AI调用：

#### execute_command
执行指定的指令
- `command_text`: 要执行的指令，如 "rmd ls"
- `args`: 指令参数，可选

#### add_command_mapping
添加指令映射
- `command_name`: 指令名称，如 "rmd ls"
- `llm_function`: 对应的LLM函数名称
- `description`: 指令描述

#### list_command_mappings
列出所有指令映射

#### remove_command_mapping
删除指令映射
- `command_name`: 要删除的指令名称

### 动态LLM函数

插件会自动为每个指令映射注册对应的LLM函数：

- 映射 `rmd ls` → `list_reminders` 会注册 `list_reminders` 函数
- 映射 `rmd help` → `show_help` 会注册 `show_help` 函数
- 映射 `weather` → `get_weather` 会注册 `get_weather` 函数

这些动态函数会被系统识别，AI可以直接调用它们。

## 配置说明

插件会在 `data/command_to_llm/command_mappings.json` 文件中保存指令映射配置，格式如下：

```json
{
  "rmd ls": {
    "llm_function": "list_reminders",
    "description": "列出所有提醒",
    "created_at": "2024-01-01 12:00:00"
  },
  "weather": {
    "llm_function": "get_weather",
    "description": "获取天气信息",
    "created_at": "2024-01-01 12:00:00"
  }
}
```

## 注意事项

1. **指令映射是全局的**，所有会话共享
2. **指令名称区分大小写**
3. **确保映射的LLM函数确实存在**，否则执行时会失败
4. **建议为每个映射添加清晰的描述**，帮助AI理解指令用途
5. **删除映射时使用完整的指令名**，包括 `--` 分隔符
6. **插件会自动处理多平台适配**，支持各种消息平台

## 常见问题

删除时需要使用完整的指令名。例如，如果映射是 `rmd--ls`，删除时也要用 `rmd--ls`，不能用 `rmd ls` 或 `rmd`。


## 作者

- 作者：kjqwdw
- 版本：v1.0.0

## 支持

如需帮助，请参考 [AstrBot插件开发文档](https://astrbot.soulter.top/center/docs/%E5%BC%80%E5%8F%91/%E6%8F%92%E4%BB%B6%E5%BC%80%E5%8F%91/)

## 问题反馈

如有问题或建议，请访问以下地址反馈：
[反馈](https://github.com/kjqwer/astrbot_plugin_command_to_llm/issues)