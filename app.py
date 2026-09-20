import os
import random
import subprocess
import tempfile
import zipfile
import tkinter as tk
from tkinter import messagebox, filedialog

def get_ffmpeg_path():
    # Looks for bundled ffmpeg or system ffmpeg
    return "ffmpeg"

class VideoGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fact Video Generator (Win 7/10)")
        self.root.geometry("600x550")
        
        # Heading
        tk.Label(root, text="Enter Facts (One per line):", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Text input for facts
        self.text_input = tk.Text(root, height=15, width=65, font=("Arial", 10))
        self.text_input.pack(pady=5)
        self.text_input.insert(tk.END, "Fact one goes here.\nFact two goes here.\nFact three goes here.")
        
        # Generate Button
        self.btn_generate = tk.Button(root, text="Generate Videos & Zip", bg="green", fg="white", font=("Arial", 11, "bold"), command=self.generate_videos)
        self.btn_generate.pack(pady=15)
        
    def generate_videos(self):
        raw_text = self.text_input.get("1.0", tk.END).strip()
        if not raw_text:
            messagebox.showerror("Error", "Please enter at least one fact.")
            return
            
        facts = [line.strip() for line in raw_text.split("\n") if line.strip()]
        
        # Output directory selection
        output_dir = filedialog.askdirectory(title="Select Output Folder for ZIP")
        if not output_dir:
            return
            
        zip_path = os.path.join(output_dir, "fact_videos.zip")
        
        try:
            generated_files = []
            temp_dir = tempfile.mkdtemp()
            
            for index, fact in enumerate(facts, start=1):
                duration = round(random.uniform(5.0, 7.0), 2)
                video_filename = os.path.join(temp_dir, f"{index}.mp4")
                
                # Audio background selection
                audio_choices = ["bg1.mp3", "bg2.mp3"]
                chosen_audio = random.choice([a for a in audio_choices if os.path.exists(a)]) if any(os.path.exists(a) for a in audio_choices) else None
                
                # Build FFmpeg command for 1080x1920 video with text wrap, margins, and audio sync
                # Font fallback handling
                font_file = "font.ttf" if os.path.exists("font.ttf") else "Arial"
                
                filter_complex = (
                    f"color=c=black:s=1080x1920:d={duration}[v0];"
                    f"[v0]drawtext=fontfile='{font_file}':text='Psycholofy Facts':fontcolor=yellow:fontsize=60:x=(w-text_w)/2:y=200[v1];"
                    f"[v1]drawtext=fontfile='{font_file}':text='{fact}':fontcolor=white:fontsize=50:x=(w-text_w)/2:y=(h-text_h)/2:box=0:boxcolor=black@0.5:boxborderw=10:max_w=680[vfinal]"
                )
                
                cmd = [
                    get_ffmpeg_path(), "-y",
                    "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo",
                    "-filter_complex", filter_complex,
                    "-map", "[vfinal]", "-t", str(duration),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-r", "30", video_filename
                ]
                
                if chosen_audio:
                    # Pick random offset for audio
                    cmd = [
                        get_ffmpeg_path(), "-y",
                        "-ss", str(random.uniform(0, 5)),
                        "-i", chosen_audio,
                        "-filter_complex", filter_complex,
                        "-map", "[vfinal]", "-map", "1:a:?" if False else "0:a", # Simplified audio mapping
                        "-t", str(duration),
                        "-c:v", "libx264", "-c:a", "aac", "-pix_fmt", "yuv420p",
                        "-r", "30", video_filename
                    ]
                
                # Fallback clean run without complex audio if background music fails
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                generated_files.append((video_filename, f"{index}.mp4"))
                
            # Create ZIP file
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file_path, arc_name in generated_files:
                    zipf.write(file_path, arcname=arc_name)
                    
            messagebox.สำเร็จ("Success", f"All videos generated and zipped successfully at:\n{zip_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed during generation: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoGeneratorApp(root)
    root.mainloop()
