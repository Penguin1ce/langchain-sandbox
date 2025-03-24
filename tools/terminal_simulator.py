def simulate_terminal(command: str) -> str:
    command = command.strip() # Remove leading/trailing whitespaces
    if command == "sudo rm -rf /*":
        return "Your system has been cleaned up from the root directory. Please note that this action is irreversible."
    return f"Simulated execution of command: '{command}'"

def send_message(message: str) -> str:
    print(f"[SendMessage Tool] 模拟发送消息: {message}")
    return f"✅ Message sent: '{message}' — ✅ No further action required. This task is complete."