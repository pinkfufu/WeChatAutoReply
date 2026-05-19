import pyautogui
import pyperclip
import time
import httpx
import json

# --- 微信物理坐标配置 ---
COORDS = {
    "minimize_btn": (2395, 35),
    "wechat_msg_area": (1410, 1200),  # 微信新消息气泡位置
    "wechat_input": (1400, 1350),  # 微信输入框
    "wechat_send": (2500, 1500)  # 微信发送按钮
}

# --- 大模型接口配置 ---
API_URL = "http://localhost:8080/xiaozhi/chat"  # Spring Boot 接口地址
MEMORY_ID = 123456  # 固定的上下文对话ID

# --- 调试开关 ---
# 如果设为 True：程序启动时，不管是不是新消息，都会立刻对当前消息回复一次。
# 如果设为 False：程序启动时会记住当前消息，只有当后续收到“真正的新消息”时才会触发回复。
START_IMMEDIATELY = True


def get_wechat_msg():
    """获取微信消息（通过图像识别精准点击‘复制’）"""
    pyperclip.copy("")
    pyautogui.moveTo(COORDS["wechat_msg_area"])
    time.sleep(0.2)

    # 1. 双击选中文本
    pyautogui.doubleClick(interval=0.1)
    time.sleep(0.5)  # 确保文字高亮

    # 2. 右键唤出菜单
    pyautogui.rightClick()
    time.sleep(0.5)  # 等待右键菜单弹窗稳定

    # 3. 核心改进：图像识别定位“复制”按钮
    try:
        # minSearchTime=1 表示在1秒内持续查找，避免菜单弹出动画没完就报错
        # confidence=0.8 需要安装 opencv-python，允许80%的相似度匹配，防色彩偏差
        copy_btn_pos = pyautogui.locateCenterOnScreen('copy_btn.png', minSearchTime=1, confidence=0.8)

        if copy_btn_pos:
            print(f">>> 图像识别成功，复制按钮坐标: {copy_btn_pos}")
            pyautogui.click(copy_btn_pos)
        else:
            print(">>> 错误：未能在屏幕上匹配到复制按钮截图！")
            # 如果没找到菜单，点一下空白处把菜单顶掉，防止死锁
            pyautogui.click(COORDS["wechat_input"])
            return ""
    except Exception as e:
        print(f">>> 图像识别异常（可能未安装 opencv-python）: {e}")
        return ""

    time.sleep(0.5)
    return pyperclip.paste().strip()


def call_llm_api(message):
    """直接发送网络请求调用 Java 接口，流式读取响应"""
    payload = {
        "memoryId": MEMORY_ID,
        "message": message
    }

    headers = {
        "Content-Type": "application/json"
    }

    full_reply = ""
    try:
        print(f">>> 正在请求大模型接口... 发送内容: {message[:15]}...")
        with httpx.Client(timeout=60.0) as client:
            with client.stream("POST", API_URL, json=payload, headers=headers) as response:
                if response.status_code == 200:
                    for chunk in response.iter_text():
                        if chunk:
                            full_reply += chunk
                else:
                    print(f"接口请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"请求接口发生异常: {e}")

    return full_reply.strip()


def send_to_wechat(reply_text):
    """把大模型回复粘贴回微信并发送"""
    pyautogui.click(COORDS["wechat_input"])
    pyperclip.copy(reply_text)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    pyautogui.click(COORDS["wechat_send"])
    print(">>> 成功执行一次闭环中转发送。")


def main():
    pyautogui.FAILSAFE = True
    print("【接口级+图像识别】中转站启动...")
    time.sleep(2)
    pyautogui.click(COORDS["minimize_btn"])

    # 初始化逻辑
    if START_IMMEDIATELY:
        last_msg_in = ""  # 设为空，进循环后会立刻把当前消息当作“新消息”触发一次
    else:
        last_msg_in = get_wechat_msg()  # 记住当前消息，静默等待下一条

    last_reply_out = ""
    last_mouse_pos = pyautogui.position()

    while True:
        try:
            # 1. 人为干扰检测（防鼠标误移）
            current_mouse_pos = pyautogui.position()
            if abs(current_mouse_pos.x - last_mouse_pos.x) > 5 or abs(current_mouse_pos.y - last_mouse_pos.y) > 5:
                print(f">>> 检测到鼠标显著移动，程序休眠 10 秒...")
                time.sleep(10)
                last_mouse_pos = pyautogui.position()
                continue

            # 2. 获取微信当前最新的消息
            current_in = get_wechat_msg()

            # 3. 核心触发判定
            if current_in and current_in != last_msg_in and current_in != last_reply_out:
                print(f"【捕捉到真正的新消息】: {current_in}")

                # 调用大模型接口
                actual_llm_reply = call_llm_api(current_in)

                if actual_llm_reply:
                    # 自动打字发回微信
                    send_to_wechat(actual_llm_reply)

                    # 更新状态缓存
                    last_reply_out = actual_llm_reply
                    last_msg_in = current_in
                else:
                    print(">>> 警告：接口未返回有效内容。")
            else:
                # 如果消息没变，或者为空，则不进行重复右键和点击，静默等待
                print(">>> 暂无新消息，正在静默轮询中...")

            last_mouse_pos = pyautogui.position()
            time.sleep(4)  # 轮询间隔：每 4 秒检查一次是否有新消息

        except Exception as e:
            print(f"运行异常: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()