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
default_interval = 1  # 默认间隔时间 (秒)
screen_width, screen_height = pyautogui.size()
region_selection = False
region_start = None


def find_changed_points(img1, img2, threshold=30, min_area=50):
    """检测图像变化点"""
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(gray1, gray2)
    _, binary = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    changed_points = []
    for contour in contours:
        if cv2.contourArea(contour) > min_area:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                changed_points.append((cx, cy))
    return changed_points


def monitor_and_click(regions, interval, log, status_label):
    """动态监测多个区域并点击变化点"""
    global running
    prev_screenshots = {region: None for region in regions}

    try:
        while running:
            for region in regions:
                # 截取当前区域
                current_screenshot = np.array(ImageGrab.grab(bbox=region))

                # 初始化上一帧
                if prev_screenshots[region] is None:
                    prev_screenshots[region] = current_screenshot
                    continue

                # 检测变化点
                points = find_changed_points(prev_screenshots[region], current_screenshot)
                for px, py in points:
                    if not running:
                        break
                    screen_x = region[0] + px
                    screen_y = region[1] + py
                    pyautogui.moveTo(screen_x, screen_y)
                    pyautogui.click()
                    log.insert(tk.END, f"点击位置: ({screen_x}, {screen_y})\n")
                    log.see(tk.END)

                prev_screenshots[region] = current_screenshot
                time.sleep(interval)

    except Exception as e:
        log.insert(tk.END, f"程序异常: {str(e)}\n")
        log.see(tk.END)
        status_label.config(text="状态: 异常", fg="red")


def start_monitoring(regions, interval, log, status_label):
    """启动监测线程"""
    global running
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
    log.insert(tk.END, "停止动态监测。\n")
    log.see(tk.END)


def on_mouse_event(event, x, y, flags, param):
    """鼠标事件回调函数"""
    global region_selection, region_start, regions

    if event == cv2.EVENT_LBUTTONDOWN:
        if not region_selection:
            region_selection = True
            region_start = (x, y)  # 记录起点坐标
        else:
            region_selection = False
            region_end = (x, y)  # 记录终点坐标

            # 构造区域并添加到区域列表
            x1, y1 = region_start
            x2, y2 = region_end
            regions.append((min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)))


def select_region():
    """启动区域选择模式"""
    global region_selection

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
            cv2.rectangle(temp_screen, region_start, pyautogui.position(), (0, 255, 0), 2)

        cv2.imshow(window_name, temp_screen)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC键退出
            break

    cv2.destroyWindow(window_name)


def main():
    # 创建主窗口
    root = tk.Tk()
    root.title("鼠标动态监测连点器")
    root.geometry("600x500")

    tk.Label(root, text="选择检测区域后点击“开始”运行").pack()

    region_label = tk.Label(root, text=f"当前检测区域: {regions}")
    region_label.pack()

    tk.Button(root, text="选择检测区域", command=lambda: (select_region(), region_label.config(text=f"当前检测区域: {regions}"))).pack()

    # 状态标签
    status_label = tk.Label(root, text="状态: 停止", fg="red", font=("Arial", 12))
    status_label.pack()

    # 日志显示区域
    log = tk.Text(root, height=15)
    log.pack()

    # 启动按钮
    tk.Button(root, text="开始", command=lambda: start_monitoring(regions, default_interval, log, status_label),
              bg="green", fg="white").pack()

    # 停止按钮
    tk.Button(root, text="停止", command=lambda: stop_monitoring(log, status_label),
              bg="red", fg="white").pack()

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
