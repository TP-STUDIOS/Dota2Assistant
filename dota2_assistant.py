import os
import threading
import time
import pyautogui
from dotenv import load_dotenv
from colorama import init, Fore, Style
import keyboard

init()

class Dota2Assistant:
    def __init__(self):
        load_dotenv()
        self.auto_accept_hotkey = os.getenv('AUTO_ACCEPT_HOTKEY')
        self.auto_spam_hotkey = os.getenv('AUTO_SPAM_HOTKEY')
        self.anti_pause_hotkey = os.getenv('ANTI_PAUSE')

        if not self.auto_accept_hotkey or not self.auto_spam_hotkey or not self.anti_pause_hotkey:
            raise ValueError("Необходимо указать AUTO_ACCEPT_HOTKEY, AUTO_SPAM_HOTKEY и ANTI_PAUSE в файле .env")
        self.auto_accept_enabled = False
        self.auto_spam_enabled = False
        self.anti_pause_enabled = False
        self.current_count = 1000
        self.stop_search = False
        self.stop_spam = False
        self.stop_anti_pause = False
        self.search_thread = None
        self.spam_thread = None
        self.anti_pause_thread = None
        self.last_auto_spam_press = 0
        self.last_auto_accept_press = 0
        self.last_anti_pause_press = 0
        self.press_cooldown = 0.5 
        keyboard.add_hotkey(self.anti_pause_hotkey, self.safe_toggle_anti_pause)
        keyboard.add_hotkey(self.auto_accept_hotkey, self.safe_toggle_auto_accept)
        keyboard.add_hotkey(self.auto_spam_hotkey, self.safe_toggle_auto_spam)
        self.display_header()
        self.update_display()

    def display_header(self):
        print(Fore.CYAN + '''
        ████████╗██████╗░░██████╗████████╗██╗░░░██╗██████╗░██╗░█████╗░
        ╚══██╔══╝██╔══██╗██╔════╝╚══██╔══╝██║░░░██║██╔══██╗██║██╔══██╗
        ░░░██║░░░██████╔╝╚█████╗░░░░██║░░░██║░░░██║██║░░██║██║██║░░██║
        ░░░██║░░░██╔═══╝░░╚═══██╗░░░██║░░░██║░░░██║██║░░██║██║██║░░██║
        ░░░██║░░░██║░░░░░██████╔╝░░░██║░░░╚██████╔╝██████╔╝██║╚█████╔╝
        ░░░╚═╝░░░╚═╝░░░░░╚═════╝░░░░╚═╝░░░░╚═════╝░╚═════╝░╚═╝░╚════╝░
        ''' + Fore.WHITE)

    def update_display(self):
        print("\r", end="")  
        accept_state = "on" if self.auto_accept_enabled else "off"
        spam_state = "on" if self.auto_spam_enabled else "off"
        pause_state = "on" if self.anti_pause_enabled else "off"
        accept_color = Fore.GREEN if self.auto_accept_enabled else Fore.RED
        spam_color = Fore.GREEN if self.auto_spam_enabled else Fore.RED
        pause_color = Fore.GREEN if self.anti_pause_enabled else Fore.RED
        print(f"AutoAccept {accept_color}{accept_state}{Style.RESET_ALL} [{self.auto_accept_hotkey}] | "
              f"AutoSpam {spam_color}{spam_state}{Style.RESET_ALL} [{self.auto_spam_hotkey}] | "
              f"AntiPause {pause_color}{pause_state}{Style.RESET_ALL} [{self.anti_pause_hotkey}]", end='')

    def search_and_click(self):
        while not self.stop_search:
            image_path = os.path.join("src", "accept_button.jpg")
            try:
                location = pyautogui.locateOnScreen(image_path, confidence=0.8)
                if location:
                    pyautogui.click(pyautogui.center(location))
            except Exception as e:
                print(f"Error in search_and_click: {e}")
            time.sleep(2)

    def auto_spam(self):
        while self.auto_spam_enabled:
            try:
                message = f"{self.current_count} - 7 = {self.current_count - 7}"
                pyautogui.hotkey('shift', 'enter')
                time.sleep(0.05)
                pyautogui.write(message)
                pyautogui.press('enter')
                self.current_count -= 7
                if self.current_count < -1:
                    self.current_count = 1000
                time.sleep(0.1)
            except Exception as e:
                print(f"Error in auto_spam: {e}") 

    def anti_pause(self):
        while self.anti_pause_enabled:
            image_path = os.path.join("src", "pause.jpg")
            try:
                location = pyautogui.locateOnScreen(image_path, confidence=0.8)
                if location:
                    pyautogui.press('F9')  
            except Exception as e:
                print(f"Error anti_pause: {e}")  
            time.sleep(1)  

    def toggle_auto_spam(self):
        if self.auto_spam_enabled:
            self.auto_spam_enabled = False
            self.stop_spam = True
            if self.spam_thread:
                self.spam_thread.join()
                self.spam_thread = None
            self.update_display()   
        else:
            self.auto_spam_enabled = True
            self.current_count = 1000
            self.spam_thread = threading.Thread(target=self.auto_spam)
            self.spam_thread.daemon = True
            self.spam_thread.start()
            self.update_display()

        self.update_display()  

    def toggle_auto_accept(self):
        if self.auto_accept_enabled:
            self.auto_accept_enabled = False
            self.stop_search = True
            if self.search_thread:
                self.search_thread.join()
                self.search_thread = None
            self.update_display()
        else:
            self.auto_accept_enabled = True
            self.stop_search = False
            self.search_thread = threading.Thread(target=self.search_and_click)
            self.search_thread.daemon = True
            self.search_thread.start()
            self.update_display()

        self.update_display()  

    def toggle_anti_pause(self):
        if self.anti_pause_enabled:
            self.anti_pause_enabled = False
            self.stop_anti_pause = True
            if self.anti_pause_thread:
                self.anti_pause_thread.join()
                self.anti_pause_thread = None
            self.update_display()
        else:
            self.anti_pause_enabled = True
            self.stop_anti_pause = False
            self.anti_pause_thread = threading.Thread(target=self.anti_pause)
            self.anti_pause_thread.daemon = True
            self.anti_pause_thread.start()
            self.update_display()   

        self.update_display()  

    def safe_toggle_auto_spam(self):
        current_time = time.time()
        if current_time - self.last_auto_spam_press > self.press_cooldown:
            self.last_auto_spam_press = current_time
            self.toggle_auto_spam()

    def safe_toggle_auto_accept(self):
        current_time = time.time()
        if current_time - self.last_auto_accept_press > self.press_cooldown:
            self.last_auto_accept_press = current_time
            self.toggle_auto_accept()

    def safe_toggle_anti_pause(self):
        current_time = time.time()
        if current_time - self.last_anti_pause_press > self.press_cooldown:
            self.last_anti_pause_press = current_time
            self.toggle_anti_pause()

if __name__ == "__main__":
    assistant = Dota2Assistant()
    keyboard.wait('ctrl','shift','m')  
