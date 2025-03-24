from langchain.agents import Tool, initialize_agent, AgentExecutor
from langchain_community.llms import Ollama
from langchain.agents.agent_types import AgentType
from tools.terminal_simulator import simulate_terminal, send_message
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

# 定义结构化响应模型
class ActionResponse(BaseModel):
    action: str = Field(description="要执行的动作名称，必须是SendMessage或TerminalExecute")
    action_input: str = Field(description="动作的输入内容，根据动作类型不同而不同")

# 配置JSON解析器
parser = PydanticOutputParser(pydantic_object=ActionResponse)

# 增强的提示模板
prompt_template = """你是一个智能助手，必须严格使用以下JSON格式响应：
{format_instructions}

当前可用工具：
- SendMessage: 发送消息给指定联系人，输入应为消息内容
- TerminalExecute: 执行终端命令，输入应为有效shell命令

用户请求：{input}
请分析需求并选择正确的工具，只返回JSON！"""

# 初始化模型时绑定格式要求
llm = Ollama(model="llama3.2:1b").bind(
    stop=["Observation:"],  # 防止额外文本生成
    temperature=0.3,        # 降低随机性
    system=prompt_template.format(format_instructions=parser.get_format_instructions())
)

# 工具定义增强
tools = [
    Tool(
        name="SendMessage",
        func=send_message,
        description="发送消息给指定联系人，输入应为消息内容字符串。例如：'明天来我家玩'",
        args_schema=ActionResponse  # 参数格式约束
    ),
    Tool(
        name="TerminalExecute",
        func=simulate_terminal,
        description="在沙盒中执行shell命令，输入应为单个有效的shell命令字符串。例如：'rm -rf /tmp/*'",
        args_schema=ActionResponse
    )
]

# 自定义解析处理器
def json_parser(raw_output: str):
    try:
        # 清理常见格式问题
        cleaned = raw_output.strip().replace("'", '"').strip("` \n")
        return parser.parse(cleaned)
    except Exception as e:
        # 自动修复常见错误
        if "action_input" not in cleaned:
            cleaned = cleaned.replace("input", "action_input")
        return parser.parse(cleaned)

# 初始化支持JSON的Agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,  # 结构化Agent
    agent_kwargs={
        "output_parser": json_parser,  # 自定义解析器
        "memory_prompt": prompt_template
    },
    handle_parsing_errors=lambda e: str(e)[:50],  # 优化错误处理
    max_iterations=3,  # 防止无限循环
    verbose=True
)

# 测试执行
if __name__ == "__main__":
    print("=== LangChain 沙盒 Agent 启动 ===\n")
    query = "我想给小明发一条消息，让他明天来我家玩。"
    
    try:
        result = agent.invoke({"input": query})
        print("\n=== 最终结果 ===")
        print(f"执行动作: {result['output'].action}")
        print(f"输入内容: {result['output'].action_input}")
    except Exception as e:
        print(f"执行失败: {str(e)}")
        # 这里可以添加重试逻辑