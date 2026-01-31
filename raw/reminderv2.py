import customtkinter as ctk
from tkinter import messagebox, filedialog
import platform
import os
import pygame
import webbrowser

# --- Setup Audio ---
try:
    if platform.system() == "Windows":
        import winsound
    else:
        winsound = None
except ImportError:
    winsound = None

class ReminderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        pygame.mixer.init()

        # --- Konfigurasi Window Utama ---
        self.title("XD Reminder Pro")
        self.geometry("460x800") 
        self.resizable(False, False)

        # Tema: Dark Mode dengan warna biru sebagai default
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        # Variabel State
        self.timer_id = None
        self.is_running = False
        self.custom_sound_path = None
        self.total_seconds = 0 # Disimpan untuk progress bar
        
        # Animasi Judul
        self.title_phrases = ["⚡ FOCUS MODE ⚡", "Reminder by XDwhobs", "Don't Waste Time!"]
        self.title_label = None 

        self.create_widgets()

    def create_widgets(self):
        """Membangun UI dengan Layout Card yang modern."""
        
        # Container Utama (Scrollable biar aman kalau layar kecil)
        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # --- HEADER ---
        self.title_label = ctk.CTkLabel(
            self.main_scroll, text="", 
            font=ctk.CTkFont(family="Roboto", size=26, weight="bold"),
            text_color="#3B8ED0" # Warna Biru Muda
        )
        self.title_label.pack(pady=(20, 25))
        self.animate_title() 

        # --- CARD 1: AKTIVITAS ---
        self.create_card_activity()

        # --- CARD 2: WAKTU ---
        self.create_card_time()

        # --- CARD 3: MEDIA / SUARA ---
        self.create_card_media()

        # --- FOOTER: TIMER & KONTROL ---
        self.create_footer_controls()
        
    def create_card_activity(self):
        card = ctk.CTkFrame(self.main_scroll, corner_radius=15, fg_color="#2B2B2B")
        card.pack(fill="x", pady=10, padx=5)

        header = ctk.CTkLabel(card, text="🎯  Target Aktivitas", font=ctk.CTkFont(size=14, weight="bold"))
        header.pack(anchor="w", padx=15, pady=(15, 5))

        self.activity_entry = ctk.CTkEntry(
            card, placeholder_text="Misal: Coding Python...", height=40,
            border_width=0, fg_color="#3A3A3A"
        )
        self.activity_entry.pack(fill="x", padx=15, pady=(0, 10))

        # Quick Tags (Tombol Kecil)
        tag_frame = ctk.CTkFrame(card, fg_color="transparent")
        tag_frame.pack(padx=15, pady=(0, 15), anchor="w")
        
        tags = ["📚 Belajar", "🎮 Gaming", "💤 Istirahat", "💻 Coding"]
        for tag in tags:
            btn = ctk.CTkButton(
                tag_frame, text=tag, width=60, height=25,
                fg_color="#404040", hover_color="#505050",
                font=ctk.CTkFont(size=11),
                command=lambda t=tag: self.set_entry_text(self.activity_entry, t)
            )
            btn.pack(side="left", padx=(0, 5))

    def create_card_time(self):
        card = ctk.CTkFrame(self.main_scroll, corner_radius=15, fg_color="#2B2B2B")
        card.pack(fill="x", pady=10, padx=5)

        header = ctk.CTkLabel(card, text="⏱️  Durasi Fokus", font=ctk.CTkFont(size=14, weight="bold"))
        header.pack(anchor="w", padx=15, pady=(15, 5))

        input_frame = ctk.CTkFrame(card, fg_color="transparent")
        input_frame.pack(pady=(0, 10))

        # Menit
        self.minutes_entry = ctk.CTkEntry(input_frame, placeholder_text="00", width=70, height=50, 
                                          font=ctk.CTkFont(size=24, weight="bold"), justify="center", fg_color="#3A3A3A", border_width=0)
        self.minutes_entry.pack(side="left")
        ctk.CTkLabel(input_frame, text="Min", text_color="gray").pack(side="left", padx=(5, 15))

        # Detik
        self.seconds_entry = ctk.CTkEntry(input_frame, placeholder_text="00", width=70, height=50, 
                                          font=ctk.CTkFont(size=24, weight="bold"), justify="center", fg_color="#3A3A3A", border_width=0)
        self.seconds_entry.pack(side="left")
        ctk.CTkLabel(input_frame, text="Sec", text_color="gray").pack(side="left", padx=5)

        # Quick Time Buttons
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(pady=(0, 15))
        times = [("10m", 10), ("25m", 25), ("45m", 45)]
        for label, val in times:
            btn = ctk.CTkButton(
                btn_frame, text=label, width=60, height=25,
                fg_color="#404040", hover_color="#505050",
                command=lambda m=val: self.set_template_time(minutes=m)
            )
            btn.pack(side="left", padx=5)

    def create_card_media(self):
        card = ctk.CTkFrame(self.main_scroll, corner_radius=15, fg_color="#2B2B2B")
        card.pack(fill="x", pady=10, padx=5)

        header = ctk.CTkLabel(card, text="🎵  Alarm & Musik", font=ctk.CTkFont(size=14, weight="bold"))
        header.pack(anchor="w", padx=15, pady=(15, 10))

        # --- Opsi File Lokal ---
        self.select_sound_button = ctk.CTkButton(
            card, text="📂 Pilih File Audio", command=self.select_sound_file, 
            fg_color="#404040", hover_color="#505050", width=200
        )
        self.select_sound_button.pack(padx=15, anchor="w")

        self.sound_file_label = ctk.CTkLabel(
            card, text="File: Default Beep", font=ctk.CTkFont(size=11), text_color="gray"
        )
        self.sound_file_label.pack(padx=15, pady=(2, 10), anchor="w")

        self.use_custom_sound_checkbox = ctk.CTkCheckBox(card, text="Gunakan File Lokal", font=ctk.CTkFont(size=12))
        self.use_custom_sound_checkbox.pack(padx=15, anchor="w")
        self.use_custom_sound_checkbox.configure(state="disabled")

        ctk.CTkFrame(card, height=2, fg_color="#3A3A3A").pack(fill="x", padx=15, pady=10) # Divider line

        # --- Opsi YouTube ---
        yt_header_frame = ctk.CTkFrame(card, fg_color="transparent")
        yt_header_frame.pack(fill="x", padx=15)
        
        self.use_youtube_checkbox = ctk.CTkCheckBox(
            yt_header_frame, text="Putar YouTube Music", 
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.toggle_youtube_entry,
            fg_color="#FF0000", hover_color="#CC0000" # Warna Merah YouTube
        )
        self.use_youtube_checkbox.pack(side="left")

        self.youtube_entry = ctk.CTkEntry(
            card, placeholder_text="Tempel link YouTube di sini...", height=35,
            text_color="#3B8ED0"
        )
        self.youtube_entry.pack(fill="x", padx=15, pady=(5, 15))
        self.youtube_entry.insert(0, "") # Default kosong
        self.youtube_entry.configure(state="disabled")

    def create_footer_controls(self):
        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self.main_scroll, height=15, corner_radius=10)
        self.progress_bar.pack(fill="x", padx=10, pady=(10, 5))
        self.progress_bar.set(0) # 0%

        # Timer Display Besar
        self.timer_label = ctk.CTkLabel(
            self.main_scroll, text="00:00", 
            font=ctk.CTkFont(family="Consolas", size=60, weight="bold"),
            text_color="#ffffff"
        )
        self.timer_label.pack(pady=5)

        # Tombol Kontrol
        control_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        control_frame.pack(pady=10, fill="x")

        self.start_button = ctk.CTkButton(
            control_frame, text="MULAI FOKUS", command=self.start_timer,
            font=ctk.CTkFont(size=16, weight="bold"), height=50, corner_radius=25,
            fg_color="#2CC985", hover_color="#229A65", text_color="white" # Hijau Start
        )
        self.start_button.pack(side="left", fill="x", expand=True, padx=5)

        self.cancel_button = ctk.CTkButton(
            control_frame, text="BATAL", command=self.cancel_timer, state="disabled",
            font=ctk.CTkFont(size=16, weight="bold"), height=50, corner_radius=25,
            fg_color="#D32F2F", hover_color="#B71C1C" # Merah Batal
        )
        self.cancel_button.pack(side="left", fill="x", expand=True, padx=5)

    # --- LOGIC METHODS (Sama seperti sebelumnya dengan sedikit update UI) ---

    def set_entry_text(self, entry_widget, text):
        entry_widget.delete(0, "end")
        entry_widget.insert(0, text)
        
    def set_template_time(self, minutes, seconds=0):
        self.minutes_entry.delete(0, "end")
        self.seconds_entry.delete(0, "end")
        self.minutes_entry.insert(0, str(minutes))
        self.seconds_entry.insert(0, str(seconds))

    def animate_title(self, phrase_index=0, char_index=0, is_deleting=False):
        current_phrase = self.title_phrases[phrase_index]
        if not is_deleting:
            if char_index <= len(current_phrase):
                self.title_label.configure(text=current_phrase[:char_index])
                self.after(150, self.animate_title, phrase_index, char_index + 1, False)
            else:
                self.after(3000, self.animate_title, phrase_index, char_index - 1, True)
        else:
            if char_index >= 0:
                self.title_label.configure(text=current_phrase[:char_index])
                self.after(80, self.animate_title, phrase_index, char_index - 1, True)
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
            # Potong nama file jika terlalu panjang
            display_name = (file_name[:25] + '..') if len(file_name) > 25 else file_name
            self.sound_file_label.configure(text=f"File: {display_name}", text_color="#2CC985")
            
            self.use_custom_sound_checkbox.configure(state="normal")
            self.use_custom_sound_checkbox.select()
            self.use_youtube_checkbox.deselect() 
            self.toggle_youtube_entry()

    def toggle_youtube_entry(self):
        if self.use_youtube_checkbox.get() == 1:
            self.youtube_entry.configure(state="normal", fg_color="#3A3A3A")
            if self.use_custom_sound_checkbox.get() == 1:
                self.use_custom_sound_checkbox.deselect()
        else:
            self.youtube_entry.configure(state="disabled", fg_color="#2B2B2B")
        
    def start_timer(self):
        activity = self.activity_entry.get().strip()
        minutes_str = self.minutes_entry.get().strip() or "0"
        seconds_str = self.seconds_entry.get().strip() or "0"

        if not activity:
            messagebox.showwarning("⚠️ Ops!", "Mau ngapain? Isi dulu aktivitasnya.")
            return

        if self.use_youtube_checkbox.get() == 1:
            yt_link = self.youtube_entry.get().strip()
            if not yt_link:
                messagebox.showwarning("⚠️ Link Error", "Link YouTube nya belum diisi.")
                return
        
        try:
            minutes = int(minutes_str)
            seconds = int(seconds_str)
            self.total_seconds = (minutes * 60) + seconds # Simpan total waktu

            if self.total_seconds <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("⚠️ Waktu Error", "Masukkan angka menit/detik yang benar.")
            return

        self.is_running = True
        self.toggle_controls()
        self.countdown(self.total_seconds, activity)
        
    def countdown(self, remaining_seconds, activity):
        if not self.is_running:
            return

        # Update Progress Bar
        if self.total_seconds > 0:
            progress = remaining_seconds / self.total_seconds
            self.progress_bar.set(progress)
            
            # Ubah warna progress bar jika mau habis (Kurang dari 20%)
            if progress < 0.2:
                self.progress_bar.configure(progress_color="#D32F2F") # Merah
            else:
                self.progress_bar.configure(progress_color="#3B8ED0") # Biru

        if remaining_seconds >= 0:
            mins, secs = divmod(remaining_seconds, 60)
            self.timer_label.configure(text=f"{mins:02d}:{secs:02d}", text_color="#ffffff")
            self.timer_id = self.after(1000, self.countdown, remaining_seconds - 1, activity)
        else:
            self.is_running = False
            self.progress_bar.set(0)
            self.play_sound()
            
            # Flash Effect pada timer label saat selesai
            self.timer_label.configure(text="SELESAI!", text_color="#2CC985")
            
            messagebox.showinfo("🎉 Waktu Habis!", f"Waktunya '{activity}' sudah selesai!")
            self.reset_ui()
            
    def cancel_timer(self):
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        self.is_running = False
        self.progress_bar.set(0)
        self.reset_ui()

    def reset_ui(self):
        self.timer_label.configure(text="00:00", text_color="#ffffff")
        self.progress_bar.configure(progress_color="#3B8ED0") # Reset warna bar
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
        self.toggle_controls()

    def toggle_controls(self):
        if self.is_running:
            state = "disabled"
            self.cancel_button.configure(state="normal")
            self.start_button.configure(text="SEDANG BERJALAN...", fg_color="#404040") # Abu-abu
        else:
            state = "normal"
            self.cancel_button.configure(state="disabled")
            self.start_button.configure(text="MULAI FOKUS", fg_color="#2CC985") # Kembali Hijau

        self.start_button.configure(state=state)
        self.activity_entry.configure(state=state)
        self.minutes_entry.configure(state=state)
        self.seconds_entry.configure(state=state)
        self.select_sound_button.configure(state=state)
        
        self.use_youtube_checkbox.configure(state=state)
        
        # Logika Custom File
        if self.custom_sound_path and not self.is_running:
            self.use_custom_sound_checkbox.configure(state="normal")
        else:
            self.use_custom_sound_checkbox.configure(state="disabled")

        # Logika Input Youtube
        if self.is_running:
            self.youtube_entry.configure(state="disabled")
        else:
             if self.use_youtube_checkbox.get() == 1:
                self.youtube_entry.configure(state="normal")

    def play_sound(self):
        use_youtube = self.use_youtube_checkbox.get() == 1
        use_custom = self.use_custom_sound_checkbox.get() == 1
        
        if use_youtube:
            link = self.youtube_entry.get().strip()
            if link:
                webbrowser.open(link)
            else:
                self.play_default_sound()
        
        elif use_custom and self.custom_sound_path:
            try:
                pygame.mixer.music.load(self.custom_sound_path)
                pygame.mixer.music.play()
            except pygame.error as e:
                messagebox.showerror("Error", f"Gagal memutar audio.\n{e}")
                self.play_default_sound()
        else:
            self.play_default_sound()
            
    def play_default_sound(self):
        if winsound:
            try:
                winsound.Beep(1000, 500)
            except Exception:
                pass

if __name__ == "__main__":
    app = ReminderApp()
    app.mainloop()