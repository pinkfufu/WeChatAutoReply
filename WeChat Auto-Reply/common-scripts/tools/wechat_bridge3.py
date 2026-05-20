import pyautogui
import pyperclip
import time
import httpx
import json
from PIL import ImageChops

# --- 微信物理坐标配置 ---
COORDS = {
    "minimize_btn": (2395, 35),
    "wechat_msg_area": (1410, 1200),  # 微信新消息气泡位置
    "wechat_input": (1400, 1350),  # 微信输入框
    "wechat_send": (2500, 1500)  # 微信发送按钮
}

# --- 大模型接口配置 ---
API_URL = "http://localhost:8080/xiaozhi/chat"
MEMORY_ID = 123456

# --- 调试开关 ---
START_IMMEDIATELY = True


def get_wechat_msg():
    """移过去右键多选复制内容"""
    original_mouse_pos = pyautogui.position()
    pyperclip.copy("")

    pyautogui.moveTo(COORDS["wechat_msg_area"])
    time.sleep(0.1)
    pyautogui.rightClick()
    time.sleep(0.4)

    try:
        # 置信度 0.75 确保高兼容
        select_btn_pos = pyautogui.locateCenterOnScreen('select_more_btn.png', minSearchTime=1, confidence=0.75)

        if select_btn_pos:
            pyautogui.click(select_btn_pos)
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.2)

            # 点击聊天区解除多选
            pyautogui.click(COORDS["wechat_msg_area"])
            time.sleep(0.1)

            current_msg = pyperclip.paste().strip()

            # 过滤名字前缀
            if "内容:" in current_msg or ":\n" in current_msg:
                parts = current_msg.split('\n')
                if len(parts) > 1:
                    current_msg = "".join(parts[1:]).strip()

            pyautogui.moveTo(original_mouse_pos)
            return current_msg
        else:
            pyautogui.click(COORDS["wechat_msg_area"])
            pyautogui.moveTo(original_mouse_pos)
            return ""

    except Exception as e:
        pyautogui.click(COORDS["wechat_msg_area"])
        pyautogui.moveTo(original_mouse_pos)
        return ""


def call_llm_api(message):
    """请求大模型，拦截500"""
    payload = {"memoryId": MEMORY_ID, "message": message}
    headers = {"Content-Type": "application/json"}
    full_reply = ""
    try:
        print(f">>> 🤖 正在请求大模型接口... 发送内容: {message[:15]}...")
        with httpx.Client(timeout=60.0) as client:
            with client.stream("POST", API_URL, json=payload, headers=headers) as response:
                if response.status_code == 200:
                    for chunk in response.iter_text():
                        if chunk:
                            full_reply += chunk
                elif response.status_code == 500:
                    print(">>> ⚠️ [安全拦截] 接口返回 500，判定为话题敏感！")
                    full_reply = "【系统提示】当前话题涉及敏感内容，无法生成回复。请更换话题再试。"
    except Exception as e:
        print(f"请求接口发生异常: {e}")
        full_reply = "【系统提示】大模型中转接口发生异常，请联系管理员检查后台。"

    return full_reply.strip()


def send_to_wechat(reply_text):
    """发送给微信"""
    pyautogui.click(COORDS["wechat_input"])
    pyperclip.copy(reply_text)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    pyautogui.click(COORDS["wechat_send"])
    print(">>> 🚀 成功执行一次闭环中转发送。")


def main():
    pyautogui.FAILSAFE = True
    print("==================================================")
    print("【斗图主动拦截功能版】中转站启动...")
    print("==================================================")
    time.sleep(2)
    pyautogui.click(COORDS["minimize_btn"])

    last_msg_in = ""
    last_reply_out = ""
    last_mouse_pos = pyautogui.position()

    # 上一次成功发送回复给微信的时间戳
    last_reply_time = 0

    # 监控区域配置
    monitor_region = (COORDS["wechat_msg_area"][0] - 200, COORDS["wechat_msg_area"][1] - 100, 400, 200)
    last_screenshot = pyautogui.screenshot(region=monitor_region)

    while True:
        try:
            # 1. 人为干扰检测
            current_mouse_pos = pyautogui.position()
            if abs(current_mouse_pos.x - last_mouse_pos.x) > 20 or abs(current_mouse_pos.y - last_mouse_pos.y) > 20:
                print(f">>> 🛏️ 检测到主人在使用电脑，程序静默休眠 10 秒...")
                time.sleep(10)
                last_mouse_pos = pyautogui.position()
                last_screenshot = pyautogui.screenshot(region=monitor_region)
                continue

            # 2. 像素画面比对
            current_screenshot = pyautogui.screenshot(region=monitor_region)
            diff = ImageChops.difference(last_screenshot, current_screenshot)

            if diff.getbbox() is None:
                last_mouse_pos = pyautogui.position()
                time.sleep(4)
                continue

            # 3. 画面变了，说明进来了新消息
            print("🔔 检测到微信区域画面变动，正在提取消息...")
            current_in = get_wechat_msg()

            # 计算距离上一次回复过去了多少秒
            time_passed = time.time() - last_reply_time

            # 4. 核心判定规则升级
            is_new_msg = False
            is_dou_tu = False  # 新增斗图标记

            if current_in and current_in != last_reply_out:
                if current_in != last_msg_in:
                    is_new_msg = True
                elif time_passed <= 10.0:
                    # 【核心修改点】10秒之内连续发的相同内容，判定为被斗图/刷屏了！
                    print(f"✨ 检测到对方正在刷屏/斗图！触发主动劝导机制。")
                    is_dou_tu = True

            if is_dou_tu:
                # 如果被斗图了，绕过大模型，由机器人直接警告
                warning_reply = "【系统提示】请不要连续刷屏或斗图，请文明聊天哦～"
                send_to_wechat(warning_reply)

                # 刷新状态，防止这句话反复发
                last_reply_out = warning_reply
                last_msg_in = current_in
                last_reply_time = time.time()

            elif is_new_msg:
                print(f"🔥 【捕捉到真正的新消息】: {current_in}")

                actual_llm_reply = call_llm_api(current_in)
                if actual_llm_reply:
                    send_to_wechat(actual_llm_reply)
                    last_reply_out = actual_llm_reply
                    last_msg_in = current_in
                    last_reply_time = time.time()
            else:
                print(">>> 💤 经过比对，判定为重复触发的旧消息，已忽略。")

            # 刷新监控基准
            last_screenshot = pyautogui.screenshot(region=monitor_region)
            last_mouse_pos = pyautogui.position()
            time.sleep(4)

        except Exception as e:
            print(f"运行异常: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()