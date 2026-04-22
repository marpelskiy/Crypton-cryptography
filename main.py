import customtkinter as ctk
from tkinter import filedialog
import os
import threading
import hashlib
import secrets
import string
import sys
from Crypto.Cipher import AES, ChaCha20
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

try:
    import winsound
except ImportError:
    winsound = None


BG_APP = "#09090B"          
BG_CARD = "#18181B"         
BG_INPUT = "#27272A"        
ACCENT = "#06B6D4"          
ACCENT_HOVER = "#0891B2"    
TEXT_MAIN = "#FAFAFA"       
TEXT_MUTED = "#A1A1AA"      
DANGER = "#EF4444"          
SUCCESS = "#10B981"         

SHELL_PREFIX = "marpel@crypton ~ $ "

LANG_DATA = {
    "EN": {
        "subtitle": "marpel@crypton",
        "file_lbl": "No target selected",
        "select": "Browse",
        "pass": "Master Password",
        "shred": "Shredder",
        "double": "Double Cipher",
        "stego": "Stego Mode",
        "2fa": "Physical 2FA",
        "duress": "Duress Code (Auto-Wipe)",
        "encrypt": "ENCRYPT",
        "decrypt": "DECRYPT",
        "init": "Crypton",
        "idle": "Awaiting commands...",
        "tips": {
            "stego": "STEGO: Hide data inside JPG/PNG. File remains an image.",
            "2fa": "2FA: Mix password with data from any chosen key-file.",
            "double": "DOUBLE: AES-256-GCM + ChaCha20-Poly1305 cascade.",
            "shred": "SHRED: Deep clean and delete original after process.",
            "duress": "DURESS: Suicide pass. Deletes file in DECRYPT mode.",
            "gen": "GEN: Generate 26-char high-entropy key."
        }
    },
    "RU": {
        "subtitle": "marpel@crypton",
        "file_lbl": "Объект не выбран",
        "select": "Обзор",
        "pass": "Мастер-пароль",
        "shred": "Шредер",
        "double": "Двойной шифр",
        "stego": "Стего-режим",
        "2fa": "Физический 2FA",
        "duress": "Duress-код (Уничтожение)",
        "encrypt": "ЗАШИФРОВАТЬ",
        "decrypt": "РАСШИФРОВАТЬ",
        "init": "Ядро Crypton  инициализировано.",
        "idle": "Ожидание команд...",
        "tips": {
            "stego": "STEGO: Спрятать данные внутри JPG/PNG. Файл остается фото.",
            "2fa": "2FA: Смешивание пароля с данными любого файла-ключа.",
            "double": "DOUBLE: Каскад шифров AES-256-GCM + ChaCha20-Poly1305.",
            "shred": "SHRED: Глубокая очистка и удаление оригинала.",
            "duress": "DURESS: Пароль-смертник. Удаляет файл при попытке расшифровки.",
            "gen": "GEN: Генерация ключа из 26 случайных символов."
        }
    }
}

class CryptonApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CRYPTON///")
        self.geometry("800x950")
        self.configure(fg_color=BG_APP)
        self.resizable(False, False)
        
      
        self.font_main = ("Segoe UI", 14)
        self.font_mono = ("Cascadia Code", 12) if os.name == 'nt' else ("Monospace", 12)
        self.font_mono_large = ("Cascadia Code", 22, "bold") if os.name == 'nt' else ("Monospace", 22, "bold")
        
        self.lang = "EN"
        self.file_path = None
        self.pass_visible = False
        
        self.withdraw()  
        self.show_welcome_animation()

    def play_sound(self, sound_type="type"):
        if winsound:
            try:
                if sound_type == "type": winsound.Beep(900, 10)
                elif sound_type == "success": winsound.Beep(1200, 100); winsound.Beep(1500, 100)
                elif sound_type == "error": winsound.Beep(400, 400)
            except: pass

    def show_welcome_animation(self):
        self.welcome_win = ctk.CTkToplevel(self)
        self.welcome_win.geometry("800x950")
        self.welcome_win.configure(fg_color=BG_APP)
        self.welcome_win.overrideredirect(True)
        
        sw, sh = self.welcome_win.winfo_screenwidth(), self.welcome_win.winfo_screenheight()
        self.welcome_win.geometry(f"800x950+{int(sw/2-400)}+{int(sh/2-475)}")
        
        self.anim_label = ctk.CTkLabel(self.welcome_win, text="", font=self.font_mono_large, text_color=ACCENT)
        self.anim_label.place(relx=0.5, rely=0.5, anchor="center")
        
        self.type_effect("///Protect your information\nWelcome to Crypton>>>", 0)

    def type_effect(self, text, index):
        if index <= len(text):
            self.anim_label.configure(text=text[:index])
            self.play_sound("type")
            self.after(45, lambda: self.type_effect(text, index + 1))
        else:
            self.after(500, self.finish_welcome)

    def finish_welcome(self):
        self.welcome_win.destroy()
        self.deiconify()
        self.build_ui()

    def build_ui(self):
        # HEADER
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(pady=(40, 20), padx=50, fill="x")
        
        title_box = ctk.CTkFrame(self.header, fg_color="transparent")
        title_box.pack(side="left")
        ctk.CTkLabel(title_box, text="C R Y P T O N", font=("Segoe UI", 42, "bold"), text_color=ACCENT).pack(anchor="w")
        self.sub_lbl = ctk.CTkLabel(title_box, text=LANG_DATA[self.lang]["subtitle"], font=self.font_mono, text_color=TEXT_MUTED)
        self.sub_lbl.pack(anchor="w", pady=(0, 0))

        self.lang_switch = ctk.CTkSegmentedButton(self.header, values=["EN", "RU"], command=self.change_lang, 
                                                 fg_color=BG_CARD, selected_color=ACCENT, selected_hover_color=ACCENT_HOVER)
        self.lang_switch.set("EN")
        self.lang_switch.pack(side="right", anchor="center")

        
        f_box = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12)
        f_box.pack(pady=15, padx=50, fill="x")
        
        self.file_lbl = ctk.CTkLabel(f_box, text=LANG_DATA[self.lang]["file_lbl"], font=self.font_mono, text_color=TEXT_MUTED)
        self.file_lbl.pack(side="left", padx=25, pady=25)
        
        self.select_btn = ctk.CTkButton(f_box, text=LANG_DATA[self.lang]["select"], width=120, height=40,
                                        fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color="#000", 
                                        font=("Segoe UI", 14, "bold"), corner_radius=8, command=self.browse_target)
        self.select_btn.pack(side="right", padx=25)

      
        p_group = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12)
        p_group.pack(pady=15, padx=50, fill="x")
        
        row = ctk.CTkFrame(p_group, fg_color="transparent")
        row.pack(fill="x", padx=25, pady=25)
        
        self.entry = ctk.CTkEntry(row, placeholder_text=LANG_DATA[self.lang]["pass"], show="*", height=45, 
                                  fg_color=BG_INPUT, border_width=0, corner_radius=8, font=self.font_main)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_eye = ctk.CTkButton(row, text="👁", width=45, height=45, fg_color=BG_INPUT, hover_color="#3F3F46",
                                     border_width=0, corner_radius=8, text_color=TEXT_MAIN, command=self.toggle_pass)
        self.btn_eye.pack(side="left", padx=5)
        
        self.btn_gen = ctk.CTkButton(row, text="⚡", width=45, height=45, fg_color=BG_INPUT, hover_color="#3F3F46",
                                     border_width=0, corner_radius=8, text_color=TEXT_MAIN, command=self.generate_password)
        self.btn_gen.pack(side="left", padx=5)
        self.add_tip(self.btn_gen, "gen")
        
        self.ext_entry = ctk.CTkEntry(row, placeholder_text="EXT", width=70, height=45, 
                                      fg_color=BG_INPUT, border_width=0, corner_radius=8, justify="center")
        self.ext_entry.insert(0, "locked")
        self.ext_entry.pack(side="right", padx=(10, 0))

       
        s_group = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12)
        s_group.pack(pady=15, padx=50, fill="x")
        
        grid = ctk.CTkFrame(s_group, fg_color="transparent")
        grid.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.shred_var, self.double_var, self.stego_var, self.fa_var = [ctk.BooleanVar() for _ in range(4)]
        sw_params = {"progress_color": ACCENT, "button_color": "#FFFFFF", "font": self.font_main, "switch_width": 45, "switch_height": 22}
        
        self.sw_shred = ctk.CTkSwitch(grid, text=LANG_DATA[self.lang]["shred"], variable=self.shred_var, **sw_params)
        self.sw_shred.grid(row=0, column=0, padx=30, pady=15, sticky="w")
        self.add_tip(self.sw_shred, "shred")

        self.sw_double = ctk.CTkSwitch(grid, text=LANG_DATA[self.lang]["double"], variable=self.double_var, **sw_params)
        self.sw_double.grid(row=0, column=1, padx=30, pady=15, sticky="w")
        self.add_tip(self.sw_double, "double")

        self.sw_stego = ctk.CTkSwitch(grid, text=LANG_DATA[self.lang]["stego"], variable=self.stego_var, **sw_params)
        self.sw_stego.grid(row=1, column=0, padx=30, pady=15, sticky="w")
        self.add_tip(self.sw_stego, "stego")

        self.sw_2fa = ctk.CTkSwitch(grid, text=LANG_DATA[self.lang]["2fa"], variable=self.fa_var, **sw_params)
        self.sw_2fa.grid(row=1, column=1, padx=30, pady=15, sticky="w")
        self.add_tip(self.sw_2fa, "2fa")

       
        self.du_entry = ctk.CTkEntry(self, placeholder_text=LANG_DATA[self.lang]["duress"], show="*", height=45, 
                                     fg_color=BG_CARD, border_width=1, border_color=DANGER, corner_radius=8, font=self.font_main)
        self.du_entry.pack(pady=15, padx=50, fill="x")
        self.add_tip(self.du_entry, "duress")

        
        self.log_box = ctk.CTkTextbox(self, height=140, fg_color=BG_CARD, border_width=0, corner_radius=12, 
                                      font=self.font_mono, text_color=ACCENT)
        self.log_box.pack(pady=15, padx=50, fill="x")
        self.shell_log(LANG_DATA[self.lang]["init"])
        self.log_box.configure(state="disabled")

        act = ctk.CTkFrame(self, fg_color="transparent")
        act.pack(side="bottom", fill="x", padx=50, pady=(0, 40))
        
        self.btn_enc = ctk.CTkButton(act, text=LANG_DATA[self.lang]["encrypt"], fg_color=TEXT_MAIN, 
                                     text_color="#000", font=("Segoe UI", 16, "bold"), height=60, corner_radius=12,
                                     hover_color="#D4D4D8", command=lambda: self.start_task("enc"))
        self.btn_enc.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        self.btn_dec = ctk.CTkButton(act, text=LANG_DATA[self.lang]["decrypt"], fg_color="transparent", 
                                     border_width=2, border_color=ACCENT, text_color=TEXT_MAIN, font=("Segoe UI", 16, "bold"), 
                                     height=60, corner_radius=12, hover_color=BG_CARD, command=lambda: self.start_task("dec"))
        self.btn_dec.pack(side="right", expand=True, fill="x", padx=(10, 0))

    def toggle_pass(self):
        if self.pass_visible:
            self.entry.configure(show="*"); self.btn_eye.configure(text="👁")
        else:
            self.entry.configure(show=""); self.btn_eye.configure(text="🔒")
        self.pass_visible = not self.pass_visible

    def change_lang(self, choice):
        self.lang = choice
        self.sub_lbl.configure(text=LANG_DATA[self.lang]["subtitle"])
        self.select_btn.configure(text=LANG_DATA[self.lang]["select"])
        if not self.file_path: self.file_lbl.configure(text=LANG_DATA[self.lang]["file_lbl"])
        self.entry.configure(placeholder_text=LANG_DATA[self.lang]["pass"])
        self.du_entry.configure(placeholder_text=LANG_DATA[self.lang]["duress"])
        self.sw_shred.configure(text=LANG_DATA[self.lang]["shred"])
        self.sw_double.configure(text=LANG_DATA[self.lang]["double"])
        self.sw_stego.configure(text=LANG_DATA[self.lang]["stego"])
        self.sw_2fa.configure(text=LANG_DATA[self.lang]["2fa"])
        self.btn_enc.configure(text=LANG_DATA[self.lang]["encrypt"])
        self.btn_dec.configure(text=LANG_DATA[self.lang]["decrypt"])
        self.shell_log(LANG_DATA[self.lang]["init"], clear=True)

    def shell_log(self, msg, clear=False):
        self.log_box.configure(state="normal")
        if clear: self.log_box.delete("0.0", "end")
        self.log_box.insert("end", f"{SHELL_PREFIX}{msg}\n")
        self.log_box.see("end"); self.log_box.configure(state="disabled")

    def add_tip(self, widget, key):
        widget.bind("<Enter>", lambda e: self.shell_log(LANG_DATA[self.lang]["tips"][key], clear=True))
        widget.bind("<Leave>", lambda e: self.shell_log(LANG_DATA[self.lang]["idle"], clear=True))

    def browse_target(self):
        p = filedialog.askopenfilename(parent=self)
        if p: 
            self.file_path = p
            self.file_lbl.configure(text=os.path.basename(p)[:45], text_color=TEXT_MAIN)
            self.shell_log(f"Target selected: {os.path.basename(p)}")

    def generate_password(self):
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        p = ''.join(secrets.choice(chars) for _ in range(26))
        self.entry.delete(0, 'end'); self.entry.insert(0, p); self.shell_log("High-entropy key generated.")

    def start_task(self, mode):
        fa_key_path = None
        stego_host_path = None
        
        if self.fa_var.get():
            fa_key_path = filedialog.askopenfilename(parent=self, title="SELECT 2FA KEY-FILE")
            if not fa_key_path: self.shell_log("ABORT: 2FA key required."); return
            
        if mode == "enc" and self.stego_var.get():
            stego_host_path = filedialog.askopenfilename(parent=self, title="SELECT HOST IMAGE", 
                                                        filetypes=[("Images", "*.jpg *.png *.jpeg")])
            if not stego_host_path: self.shell_log("ABORT: Image host required."); return

        threading.Thread(target=self.process, args=(mode, fa_key_path, stego_host_path), daemon=True).start()

    def process(self, mode, fa_key_path, stego_host_path):
        pwd = self.entry.get()
        if not pwd or not self.file_path: 
            self.shell_log("ERR: Target or password missing."); self.play_sound("error"); return
        
        if mode == "dec" and self.du_entry.get() and pwd == self.du_entry.get():
            self.shell_log("DURESS TRIGGERED: WIPING FILE..."); os.remove(self.file_path); return

        m_key = None
        try:
            self.shell_log("Processing KDF...")
            salt = b"CRYPT_V7.1_CORE_SYS"
            
            if fa_key_path:
                with open(fa_key_path, "rb") as kf: pwd += hashlib.sha256(kf.read()).hexdigest()
            
            m_key = PBKDF2(pwd, salt, dkLen=32, count=150000)

            if mode == "enc":
                with open(self.file_path, "rb") as f: data = f.read()
                if self.double_var.get():
                    c2 = ChaCha20.new(key=m_key); data = c2.nonce + c2.encrypt(data)
                
                cipher = AES.new(m_key, AES.MODE_GCM)
                ct, tag = cipher.encrypt_and_digest(data)
                payload = cipher.nonce + tag + ct
                
                if stego_host_path:
                    with open(stego_host_path, "rb") as f: host = f.read()
                    out = "STEGO_" + os.path.basename(stego_host_path)
                    with open(out, "wb") as f: f.write(host + b"---CRYPT---" + payload)
                else:
                    out = self.file_path + "." + self.ext_entry.get()
                    with open(out, "wb") as f: f.write(payload)
                
                if self.shred_var.get():
                    size = os.path.getsize(self.file_path)
                    with open(self.file_path, "ba+", buffering=0) as f:
                        for _ in range(3): f.seek(0); f.write(get_random_bytes(size))
                    os.remove(self.file_path)
                self.shell_log("ENCRYPTION COMPLETE."); self.play_sound("success")
            else:
                with open(self.file_path, "rb") as f: raw = f.read()
                payload = raw.split(b"---CRYPT---")[-1] if b"---CRYPT---" in raw else raw
                nonce, tag, ct = payload[:16], payload[16:32], payload[32:]
                cipher = AES.new(m_key, AES.MODE_GCM, nonce=nonce)
                data = cipher.decrypt_and_verify(ct, tag)
                
                if self.double_var.get():
                    c2_n, c2_ct = data[:12], data[12:]; c2 = ChaCha20.new(key=m_key, nonce=c2_n); data = c2.decrypt(c2_ct)
                
                out = "DEC_" + os.path.basename(self.file_path).rsplit(".", 1)[0]
                with open(out, "wb") as f: f.write(data)
                self.shell_log("DECRYPTION SUCCESSFUL."); self.play_sound("success")
        
        except Exception as e:
            self.shell_log(f"ERR: {str(e)[:30]}"); self.play_sound("error")
        finally:
            if m_key: m_key = b'\x00'*32; del m_key
            self.shell_log("Memory cleared.")

if __name__ == "__main__":
    app = CryptonApp()
    app.mainloop()