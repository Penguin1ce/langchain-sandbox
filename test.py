import json
import ollama

# 定义工具数据（没有提供消息内容，交给模型决定）
tools_json = {
  "tools": [
    {
      "tool": "fetch_inventory",
      "parameters": {
        "inventory_data": [
          {
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "stock": 50
          },
          {
            "title": "1984",
            "author": "George Orwell",
            "stock": 40
          },
          {
            "title": "To Kill a Mockingbird",
            "author": "Harper Lee",
            "stock": 30
          },
          {
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "stock": 25
          }
        ]
      }
    },
    {
      "tool": "send_email",
      "parameters": {
        "email": "example@example.com",
        "subject": "Book Inventory Update",
        "message": "The updated inventory is as follows:\n- The Great Gatsby: 50 copies\n- 1984: 40 copies\n- To Kill a Mockingbird: 30 copies\n- Pride and Prejudice: 25 copies"
      }
    }
  ]
}

# 使用 Ollama API 调用大模型
def call_ollama(json_input, user_message):
    try:
        # 创建一个包含系统输入和用户消息的对话
        messages = [
            {"role": "system", "content": json.dumps(json_input)},  # 系统提供工具数据
            {"role": "user", "content": user_message}  # 用户提问
        ]

        # 将对话传递给 Ollama 模型 qwen2.5 qwen2.5-coder:1.5b
        response = ollama.chat(model="qwen2.5", messages=messages)

        # 打印整个响应，查看返回的格式
        print("Response from Ollama:", response)

        # 获取 message 内容
        if "message" in response:
            return response["message"]["content"]
        else:
            print("Response does not contain 'message' field.")
            return None
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return None
# 默认 agent 提示词 + 工具定义
agent_system_prompt = """You are an assistant that is capable of utilizing numerous tools and functions to complete the given task.  1. First, I will provide you with the task description, and your task will commence. Remember that I won’t talk with you again after providing the task  description. You need to finish the task on your own. 2. At each step, you need to analyze the current status and determine the next course of action and whether to execute a function call. 3. You should invoke only one tool at a time and wait for its return results before proceeding to the next tool invocation or outputting the final result. You should not call multiple tools or one tool with different arguments simultaneously before receiving the return result from a tool call.  4. If you choose to execute a function call, ONLY output the JSON format result and DO NOT output anything else. The json format is {"name": "function name", "arguments": {dictionary of argument name and its value}}. DO NOT use quotes to surround the actual arguments. For example, output {"name": "update_expiration_information", "arguments": {"product_id": "P1234", "new_expiration_level": 0}} instead of {"name": "update_expiration_information", "arguments": {"product_id": "P5678", "new_expiration_level": 0} }. Avoid inserting addtional lines between different keys in arguments.  5. DO NOT execute any function whose definition is not provided. You can only call the tools provided. 6. After the function call, you will receive the result, transitioning you to a new state. Subsequently, you will analyze your current status, make decisions about the next steps, and repeat this process. 7. Avoid repeating unnecessary function calls. For example, if you have already sent an email, do not send the same email again. Similarly, if you have obtained search results, refrain from performing the same search repeatedly. 8. After one or more iterations of function calls, you will ultimately complete the task and provide your final answer. Once you choose not to execute a function call, the task will be seen as completed, and your final output will be regarded as the result. 9. Note that the user can’t see the tool call progress, so if the answer of the query is included in the result of tool calls, you should output the results to answer my question.
Here are the tools you can use:
""" + json.dumps(tools_json, indent=2)
# 用户查询《了不起的盖茨比》的库存数量，并要求发送电子邮件
user_query = "查询《了不起的盖茨比》的库存数量,给jcz810@outlook.com发送这本书的库存信息"

# 调用函数
result = call_ollama(agent_system_prompt, user_query)

# 输出模型的回答
print("Model's response:", result)
