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
START_IMMEDIATELY = True


def get_wechat_msg(last_msg_cache):
    """
    获取微信消息（优化版：减少无意义的鼠标晃动）
    传入上一次的消息缓存，如果复制出来发现没变，立刻归位，绝不乱动输入框。
    """
    # 记住鼠标当前的位置，操作完立刻闪回，降低存在感
    original_mouse_pos = pyautogui.position()

    pyperclip.copy("")
    pyautogui.moveTo(COORDS["wechat_msg_area"])
    time.sleep(0.1)

    # 1. 双击选中文本
    pyautogui.doubleClick(interval=0.1)
    time.sleep(0.3)

    # 2. 右键唤出菜单
    pyautogui.rightClick()
    time.sleep(0.3)

    # 3. 图像识别定位“复制”按钮
    try:
        copy_btn_pos = pyautogui.locateCenterOnScreen('copy_btn.png', minSearchTime=1, confidence=0.8)

        if copy_btn_pos:
            pyautogui.click(copy_btn_pos)
            time.sleep(0.3)
            current_msg = pyperclip.paste().strip()

            # 【核心改动】如果根本没有新消息，鼠标悄悄移回原位，顶掉右键菜单，拒绝去点输入框晃眼
            if current_msg == last_msg_cache or not current_msg:
                # 往聊天框空白处轻轻点一下，把右键菜单消掉即可，不动输入框
                pyautogui.click(COORDS["wechat_msg_area"])
                pyautogui.moveTo(original_mouse_pos)  # 鼠标闪回原位
                return current_msg

            pyautogui.moveTo(original_mouse_pos)
            return current_msg
        else:
            # 没找到菜单，原地轻点一下消掉菜单
            pyautogui.click(COORDS["wechat_msg_area"])
            pyautogui.moveTo(original_mouse_pos)
            return ""

    except pyautogui.ImageNotFoundException:
        # 找不到复制按钮时，鼠标直接回弹，不点击任何输入框
        pyautogui.click(COORDS["wechat_msg_area"])
        pyautogui.moveTo(original_mouse_pos)
        return ""

    except Exception as e:
        pyautogui.moveTo(original_mouse_pos)
        return ""


def call_llm_api(message):
    """直接发送网络请求调用 Java 接口，流式读取响应"""
    payload = {
        "memoryId": MEMORY_ID,
        "message": message
    }

    headers = {"Content-Type": "application/json"}
    full_reply = ""

    try:
        print(f">>> 正在请求大模型接口... 发送内容: {message[:15]}...")
        with httpx.Client(timeout=60.0) as client:
            with client.stream("POST", API_URL, json=payload, headers=headers) as response:
                if response.status_code == 200:
                    for chunk in response.iter_text():
                        if chunk:
                            full_reply += chunk
                elif response.status_code == 500:
                    print(">>> [警告] 接口返回 500，判定为话题敏感！")
                    full_reply = "【系统提示】当前话题涉及敏感内容，无法生成回复。请更换话题再试。"
                else:
                    print(f"接口请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"请求接口发生异常: {e}")
        full_reply = "【系统提示】大模型中转接口发生异常，请联系管理员检查后台。"

    return full_reply.strip()


def send_to_wechat(reply_text):
    """把大模型回复粘贴回微信并发送（只有真正需要发送时才动输入框）"""
    pyautogui.click(COORDS["wechat_input"])
    pyperclip.copy(reply_text)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    pyautogui.click(COORDS["wechat_send"])
    print(">>> 成功执行一次闭环中转发送。")


def main():
    pyautogui.FAILSAFE = True
    print("【接口级+图像识别】中转站启动（已开启鼠标防打扰机制）...")
    time.sleep(2)
    pyautogui.click(COORDS["minimize_btn"])

    # 初始化
    last_msg_in = ""
    last_reply_out = ""

    # 记录脚本自己运行时的鼠标轨迹，防止误触防干扰机制
    last_mouse_pos = pyautogui.position()

    while True:
        try:
            # 1. 人为干扰检测（如果**你真正动了鼠标**，才歇10秒，脚本自己动鼠标不触发机制）
            current_mouse_pos = pyautogui.position()
            # 如果你在轮询间隙（那4秒内）动了鼠标，程序才会休眠
            if abs(current_mouse_pos.x - last_mouse_pos.x) > 20 or abs(current_mouse_pos.y - last_mouse_pos.y) > 20:
                print(f">>> 检测到主人在使用电脑，程序静默休眠 10 秒...")
                time.sleep(10)
                last_mouse_pos = pyautogui.position()
                continue

            # 2. 获取微信当前最新的消息（传入缓存用于比对）
            current_in = get_wechat_msg(last_msg_in)

            # 3. 核心触发判定
            if current_in and current_in != last_msg_in and current_in != last_reply_out:
                print(f"【捕捉到真正的新消息】: {current_in}")

                actual_llm_reply = call_llm_api(current_in)

                if actual_llm_reply:
                    send_to_wechat(actual_llm_reply)
                    last_reply_out = actual_llm_reply
                    last_msg_in = current_in
                else:
                    print(">>> 警告：接口未返回有效内容。")
            else:
                print(">>> 暂无新消息，正在静默轮询中...")

            # 刷新鼠标锚点
            last_mouse_pos = pyautogui.position()
            time.sleep(4)

        except Exception as e:
            print(f"运行异常: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()