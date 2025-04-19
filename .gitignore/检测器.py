import cv2
import numpy as np
from PIL import ImageGrab
import pyautogui
import threading
import keyboard
import tkinter as tk
import time
import win32gui

# 全局变量
running = False
regions = []  # 存储监测区域
default_interval = 0.5  # 默认间隔时间 (秒)
screen_width, screen_height = pyautogui.size()
region_selection = False
region_start = None


def detect_red(image, threshold=0.01):
    """
    检测图像中的红色，并返回红色区域的中心点
    Returns:
        tuple: (是否检测到红色, (中心点x, 中心点y))
    """
    # 转换到HSV色彩空间
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 定义红色的HSV范围
    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 70, 50])
    upper_red2 = np.array([180, 255, 255])

    # 创建红色掩码
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    # 添加形态学操作来减少噪声
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # 寻找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # 找到最大的红色区域
        largest_contour = max(contours, key=cv2.contourArea)
        # 计算轮廓的矩moments
        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            # 计算红色区域的中心点
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            # 计算红色像素占比
            red_ratio = np.sum(mask > 0) / (mask.shape[0] * mask.shape[1])
            print(f"红色像素占比: {red_ratio}, 中心点: ({cx}, {cy})")
            return red_ratio > threshold, (cx, cy)

    return False, None


def monitor_and_click(regions, interval, log, status_label):
    """监测区域内的红色并点击"""
    global running

    try:
        while running:
            for region in regions:
                # 截取当前区域
                screenshot = ImageGrab.grab(bbox=region)
                current_screenshot = np.array(screenshot)
                # 转换颜色空间从RGB到BGR
                current_screenshot = cv2.cvtColor(current_screenshot, cv2.COLOR_RGB2BGR)

                # 检测红色
                has_red, center = detect_red(current_screenshot)
                if has_red and center:
                    # 将相对坐标转换为屏幕坐标
                    screen_x = region[0] + center[0]  # 区域左上角x + 相对x
                    screen_y = region[1] + center[1]  # 区域左上角y + 相对y

                    # 移动鼠标并点击
                    pyautogui.click(screen_x, screen_y)
                    log.insert(tk.END, f"检测到红色，点击位置: ({screen_x}, {screen_y})\n")
                    log.see(tk.END)
                else:
                    # 没有检测到红色，将鼠标向右移动5个像素
                    current_x, current_y = pyautogui.position()
                    pyautogui.moveTo(current_x + 5, current_y)
                    log.insert(tk.END, "未检测到红色，鼠标右移5像素\n")
                    log.see(tk.END)

                time.sleep(interval)

    except Exception as e:
        log.insert(tk.END, f"程序异常: {str(e)}\n")
        log.see(tk.END)
        status_label.config(text="状态: 异常", fg="red")


def start_monitoring(regions, interval, log, status_label):
    """启动监测线程"""
    global running
    if not regions:
        log.insert(tk.END, "请先选择检测区域！\n")
        log.see(tk.END)
        return

    if running:
        return

    running = True
    status_label.config(text="状态: 运行中", fg="green")
    monitor_thread = threading.Thread(target=monitor_and_click, args=(regions, interval, log, status_label))
    monitor_thread.daemon = True
    monitor_thread.start()


def stop_monitoring(log, status_label):
    """停止监测"""
    global running
    running = False
    status_label.config(text="状态: 停止", fg="red")
    log.insert(tk.END, "停止红色检测。\n")
    log.see(tk.END)


def on_mouse_event(event, x, y, flags, param):
    """鼠标事件回调函数"""
    global region_selection, region_start, regions

    if event == cv2.EVENT_LBUTTONDOWN:
        if not region_selection:
            region_selection = True
            region_start = (x, y)
        else:
            region_selection = False
            region_end = (x, y)

            # 构造区域并添加到区域列表
            x1, y1 = region_start
            x2, y2 = region_end
            regions.append((min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)))


def select_region():
    """启动区域选择模式"""
    global region_selection, regions

    # 清空之前的区域
    regions = []

    # 显示透明覆盖层
    hwnd = win32gui.GetForegroundWindow()
    win32gui.SetWindowText(hwnd, "点击两次选择检测区域（按 ESC 退出）")

    region_selection = False
    window_name = "选择检测区域"
    screen = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback(window_name, on_mouse_event)

    while True:
        temp_screen = screen.copy()
        if region_selection and region_start:
            x1, y1 = region_start
            current_pos = pyautogui.position()
            cv2.rectangle(temp_screen, region_start, current_pos, (0, 255, 0), 2)

        cv2.imshow(window_name, temp_screen)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC键退出
            break

    cv2.destroyWindow(window_name)


def main():
    # 创建主窗口
    root = tk.Tk()
    root.title("红色检测器")
    root.geometry("600x500")

    # 创建说明标签
    tk.Label(root,
             text="使用说明：\n1. 点击'选择检测区域'按钮\n2. 用鼠标框选要检测的区域\n3. 按ESC完成选择\n4. 点击'开始'运行检测",
             justify=tk.LEFT).pack(pady=10)

    region_label = tk.Label(root, text="当前检测区域: 未选择")
    region_label.pack()

    # 选择区域按钮
    tk.Button(root, text="选择检测区域",
              command=lambda: (select_region(),
                               region_label.config(text=f"当前检测区域: {regions}"))).pack(pady=5)

    # 状态标签
    status_label = tk.Label(root, text="状态: 停止", fg="red", font=("Arial", 12))
    status_label.pack(pady=5)

    # 日志显示区域
    log = tk.Text(root, height=15)
    log.pack(pady=10)

    # 按钮框架
    button_frame = tk.Frame(root)
    button_frame.pack(pady=5)

    # 启动按钮
    tk.Button(button_frame, text="开始",
              command=lambda: start_monitoring(regions, default_interval, log, status_label),
              bg="green", fg="white", width=10).pack(side=tk.LEFT, padx=5)

    # 停止按钮
    tk.Button(button_frame, text="停止",
              command=lambda: stop_monitoring(log, status_label),
              bg="red", fg="white", width=10).pack(side=tk.LEFT, padx=5)

    # 添加快捷键说明
    tk.Label(root, text="快捷键：F11 - 停止检测", fg="gray").pack(pady=5)

    # 热键监听
    def listen_hotkey():
        while True:
            keyboard.wait("f11")
            if running:
                stop_monitoring(log, status_label)

    hotkey_thread = threading.Thread(target=listen_hotkey)
    hotkey_thread.daemon = True
    hotkey_thread.start()

    root.mainloop()


if __name__ == "__main__":
    main()
