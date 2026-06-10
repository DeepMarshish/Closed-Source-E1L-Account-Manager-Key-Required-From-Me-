try:
    from dataclasses import dataclass, field
    import requests
    from email.utils import parsedate_to_datetime
    import base64
    import traceback
    import subprocess
    import threading
    import hashlib
    import socket
    import msvcrt
    import hmac
    import time
    import zlib
    import requests
    from getpass import getpass
    import re
    import os
    import sys
    import math 
    import heapq
    from pathlib import Path
    import queue
    import random
    import dataclasses
    import string
    from typing import Any
    import keyboard
    import urllib.request
    from datetime import datetime
    now = datetime.now()
    curtime_formatted = f"{now.month}/{now.day}/{now.strftime('%y')} {now.strftime('%I:%M %p').lstrip('0')}"


    client = True


    main_folder = "Great Manager" 

    console_color = None #(0,0,0)


    terminal_name = "Birder Manager v0.1"


    def run_executable(executable):
        subprocess.Popen(executable, shell=True)

    class Timer(threading.Thread):
        def __init__(self):
            super().__init__()
            self.seconds = 0
            self.running = True
            self.daemon = True

        def run(self):
            while self.running:
                time.sleep(1)
                if self.running: 
                    self.seconds += 1

        def terminate(self):
            self.running = False
    @dataclass
    class Directories:
        settings: str = os.path.join(main_folder, "Settings.cfg")
        accounts: str = os.path.join(main_folder, "Accounts.txt")
        history: str = os.path.join(main_folder, "History.txt")
        executables: str = os.path.join(main_folder, "Executables.txt")

        oholEmails: str = os.path.join(os.path.dirname(__file__),"settings", "email.ini")
        oholKeys: str = os.path.join(os.path.dirname(__file__), "settings", "accountKey.ini")

    @dataclass
    class Settings:
        current_password: str | None = None

        default_exe: str | None = None
        client: str | None = None

        password_hash: str | None = None
        server_password: str = "testPassword"
        
        shady_auth_password: str = "null"
        ip_addr_hash: str | None = None

        server_ip: str | None = None
        port: int | None = None

        phex_ip: str | None = None
        phex_port: int | None = None

        security_mode: str | None = None
        mask_accounts: str | None = None



        default_settings: str = (
            "STR|client = client_birdery\n"
            "STATIC|password_hash = null\n"
            "STATIC|shady_auth_password = null\n"
            "STR|ip_addr_hash = null\n"
            "STR|server_password = testPassword\n"
            "STR|server_ip = bigserver2.onehouronelife.com\n"
            "INT|port = 8005\n"
            "STR|phex_ip = null\n"
            "INT|phex_port = 0000\n"
            "BOOL|security_mode = False\n"
            "BOOL|mask_accounts = True\n"
           
        )

        @staticmethod
        def to_bool(value):
            return str(value).strip().lower() == "true"

    @dataclass
    class Memory:
        server_name: str | None = None
        executables: list = field(default_factory=list)
        accounts: list = field(default_factory=list)
        total_accounts: int | None = None
        google_time : any| None = None

    class FileEditor:
        def __init__(self, filepath, autosave=True):
            self.filepath = filepath
            self.autosave = autosave
            self.lock = threading.RLock()
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    self.lines = [line.rstrip("\n") + "\n" for line in f.readlines()]
            except FileNotFoundError:
                self.lines = []

            self.empty = len(self.lines) == 0

        def _update_empty(self):
            self.empty = len(self.lines) == 0

        def save(self):
            with self.lock:
                with open(self.filepath, "w", encoding="utf-8") as f:
                    f.writelines(self.lines)
                self._update_empty()
            return self

        def total_lines(self):
            with self.lock:
                return len(self.lines) + 1

        def _resolve_line_number(self, line_number, for_write=False):
            if isinstance(line_number, str) and line_number.upper() == "L":
                return self.total_lines()
            if isinstance(line_number, int):
                return line_number
            return None

        def read(self, line_number):
            with self.lock:
                line_number = self._resolve_line_number(line_number)
                if isinstance(line_number, int) and 1 <= line_number < self.total_lines():
                    return self.lines[line_number - 1].rstrip("\n")
                return None

        def write(self, line_number, value):
            with self.lock:
                line_number = self._resolve_line_number(line_number, for_write=True)
                if not isinstance(line_number, int) or line_number < 1:
                    return self

                while len(self.lines) < line_number:
                    self.lines.append("\n")

                self.lines[line_number - 1] = value.rstrip("\n") + "\n"

                self._update_empty()

                if self.autosave:
                    self.save()

            return self

        def delete(self, line_number):
            with self.lock:
                line_number = self._resolve_line_number(line_number)
                if isinstance(line_number, int) and 1 <= line_number < self.total_lines():
                    del self.lines[line_number - 1]

                    self._update_empty()

                    if self.autosave:
                        self.save()

            return self

        def locate(self, key, equalizer="=", start_after=None):
            with self.lock:
                for index, line in enumerate(self.lines, start=1):

                    working_line = line

                    if start_after is not None:
                        pos = working_line.rfind(start_after)

                        if pos != -1:
                            working_line = working_line[pos + len(start_after):]

                    if equalizer in working_line:
                        base = working_line.split(equalizer, 1)[0].strip()

                        if base.lower() == key.lower():
                            return index

                return None


        def read_equality(self, key, equalizer="=", start_after=None):
            with self.lock:
                idx = self.locate(key, equalizer, start_after)

                if idx:
                    line = self.lines[idx - 1]

                    if start_after is not None:
                        pos = line.rfind(start_after)

                        if pos != -1:
                            line = line[pos + len(start_after):]

                    _, value = line.split(equalizer, 1)

                    return value.strip()

                return None
            
        def write_equality(self, key, replacement_value, equalizer="=", start_after=None):
            replacement_value = str(replacement_value).strip()

            with self.lock:
                idx = self.locate(key, equalizer, start_after)

                if idx:
                    original_line = self.lines[idx - 1]

                    prefix = ""
                    working_line = original_line

                    if start_after is not None:
                        pos = original_line.rfind(start_after)

                        if pos != -1:
                            prefix = original_line[:pos + len(start_after)]
                            working_line = original_line[pos + len(start_after):]

                    base, _ = working_line.split(equalizer, 1)

                    self.lines[idx - 1] = (
                        f"{prefix}{base.strip()} {equalizer} {replacement_value}\n"
                    )
                else:
                    prefix = f"{start_after}" if start_after else ""

                    self.lines.append(
                        f"{prefix}{key} {equalizer} {replacement_value}\n"
                    )

                if self.autosave:
                    self.save()

            return self

        def reverse_logic(self, key, equalizer="=", start_after=None):
            with self.lock:
                idx = self.locate(key, equalizer, start_after)

                if idx:
                    line = self.lines[idx - 1]

                    prefix = ""
                    working_line = line

                    if start_after is not None:
                        pos = line.rfind(start_after)

                        if pos != -1:
                            prefix = line[:pos + len(start_after)]
                            working_line = line[pos + len(start_after):]

                    base, value = working_line.split(equalizer, 1)

                    new_value = (
                        "False"
                        if value.strip().lower() == "true"
                        else "True"
                    )

                    self.lines[idx - 1] = (
                        f"{prefix}{base.strip()} {equalizer} {new_value}\n"
                    )

                    self._update_empty()

                    if self.autosave:
                        self.save()
                
        def read_equality_at_line(self, line_number, equalizer="=", start_after=None):
            with self.lock:
                if not isinstance(line_number, int):
                    return None

                if 1 <= line_number < self.total_lines():
                    line = self.lines[line_number - 1]

                    if start_after is not None:
                        pos = line.rfind(start_after)

                        if pos != -1:
                            line = line[pos + len(start_after):]

                    if equalizer in line:
                        _, value = line.split(equalizer, 1)
                        return value.strip()

                return None



        def make(self):
            with self.lock:
                open(self.filepath, "w", encoding="utf-8").close()
                self.lines = []
                self._update_empty()
            return self

    class ClientMenu:
        def __init__(self,
                    main_menu=False,
                    options=None,
                    title=None,
                    placement=None,
                    parent=None,
                    replacement_display=None,
                    color=(255, 255, 255)):

            self.parent = parent
            self.options = options or {}
            self.main_menu = main_menu
            self.title = title
            self.placement = placement
            self.result = None
            self.replacement_display = replacement_display
            self.color = color

        def menu(self):
            while True:

                if self.replacement_display:
                    if callable(self.replacement_display):
                        self.replacement_display(self)
                    else:
                        Special.print_as_rgb(self.replacement_display, rgb=self.color)

                else:
                    if self.title:
                        Special.print_as_rgb(self.title, rgb=self.color)

                    keys = list(self.options.keys())

                    if self.placement:
                        columns, rows = self.placement
                        count = 0

                        for _ in range(rows):
                            line_parts = []

                            for _ in range(columns):
                                if count < len(keys):
                                    key_name = keys[count]
                                    option_key = self.options[key_name].get("Key", "")
                                    line_parts.append(f"[{option_key.upper()}] {key_name}")
                                    count += 1

                            if line_parts:
                                line = "  ".join(line_parts)
                                Special.print_as_rgb(line, rgb=self.color)

                    else:
                        for key_name in keys:
                            option_key = self.options[key_name].get("Key", "")
                            Special.print_as_rgb(
                                f"[{option_key.upper()}] {key_name}",
                                rgb=self.color
                            )

                uinput = input("\033[38;2;180;180;180m> \033[0m").strip().lower()

                # GLOBAL EXIT
                if uinput == "exit":
                    sys.exit()

                chosen_option = None

                for name, data in self.options.items():
                    key = data.get("Key", "")

                    if key.lower() == uinput:
                        chosen_option = data
                        break

                if not chosen_option:
                    Special.print_as_rgb(
                        "\nInvalid Option...",
                        rgb=(255, 80, 80)
                    )
                    msvcrt.getch()
                    os.system("cls")
                    continue

                func = chosen_option["Function"]
                single_run = chosen_option.get("Single Run", False)

                os.system("cls")

                # RUN ONCE
                if single_run:
                    result = func()

                    os.system("cls")

                    if result == "exit":
                        sys.exit()

                    if result == "return":
                        return

                # LOOPING FUNCTION
                else:
                    while True:
                        self.result = func()

                        os.system("cls")

                        if self.result == "return":
                            break

                        if self.result == "exit":
                            sys.exit()

        def eInput(self, text="> "):
            prompt_colored = f"\033[38;2;180;180;180m{text}\033[0m"

            uinput = input(prompt_colored).strip()

            if uinput.lower() == "exit":
                sys.exit()

            if uinput.lower() == "back":
                return "return"

            return uinput

    password_cohash = "Breakfest Living"
    class Security:
        
        def __init__(self):
            pass
        @staticmethod
        def encrypt(plaintext: str, key: str) -> str:
            """Stronger encryption using PBKDF2 with password_cohash as salt"""
            if not plaintext:
                return ""
            
            # Use your existing password_cohash as salt
            salt = password_cohash.encode('utf-8')
            
            derived_key = hashlib.pbkdf2_hmac(
                'sha256', 
                key.encode('utf-8'), 
                salt, 
                iterations=10000, 
                dklen=32
            )
            
            data = plaintext.encode('utf-8')
            iv = os.urandom(12)
            
            result = bytearray(iv)
            
            for i, byte in enumerate(data):
                k = derived_key[i % len(derived_key)]
                result.append(byte ^ k ^ iv[i % 12])
            
            return base64.urlsafe_b64encode(result).decode('utf-8')

        @staticmethod
        def decrypt(ciphertext: str, key: str) -> str:
            try:
                if not ciphertext:
                    return ""


                padding = len(ciphertext) % 4
                if padding:
                    ciphertext += "=" * (4 - padding)

                data = base64.urlsafe_b64decode(ciphertext.encode("utf-8"))

                salt = password_cohash.encode("utf-8")
                derived_key = hashlib.pbkdf2_hmac(
                    "sha256",
                    key.encode("utf-8"),
                    salt,
                    iterations=10000,
                    dklen=32
                )

                iv = data[:12]
                encrypted = data[12:]

                result = bytearray()
                for i, byte in enumerate(encrypted):
                    k = derived_key[i % len(derived_key)]
                    result.append(byte ^ k ^ iv[i % 12])

                return result.decode("utf-8")

            except Exception:
                return None
                

        @staticmethod
        def unpackage_account(datastr, password): 
            raw = Security.decrypt(datastr, password)
            try:
                name, email, key, extra = raw.split("/") # 1:x/x/x/x 
                return (name, email, key, extra)
            except Exception:
                return ("Account Info Corrupt", "Corrupt Email", "Corrupt Key", "Corrupt Extra Data")
            
        @staticmethod
        def package_account(fullstr, password):
            encrypted = Security.encrypt(fullstr, password)
            return encrypted

        @staticmethod
        def HMAC_SHA1(key, message):
            hmac_object = hmac.new(key.encode(), message.encode(), hashlib.sha1)
            return hmac_object.hexdigest()

    class Special:
        @staticmethod
        def type_text(text, speed=0.05):
            for char in text:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(speed)
            print()
        @staticmethod
        def input_type_text(prompt="", speed=0.05):
            for char in prompt:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(speed)
            return input()
        
        @staticmethod
        def set_rgb(rgb=None):
            if rgb is None:


                print("\033[0m", end="")
                return
            r, g, b = rgb
            print(f"\033[38;2;{r};{g};{b}m", end="")

        @staticmethod
        def print_as_rgb(*args, rgb=None, sep=" ", end="\n"):
            text = sep.join(map(str, args))
            if rgb is None:

                print(text, end=end)
            else:

                r, g, b = rgb
                print(f"\033[38;2;{r};{g};{b}m{text}\033[0m", end=end)

        @staticmethod
        def underline(text, char="─"):
            text = str(text).replace("\n", "").strip()
            print(text)
            print(char * len(text))

        @staticmethod
        def hide_input(prompt, char="*"):
            print(prompt, end="", flush=True)

            value = ""

            while True:
                key = msvcrt.getch()

                if key in {b"\r", b"\n"}:
                    print("")
                    break

                # BACKSPACE
                elif key == b"\x08":
                    if len(value) > 0:
                        value = value[:-1]
                        print("\b \b", end="", flush=True)
                else:
                    try:
                        c = key.decode("utf-8")
                        value += c

                        if char is None:
                            pass  
                        else:
                            print(char, end="", flush=True)

                    except:
                        pass

            return value

    # Data Classes
    cDirectories = Directories
    cSettings = Settings
    cMemory = Memory()
    cSecurity = Security
    def get_google_server_time():
        
        try:
            response = requests.head("https://www.google.com", timeout=5)
            http_date = response.headers.get("Date")

            if not http_date:
                print("Error: 'Date' header missing from response.")
                return None


            utc_time = parsedate_to_datetime(http_date)  


            return {
                "datetime_obj": utc_time,
                "YEAR": utc_time.year,
                "MONTH": utc_time.month,
                "DAY": utc_time.day,
                "HOUR": utc_time.hour,
                "MINUTE": utc_time.minute,
                "SECOND": utc_time.second,
                "WEEKDAY_NAME": utc_time.strftime("%A"),
                "WEEKDAY_NUM": utc_time.weekday(), 
                "WEEK_OF_YEAR": utc_time.isocalendar()[1],
            }

        except requests.exceptions.RequestException as e:
            print(f"Could not connect to Google: {e}")
            return None
    def check_shady_antipiracy():
        resort_memory()
        cMemory.google_time = get_google_server_time()
        feSettings = FileEditor(cDirectories.settings)

        currDay = int(cMemory.google_time["DAY"])
        currMonth = int(cMemory.google_time["MONTH"])
        currYear = int(cMemory.google_time["YEAR"])

        def check_key_validity(encrypted_key=None):
            if encrypted_key is None:
                encrypted_key = cSettings.shady_auth_password

            try:
                decrypted_key = cSecurity.decrypt(
                    encrypted_key,
                    "ShayActuallyIsn'tTransIt'sJustALie?!?#?#!?@#?!!@#@###@(#*@#(#!@@##!#!@N#@#!@N##I!)#I##!!@!)"
                )
                day, month, year = map(int, decrypted_key.split("/"))
            except Exception:
                print("Stored key is corrupted. Please restart and enter a valid key.")
                feSettings.write_equality("shady_auth_password", "null", start_after="|")
                msvcrt.getch()
                sys.exit()

            denied = False
            if currYear > year:
                denied = True
            elif currYear == year:
                if currMonth > month:
                    denied = True
                elif currMonth == month:
                    if currDay > day:
                        denied = True

            if denied:
                print("Key outdated, request a new key from Shady or an administrator.")
                feSettings.write_equality("shady_auth_password", "null", start_after="|")
                msvcrt.getch()
                sys.exit()

        if cSettings.shady_auth_password == "null":
            while True:
                os.system("cls")
                print("[Shady]: Enter your time based authentication password for your distribution.")
                auth_pass = input("> ").strip()
                if auth_pass.lower() == "exit":
                    sys.exit()
                try:
                    expiration_date = cSecurity.decrypt(
                        auth_pass,
                        "ShayActuallyIsn'tTransIt'sJustALie?!?#?#!?@#?!!@#@###@(#*@#(#!@@##!#!@N#@#!@N##I!)#I##!!@!)"
                    )
                    parts = expiration_date.split("/")
                    if len(parts) != 3:
                        raise ValueError

                    check_key_validity(auth_pass)

                    feSettings.write_equality("shady_auth_password", auth_pass, start_after="|")
                    cSettings.shady_auth_password = auth_pass
                    return
                except Exception:
                    print("Invalid Key...")
                    msvcrt.getch()
                    continue
        else:
            check_key_validity()


    def generate_client_codes():
        if client:
            print("Script administators only.")
            msvcrt.getch()
            return 

        while True:
            os.system("cls")
            print(
                "[Console]: Welcome back Shady!\n"
                "[Console]: Please enter your desired client expiration date in the format day/month/year (UTC TIME)."
            )
            expiration = input("> ").strip()

            parts = expiration.split("/")
            if len(parts) != 3:
                print("Invalid expiration time Shady. Must be in Day/Month/Year format.")
                msvcrt.getch()
                continue

            try:
                map(int, parts)
            except ValueError:
                print("Invalid date formatting. Must use numbers.")
                msvcrt.getch()
                continue

            break

        code = cSecurity.encrypt(
            expiration,
            "ShayActuallyIsn'tTransIt'sJustALie?!?#?#!?@#?!!@#@###@(#*@#(#!@@##!#!@N#@#!@N##I!)#I##!!@!)"
        )
        print(f"\nYour code for [D/M/Y] {expiration} is:\n{code}")
        msvcrt.getch()
        return 
    def request_password(return_password=False, main_menu=False):
        while True:
            os.system("cls") 
            print("If you're locked out type [reset or exit]\n")
            password = Special.hide_input("[Console]: Password Required: ")
            if password.lower() == "exit":
                    sys.exit()
            elif password.lower() == "reset":
                uinput = input("Reset Passwords? [Y/N]: ")
                if uinput.lower() == "y" or uinput.lower() == "yes":
                    feSettings = FileEditor(cDirectories.settings)
                    os.system("cls")
                    feSettings.write_equality("password_hash", "null", start_after="|")
                    print("[Console]: Reset Password To Null, Restart To Make New Password Or Go To Settings...")
                    msvcrt.getch()
                    break
                else:
                    os.system("cls")
                    print("Cancelled")
                    msvcrt.getch()
            password_hash = cSecurity.HMAC_SHA1(password, password_cohash)
            if password_hash == cSettings.password_hash :
                if return_password:
                    return password
                return
            else:
                print("Invalid Password") 
                msvcrt.getch()
            
    def resort_memory(): 

        # Initial
        if not os.path.exists(main_folder):
            os.makedirs(main_folder)
            open(cDirectories.accounts, 'w').close(); open(cDirectories.history, 'w').close()
            open(cDirectories.executables, 'w').close()
            with open(cDirectories.settings, 'w', encoding="utf-8") as f:
                f.write(cSettings.default_settings)
        
        # Post Initial
        if os.path.exists(main_folder):
            feSettings = FileEditor(cDirectories.settings) 
            feExecutables = FileEditor(cDirectories.executables)   
            feAccounts = FileEditor(cDirectories.accounts)

            if feSettings.read_equality("password_hash", start_after="|") == "null":
                os.system("cls")
                Special.type_text("You lack a password.\nYou'll need one to keep your accounts secure.",0.02)
                Special.type_text("I don't recommened using common passwords or the ones you keep saved.",0.02)
                Special.type_text("If you forget your password you can't get it back.",0.02)
                msvcrt.getch()
                os.system("cls")

                # Password Setup
                while True:
                    os.system("cls")
                    new_password = Special.hide_input("Enter your password for this client: ").strip()
                    if not new_password or new_password.lower() == "exit":
                        os.system("cls")
                        Special.print_as_rgb("[Console]: Invalid Password Format...", rgb=(255,0,0))
                        msvcrt.getch()
                        continue

                    confirmed_password = Special.hide_input("Enter again to make sure they're the same: ").strip()
                    if new_password != confirmed_password:
                        os.system("cls")
                        Special.print_as_rgb("[Console]: Passwords do not match", rgb=(255,0,0))
                        msvcrt.getch()
                        continue
                    os.system("cls")
                    feSettings.write_equality("password_hash", cSecurity.HMAC_SHA1(new_password, password_cohash), start_after="|")
                    break


                # Directory Setup
            if feExecutables.empty:
                while True: # Format DEFAULT|PATH or NAME : PATH (default will always be on line 0 and be the same)
                    os.system("cls")
                    Special.type_text("To run this client you need an executable.",0.01)
                    Special.type_text("Make sure you copy and paste the directory.",0.01)
                    setup_executable = Special.input_type_text("[Console]: Enter your default directory: ",0.01)
                    fullstr = f"DEFAULT|{setup_executable}"
                    feExecutables.write(1, fullstr)
                    break

            # Memory Sync
            def set_internet_values():
            
                try:
                    cSettings.server_ip = socket.gethostbyname(feSettings.read_equality("server_ip", start_after="|"))
                except:
                    os.system("cls")
                    Special.type_text("Server IP invalid... this may disable internet features.",0.01)
                    Special.type_text("You can resolve this at the settings menu.",0.01)
                    msvcrt.getch()

                try:
                    cSettings.port = int(feSettings.read_equality("port", start_after="|"))
                except:
                    os.system("cls")
                    Special.type_text("Server port is not an integer",0.01)
                    Special.type_text("You can resolve this at the settings menu.",0.01)
                    msvcrt.getch()
                
                cSettings.server_password = feSettings.read_equality("server_password", start_after="|")

                if cSettings.server_password != "testPassword":
                    Special.type_text("[Console] Warning!: Your One Hour One Life server password is different from the usual password.",0.01)
                    msvcrt.getch()

            def set_client_values():
                
                cSettings.client = feSettings.read_equality("client", start_after="|")
                
                cSettings.password_hash = feSettings.read_equality("password_hash", start_after="|")
                cSettings.default_exe = feExecutables.read_equality("DEFAULT", equalizer="|")

                cSettings.server_password = feSettings.read_equality("server_password", start_after="|")
                cSettings.shady_auth_password = feSettings.read_equality("shady_auth_password", start_after="|")
                cSettings.ip_addr_hash = feSettings.read_equality("ip_addr_hash", start_after="|")
                
                cSettings.phex_ip = feSettings.read_equality("phex_ip", start_after="|")
                cSettings.security_mode = cSettings.to_bool(feSettings.read_equality("security_mode", start_after="|")) # should be covered by my new settings system
                cSettings.mask_accounts = cSettings.to_bool(feSettings.read_equality("mask_accounts", start_after="|"))
               

                try:
                    cSettings.phex_port = int(feSettings.read_equality("phex_port", start_after="|"))
                except:
                    cSettings.phex_port = 0000

            def sort_actual_memory():
                cMemory.accounts.clear()
                cMemory.total_accounts = feAccounts.total_lines() -1 
                cMemory.executables.clear()

                cMemory.server_name = feSettings.read_equality("server_name", start_after="|")

                cMemory.executables.append("Filler")
                for i in range(1, feExecutables.total_lines()):
                    cMemory.executables.append(feExecutables.read(i))

                cMemory.accounts.append("Filler")
                for i in range(1, feAccounts.total_lines()):
                    cMemory.accounts.append(feAccounts.read(i))


            # end point
            set_internet_values()
            set_client_values()    
            sort_actual_memory()

            if cSettings.security_mode == True:
                cSettings.current_password = None
            
    def debug():
        resort_memory()
        print("Debug Started\n")
        msvcrt.getch()

    # ACC MANAGER CLASS FUNCTIONS

    def setup_ipcheck():
        global console_color
        try:
            current_ip = urllib.request.urlopen("https://api.ipify.org").read().decode()
            current_ip.strip(); current_ip=str(current_ip)
            x = cSecurity.HMAC_SHA1(current_ip, cSettings.current_password)
            
            
            if (
                cSettings.ip_addr_hash.lower() == "null"
                or cSettings.ip_addr_hash == x
            ):
                console_color = (160,0,0)
        except Exception as e:
            print(repr(e))
            msvcrt.getch()

    def fAdd_Accounts():
        resort_memory()
        x = AccManager(casecode_menu="add accounts", menu_title_custom="ACCOUNT ADDING")
        if x.exit:
            return "return" 
    
    def fRemove_Accounts():
        resort_memory()
        x = AccManager(casecode_menu="delete accounts", rgb=(255, 0, 0), menu_title_custom="ACCOUNT DELETION")
        if x.exit:
            return "return"      

    def fEdit_Accounts():
        resort_memory()
        x = AccManager(casecode_menu="edit accounts", menu_title_custom="EDITING ACCOUNTS")
        if x.exit:
            return "return"    

    def fDuplicate_Account_Detector():
        resort_memory()
        x = AccManager(casecode_menu="duplicate detector",rgb=(0,144,255) ,menu_title_custom="ACCOUNT DUPLICATE DETECTION SYSTEM")
        if x.exit:
            return "return"  
            
    def fSelect_Accounts():
        resort_memory()
        x = AccManager(casecode_menu="select accounts", menu_title_custom=f"ACCOUNT SELECTION")
        if x.exit:
            return "return"

    def Client_Settings():
        resort_memory()
        feSettings = FileEditor(cDirectories.settings)

        while True:
            Special.underline("Client Configuration")

            for i in range(1, feSettings.total_lines()):
                if not feSettings.read(i).split("|")[0] == "STATIC":
                    rgb = None
                else:
                    rgb = (255,0,0)
                Special.print_as_rgb(f"[{i}] {feSettings.read(i).split('|')[1]}", rgb=rgb)
            uinput = input("> ").strip()

            if uinput.lower() == "exit":
                return "return"

            try:
                number = int(uinput)

                if number < 1 or number > feSettings.total_lines():
                    raise ValueError

            except ValueError:
                print("Invalid Number...")
                msvcrt.getch()
                return

            line = feSettings.read(number)  # only works because numbers sync with display
            type, line = line.split("|", 1)  # TYPE|SETTING=VALUE

            if type == "STATIC":
                print("This Value Can Not Be Changed")
                msvcrt.getch()
                return

            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
            else:
                key = line.strip()
                value = ""

            while True:
                
                if type == "BOOL":
                    if key == "security_mode":
                        request_password()
                    feSettings.reverse_logic(key, start_after="|")
                    resort_memory(); return

                os.system("cls")

                print(f"Editing: '{key} = {value}'")
                print("Enter new value or type 'EXIT' to cancel:")

                new_value = input("> ").strip()

                if new_value.lower() == "exit":
                    return

                correct_type = True

                try:
                    if type == "INT":
                        int(new_value)

                    elif type == "STR":
                        if key == "ip_addr_hash":
                            new_value = cSecurity.HMAC_SHA1(new_value.strip(), cSettings.current_password)

                    elif type == "0INT":
                        x = int(new_value)

                        if x != 1 and x != 0:
                            correct_type = False

                    if not correct_type:
                        print("Invalid Value For This Key")
                        msvcrt.getch()
                        continue

                    break

                except:
                    print("Invalid Value For This Key")
                    msvcrt.getch()
                    continue

            feSettings.write_equality(key, new_value, start_after="|")
            resort_memory(); return
        
    def Executable_Settings():
        resort_memory()
        feExecutables = FileEditor(cDirectories.executables)

        while True:
            os.system("cls")

            Special.underline("Executable Manager")

            print("[1] Add Executable")
            print("[2] Change Default")
            print("[3] Remove Executable")
            print("[4] View Executables\n")

            uinput = input("> ").strip().lower()

            if uinput == "exit":
                return "return"

            if uinput == "1":
                os.system("cls")

                path = input("[Executable Path]: ").strip().strip('"')

                if path.lower() == "exit":
                    continue

                if not os.path.exists(path):
                    print("Path does not exist.")
                    msvcrt.getch()
                    continue

                line_type = "SUB"

                if feExecutables.empty:
                    line_type = "DEFAULT"

                feExecutables.write(
                    feExecutables.total_lines(),
                    f"{line_type}|{path}"
                )

                resort_memory()

                print("Executable Added.")
                msvcrt.getch()

            elif uinput == "2":
                os.system("cls")

                if feExecutables.empty:
                    print("No executables found.")
                    msvcrt.getch()
                    continue

                for i in range(1, feExecutables.total_lines()):
                    line = feExecutables.read(i)

                    if "|" not in line:
                        continue

                    line_type, path = line.split("|", 1)

                    rgb = (0, 255, 0) if os.path.exists(path.strip()) else (255, 0, 0)

                    display = "[DEFAULT]" if line_type == "DEFAULT" else "[SUB]"

                    Special.print_as_rgb(
                        f"{i}. {display} {path}",
                        rgb=rgb
                    )

                try:
                    number = input("\n[New Default Number]: ")
                    if number.lower() == "exit":
                        return
                    number = int(number)
                except:
                    print("Invalid Number.")
                    msvcrt.getch()
                    continue

                if number < 1 or number >= feExecutables.total_lines():
                    print("Executable does not exist.")
                    msvcrt.getch()
                    continue

                current_default = None

                for i in range(1, feExecutables.total_lines()):
                    line = feExecutables.read(i)

                    if "|" not in line:
                        continue

                    line_type, path = line.split("|", 1)

                    if line_type == "DEFAULT":
                        current_default = i
                        break

                if current_default:
                    old_path = feExecutables.read(current_default).split("|", 1)[1]
                    feExecutables.write(current_default, f"SUB|{old_path}")

                new_path = feExecutables.read(number).split("|", 1)[1]
                feExecutables.write(number, f"DEFAULT|{new_path}")

                resort_memory()

                print("Default Executable Changed.")
                msvcrt.getch()

            elif uinput == "3":
                os.system("cls")

                if feExecutables.empty:
                    print("No executables found.")
                    msvcrt.getch()
                    continue

                for i in range(1, feExecutables.total_lines()):
                    line = feExecutables.read(i)

                    if "|" not in line:
                        continue

                    line_type, path = line.split("|", 1)

                    rgb = (0, 255, 0) if os.path.exists(path.strip()) else (255, 0, 0)

                    Special.print_as_rgb(
                        f"{i}. [{line_type}] {path}",
                        rgb=rgb
                    )

                try:
                    number = input("\n[Delete Number]: ")
                    if number.lower() == "exit":
                        return
                    number = int(number)

                except:
                    print("Invalid Number.")
                    msvcrt.getch()
                    continue

                if number < 1 or number >= feExecutables.total_lines():
                    print("Executable does not exist.")
                    msvcrt.getch()
                    continue

                line = feExecutables.read(number)

                if line.startswith("DEFAULT|"):
                    print("You cannot delete the default executable.")
                    msvcrt.getch()
                    continue

                feExecutables.delete(number)

                resort_memory()

                print("Executable Deleted.")
                msvcrt.getch()

            elif uinput == "4":
                os.system("cls")

                if feExecutables.empty:
                    print("No executables found.")
                    msvcrt.getch()
                    continue

                for i in range(1, feExecutables.total_lines()):
                    line = feExecutables.read(i)

                    if "|" not in line:
                        continue

                    line_type, path = line.split("|", 1)

                    rgb = (0, 255, 0) if os.path.exists(path.strip()) else (255, 0, 0)

                    display = "[DEFAULT]" if line_type == "DEFAULT" else "[SUB]"

                    Special.print_as_rgb(
                        f"{i}. {display} {path}",
                        rgb=rgb
                    )

                print("")
                msvcrt.getch()

            else:
                print("Invalid Option.")
                msvcrt.getch()

    def Onelife_Settings():
        resort_memory()
        settings_data = {
            "vogModeOn":"1","useSteamUpdate":"1","useLifeTokenServer":"1","useFitnessServer":"1","upLeftDownRightKeys":"wasd",
            "tutorialDone":"0","targetFrameRate":"60","useCustomServer":"0","soundSampleRate":"44100","soundEffectsOff":"0",
            "soundEffectsLoudness":"1.0","skipFPSMeasure":"1","serverPassword":"testPassword","recordGame":"0",
            "recordAudioLengthInSeconds":"130","recordAudio":"0","reportWildBugToUser":"0","outputAllFrames":"0",
            "mouseSpeed":"1.0","musicOff":"0","musicLoudness":"1.0","mapPullStartY":"-100","mapPullStartX":"-100",
            "mapPullMode":"0","mapPullEndY":"100","mapPullEndX":"100","loginSuccess":"1","keepPastRecordings":"20",
            "halfFrameRate":"0","fullscreen":"0","forceBigPointer":"0","emotDuration":"10","eKeyForRightClick":"0",
            "enableSpeedControlKeys":"0","enableLiveTriggers":"0","compressExports":"1","checkReviewSpelling":"1",
            "blendOutputFramePairs":"1","blendOutputFrameFraction":"0","borderlessHeightAdjust":"1","borderless":"0",
            "ahapSkipDataUpdate":"0","autoLogIn":"0","screenWidth":"1280","screenHeight":"720"
        }
        flat_list = list(settings_data.keys())
        while True:
            os.system("cls")
            Special.underline("One Hour One Life Configuration")
            for idx, setting_name in enumerate(flat_list, 1):
                file_path = os.path.join("settings", f"{setting_name}.ini")
                value = settings_data[setting_name]
                if os.path.isfile(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        value = f.read().strip()
                print(f"{idx}. {setting_name} = {value}")
            print("\nType a number or setting name.\nType 'Reset' to reset settings.\nType 'Exit' to return.")
            uinput = input("> ").strip()
            if uinput.lower() == "exit":
                return "return"
            if uinput.upper() == "RESET":
                for name in flat_list:
                    file_path = os.path.join("settings", f"{name}.ini")
                    FileEditor(file_path).write(1, settings_data[name])
                print("All settings reset..")
                msvcrt.getch()
                continue
            selected = None
            if uinput.isdigit():
                idx = int(uinput)-1
                if 0 <= idx < len(flat_list):
                    selected = flat_list[idx]
            else:
                for name in flat_list:
                    if name.lower() == uinput.lower():
                        selected = name
                        break
            if not selected:
                print("Invalid setting..")
                msvcrt.getch()
                continue
            file_path = os.path.join("settings", f"{selected}.ini")
            current_value = settings_data[selected]
            if os.path.isfile(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    current_value = f.read().strip()
            print(f"Current value: {selected} = {current_value}")
            new_value = input("New value: ").strip()
            if new_value:
                FileEditor(file_path).write(1, new_value)
    

    def fEdit_Accounts():
        resort_memory()
        x = AccManager(casecode_menu="edit accounts", menu_title_custom="EDITING ACCOUNTS")
        if x.exit:
            return "return"  
        
    def Record_Genescores():
        resort_memory()
        x = AccManager(casecode_menu="record genescores", menu_title_custom="RECORD GENESCORES")
        if x.exit:
            return "return"  
        
    def Active_Account_Detector():
        resort_memory()
        x = AccManager(casecode_menu="active account detector", menu_title_custom="ACTIVE ACCOUNT DETECTOR")
        if x.exit:
            return "return"  

    def Exe_Launcher():
        resort_memory()
        feExecutables = FileEditor(cDirectories.executables)

        while True:
            os.system("cls")
            Special.underline("Executable Launcher")

            if feExecutables.empty or feExecutables.total_lines() <= 1:
                print("No executables found.")
                msvcrt.getch()
                return

            executables = []

            for i in range(1, feExecutables.total_lines()):
                line = feExecutables.read(i)
                if not line or "|" not in line:
                    continue

                line_type, path = line.split("|", 1)
                path = path.strip()

                executables.append((i, line_type, path))

            for idx, (line_no, line_type, path) in enumerate(executables, start=1):
                display = "[DEFAULT]" if line_type == "DEFAULT" else "[SUB]"
                Special.print_as_rgb(f"{idx}. {display} {path}")

            choice = input("> ").strip().lower()

            if choice == "exit":
                return "return"

            try:
                choice = int(choice)
            except:
                print("Invalid selection.")
                msvcrt.getch()
                continue

            if choice < 1 or choice > len(executables):
                print("Out of range.")
                msvcrt.getch()
                continue

            _, _, path = executables[choice - 1]

            if not os.path.exists(path):
                print("Executable path no longer exists.")
                msvcrt.getch()
                continue

            run_executable(path)
        
    def Change_Password():
        resort_memory()

        old_pass = request_password(return_password=True)

        feSettings = FileEditor(cDirectories.settings)
        feAccounts = FileEditor(cDirectories.accounts)

        if feAccounts.empty or feAccounts.total_lines() <= 1:
            print("You have no accounts to re-encrypt.")
            msvcrt.getch()
            return "return"

        decrypted_accounts = []
        corrupt_count = 0

        for i in range(1, feAccounts.total_lines() + 1):
            line = feAccounts.read(i)
            if not line or not line.strip():
                continue

            try:
                decrypted = cSecurity.decrypt(line.strip(), old_pass)
                if decrypted:
                    decrypted_accounts.append(decrypted)
                else:
                    corrupt_count += 1
            except Exception:
                corrupt_count += 1
                continue

        if not decrypted_accounts:
            print("Failed to decrypt any accounts. Wrong password or all data is corrupt.")
            msvcrt.getch()
            return "return"

        if corrupt_count > 0:
            print(f"Warning: {corrupt_count} account(s) could not be decrypted.")

        # Get new password
        while True:
            os.system("cls")
            Special.underline("Change Client Password")

            new_pass = Special.hide_input("New password: ")
            if new_pass.lower() == "exit":
                return "return"
            if not new_pass:
                print("Password cannot be empty.")
                msvcrt.getch()
                continue

            confirm = Special.hide_input("Confirm new password: ")
            if confirm.lower() == "exit":
                return "return"

            if new_pass != confirm:
                print("Passwords do not match. Try again.")
                msvcrt.getch()
                continue

            break

        # Update hash and re-encrypt accounts
        new_hash = cSecurity.HMAC_SHA1(new_pass, password_cohash)
        feSettings.write_equality("password_hash", new_hash, start_after="|")

        # Re-encrypt all accounts with new password
        new_file = []
        for raw_account in decrypted_accounts:
            try:
                encrypted = cSecurity.package_account(raw_account, new_pass)
                new_file.append(encrypted)
            except Exception:
                continue

        # Replace file content
        feAccounts.lines = [line + "\n" if not line.endswith("\n") else line for line in new_file]
        feAccounts.save()

        # Update in-memory password if not in security mode
        cSettings.current_password = new_pass

        resort_memory()  # Refresh everything

        print(f"\n[Success] Password changed successfully!")
        print(f"{len(decrypted_accounts)} account(s) re-encrypted.")
        msvcrt.getch()
        return "return"
  
    def display_account_emails():
        resort_memory()
        if cSettings.security_mode:
            cSettings.current_password = request_password(return_password=True)
        os.system("cls")
        Special.underline("ACCOUNT EMAILS")
        AccManager.display_options(cSettings.current_password)
        msvcrt.getch()
        return

    def display_account_keys():
        resort_memory()
        cSettings.current_password = request_password(return_password=True)
        os.system("cls")
        Special.underline("ALL ACCOUNTS")
        AccManager.display_accounts(cSettings.current_password)
        msvcrt.getch()
        return
     
    def fSurveillance():
        resort_memory()
        dictonary  = {"fsDisplayed Init":False,
                      "fsPending": False,
                      "fsDisplayed Pending": False}
        x = AccManager(casecode_menu="Automation",casecode_bot="Surveillance", monitoring=True, auto_restart=True, dictionary_data=dictonary,menu_title_custom=f"Choose An Account For The Surveillance",Tutorial=2)
        if x.exit:
            return "return"

    def fDtAdvertising():
        if client:
            print("Script administators only.")
            msvcrt.getch()
            return "return"

        resort_memory()
        while True:
            dictonary  = {"faSpeech":None} # msg, time|next msg... (.split("|"))
            os.system("cls")
            print("Enter your advertising speech loop, format msg-time|msg-time|ect..")
            dictonary["faSpeech"] = input("> ")
            if dictonary["faSpeech"].lower() == "exit":
                return "return"
            dictonary["faSpeech"] = dictonary["faSpeech"].upper()
            dictonary["faSpeech"] = dictonary["faSpeech"].strip()
            
            if "-" not in dictonary["faSpeech"]:
                print("Invalid format detected."); msvcrt.getch(); continue
            break
            
        x = AccManager(casecode_menu="Automation",casecode_bot="Donkeytown Advertising", monitoring=True, auto_restart=True, dictionary_data=dictonary,menu_title_custom=f"Choose An Account For The Advertising",Tutorial=0)
        if x.exit:
            return "return"


    class AccManager:
        def __init__(self, menu_type="Regular", casecode_menu=None, casecode_bot=None, Tutorial=0, dictionary_data=None, menu_title_custom=None, rgb=console_color, monitoring=False, auto_restart=False):
            self.menu = menu_type
            self.casecode_menu = casecode_menu
            self.casecode_bot = casecode_bot
            self.monitoring = monitoring
            self.auto_restart = auto_restart
            self.dictionary_data = dictionary_data
            self.Tutorial = Tutorial
            self.menu_title_custom = menu_title_custom
            self.rgb = rgb
            self.exit = False

            resort_memory()
            Special.set_rgb(self.rgb)
            
            if self.menu_title_custom:
                Special.underline(f"{self.menu_title_custom} [{cMemory.total_accounts}]")
            else:
                Special.underline(f"ACCOUNT MANAGING MENU [{cMemory.total_accounts}]\n")

            if menu_type == "Regular":
                self.account_manager()

            elif menu_type == "Multithreaded":
                self.account_manager_mt()
            
        @staticmethod
        def display_accounts(password): # in memory we will store all the accounts as their encryped selves
            resort_memory()
            for i, account in enumerate(cMemory.accounts[1:], start=1):
                try:
                    name, email, key, extra = cSecurity.unpackage_account(account, password)
                except:
                    print(f"{i}. Corrupted Account")
                    break
                print(f"{i}. Account Name: {"$$$$$$$$$$$$$$$$$" if cSettings.mask_accounts else name}")
                print(f"Email: {"$$$$$$$$$$$$@$$$$$$$.$$$" if cSettings.mask_accounts else  email}")
                print(f"Key: {"$$$$$-$$$$$-$$$$$-$$$$$" if cSettings.mask_accounts else  key}")
                try:
                    leaderboard, genescore = extra.split(":") 
                except:
                    print("Leaderboard And Genescore: Corrupted")
                    break
                print(f"Leaderboard And Genescore: {"N/A" if cSettings.mask_accounts else leaderboard}, {genescore}\n\n")
        
        @staticmethod
        def display_options(password):
            resort_memory()
            for i, account in enumerate(cMemory.accounts[1:], start=1):
                try: 
                    name, email, key, extra = cSecurity.unpackage_account(account, password)
                    Leaderboard, Genescore = extra.split(":")
                except:
                    print(f"{i} Corrupted Account")
                    continue
                print(f"{i:>3}. {('$$$$$$$$$$$$@$$$$$$$.$$$' if cSettings.mask_accounts else (name or email))[:30]:<30} [{('N/A' if Leaderboard == 'null' or cSettings.mask_accounts else Leaderboard):>8} || {('N/A' if Genescore == 'null' else Genescore):>8}]")
            print("")

        def account_manager(self): 
            resort_memory()
            feAccounts = FileEditor(cDirectories.accounts)
            feOholKey = FileEditor(cDirectories.oholKeys)
            feOholEmail = FileEditor(cDirectories.oholEmails)
            
            if cSettings.security_mode:
                cSettings.current_password = request_password(return_password=True)
            
            if self.casecode_menu == "add accounts":
                resort_memory()
                self.display_options(cSettings.current_password)
                addName = input("[Name Of Account]: ")
                if addName.lower() == "exit":
                    self.exit = True
                    Special.set_rgb(console_color)
                    return
                addEmail = input("[Email]: ")
                if addEmail.lower() == "exit":
                    self.exit = True
                    Special.set_rgb(console_color)
                    return
                addKey = input("[Key]: ")
                if addKey.lower() == "exit":
                    self.exit = True
                    Special.set_rgb(console_color)
                    return
                
                full_str = f"{addName}/{addEmail}/{addKey}/null:null"
                encrypted = cSecurity.package_account(full_str, cSettings.current_password)
                feAccounts.write(feAccounts.total_lines(), encrypted)
                Special.set_rgb(console_color)
                return
             
            if self.casecode_menu == "edit accounts":
                resort_memory()
                self.display_options(cSettings.current_password)
                try: 
                    number = input("> ")
                    if number.lower() == "exit":
                        self.exit = True
                        return
                    number = int(number)
                    if number < 1 or number > feAccounts.total_lines():
                        print("Attempted to select a non-existant account..")
                        msvcrt.getch()
                        return
                except:
                    print("The characters you have tried to enter do not qualify as a valid number.")
                    msvcrt.getch()
                    return  


                name, email, key, extra = cSecurity.unpackage_account(cMemory.accounts[number], cSettings.current_password) # name, email, key values need to be stored in order to edit accounts
                
                while True:
                    os.system("cls")
                    Special.underline(f"Editing Account No. {number}")
                    print(f"[1] Name: {name}")
                    print(f"[2] Email: {email}")
                    print(f"[3] Key: {key}")
                        
                    try: 
                        numberA = input("> ")
                        if numberA.lower() == "exit":
                            return # returns to menu screen
                        numberA = int(numberA)
                        if numberA not in (1, 2, 3):
                            print("Attempted to select an invalid option.")
                            msvcrt.getch()
                            continue
                    except:
                        print("The characters you have tried to enter do not qualify as a valid number.")
                        msvcrt.getch()
                        continue
                    
                    copy = None
                    if numberA == 1:
                        copy = name
                        name = input("[New Name]: ")
                        if name.lower() == "exit":
                            name  = copy
                            continue
                    if numberA == 2:
                        copy = email
                        email = input("[New Email]: ")
                        if email.lower() == "exit":
                            email = copy
                            continue
                    if numberA == 3:
                        copy = key
                        key = input("[New Key]: ")
                        if key.lower() == "exit":
                            key = copy
                            continue
                    
                    fullstr = cSecurity.encrypt(f"{name}/{email}/{key}/{extra}", cSettings.current_password)
                    feAccounts.write(number, fullstr)
            
            if self.casecode_menu == "duplicate detector":
                resort_memory()

                seen = {}
                duplicate_numbers = []

                for i, account in enumerate(cMemory.accounts[1:], start=1):
                    try:
                        name, email, key, extra = cSecurity.unpackage_account(account, cSettings.current_password)
                    except:
                        print(f"Account {i} Failed to Unpackage")
                        continue

                    if key in seen:
                        duplicate_numbers.append(i)
                    else:
                        seen[key] = i

                if duplicate_numbers:
                    print("[Console]: Detected Duplicate Keys\n")
                    print("Delete Duplicates? [Y/N]")
                    choice = input("> ")

                    if choice.lower() == "y":
                        feAccounts = FileEditor(cDirectories.accounts)

                        for num in sorted(duplicate_numbers, reverse=True):
                            feAccounts.delete(num)

                        print("Duplicate Accounts Deleted Successfully!")
                        msvcrt.getch()
                        Special.set_rgb(console_color)
                        return
                    elif choice.lower() == "n":
                        self.exit = True
                        return

                else:
                    print("Found no duplicate keys!")
                    Special.set_rgb(console_color)
                    msvcrt.getch()
                    return
        
            # The Multi And Single Selection Boundery 
            while True:
                os.system("cls")

                if self.menu_title_custom:
                    Special.underline(f"{self.menu_title_custom} [{cMemory.total_accounts }]")
                else:
                    Special.underline(f"ACCOUNT MANAGING MENU [{cMemory.total_accounts }]\n")

                print("[1] Select: e.g. [x, y, z, a]")
                print("[2] Cycle: e.g. [x -> y]\n")
                
                choice = input("> ")

                if choice.lower() == "exit":
                    self.exit = True
                    Special.set_rgb(console_color)
                    return
                try:
                    choice = int(choice)
                except:
                    print("Invalid Number.")
                    msvcrt.getch()
                    continue

                if choice not in (1, 2):
                    print("Invalid option.")
                    msvcrt.getch()
                    continue
                break

            selected = []

            while True:
                os.system("cls")
                if self.menu_title_custom:
                    Special.underline(f"{self.menu_title_custom} [{cMemory.total_accounts }]")
                else:
                    Special.underline(f"ACCOUNT MANAGING MENU [{cMemory.total_accounts }]\n")
                
                self.display_options(cSettings.current_password)

              
                if cMemory.total_accounts == 0:
                    print("You Have No Accounts...")
                    msvcrt.getch()
                    self.exit = True
                    return
                            
                if choice == 1:
                    try:
                        raw = input("[Sequence] > ")
                        if raw.lower() == "exit":
                           self.exit = True
                           return

                        selected = [int(x.strip()) for x in raw.split(",")]

                    except:
                        print("Invalid number list.")
                        msvcrt.getch()
                        continue

                    for number in selected:
                        if msvcrt.kbhit() and msvcrt.getch() == b'\r':
                            print("\n[Ended Prematurely]")
                            msvcrt.getch()
                            return
                        if number < 1 or number > feAccounts.total_lines():
                            print("Account does not exist.")
                            msvcrt.getch()
                            return

                else:
                    try:
                        start = input("[Starting Number] > ")
                        if start.lower() == "exit":
                            self.exit = True
                            Special.set_rgb(console_color)
                            return

                        end = input("[Ending Number] > ")
                        if end.lower() == "exit":
                            self.exit = True
                            Special.set_rgb(console_color)
                            return

                        start = int(start)
                        end = int(end)

                    except:
                        print("Invalid number.")
                        msvcrt.getch()
                        continue

                    if start < 1 or end > feAccounts.total_lines() or end < start:
                        print("Out of range.")
                        msvcrt.getch()
                        continue

                    selected = list(range(start, end + 1))
                break
                
            if self.casecode_menu == "delete accounts":
                resort_memory()
                print(f"\nAccounts Scheduled For Deletion: {selected}")
                choice = input("[Console]: Delete? [Y/N] > ")

                if choice.lower() == "y":
                    for number in sorted(selected, reverse=True):
                        if msvcrt.kbhit() and msvcrt.getch() == b'\r':
                            print("\n[Ended Prematurely]")
                            msvcrt.getch()
                            return

                        feAccounts.delete(number)

                    print(f"\n[Console]: Accounts: {selected} Deleted")
                    msvcrt.getch()
                else:
                    print(f"\n[Console]: Deletion Cancelled {selected}")
                    msvcrt.getch()
                Special.set_rgb(console_color)
                return
            
            if self.casecode_menu == "select accounts":
                resort_memory()
                for number in selected:
                    if msvcrt.kbhit() and msvcrt.getch() == b'\r':
                        print("\n[Ended Prematurely]")
                        msvcrt.getch()
                        return 
                    name, email, key, extra = cSecurity.unpackage_account(cMemory.accounts[number], cSettings.current_password)
                    time.sleep(2)
                    feOholEmail.write(1, email)
                    feOholKey.write(1, key)
                    del name, email, key, extra
                    run_executable(cSettings.default_exe)
                    resort_memory()

                Special.set_rgb(console_color)
                return
            if self.casecode_menu == "delete accounts":
                resort_memory()
                print(f"\nAccounts Scheduled For Deletion: {selected}")
                choice = input("[Console]: Delete? [Y/N] > ")

                if choice.lower() == "y":
                    for number in sorted(selected, reverse=True):
                        if msvcrt.kbhit() and msvcrt.getch() == b'\r':
                            print("\n[Ended Prematurely]")
                            msvcrt.getch()
                            return

                        feAccounts.delete(number)

                    print(f"\n[Console]: Accounts: {selected} Deleted")
                    msvcrt.getch()
                else:
                    print(f"\n[Console]: Deletion Cancelled {selected}")
                    msvcrt.getch()
                Special.set_rgb(console_color)
                return
            
            if self.casecode_menu == "record genescores":
                resort_memory()
                while True:
                    os.system("cls")
                    print("[1] Update Genescores")
                    print("[2] Review Genescore Changes")
                    choice = 1
                    try:
                        choice  = input("> ")
                        if choice == "exit":
                            self.exit = True

                        choice = int(choice)
                            
                        if choice in (1,2):
                            break
                        continue
                    except:
                        continue
                os.system("cls")

                if self.menu_title_custom:
                    Special.underline(f"{self.menu_title_custom} [{cMemory.total_accounts }]")
                else:
                    Special.underline(f"ACCOUNT MANAGING MENU [{cMemory.total_accounts }]\n")
                    
                if choice == 1:
                    
                    for number in selected:
                        if msvcrt.kbhit() and msvcrt.getch() == b'\r':
                            print("\n[Ended Prematurely]")
                            msvcrt.getch()
                            return
                        try:
                            name, email, key, extra = cSecurity.unpackage_account(cMemory.accounts[number], cSettings.current_password)
                            ticket_id = key.replace("-", "").upper()

                            sequence_number = requests.get(f"https://onehouronelife.com/fitnessServer/server.php?action=get_client_sequence_number&email={email}", timeout=5).text.split()[0]

                            hash_value = hmac.new(ticket_id.encode(), sequence_number.encode(), hashlib.sha1).hexdigest()

                            response = requests.get("https://onehouronelife.com/fitnessServer/server.php", params={"action": "get_client_score", "email": email, "sequence_number": sequence_number, "hash_value": hash_value}, timeout=6).text.splitlines()

                            leaderboard_name = response[0].strip()
                            score = response[1].strip()
                            leaderboard_namet = " ".join(leaderboard_name.split("_"))
                            extra = f"{leaderboard_namet}:{score}"
                            fullstr = f"{name}/{email}/{key}/{extra}"

                            feAccounts.write(number, cSecurity.package_account(fullstr, cSettings.current_password))

                            print(f"{number}. {name or email}: Score {score}")

                        except:
                            print(f"{number}. {name or email} Failed")

                    msvcrt.getch()
                    self.exit = True
                    return
                else:
                    for number in selected:
                        if msvcrt.kbhit() and msvcrt.getch() == b'\r':
                            print("\n[Ended Prematurely]")
                            msvcrt.getch()
                            return
                        try:
                            name, email, key, extra = cSecurity.unpackage_account(cMemory.accounts[number], cSettings.current_password)
                            ticket_id = key.replace("-", "").upper()

                            sequence_number = requests.get(f"https://onehouronelife.com/fitnessServer/server.php?action=get_client_sequence_number&email={email}", timeout=5).text.split()[0]

                            hash_value = hmac.new(ticket_id.encode(), sequence_number.encode(), hashlib.sha1).hexdigest()

                            response = requests.get("https://onehouronelife.com/fitnessServer/server.php", params={"action": "get_client_score", "email": email, "sequence_number": sequence_number, "hash_value": hash_value}, timeout=6).text.splitlines()

                            leaderboard_name = response[0].strip()
                            score = response[1].strip()

                            acc_lead_name, acc_genescore = extra.split(":")

                            fullstr = f"{name}/{email}/{key}/{extra}"

                            print(f"{number}. {name or email}|| {leaderboard_name} || [{acc_genescore}] -> [{score}]")

                        except:
                            print(f"{number}. {name or email} Failed")
                        

                    msvcrt.getch()
                    self.exit = True
                    return

            if self.casecode_menu == "active account detector":
                os.system("cls")
                if self.menu_title_custom:
                    Special.underline(f"{self.menu_title_custom} [{cMemory.total_accounts }]")
                else:
                    Special.underline(f"ACCOUNT MANAGING MENU [{cMemory.total_accounts }]\n")
                for number in selected:

                    if msvcrt.kbhit() and msvcrt.getch() == b'\r':
                        print("\n[Ended Prematurely]")
                        msvcrt.getch()
                        return

                    name, email, key, extra = cSecurity.unpackage_account(cMemory.accounts[number], cSettings.current_password)

                    ticket_server = f"https://onehouronelife.com/ticketServer/server.php?action=show_downloads&ticket_id={key}"

                    try:
                        server_response = requests.get(ticket_server, timeout=1)
                        server_response.raise_for_status()
                        response_text = server_response.text.strip()

                        if "Your ticket number was not found" in response_text:
                            status = "[Disabled]"
                        elif "You no longer own the game on Steam" in response_text:
                            status = "[Disabled - Game No Longer Owned On Steam]"
                        else:
                            status = "[Active]"

                    except:
                        status = "Request Failed [Unknown]"

                    display = email if name.upper() == "NONE" else name
                    print(f"{number}. {display}: {status}")

                msvcrt.getch()
                self.exit = True
                return

            if self.casecode_menu == "Automation":
                os.system("cls")
                resort_memory()
                for number in selected:
                    if msvcrt.kbhit() and msvcrt.getch() == b'\r':
                        print("\n[Ended Prematurely]")
                        msvcrt.getch()
                        return 
                    name, email, key, extra = cSecurity.unpackage_account(cMemory.accounts[number], cSettings.current_password)
                    account_tuple = (name, email, key, extra)
                    program = Automation(account_tuple=account_tuple, monitoring=self.monitoring, casecode=self.casecode_bot, auto_restart=self.auto_restart, dictionary_data=self.dictionary_data, tutorial=self.Tutorial)
                    thread = threading.Thread(target=program.run, daemon=True)
                    thread.start()
                    thread.join()
                    if program.status[0] == "Error":
                        print(f"Error Info: {program.status[1]}")
                        msvcrt.getch()
                    elif program.status[0] == "Stopped":
                        print(program.status[1])
                        msvcrt.getch()
                    else:
                        print(program.status[1])
                        msvcrt.getch()
                    resort_memory()

                Special.set_rgb(console_color)
                return    

        def account_manager_mt(self):
            resort_memory()
            feAccounts = FileEditor(cDirectories.accounts)
            if cSettings.security_mode:
                cSettings.current_password = request_password(return_password=True)

            if self.menu_title_custom:
                Special.underline(f"{self.menu_title_custom} [{cMemory.total_accounts }]")
            else:
                Special.underline(f"ACCOUNT MANAGING MENU [{cMemory.total_accounts }]\n")

            self.display_options(Settings.current_password)

            if not self.casecode_menu:
                pass

    class StreamParser:
        def __init__(self):
            self.buffer = b""

        def feed(self, data: bytes):
            self.buffer += data

        def get_messages(self):
            messages = []

            while True:
                if not self.buffer:
                    break

                hashtag_pos = self.buffer.find(b"#")
                if hashtag_pos == -1:
                    break  

                header_block = self.buffer[:hashtag_pos+1]
                header_text = header_block.decode("utf-8", errors="ignore")

                if header_text.startswith("CM"):
                    parts = header_text.split()
                    if len(parts) < 3:
                        break

                    compressed_size = int(parts[2])
                    total_needed = hashtag_pos + 1 + compressed_size

                    if len(self.buffer) < total_needed:
                        break 
                    compressed_data = self.buffer[hashtag_pos+1:total_needed]
                    decompressed = zlib.decompress(compressed_data).decode()

                    messages.append(decompressed)

                    self.buffer = self.buffer[total_needed:]
                    continue

                elif header_text.startswith("MC"):
                    parts = header_text.split()
                    if len(parts) < 7:
                        break

                    compressed_size = int(parts[6])
                    total_needed = hashtag_pos + 1 + compressed_size

                    if len(self.buffer) < total_needed:
                        break

                    compressed_data = self.buffer[hashtag_pos+1:total_needed]
                    decompressed = zlib.decompress(compressed_data)

                    full_message = header_text + decompressed.decode()
                    messages.append(full_message)

                    self.buffer = self.buffer[total_needed:]
                    continue

                
                else:
                    message = header_text[:-1]  # remove #
                    messages.append(message)
                    self.buffer = self.buffer[hashtag_pos+1:]
                    continue

            return messages
        
    class Automation:
        def __init__(self, account_tuple=(None,None,None,"null:null"), dictionary_data=None, tutorial=0, casecode=None, auto_restart=False, monitoring=False):
            self.name, self.email, self.key, self.extra = account_tuple
            self.key = self.key.replace("-","")
            self.leaderboard, self.genescore = self.extra.split(":")
            self.dictionary_data = dictionary_data
            self.tutorial = tutorial
            self.casecode = casecode
            self.auto_restart = auto_restart
            self.monitoring = monitoring
            #self.status(Status, Message) Status always in (T)itle format. 
            self.stop_active = False; self.restart_active = False; self.status = ("Neutral", "All fine!")
            self.msg_index = 0
            self.next_msg_time = 0
            self.timer = Timer()
        @dataclass
        class LiveObject:
            def readplayersprite(self, gender_id):
                mapping = {
                    # White
                    19: ("White", "Female"), 350: ("White", "Female"), 1007: ("White", "Female"),
                    352: ("White", "Male"), 347: ("White", "Male"), 1008: ("White", "Male"),
                    # Ginger
                    1628: ("Ginger", "Female"), 2462: ("Ginger", "Female"),
                    3081: ("Ginger", "Male"), 3080: ("Ginger", "Male"), 2403: ("Ginger", "Male"),
                    # Brown
                    351: ("Brown", "Female"), 353: ("Brown", "Female"), 1009: ("Brown", "Female"),
                    354: ("Brown", "Male"), 355: ("Brown", "Male"), 1010: ("Brown", "Male"),
                    # Black
                    2404: ("Black", "Female"), 2464: ("Black", "Female"),
                    1629: ("Black", "Male"), 3078: ("Black", "Male"), 3079: ("Black", "Male"),
                    # Special
                    3201: ("Jason", "Developer")
                }
            
                return mapping.get(gender_id, ("Unknown", "Unknown"))
            dead: bool = False
            p_id: int = None; po_id: int = None; facing: int = None; action: int = None
            action_target_x: int = None; action_target_y: int = None

            lineage = None

            # Can be int OR container string like "12,45,78"
            o_id: str = None

            # 1 or 0 in protocol
            o_origin_valid: int = None
            o_origin_x: int = None; o_origin_y: int = None
            o_transition_source_id: int = None

            heat: float = None
            done_moving_seqNum: int = None

            # 0 or 1
            force: int = None

            x: int = None; y: int = None

            age: float = None; age_r: float = None; move_speed: float = None

            clothing_set: str = None

            # 0 or 1
            just_ate: int = None

            last_ate_id: int = None; responsible_id: int = None

            # 0 or 1
            held_yum: int = None

            # not present in protocol
            held_learned: int = None

            # local/client-side only
            race: int = None; sex: int = None; name: str = None

            def update_pu(self, playerUpdate=None):
                try:
                    if not playerUpdate: return

                    pu = playerUpdate.split()

                    self.p_id = int(pu[0]); self.po_id = int(pu[1]); self.facing = int(pu[2]); self.action = int(pu[3])
                    self.action_target_x = int(pu[4]); self.action_target_y = int(pu[5]); self.o_id = pu[6]
                    self.o_origin_valid = int(pu[7]); self.o_origin_x = -int(pu[8]); self.o_origin_y = -int(pu[9])
                    self.o_transition_source_id = int(pu[10]); self.heat = float(pu[11]); self.done_moving_seqNum = int(pu[12])
                    self.force = int(pu[13])
                    self.x = pu[14]; self.y = pu[15]
                    if not (self.x == "X" or self.y == "X"):
                        self.x = int(self.x); self.y = int(self.y)
                    else:
                        self.dead = True

                    self.age = float(pu[16]); self.age_r = float(pu[17]); self.move_speed = float(pu[18])
                    self.clothing_set = pu[19]; self.just_ate = int(pu[20]); self.last_ate_id = int(pu[21])
                    self.responsible_id = int(pu[22]); self.held_yum = int(pu[23])

                    if len(pu) > 24: self.held_learned = int(pu[24])
                    self.race, self.sex = self.readplayersprite(int(self.po_id))
                except Exception as e:
                    traceback.print_exc()
                    msvcrt.getch()
        class NonLiveObject:

            def __init__(self, o_num=None):
                self.o_num = o_num

                self.id = None
                self.name = None
                self.props = {}
                self.sprites = []

                path = os.path.join("objects", f"{o_num}.txt")

                if not os.path.exists(path):
                    return

                with open(path, "r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f if line.strip()]

                if len(lines) < 2:
                    return

                # Header
                if lines[0].startswith("id="):
                    self.id = lines[0].split("=", 1)[1]

                self.name = lines[1]

                idx = 2

                # Parse object properties before sprites
                while idx < len(lines):
                    line = lines[idx]

                    if line.startswith("spriteID="):
                        break

                    for part in line.replace("#", ",").split(","):
                        if "=" not in part:
                            continue

                        k, v = part.split("=", 1)
                        self.props[k.strip()] = v.strip()

                    idx += 1

                # Apply props as attributes
                for k, v in self.props.items():
                    setattr(self, k, v)

                num_sprites = int(self.props.get("numSprites", 0))

                # Parse sprite blocks
                current_sprite = None

                while idx < len(lines):

                    line = lines[idx]

                    if line.startswith("headIndex="):
                        break

                    if line.startswith("spriteID="):

                        if current_sprite:
                            self.sprites.append(current_sprite)

                        current_sprite = {}

                    parts = line.split(",")

                    for part in parts:
                        if "=" not in part:
                            continue

                        k, v = part.split("=", 1)

                        if current_sprite is not None:
                            current_sprite[k.strip()] = v.strip()

                    idx += 1

                if current_sprite:
                    self.sprites.append(current_sprite)

                # Parse trailing properties
                while idx < len(lines):

                    line = lines[idx]

                    for part in line.replace("#", ",").split(","):

                        if "=" not in part:
                            continue

                        k, v = part.split("=", 1)

                        self.props[k.strip()] = v.strip()
                        setattr(self, k.strip(), v.strip())

                    idx += 1

                # Convenience lists

                if hasattr(self, "sounds"):
                    self.soundsList = self.sounds.split(",")

                if hasattr(self, "useVanishIndex"):
                    self.useVanishIndexList = self.useVanishIndex.split(",")

                if hasattr(self, "useAppearIndex"):
                    self.useAppearIndexList = self.useAppearIndex.split(",")

                if hasattr(self, "heldOffset"):
                    parts = self.heldOffset.split(",")
                    self.heldOffsetX = parts[0] if len(parts) > 0 else None
                    self.heldOffsetY = parts[1] if len(parts) > 1 else None

                if hasattr(self, "clothingOffset"):
                    parts = self.clothingOffset.split(",")
                    self.clothingOffsetX = parts[0] if len(parts) > 0 else None
                    self.clothingOffsetY = parts[1] if len(parts) > 1 else None

            def __getattr__(self, name):
                return None
        class Tile:
            def __init__(self, cell=None, x=None, y=None):
                self.biome, self.floor, parse = cell.split(":", 2)

                self.object = None

                # [container, [contents]]
                self.subcontainers = []

                # direct contents only
                self.contained = []

                sections = parse.split(":")

                # Main object
                first = sections[0].split(",")

                self.object = first[0]

                # direct contents of main object
                if len(first) > 1:
                    self.contained.extend(first[1:])

                # subcontainers
                for sub in sections[1:]:
                    parts = sub.split(",")

                    container = parts[0]
                    contents = parts[1:]

                    # Only add the container itself
                    self.contained.append(container)

                    # store full subcontainer data separately
                    self.subcontainers.append([container, contents])
                self.properties = Automation.NonLiveObject(self.object)

        class ClothingSet:
            def __init__(self, set):

                def process_clothing(raw_clothing_str):
                    if "," in raw_clothing_str:
                        clothing_object, clothing_contents = raw_clothing_str.split(",", 1)
                        clothing_contents = clothing_contents.split(",")
                    else:
                        clothing_object = raw_clothing_str
                        clothing_contents = []

                    return (clothing_object, clothing_contents)

                rHat, rTunic, rFront_Shoe, rBack_Shoe, rBottom, rBackpack = set.split(";")

                self.tHat = process_clothing(rHat)
                self.tTunic = process_clothing(rTunic)
                self.tPair_of_shoes = (
                    process_clothing(rFront_Shoe),
                    process_clothing(rBack_Shoe)
                )
                self.tBottom = process_clothing(rBottom)
                self.tBackpack = process_clothing(rBackpack)
                self.tBackpack = process_clothing(rBackpack)
        
        class HeldInventory:
            def __init__(self, set):
            
                self.objects = []
                if "," in set:
                    self.base_obj, contents = set.split(",", 1)
                    contents = contents.split(",")
                    # base, content []
                    for object in contents:
                        if ":" in object:
                            x, y = object.split(":",1)
                            object = (x, y.split(":"))
                        else:
                            object = (object, [])
                        self.objects.append(object)
                else:
                    self.base_obj = set 
                  

        class Map:
            def __init__(self):
                self.mapsizeX = 64
                self.mapsizeY = 64
                self.mapCells = self.mapsizeX * self.mapsizeY

                self.mapGrid = [[0 for _ in range(self.mapsizeX)] for _ in range(self.mapsizeY)]
                            
            def chunk_change(self, mc_split, initial=True):
                pass
            
            def map_change(self, mx_split=True):
                pass
            
        @dataclass
        class Automation_Memory:
            players: list = field(default_factory=list)
            families: list = field(default_factory=list)
            my_pid: int | None = None # refer to bot in the 1st person
            my_player: Any | None = None
            my_vision: Any | None = None
            total_players: int = 0


        def run(self):
            def fetch_livePlayer(p_id):
                for livePlayer in our_memory.players:
                    if livePlayer.p_id == p_id:
                        return livePlayer       
                                
            def fetch_livePlayerbyName(name):
                for livePlayer in our_memory.players:
                    if livePlayer.name and livePlayer.name == name:
                        return livePlayer
            class Family:
                def __init__(self, name):
                    self.name = name
                    self.ghost_only = False
                    self.members = []
                    self.fertiles = 0
                    self.infertiles = 0
                    self.boys = 0
                    self.girls = 0
                    self.jason = 0

                @property
                def total(self):
                    return len(self.members)

                def update_list(self):
                    self.fertiles = 0
                    self.infertiles = 0
                    self.boys = 0
                    self.girls = 0
                    self.jason = 0
                    self.ghost_only = False

                    for member in self.members[:]:  # copy to avoid issues when removing
                        livePlayer = fetch_livePlayerbyName(member)
                        if not livePlayer:
                            continue
                                
                        if livePlayer.x == "X":
                            self.members.remove(member)
                            continue

                        if float(livePlayer.age) < 40.0 and livePlayer.sex == "Female":
                            self.fertiles += 1
                        if float(livePlayer.age) >= 40.0 and livePlayer.sex in ("Male", "Developer"):
                            self.infertiles += 1
                        if livePlayer.sex == "Female":
                            self.girls += 1
                        if livePlayer.sex == "Developer":
                            self.jason += 1
                        else:
                            self.boys += 1

            # Ensure consistent startup state
            self.stop_active = False
            self.restart_active = False
            self.status = ("Starting", "All fine!")

            while not self.stop_active:
                our_memory = self.Automation_Memory()
                self.restart_active = False  # reset exactly once per connection attempt

                pieSocket = None
                parser = None

                try:
                    pieSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    pieSocket.connect((cSettings.server_ip, cSettings.port))
                    pieSocket.setblocking(False)
                    parser = StreamParser()

                except Exception:
                    traceback.print_exc()
                    self.status = ("Error", "Failed to connect to the server, automation stopped.")
                    self.stop_active = True
                    break

                try:
                    # Main read loop: exits when stop_active or restart_active is set
                    while not self.stop_active and not self.restart_active:
                        # 1) Handle user input first (preempts read loop behavior)
                        while msvcrt.kbhit():
                            key = msvcrt.getch()
                            if key in (b'u', b'U'):
                                self.status = (self.status[0], "Displayed Surveillance Updating")
                            elif key in (b'r', b'R'):
                                self.restart_active = True
                                self.status = ("Restarting", "Manual restart requested")
                                break
                            elif key == b'\r':
                                self.stop_active = True
                                self.status = (self.status[0], "Stopping requested")
                                break

                        if self.stop_active or self.restart_active:
                            break

                        # 2) Receive data (non-blocking)
                        try:
                            data = pieSocket.recv(10000)
                            if not data:
                                # Connection dropped by server
                                if self.auto_restart:
                                    self.restart_active = True
                                    self.status = ("Respawning", "Bot attempting respawn (no data)")
                                else:
                                    self.status = ("Disconnected", "Bot was forcefully disconnected.")
                                    self.stop_active = True
                                break

                            parser.feed(data)

                        except BlockingIOError:
                            continue
                        except ConnectionResetError:
                            # Treat as restartable failure
                            self.restart_active = True
                            self.status = ("Restarting", "Connection reset by peer")
                            break

                        # 3) Process parsed messages
                        for message in parser.get_messages():
                            message = message.replace("#", "")
                            message_split = message.split()
                            if not message_split:
                                continue

                            header = message_split[0]
                            del message_split[0]

                            message_linesplit = message.splitlines()
                            if message_linesplit:
                                # your original logic deletes first line; keep same behavior
                                del message_linesplit[0]

                            # ====== LOGIN / ACCEPTED / REJECTED ======
                            if header == "SN":
                                Secret = message_split[1]
                                Hash = cSecurity.HMAC_SHA1(cSettings.server_password, Secret)
                                Keyhash = cSecurity.HMAC_SHA1(self.key, Secret)

                                Login = f"LOGIN {cSettings.client} {self.email} {Hash} {Keyhash} {self.tutorial}#"
                                pieSocket.sendall(Login.encode())

                            if header == "ACCEPTED":
                                self.status = ("Active", "All fine!")
                                if self.monitoring:
                                    pieSocket.sendall(
                                        "MOVE 0 0 @2 -1 -1 -2 -2 -3 -2 -4 -2 -5 -2 -6 -2 -7 -2 -8 -2 -9 -2 -10 -2 -11 -2 -12 -2#".encode()
                                    )

                            if header in ("REJECTED", "SHUTDOWN", "SERVER_FULL"):
                                self.status = (f"Error", f"Server Rejection: {header}")
                                self.stop_active = True
                                break
                            elif header in ("NO_LIFE_TOKENS"):
                                    print("[Life Tokens Exhausted, waiting 13500 seconds.]")
                                    self.status = ("Restarting", "Restarting After No Life Tokens")
                                    time.sleep(13500)
                                    self.restart_active = True
                            # ====== MAP CHUNK ======
                            if header == "MC":
                                # NOTE: your original code had "our_memory.my_vision" as sometimes class,
                                # but this is beyond restart. We keep your approach but make it instance-safe.
                                if our_memory.my_vision is None:
                                    our_memory.my_vision = self.Map()

                                sizeX = int(message_split[0])
                                sizeY = int(message_split[1])
                                mc_x = int(message_split[2])
                                mc_y = int(message_split[3])

                                flat_map = message_split[6:]
                                _ = our_memory.my_vision  # keep reference

                                map_2d = [
                                    [
                                        self.Tile(
                                            cell=flat_map[(sizeY - 1 - y) * sizeX + x],
                                            x=x,
                                            y=y
                                        )
                                        for x in range(sizeX)
                                    ]
                                    for y in range(sizeY)
                                ]
                                # You didn’t assign map_2d into memory. Keeping behavior minimal.

                            elif header == "MX":
                                # your original MX parsing (kept structure)
                                for tile_change in message_linesplit:
                                    tc = tile_change.split()
                                    if len(tc) < 5:
                                        continue
                                    mx_x = tc[0]
                                    mx_y = tc[1]
                                    new_floor_id = tc[2]
                                    new_id = tc[3]
                                    player = tc[4]
                                    # optional old coords
                                    if len(tc) > 5:
                                        old_x = tc[5]
                                        old_y = tc[6]

                            # ====== PLAYER UPDATE ======
                            if header == "PU":
                                if not our_memory.my_pid:
                                    our_memory.my_pid = int(message_linesplit[-1].split()[0])
                                    our_memory.my_player = self.LiveObject()
                                    our_memory.my_player.update_pu(playerUpdate=message_linesplit[-1])

                                # Your original dead handling & totals
                                if our_memory.players:
                                    for i, livePlayer in enumerate(our_memory.players):
                                        if getattr(livePlayer, "dead", False):
                                            our_memory.total_players -= 1
                                            del our_memory.players[i]
                                if not our_memory.players:
                                    for message in message_linesplit:
                                        our_memory.total_players += 1
                                        x = self.LiveObject()
                                        x.update_pu(playerUpdate=message)
                                        our_memory.players.append(x)
                                else:
                                    existing_players = {p.p_id: p for p in our_memory.players}

                                    for message in message_linesplit:
                                        pid = int(message.split()[0])

                                        if pid in existing_players:
                                            existing_players[pid].update_pu(message)
                                        else:
                                            if self.status[1] == "Displayed Surveillance":
                                                self.dictionary_data["fsPending"] = True

                                            our_memory.total_players += 1
                                            x = self.LiveObject()
                                            x.update_pu(playerUpdate=message)
                                            our_memory.players.append(x)

                            # ====== NAME / LINEAGE ======
                            if header == "NM":
                                for livePlayer in our_memory.players:
                                    for message in message_linesplit:
                                        pid = int(message.split()[0])
                                        name = " ".join(message.split()[1:])
                                        if pid == livePlayer.p_id:
                                            livePlayer.name = name

                            elif header == "LN":
                                for message in message_linesplit:
                                    for livePlayer in our_memory.players:
                                        pid = int(message.split()[0])
                                        if pid == livePlayer.p_id:
                                            livePlayer.lineage = message

                            # ====== SPECIAL CASE ======
                            if header == "PS":
                                if self.casecode == "Donkeytown Advertising":
                                    message = message.splitlines()
                                    Special.print_as_rgb(f"Successfully Recieved: {message[1]}",rgb=(0,255,0))

                            # ====== FAMILY BUILD ======
                            if our_memory.players:
                                for livePlayer in our_memory.players:
                                    if not livePlayer.name:
                                        lastname = "Unnamed"
                                        livePlayer.name = "Player Unnamed"
                                        if livePlayer.lineage:
                                            mom_pid = livePlayer.lineage.split()[1]
                                            mom = None
                                            # inline your fetch_livePlayer(mom_pid) logic
                                            for lp2 in our_memory.players:
                                                if lp2.p_id == int(mom_pid):
                                                    mom = lp2
                                                    break
                                            if mom and getattr(mom, "name", None):
                                                parts = mom.name.split()
                                                if len(parts) > 2:
                                                    lastname = parts[-1]
                                    else:
                                        parts = livePlayer.name.split()
                                        lastname = parts[1] if len(parts) == 2 else "Unnamed"

                                    # find/create family
                                    for family in our_memory.families:
                                        if family.name == lastname:
                                            break
                                    else:
                                        family = Family(name=lastname)  # requires Family class; see note below
                                        our_memory.families.append(family)

                                    if livePlayer.name and livePlayer.name not in family.members:
                                        family.members.append(livePlayer.name)

                            if our_memory.families:
                                for family in our_memory.families:
                                    family.update_list()

                            if our_memory.my_pid:
                                # update your own player reference
                                our_memory.my_player = None
                                for lp in our_memory.players:
                                    if lp.p_id == our_memory.my_pid:
                                        our_memory.my_player = lp
                                        break

                            # ====== CASE BEHAVIOR ======
                            if self.status[0] == "Active":
                                now = datetime.now()
                                if self.casecode == "Donkeytown Advertising":
                                    if not hasattr(self, 'msg_index'):
                                        self.msg_index = 0
                                        self.next_msg_time = time.time()

                                    msgs = self.dictionary_data["faSpeech"].split("|")

                                    if time.time() >= self.next_msg_time:
                                        msg = msgs[self.msg_index]
                                        Special.print_as_rgb(f"\nserver population: {our_memory.total_players}",rgb=(255,255,0))
                                        melding, tid = msg.rsplit("-", 1)
                                        wait_time = int(tid.strip())

                                        Special.print_as_rgb(f"{now}| Sent: {melding}",rgb=(0,160,0))
                                        pieSocket.sendall(f"SAY 0 0 {melding}#".encode())

                                        self.next_msg_time = time.time() + wait_time
                                        self.msg_index = (self.msg_index + 1) % len(msgs)

                                else:
                                    self.msg_index = 0
                                    self.next_msg_time = time.time()

                            # ====== SURVEILLANCE UI ======
                            if self.casecode == "Surveillance" and self.status[1] != "Displayed Surveillance" and our_memory.families:
                                self.status = (self.status[0], "Displayed Surveillance")
                                os.system("cls")
                                print("[U] - Add Pending Updates || R - [Refresh]  || [ENTER] - Exit]")
                                print(f"Ш Shady's All Seeing Eye [SHA]|| Server Population: {our_memory.total_players}")

                                if self.dictionary_data["fsPending"] and self.dictionary_data["fsDisplayed Pending"] == False:
                                    print("Display Pending")
                                    self.dictionary_data["fsDisplayed Pending"] = True

                                for fam in our_memory.families:
                                    print(f"[Family] {fam.name}: {fam.total}")
                                    print(f"[Fertiles] {fam.fertiles} ||  Infertiles: {fam.infertiles}")
                                    print(f"[Males] {fam.boys} || [Females] {fam.girls} || [Jason Rohrer] {fam.jason}")
                                    Special.print_as_rgb(
                                        "┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉\n",
                                        rgb=(0, 255, 0)
                                    )

                                    for member in fam.members:
                                        lp = None
                                        for lp2 in our_memory.players:
                                            if getattr(lp2, "name", None) == member:
                                                lp = lp2
                                                break
                                        if not lp:
                                            continue

                                        clothings = self.ClothingSet(lp.clothing_set)
                                        holdings = self.HeldInventory(lp.o_id)
                                        held_obj = self.NonLiveObject(holdings.base_obj)

                                        Special.print_as_rgb(
                                            "┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉",
                                            rgb=(255, 255, 0)
                                        )
                                        Special.print_as_rgb(f"{lp.name}", rgb=(255, 0, 255))
                                        print(f" Race: {lp.race} ||Sex: {lp.sex} || CMSN: {lp.done_moving_seqNum}")
                                        print(f" Age: {lp.age} || Heat: {lp.heat} || Speed {lp.move_speed}")
                                        print(f" Interacted With: {self.NonLiveObject(lp.o_transition_source_id).name}")
                                        print(f" Holding - [{held_obj.name}]: ", end="")

                                        if held_obj.name is not None:
                                            if int(getattr(held_obj, "numSlots", 0)) > 0:
                                                for object in holdings.objects:
                                                    if object[1] == []:
                                                        print(f"[{self.NonLiveObject(object[0]).name}] ", end="")
                                                    else:
                                                        print(
                                                            f"{self.NonLiveObject(object[0]).name}: {self.NonLiveObject(object[1]).name}|",
                                                            end=""
                                                        )

                                        print("")
                                        print(f"  Hat: {self.NonLiveObject(clothings.tHat[0]).name}")
                                        # shoes
                                        print(
                                            f"  Shoes: [{self.NonLiveObject(clothings.tPair_of_shoes[0][0]).name} || {self.NonLiveObject(clothings.tPair_of_shoes[0][0]).name}]"
                                        )
                                        print(f"  Shirt: {self.NonLiveObject(clothings.tTunic[0]).name}: ", end="")
                                        for thing in clothings.tTunic[1]:
                                            print(f"[{self.NonLiveObject(thing).name}]", end="")
                                        print(f"\n  Pants: {self.NonLiveObject(clothings.tBottom[0]).name}:", end="")
                                        for thing in clothings.tBottom[1]:
                                            print(f"[{self.NonLiveObject(thing).name}]", end="")
                                        print("")
                                        print(f"  {self.NonLiveObject(clothings.tBackpack[0]).name}: ", end="")
                                        for objs in clothings.tBackpack[1]:
                                            print(f"[{self.NonLiveObject(objs).name}]", end="")

                                        print("")

                                Special.print_as_rgb(
                                    "┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉",
                                    rgb=(255, 255, 0)
                                )

                        # ====== End for message loop ======

                except Exception:
                    # Any unexpected exception inside loop: you can decide restart vs stop.
                    traceback.print_exc()
                    # You were previously restarting sometimes; but for stability, stop on unknown crash:
                    self.stop_active = True
                    self.status = ("Error", "Unhandled exception; automation stopped.")
                    break

                finally:
                    if pieSocket:
                        try:
                            pieSocket.close()
                        except Exception:
                            pass

                if self.restart_active and not self.stop_active:
                    self.status = ("Restarting", "Program is restarting itself")
                    # cleanly continue outer while loop to reconnect
                    continue

                # If stop_active set, exit outer loop
                if self.stop_active:
                    break         


    # INDEPENDENT FUNCTIONS
    def initalize():
        if client:
            check_shady_antipiracy()

        resort_memory() # Should always come first
        os.system(f'title {terminal_name}')
        if cSettings.security_mode == False:
            cSettings.current_password = request_password(return_password=True, main_menu=True)
        else:
            request_password(return_password=False) # Not recording password to be eaisly used
        setup_ipcheck()

        os.system("cls")
        if console_color:

            reset_to_custom = f"\033[38;2;{console_color[0]};{console_color[1]};{console_color[2]}m"
        else:
            reset_to_custom = "\033[0m"
        
        cMenu = ClientMenu(
            main_menu=True,
            options={
                "Client Settings": {"Function": Client_Settings, "Single Run": False, "Key": "CS"},
                "Onelife Settings": {"Function": Onelife_Settings, "Single Run": False, "Key": "OC"},   
                "Executable Settings": {"Function": Executable_Settings, "Single Run": False, "Key": "EC"},        
                "Password Changer": {"Function": Change_Password, "Single Run": False, "Key": "PS"},       
                "Debug": {"Function": debug, "Single Run": True, "Key": "DEBUG"},
                "Add Accounts": {"Function": fAdd_Accounts, "Single Run": False, "Key": "1a"},
                "Delete Accounts": {"Function": fRemove_Accounts, "Single Run": False, "Key": "2a"},  
                "Edit Accounts": {"Function": fEdit_Accounts, "Single Run": False, "Key": "3a"}, 
                "Duplicate Account Detector": {"Function": fDuplicate_Account_Detector, "Single Run": False, "Key": "4a"},       
                "Select Accounts": {"Function": fSelect_Accounts, "Single Run": False, "Key": "1b"},
                "Exe Launcher": {"Function": Exe_Launcher, "Single Run": False, "Key": "L"},   
                "Display Emails": {"Function": display_account_emails, "Single Run": True, "Key": "VA"},
                "Display Keys": {"Function": display_account_keys, "Single Run": True, "Key": "VK"},
                "Generate Codes": {"Function": generate_client_codes, "Single Run": True, "Key": "ADMIN"},      
                "Record Genescores": {"Function": Record_Genescores, "Single Run": False, "Key": "SCR"}, 
                "Active Account Detector": {"Function": Active_Account_Detector, "Single Run": False, "Key": "ACD"}, 
                "Surveillance": {"Function": fSurveillance, "Single Run": False, "Key": "1"}, 
                "Advertising Bot": {"Function": fDtAdvertising, "Single Run": False, "Key": "2"}, 
            },
            color=console_color,
            replacement_display = (
                f"{terminal_name}\n"
                f"\033[93m/////////IP TRACKING ADVISORY - DO NOT SHARE - DO NOT LOGIN WITHOUT A VPN/////////{reset_to_custom}\n"
                "─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────\n"
                "Console|\n"
                "[CS] Console Config      [EC] Executable Config    [OC] Onelife Config    [PS] Change Password\n\n"

                "Accounts|\n"
                "[1a] Add Accounts    [2a] Delete Accounts    [3a] Edit Accounts        [4a] Duplicate Detector\n"
                "[VA] View Accounts    [VK] View Keys         [SCR] Record Genescores   [ACD] Active Account Detector\n\n"
                "[ADMIN] See client codes\n"

                "Launcher|\n"
                "[1b] Select Accounts    [L] Launcher\n\n"

                "Exploits|\n"
                "[1] Surveillance       [2] Donkeytown Advertising \n"
                "─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────\n"
                "[DEBUG] Debug Menu]"
            )
        )
        cMenu.menu()
        # After Menu

    initalize()
except Exception as e:
    print("Full Error Traceback:")
    traceback.print_exc()
    msvcrt.getch()
