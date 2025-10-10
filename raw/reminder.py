import customtkinter as ctk
from tkinter import messagebox, filedialog
import platform
import os
import pygame

try:
    if platform.system() == "Windows":
        import winsound
except ImportError:
    winsound = None

class ReminderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        pygame.mixer.init()

        self.title("Reminder by XDwhobs")
        self.geometry("420x620") 
        self.resizable(False, False)

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.timer_id = None
        self.is_running = False
        self.custom_sound_path = None
        self.title_phrases = ["Pengingat Aktivitas", "Aturlah Waktumu...", "XD XD XD XD XD"]
        self.title_label = None 

        self.create_widgets()

    def create_widgets(self):
        """Membangun semua elemen antarmuka pengguna."""
        
        main_frame = ctk.CTkFrame(self, corner_radius=15)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.title_label = ctk.CTkLabel(
            main_frame, text="", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(15, 20))
        self.animate_title() 

        activity_label = ctk.CTkLabel(main_frame, text="Mau melakukan apa?", font=ctk.CTkFont(size=14))
        activity_label.pack(padx=20, pady=(10, 5), anchor="w")
        self.activity_entry = ctk.CTkEntry(
            main_frame, placeholder_text="Contoh: Baca buku", width=280, height=35
        )
        self.activity_entry.pack(pady=(0, 10))
        activity_template_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        activity_template_frame.pack()
        activities = ["Mencuci", "Main Game", "Belajar"]
        for activity in activities:
            btn = ctk.CTkButton(
                activity_template_frame, text=activity, width=85,
                command=lambda a=activity: self.set_entry_text(self.activity_entry, a)
            )
            btn.pack(side="left", padx=5)

        time_label = ctk.CTkLabel(main_frame, text="Atur Waktu Pengingat", font=ctk.CTkFont(size=14))
        time_label.pack(padx=20, pady=(20, 5), anchor="w")

        time_input_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        time_input_frame.pack(pady=(0, 10))

        self.minutes_entry = ctk.CTkEntry(
            time_input_frame, placeholder_text="0", width=80, height=35, justify="center"
        )
        self.minutes_entry.pack(side="left")
        minutes_label = ctk.CTkLabel(time_input_frame, text="menit", font=ctk.CTkFont(size=14))
        minutes_label.pack(side="left", padx=(5, 15))

        self.seconds_entry = ctk.CTkEntry(
            time_input_frame, placeholder_text="0", width=80, height=35, justify="center"
        )
        self.seconds_entry.pack(side="left")
        seconds_label = ctk.CTkLabel(time_input_frame, text="detik", font=ctk.CTkFont(size=14))
        seconds_label.pack(side="left", padx=5)

        time_template_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        time_template_frame.pack()
        times = ["10", "15", "20"]
        for time_val in times:
            btn = ctk.CTkButton(
                time_template_frame, text=f"{time_val} min", width=85,
                command=lambda m=time_val: self.set_template_time(minutes=m)
            )
            btn.pack(side="left", padx=5)
            
        sound_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        sound_frame.pack(pady=(20, 5), padx=20, fill="x")
        self.select_sound_button = ctk.CTkButton(
            sound_frame, text="Pilih Musik Notifikasi...", command=self.select_sound_file
        )
        self.select_sound_button.pack(side="left")
        self.use_custom_sound_checkbox = ctk.CTkCheckBox(
            sound_frame, text="Gunakan musik sendiri", state="disabled"
        )
        self.use_custom_sound_checkbox.pack(side="left", padx=10)
        self.sound_file_label = ctk.CTkLabel(
            main_frame, text="File: Belum ada yang dipilih",
            font=ctk.CTkFont(size=12), text_color="gray", wraplength=300
        )
        self.sound_file_label.pack(pady=(0, 15), padx=20, anchor="w")

        self.control_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.control_frame.pack(pady=15)
        self.start_button = ctk.CTkButton(
            self.control_frame, text="Mulai Pengingat", command=self.start_timer,
            font=ctk.CTkFont(size=14, weight="bold"), height=40
        )
        self.start_button.pack(side="left", padx=5)
        self.cancel_button = ctk.CTkButton(
            self.control_frame, text="Batal", command=self.cancel_timer, state="disabled",
            fg_color="#D32F2F", hover_color="#B71C1C", height=40
        )
        self.cancel_button.pack(side="left", padx=5)
        
        self.timer_label = ctk.CTkLabel(
            main_frame, text="", font=ctk.CTkFont(family="Arial", size=48, weight="bold")
        )
        self.timer_label.pack(pady=(0, 15))
        
    def set_entry_text(self, entry_widget, text):
        entry_widget.delete(0, "end")
        entry_widget.insert(0, text)
        
    def set_template_time(self, minutes, seconds=0):
        """[BARU] Mengisi kolom menit dan detik dari tombol template."""
        self.minutes_entry.delete(0, "end")
        self.seconds_entry.delete(0, "end")
        self.minutes_entry.insert(0, str(minutes))
        self.seconds_entry.insert(0, str(seconds))

    def animate_title(self, phrase_index=0, char_index=0, is_deleting=False):
        """[BARU] Fungsi untuk membuat animasi mengetik pada judul."""
        current_phrase = self.title_phrases[phrase_index]

        if not is_deleting:
            if char_index <= len(current_phrase):
                self.title_label.configure(text=current_phrase[:char_index])
                self.after(150, self.animate_title, phrase_index, char_index + 1, False)
            else:
                self.after(2000, self.animate_title, phrase_index, char_index - 1, True)
        else:
            if char_index >= 0:
                self.title_label.configure(text=current_phrase[:char_index])
                self.after(100, self.animate_title, phrase_index, char_index - 1, True)
            else:
                next_phrase_index = (phrase_index + 1) % len(self.title_phrases)
                self.after(500, self.animate_title, next_phrase_index, 0, False)


    def select_sound_file(self):
        file_path = filedialog.askopenfilename(
            title="Pilih File Audio",
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg"), ("All files", "*.*")]
        )
        if file_path:
            self.custom_sound_path = file_path
            file_name = os.path.basename(file_path)
            self.sound_file_label.configure(text=f"File: {file_name}")
            self.use_custom_sound_checkbox.configure(state="normal")
            self.use_custom_sound_checkbox.select()
        
    def start_timer(self):
        activity = self.activity_entry.get().strip()
        minutes_str = self.minutes_entry.get().strip() or "0"
        seconds_str = self.seconds_entry.get().strip() or "0"

        if not activity:
            messagebox.showwarning("Input Kosong", "Harap masukkan aktivitas.")
            return
        
        try:
            minutes = int(minutes_str)
            seconds = int(seconds_str)
            total_seconds = (minutes * 60) + seconds

            if total_seconds <= 0:
                raise ValueError("Total waktu harus lebih dari 0")

        except ValueError:
            messagebox.showwarning("Input Tidak Valid", "Harap masukkan angka yang valid di kolom menit/detik.")
            return

        self.is_running = True
        self.toggle_controls()
        self.countdown(total_seconds, activity)
        
    def countdown(self, remaining_seconds, activity):
        if not self.is_running:
            return

        if remaining_seconds >= 0:
            mins, secs = divmod(remaining_seconds, 60)
            self.timer_label.configure(text=f"{mins:02d}:{secs:02d}")
            self.timer_id = self.after(1000, self.countdown, remaining_seconds - 1, activity)
        else:
            self.is_running = False
            self.play_sound()
            messagebox.showinfo("Waktu Habis!", f"Waktunya untuk '{activity}' telah selesai!")
            self.reset_ui()
            
    def cancel_timer(self):
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        self.is_running = False
        self.reset_ui()

    def reset_ui(self):
        self.timer_label.configure(text="")
        pygame.mixer.music.stop()
        self.toggle_controls()

    def toggle_controls(self):
        if self.is_running:
            state = "disabled"
            self.cancel_button.configure(state="normal")
        else:
            state = "normal"
            self.cancel_button.configure(state="disabled")

        self.start_button.configure(state=state)
        self.activity_entry.configure(state=state)

        self.minutes_entry.configure(state=state)
        self.seconds_entry.configure(state=state)
        
        self.select_sound_button.configure(state=state)
        
        if self.custom_sound_path and not self.is_running:
            self.use_custom_sound_checkbox.configure(state="normal")
        else:
            self.use_custom_sound_checkbox.configure(state="disabled")

    def play_sound(self):
        use_custom = self.use_custom_sound_checkbox.get() == 1
        
        if use_custom and self.custom_sound_path:
            try:
                pygame.mixer.music.load(self.custom_sound_path)
                pygame.mixer.music.play()
            except pygame.error as e:
                messagebox.showerror("Error Musik", f"Tidak bisa memutar file musik.\nError: {e}")
                self.play_default_sound()
        else:
            self.play_default_sound()
            
    def play_default_sound(self):
        if winsound:
            try:
                winsound.Beep(1000, 500)
            except Exception as e:
                print(f"Tidak bisa memainkan suara default: {e}")

if __name__ == "__main__":
    app = ReminderApp()
    app.mainloop()


