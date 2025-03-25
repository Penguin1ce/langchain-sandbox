import json
import ollama

# 定义工具数据（没有提供消息内容，交给模型决定）
json_data = {
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

        # 将对话传递给 Ollama 模型
        response = ollama.chat(model="qwen2.5-coder:1.5b", messages=messages)

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

# 用户查询《了不起的盖茨比》的库存数量，并要求发送电子邮件
user_query = "What is the stock of 'The Great Gatsby'? Please send an email with the updated inventory details."

# 调用函数
result = call_ollama(json_data, user_query)

# 输出模型的回答
print("Model's response:", result)
