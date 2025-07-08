import tkinter as tk
from tkinter import ttk, Text, RIDGE, Button
from PIL import Image, ImageTk
import speech_recognition as spr
from googletrans import LANGUAGES, Translator
from gtts import gTTS
import os

root = tk.Tk()
root.geometry("1080x720")
root.title("Voice-Based Language Translator")

background_colors = ["#cceeff", "#e0f7fa", "#d1c4e9", "#f3e5f5", "#ffe0b2", "#c8e6c9"]
textbox_colors = ["#808000", "#008080", "#800020", "#00ffff", "#b7410e", "#ff7f50"]
current_color_index = 0


def change_background_color():
    global current_color_index
    bg_color = background_colors[current_color_index]
    tb_color = textbox_colors[current_color_index]
    root.configure(bg=bg_color)
    frame_top.configure(bg=bg_color)
    frame_text.configure(bg=bg_color)
    frame_buttons.configure(bg=bg_color)
    canvas.configure(bg=bg_color)
    header_label.configure(bg=bg_color)
    t1.configure(bg=tb_color)
    t2.configure(bg=tb_color)
    current_color_index = (current_color_index + 1) % len(background_colors)
    root.after(1500, change_background_color)


root.after(0, change_background_color)

languages = list(LANGUAGES.values())
language_map = {v.lower(): k for k, v in LANGUAGES.items()}


def clear():
    t1.delete("1.0", "end")
    t2.delete("1.0", "end")


def copy():
    root.clipboard_clear()
    text = t2.get("1.0", "end").strip()
    root.clipboard_append(text)


def translate():
    from_lang = a.get().lower()
    selected_indices = output_listbox.curselection()
    to_langs = [language_map.get(output_listbox.get(i).lower()) for i in selected_indices]

    if from_lang == "auto detect":
        from_lang = "auto"
    else:
        from_lang = language_map.get(from_lang)

    if not from_lang or not to_langs:
        t2.insert("end", "Invalid language selected.\n")
        return

    text = t1.get("1.0", "end").strip()
    if not text:
        t2.insert("end", "No text to translate.\n")
        return

    try:
        translator = Translator()
        t2.delete("1.0", "end")
        for lang_code in to_langs:
            translated = translator.translate(text, src=from_lang, dest=lang_code)
            language_name = LANGUAGES[lang_code].title()
            t2.insert("end", f"[{language_name}]\n{translated.text}\n\n")
    except Exception as e:
        t2.insert("end", f"Error: {e}\n")


def texttospeech():
    text = t2.get("1.0", "end").strip()
    selected_indices = output_listbox.curselection()
    if not selected_indices:
        t2.insert("end", "No language selected for speech.\n")
        return
    lang = language_map.get(output_listbox.get(selected_indices[0]).lower())
    if not text or not lang:
        t2.insert("end", "Invalid language or empty text.\n")
        return
    try:
        speech = gTTS(text=text, lang=lang, slow=False)
        speech.save("speak.mp3")
        os.system("start speak.mp3")
    except Exception as e:
        t2.insert("end", f"Error: {e}\n")


def speechtotext():
    from_lang = "en"
    selected_indices = output_listbox.curselection()
    to_langs = [language_map.get(output_listbox.get(i).lower()) for i in selected_indices]

    if not to_langs:
        t2.insert("end", "Invalid language selected.\n")
        return

    recog1 = spr.Recognizer()
    mic = spr.Microphone()

    with mic as source:
        t1.insert("end", "Listening...\n")
        recog1.adjust_for_ambient_noise(source, duration=0.9)
        audio = recog1.listen(source)

    try:
        get_sentence = recog1.recognize_google(audio)
        t1.insert("end", get_sentence + "\n")

        translator = Translator()
        for lang_code in to_langs:
            translated = translator.translate(get_sentence, src=from_lang, dest=lang_code)
            language_name = LANGUAGES[lang_code].title()
            t2.insert("end", f"[{language_name}]\n{translated.text}\n\n")
            speak = gTTS(text=translated.text, lang=lang_code, slow=False)
            speak.save("output.mp3")
            os.system("start output.mp3")
    except spr.UnknownValueError:
        t1.insert("end", "Unable to understand the input.\n")
    except spr.RequestError as e:
        t1.insert("end", f"Request error: {e}\n")


def load_icon(path):
    try:
        img = Image.open(path).resize((32, 32), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except:
        return None


translate_text_icon = load_icon("resources/icons/documents.png")
clear_text_icon = load_icon("resources/icons/eraser.png")
copy_text_icon = load_icon("resources/icons/copy.png")
read_aloud_icon = load_icon("resources/icons/text_to_speech.png")
voice_input_icon = load_icon("resources/icons/voice_recognition.png")

canvas = tk.Canvas(root, height=50, bg="#007acc", highlightthickness=0)
canvas.pack(fill="x")

header_label = tk.Label(canvas, text="  Voice-Based Language Translator  ", font=("Arial Rounded MT Bold", 28),
                        fg="black", bg="#007acc")
header_window = canvas.create_window(root.winfo_width(), 25, window=header_label, anchor="w")


def scroll_title():
    x1, _, x2, _ = canvas.bbox(header_window)
    if x2 < 0:
        canvas.coords(header_window, root.winfo_width(), 25)
    else:
        canvas.move(header_window, -2, 0)
    root.after(20, scroll_title)


root.after(0, scroll_title)

frame_top = tk.Frame(root, pady=10)
frame_top.pack()

a = tk.StringVar()
auto_detect = ttk.Combobox(frame_top, width=20, textvariable=a, state='readonly', font=('Corbel', 16))
auto_detect['values'] = ['Auto Detect'] + sorted(languages)
auto_detect.current(0)
auto_detect.grid(row=0, column=0, padx=20)

output_listbox = tk.Listbox(frame_top, selectmode="multiple", height=6, width=25, font=('Corbel', 14),
                            exportselection=0)
for lang in sorted(languages):
    output_listbox.insert(tk.END, lang)
output_listbox.grid(row=0, column=1, padx=20)

frame_text = tk.Frame(root)
frame_text.pack(pady=10)

# Adding an extra layer frame for t1 and t2 textboxes
frame_text_layer = tk.Frame(frame_text, bg="#f0f0f0", bd=4, relief=RIDGE, highlightthickness=2,
                            highlightbackground="black")
frame_text_layer.grid(row=0, column=0, padx=20, pady=5)

frame_text_layer2 = tk.Frame(frame_text, bg="#f0f0f0", bd=4, relief=RIDGE, highlightthickness=2,
                             highlightbackground="black")
frame_text_layer2.grid(row=0, column=1, padx=20, pady=5)

# Recreating the t1 and t2 textboxes with the same dimensions
t1 = Text(frame_text_layer, width=55, height=16, font=('Calibri', 16), fg="#333", bd=4, relief=RIDGE,
          highlightthickness=2, highlightbackground="black")
t1.grid(row=0, column=0)

t2 = Text(frame_text_layer2, width=55, height=16, font=('Calibri', 16), fg="#333", bd=4, relief=RIDGE,
          highlightthickness=2, highlightbackground="black")
t2.grid(row=0, column=1)

frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=20)


def create_button(text, icon, command):
    normal_font = ('Times New Roman', 14, 'bold')
    hover_font = ('Times New Roman', 17, 'bold')

    # Updated button color and border
    btn = tk.Button(frame_buttons, text=text, image=icon, compound="right", font=normal_font,
                    command=command, bg="#4CAF50", fg="white", relief="solid", bd=5, padx=10, pady=5, cursor="hand2")

    def on_enter(e):
        btn.config(font=hover_font, padx=12, pady=6, bg="#45a049", bd=5)

    def on_leave(e):
        btn.config(font=normal_font, padx=10, pady=5, bg="#4CAF50", bd=5)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


buttons = [
    create_button(" Translate Text ", translate_text_icon, translate),
    create_button(" Clear ", clear_text_icon, clear),
    create_button(" Copy ", copy_text_icon, copy),
    create_button(" Read Aloud ", read_aloud_icon, texttospeech),
    create_button(" Voice Input ", voice_input_icon, speechtotext),
]

for i, btn in enumerate(buttons):
    btn.grid(row=0, column=i, padx=15)

root.mainloop()
