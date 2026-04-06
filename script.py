import os
import subprocess
import shutil
import sys
import time

INPUT_ROOT = "input"
OUTPUT_ROOT = "output"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FFMPEG = os.path.join(BASE_DIR, "bin", "ffmpeg.exe")
FFPROBE = os.path.join(BASE_DIR, "bin", "ffprobe.exe")
REALESRGAN_EXE = os.path.join(BASE_DIR, "realesrgan", "realesrgan-ncnn-vulkan.exe")
MODEL_DIR = os.path.join(BASE_DIR, "models")

BAR_SIZE = 30
LINE = "-" * 85

HEADER = r"""
  _  __     _ _         _             ______                      _____ _      _____ 
 | |/ /    (_) |       | |           |  ____|                    / ____| |    |_   _|
 | ' / ___  _| | ____ _| |_ ___ _   _| |__ ___  _ __ __ _  ___  | |    | |      | |  
 |  < / _ \| | |/ / _` | __/ __| | | |  __/ _ \| '__/ _` |/ _ \ | |    | |      | |  
 | . \ (_) | |   < (_| | |_\__ \ |_| | | | (_) | | | (_| |  __/ | |____| |____ _| |_ 
 |_|\_\___/|_|_|\_\__,_|\__|___/\__,_|_|  \___/|_|  \__, |\___|  \_____|______|_____|
                                                     __/ |                           
   ┬┴┬┴┤ AI Upscaling Pipeline ├┬┴┬┴                |___/                            
"""

ERROR_LOG = "error_log.txt"


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def header():
    print(HEADER)
    print(LINE)


def log_error(msg):
    with open(ERROR_LOG, "a", encoding="utf8") as f:
        f.write(msg + "\n")


def check_dependency(path):
    return os.path.exists(path)


def detect_gpu():
    """
    Checks for the presence of an NVIDIA GPU by testing the nvidia-smi command.

    Returns:
        bool: True if nvidia-smi executes successfully, False otherwise.
    """
    try:
        r = subprocess.run(["nvidia-smi"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return r.returncode == 0
    except:
        return False


def get_gpu_name():
    """
    Retrieves the hardware name of the detected NVIDIA GPU.

    Returns:
        str: The GPU name, or "Unknown" if extraction fails.
    """
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True,
            text=True
        )
        return r.stdout.strip()
    except:
        return "Unknown"


def progress_bar(progress):
    filled = int(BAR_SIZE * progress)
    empty = BAR_SIZE - filled
    return "█" * filled + "░" * empty


def find_files(exts):
    """
    Recursively scans the INPUT_ROOT directory for files matching the given extensions.

    Args:
        exts (tuple): A tuple of strings representing file extensions (e.g., ('.png', '.jpg')).

    Returns:
        tuple: A tuple containing two lists:
            - found (list): Absolute paths of files matching the extensions.
            - skipped (list): Absolute paths of files that did not match.
    """
    found = []
    skipped = []

    for root, dirs, files in os.walk(INPUT_ROOT):
        for f in files:
            full = os.path.join(root, f)

            if f.lower().endswith(exts):
                found.append(full)
            else:
                skipped.append(full)

    return found, skipped


def get_fps(video):
    """
    Extracts the framerate of a given video file using ffprobe.

    Args:
        video (str): Path to the video file.

    Returns:
        str: The framerate as a string (evaluated as a float if stored as a fraction), 
             or "30" as a fallback upon failure.
    """
    try:
        r = subprocess.run([
            FFPROBE,
            "-v", "0",
            "-select_streams", "v:0",
            "-show_entries", "stream=r_frame_rate",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video
        ], capture_output=True, text=True)

        fps = r.stdout.strip()

        if "/" in fps:
            n, d = fps.split("/")
            return str(float(n) / float(d))

        return fps

    except:
        return "30"


def get_height(file):
    """
    Extracts the vertical resolution (height) of an image or video file using ffprobe.

    Args:
        file (str): Path to the media file.

    Returns:
        int or None: The height in pixels, or None if extraction fails.
    """
    try:
        r = subprocess.run([
            FFPROBE,
            "-v", "0",
            "-select_streams", "v:0",
            "-show_entries", "stream=height",
            "-of", "csv=p=0",
            file
        ], capture_output=True, text=True)

        return int(r.stdout.strip())

    except:
        return None


def ui_progress(mode, file, done, total, start_time):
    clear()
    header()

    progress = done / total if total else 0
    elapsed = int(time.time() - start_time)

    if done > 0:
        avg = elapsed / done
        remaining = int(avg * (total - done))
    else:
        remaining = 0

    print("Mode        :", mode)
    print("File        :", file)
    print(LINE)
    print(f"[{progress_bar(progress)}] {done}/{total}")
    print("")
    print("Elapsed     :", time.strftime("%H:%M:%S", time.gmtime(elapsed)))
    print("Remaining   :", time.strftime("%H:%M:%S", time.gmtime(remaining)))


def upscale_image(src, dst, fmt, gpu, target_height):
    """
    Upscales a single image using Real-ESRGAN and applies post-processing via FFmpeg.

    Args:
        src (str): Path to the source image.
        dst (str): Path for the destination image.
        fmt (str): Output format extension.
        gpu (bool): Flag indicating whether to use hardware GPU acceleration.
        target_height (int): The desired output height. If 0, keeps the raw 2x upscale height.
    """
    try:

        tmp = dst + "_tmp.png"

        gpu_flag = "0" if gpu else "-1"

        subprocess.run([
            REALESRGAN_EXE,
            "-i", src,
            "-o", tmp,
            "-n", "realesr-animevideov3",
            "-s", "2",
            "-f", "png",
            "-g", gpu_flag,
            "-m", MODEL_DIR
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        height = get_height(src)
        ai_height = height * 2 if height else None

        if target_height > 0 and ai_height and target_height < ai_height:

            subprocess.run([
                FFMPEG,
                "-loglevel", "panic",
                "-y",
                "-i", tmp,
                "-vf", f"scale=-2:{target_height},eq=gamma=0.8:contrast=1.1:saturation=1.05",
                dst
            ])

        else:

            subprocess.run([
                FFMPEG,
                "-loglevel", "panic",
                "-y",
                "-i", tmp,
                "-vf", "eq=gamma=0.8:contrast=1.1:saturation=1.05",
                dst
            ])

        os.remove(tmp)

    except Exception as e:
        log_error(f"IMAGE ERROR: {src} -> {e}")


def process_images(files, fmt, gpu, target_height, start_time):
    """
    Orchestrates the batch upscaling of image files.

    Args:
        files (list): A list of absolute paths to the source images.
        fmt (str): Requested output format.
        gpu (bool): Flag for hardware acceleration.
        target_height (int): Requested output resolution height.
        start_time (float): The UNIX timestamp when the job started.
    """
    total = len(files)

    for i, src in enumerate(files, 1):

        rel = os.path.relpath(src, INPUT_ROOT)

        dst = os.path.join(
            OUTPUT_ROOT,
            os.path.splitext(rel)[0] + "." + fmt
        )

        os.makedirs(os.path.dirname(dst), exist_ok=True)

        ui_progress("Images", rel, i, total, start_time)

        upscale_image(src, dst, fmt, gpu, target_height)


def upscale_video(src, dst, fmt, gpu, target_height):
    """
    Upscales a single video by extracting frames, processing them sequentially with 
    Real-ESRGAN, and recompiling the video with the original audio and post-processing.

    Args:
        src (str): Path to the source video.
        dst (str): Path for the destination video.
        fmt (str): Output format extension ('mp4' or 'webm').
        gpu (bool): Flag indicating whether to use hardware GPU acceleration.
        target_height (int): The desired output height. If 0, keeps the raw 2x upscale height.
    """
    tmp_in = f"tmp_in_{os.getpid()}"
    tmp_out = f"tmp_out_{os.getpid()}"

    os.makedirs(tmp_in, exist_ok=True)
    os.makedirs(tmp_out, exist_ok=True)

    try:

        fps = get_fps(src)
        height = get_height(src)
        ai_height = height * 2 if height else None

        subprocess.run([
            FFMPEG,
            "-loglevel", "error",
            "-i", src,
            "-vsync", "0",
            f"{tmp_in}/f%08d.png"
        ])

        gpu_flag = "0" if gpu else "-1"

        subprocess.run([
            REALESRGAN_EXE,
            "-i", tmp_in,
            "-o", tmp_out,
            "-n", "realesr-animevideov3",
            "-s", "2",
            "-f", "png",
            "-g", gpu_flag,
            "-m", MODEL_DIR
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        scale_filter = "eq=gamma=0.8:contrast=1.1:saturation=1.05,format=yuv420p"

        if target_height > 0 and ai_height and target_height < ai_height:
            scale_filter = f"scale=-2:{target_height},eq=gamma=0.8:contrast=1.1:saturation=1.05,format=yuv420p"

        if fmt == "mp4":

            codec = "hevc_nvenc" if gpu else "libx265"

            subprocess.run([
                FFMPEG,
                "-loglevel", "error",
                "-y",
                "-r", fps,
                "-i", f"{tmp_out}/f%08d.png",
                "-i", src,
                "-map", "0:v:0",
                "-map", "1:a:0?",
                "-c:a", "copy",
                "-c:v", codec,
                "-preset", "p4",
                "-vf", scale_filter,
                dst
            ])

        else:

            subprocess.run([
                FFMPEG,
                "-loglevel", "error",
                "-y",
                "-r", fps,
                "-i", f"{tmp_out}/f%08d.png",
                "-i", src,
                "-map", "0:v:0",
                "-map", "1:a:0?",
                "-c:a", "libopus",
                "-c:v", "libvpx-vp9",
                "-b:v", "0",
                "-vf", scale_filter,
                dst
            ])

    except Exception as e:
        log_error(f"VIDEO ERROR: {src} -> {e}")

    finally:

        shutil.rmtree(tmp_in, ignore_errors=True)
        shutil.rmtree(tmp_out, ignore_errors=True)


def process_videos(files, fmt, gpu, target_height, start_time):
    """
    Orchestrates the batch upscaling of video files.

    Args:
        files (list): A list of absolute paths to the source videos.
        fmt (str): Requested output format.
        gpu (bool): Flag for hardware acceleration.
        target_height (int): Requested output resolution height.
        start_time (float): The UNIX timestamp when the job started.
    """
    total = len(files)

    for i, src in enumerate(files, 1):

        rel = os.path.relpath(src, INPUT_ROOT)

        dst = os.path.join(
            OUTPUT_ROOT,
            os.path.splitext(rel)[0] + "." + fmt
        )

        os.makedirs(os.path.dirname(dst), exist_ok=True)

        ui_progress("Videos", rel, i, total, start_time)

        upscale_video(src, dst, fmt, gpu, target_height)


def page(title, options):

    clear()
    header()

    print(title)

    for k, v in options.items():
        print(f" {k}) {v}")

    print(LINE)

    while True:

        c = input("> ").strip()

        if c in options:
            return c


def check_environment():
    """
    Validates that all required third-party binaries (Real-ESRGAN, FFmpeg, FFprobe) 
    are present in the expected directories before execution. Exits the program if any are missing.
    """
    missing = []

    if not check_dependency(REALESRGAN_EXE):
        missing.append("realesrgan/realesrgan-ncnn-vulkan.exe")

    if not check_dependency(FFMPEG):
        missing.append("bin/ffmpeg.exe")

    if not check_dependency(FFPROBE):
        missing.append("bin/ffprobe.exe")

    if missing:

        clear()
        header()

        print("Missing dependencies:\n")

        for m in missing:
            print(" -", m)

        print("\nFix the structure before running.")

        print(LINE)

        input("Press ENTER to exit...")

        sys.exit()


def show_summary(images, videos, skipped, gpu, target_height, image_fmt, video_fmt):
    """
    Displays a pre-flight execution summary for the user to confirm before processing begins.

    Args:
        images (list): Discovered image files.
        videos (list): Discovered video files.
        skipped (list): Files that were skipped due to unsupported extensions.
        gpu (bool): Hardware acceleration availability flag.
        target_height (int): The chosen output resolution height.
        image_fmt (str): Output format for images.
        video_fmt (str): Output format for videos.

    Returns:
        bool: True if the user confirms to start processing, False to abort.
    """
    clear()
    header()

    print("Scan results")
    print(LINE)

    print("Images found :", len(images))
    print("Videos found :", len(videos))
    print("Skipped files:", len(skipped))

    print("")

    if gpu:
        print("GPU detected :", get_gpu_name())
        print("Processing   : GPU acceleration enabled")
    else:
        print("GPU detected : none")
        print("Processing   : CPU mode")

    print("")
    print("Upscale      : 2x RealESRGAN")

    if target_height == 0:
        print("Output size  : Keep 2x result")
    else:
        print("Output size  :", str(target_height) + "p")

    print("")
    print("Output format")

    print("Images :", image_fmt.upper())
    print("Videos :", video_fmt.upper())

    print(LINE)
    print("1) Start")
    print("2) Exit")

    while True:

        c = input("> ").strip()

        if c == "1":
            return True

        if c == "2":
            return False


def main():
    """
    Primary entry point for the CLI. Handles initial environment checks, directory 
    creation, user input mapping, file scanning, and triggers the processing pipelines.
    """
    check_environment()

    os.makedirs(INPUT_ROOT, exist_ok=True)
    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    gpu = detect_gpu()

    mode = page(
        "Select task:",
        {
            "1": "Images",
            "2": "Videos",
            "3": "Images + Videos"
        }
    )

    image_fmt = "png"
    video_fmt = "mp4"

    if mode in ("1", "3"):

        c = page(
            "Image output:",
            {
                "1": "PNG",
                "2": "WEBP"
            }
        )

        image_fmt = "png" if c == "1" else "webp"

    if mode in ("2", "3"):

        c = page(
            "Video output:",
            {
                "1": "MP4",
                "2": "WEBM"
            }
        )

        video_fmt = "mp4" if c == "1" else "webm"

    clear()
    header()

    print("Output resolution")
    print(" 1) Keep 2x upscale")
    print(" 2) 720p")
    print(" 3) 1080p")
    print(" 4) 1440p")
    print(" 5) 4K")

    print(LINE)

    res_map = {
        "1": 0,
        "2": 720,
        "3": 1080,
        "4": 1440,
        "5": 2160
    }

    c = input("> ").strip()

    target_height = res_map.get(c, 0)

    img_ext = (".png", ".jpg", ".jpeg", ".webp")
    vid_ext = (".mp4", ".webm", ".mkv", ".mov")

    images = []
    videos = []
    skipped = []

    if mode in ("1", "3"):
        f, s = find_files(img_ext)
        images.extend(f)
        skipped.extend(s)

    if mode in ("2", "3"):
        f, s = find_files(vid_ext)
        videos.extend(f)
        skipped.extend(s)

    if not images and not videos:

        clear()
        header()

        print("No supported files found in 'input' folder.")
        print("Add files and run again.")

        print(LINE)

        input("Press ENTER to exit...")

        return

    if not show_summary(images, videos, skipped, gpu, target_height, image_fmt, video_fmt):
        return

    start_time = time.time()

    if images:
        process_images(images, image_fmt, gpu, target_height, start_time)

    if videos:
        process_videos(videos, video_fmt, gpu, target_height, start_time)

    clear()
    header()

    total_time = int(time.time() - start_time)

    print("Job completed")

    print(LINE)

    print("Images processed :", len(images))
    print("Videos processed :", len(videos))

    if os.path.exists(ERROR_LOG):
        print("Errors logged    :", ERROR_LOG)

    print("")
    print("Total time       :", time.strftime("%H:%M:%S", time.gmtime(total_time)))
    print("")
    print("Output folder    :", OUTPUT_ROOT)

    print(LINE)


if __name__ == "__main__":
    main()