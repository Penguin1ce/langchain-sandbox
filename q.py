import json
import ollama

# ----------------------
# ✅ 工具定义
# ----------------------
tools_json = {
  "tools": [
    {
      "tool": "fetch_inventory",
      "parameters": {
        "inventory_data": [
          {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "stock": 50},
          {"title": "1984", "author": "George Orwell", "stock": 40},
          {"title": "To Kill a Mockingbird", "author": "Harper Lee", "stock": 30},
          {"title": "Pride and Prejudice", "author": "Jane Austen", "stock": 25}
        ]
      }
    },
    {
      "tool": "send_email",
      "parameters": {
        "email": "jcz810@outlook.com",
        "subject": "Book Inventory Update",
        "message": "The updated inventory is as follows:\n- The Great Gatsby: 50 copies\n- 1984: 40 copies\n- To Kill a Mockingbird: 30 copies\n- Pride and Prejudice: 25 copies"
      }
    }
  ]
}

# ----------------------
# ✅ Agent Prompt
# ----------------------
agent_system_prompt = """You are an assistant that is capable of utilizing tools to complete a task.
Follow these rules:
1. Only call one tool at a time and wait for the result before the next call.
2. Output ONLY a JSON object in this format: {\"name\": ..., \"arguments\": {...}}
3. After receiving a tool result, analyze and decide the next step.
4. Once done, output the final result as natural language.
5. You may only use tools listed.
Here are the tools:
""" + json.dumps(tools_json, indent=2)

# ----------------------
# ✅ 工具执行器
# ----------------------
def tool_executor(name, arguments):
    if name == "fetch_inventory":
        inventory = tools_json["tools"][0]["parameters"]
        if arguments.get("inventory_data"):
            return {"inventory_data": arguments["inventory_data"]}  # 处理子集请求
        return inventory
    elif name == "send_email":
        print("\n📧 [模拟] 正在发送邮件...")
        print("To:", arguments["email"])
        print("Subject:", arguments["subject"])
        print("Message:\n", arguments["message"])
        return {"status": "success"}
    else:
        return {"error": "Unknown tool"}

# ----------------------
# ✅ Agent 执行 Loop
# ----------------------
def agent_loop(user_query):
    messages = [
        {"role": "system", "content": agent_system_prompt},
        {"role": "user", "content": user_query}
    ]

    while True:
        response = ollama.chat(model="qwen2.5", messages=messages)
        print("\n🤖 模型回复:", response["message"]["content"])
        print(response)

        try:
            # 尝试解析 JSON
            tool_call = json.loads(response["message"]["content"].replace("\\", ""))
            tool_name = tool_call["name"]
            tool_args = tool_call["arguments"]
            tool_result = tool_executor(tool_name, tool_args)

            # 添加工具调用与返回记录
            messages.append({"role": "assistant", "content": response["message"]["content"]})
            messages.append({"role": "tool", "name": tool_name, "content": json.dumps(tool_result)})
        except Exception:
            # 非工具调用，视为最终输出
            print("\n✅ 任务完成。模型最终回复：")
            print(response["message"]["content"])
            break

# ----------------------
# ✅ 启动 Agent
# ----------------------
user_query = "查询《The Great Gatsby》的库存并将结果发送邮件到 jcz810@outlook.com"
agent_loop(user_query)