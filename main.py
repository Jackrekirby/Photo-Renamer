import tkinter as tk
import customtkinter as ctk
from os import listdir, rename
from os.path import isfile, join, splitext, isdir, exists
from datetime import datetime
from exif import Image as exifImage
import subprocess
import time
from PIL import Image

# pyinstaller --onefile --noconsole main.py
icon_file = "icon.ico"


def app(pad: int, ipad: int):
    # create root
    root = ctk.CTk()

    root.title("Photo Renamer")
    icon_path = icon_file if exists(icon_file) else join("dist", icon_file)
    root.iconbitmap(icon_path)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    window_width = int(screen_width / 2)
    window_height = int(screen_height / 2)

    rootGeometry = f"{window_width}x{window_height}"
    print("root geometry", rootGeometry)
    root.geometry(rootGeometry)

    # create components

    def prompt_directory():
        directory = tk.filedialog.askdirectory()
        if not isdir(directory):
            show_error("Invalid Directory", "Please select a valid directory.")
            return

        button_select_directory.configure(text=directory)

        filenames = [
            f
            for f in listdir(directory)
            if isfile(join(directory, f)) and splitext(f)[1].lower() in (".png", ".jpg")
        ]

        label_progress.configure(text=f"{len(filenames)} Photos to Rename")
        progressbar.set(0)

        for widget in frame_files.winfo_children():
            widget.destroy()

        start_time = time.time()
        for filename in filenames:
            full_path = join(directory, filename)
            try:
                exif_image = exifImage(full_path)

                created_time = datetime.strptime(
                    exif_image.get("datetime_original"), "%Y:%m:%d %H:%M:%S"
                ).strftime("%d %b %Y %Hh%Mm%Ss")
            except Exception as e:
                created_time = "unknown"
                show_error("Error", f"Error while processing {filename}: {str(e)}")

            image = Image.open(full_path)
            tkimage = ctk.CTkImage(image, size=(16, 16))

            frame_file_row = ctk.CTkFrame(master=frame_files, fg_color="transparent")
            frame_file_row.pack(fill=tk.X)

            label_image = ctk.CTkLabel(master=frame_file_row, image=tkimage, text="")
            label_image.pack(side=tk.LEFT, padx=pad)

            label_original_name = ctk.CTkLabel(master=frame_file_row, text=filename)
            label_original_name.pack(fill=tk.X, side=tk.LEFT, padx=pad)

            label_new_name = ctk.CTkLabel(master=frame_file_row, text=str(created_time))
            label_new_name.pack(side=tk.RIGHT, padx=pad)

            elapsed = time.time() - start_time
            if elapsed > 0.5:  # update UI every 0.5 seconds
                start_time = 0
                root.update()
                root.update_idletasks()

            image.close()

    def goto_directory():
        directory: str = button_select_directory.cget("text")
        win_dir = directory.replace("/", "\\")
        print(f'explorer "{win_dir}"')
        subprocess.call(f'explorer "{win_dir}"', shell=True)

    def rename_files():
        label_progress.configure(text="Started")
        directory = button_select_directory.cget("text")

        filenames = [f for f in listdir(directory) if isfile(join(directory, f))]

        imax = len(filenames)

        for i, filename in enumerate(filenames):
            full_path = join(directory, filename)

            try:
                exif_image = exifImage(full_path)

                created_time = datetime.strptime(
                    exif_image.get("datetime_original"), "%Y:%m:%d %H:%M:%S"
                ).strftime("%d %b %Y %Hh%Mm%Ss")
            except Exception as e:
                created_time = "unknown"
                show_error("Error", f"Error while processing {filename}: {str(e)}")
                continue # skip image and try and rename others

            name, ext = splitext(filename)
            new_filename = str(created_time) + ext
            try:
                rename(full_path, join(directory, new_filename))
            except Exception as e:
                show_error("Error", f"Error while renaming {filename} to {new_filename}: {str(e)}")
                continue # if file cannot be renamed it is probably open
            
            progressbar.set((i + 1) / imax)
            label_progress.configure(text=f"{i} / {imax}")
            root.update()
            root.update_idletasks()
            time.sleep(3 / imax)

        label_progress.configure(text="Done")

    def show_error(title, message):
        tk.messagebox.showerror(title, message)

    frame_button_row = ctk.CTkFrame(
        master=root,  # fg_color="transparent"
    )
    frame_button_row.pack(fill=tk.BOTH)

    button_select_directory = ctk.CTkButton(
        master=frame_button_row,
        text="Select Directory",
        command=prompt_directory,
    )
    button_select_directory.pack(
        fill=tk.X, padx=pad, pady=pad, ipadx=ipad, ipady=ipad, side=tk.LEFT, expand=True
    )

    button_goto_directory = ctk.CTkButton(
        master=frame_button_row,
        text="Open In File Explorer",
        command=goto_directory,
    )
    button_goto_directory.pack(
        fill=tk.X, padx=pad, pady=pad, ipadx=ipad, ipady=ipad, side=tk.RIGHT
    )

    frame_file_wrapper = ctk.CTkFrame(master=root)
    frame_file_wrapper.pack(
        fill=tk.BOTH, padx=pad, pady=pad, ipadx=ipad, ipady=ipad, expand=True
    )

    frame_file_title = ctk.CTkFrame(master=frame_file_wrapper)
    frame_file_title.pack(fill=tk.X, padx=pad, pady=pad, ipadx=ipad, ipady=0)
    label_original_name_title = ctk.CTkLabel(master=frame_file_title, text="Photo")
    label_original_name_title.pack(fill=tk.X, side=tk.LEFT, padx=pad * 4)

    label_new_name_title = ctk.CTkLabel(master=frame_file_title, text="Date Taken")
    label_new_name_title.pack(side=tk.RIGHT, padx=pad * 4)

    frame_files = ctk.CTkScrollableFrame(
        master=frame_file_wrapper,
    )
    frame_files.pack(
        fill=tk.BOTH, padx=pad, pady=pad, ipadx=ipad, ipady=ipad, expand=True
    )

    frame_progress_row = ctk.CTkFrame(
        master=root,
        # fg_color="transparent"
    )
    frame_progress_row.pack(fill=tk.BOTH)

    button_run = ctk.CTkButton(
        master=frame_progress_row,
        text="Run",
        command=rename_files,
    )
    button_run.pack(fill=tk.X, padx=pad, pady=pad, ipadx=ipad, ipady=ipad, side=tk.LEFT)

    label_progress = ctk.CTkLabel(
        master=frame_progress_row, text="No Directory Selected"
    )
    label_progress.pack(
        fill=tk.NONE, padx=pad, pady=pad, ipadx=ipad, ipady=ipad, side=tk.RIGHT
    )

    progressbar = ctk.CTkProgressBar(master=frame_progress_row)
    progressbar.pack(
        fill=tk.X, padx=pad, pady=pad, ipadx=ipad, ipady=ipad, side=tk.LEFT, expand=True
    )
    progressbar.set(0)

    # run loop
    root.mainloop()


app(20, 5)
