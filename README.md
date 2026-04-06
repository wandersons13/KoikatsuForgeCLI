# 🔨 KoikatsuForge CLI `v0.3-public`

> **An advanced AI upscaling pipeline specifically tuned for Koikatsu media.**
>
> KoikatsuForge CLI is a high-performance tool that leverages the **RealESR-AnimeVideoV3** engine to transform standard images and videos into high-definition assets. Designed for stability and massive workloads, it automates the entire upscaling workflow while providing a clean, interactive user experience.

---

## ✨ Key Features

- **Intelligent Batch Processing:** The script performs recursive folder scanning, allowing you to process hundreds of files across nested directories while preserving your original folder hierarchy in the output.
- **Automated Ren'Py Archive (.rpa) Generation:** The tool can automatically compile your processed assets into production-ready `.rpa` archives, dynamically organizing them by top-level folders for effortless game integration.
- **Anime-Optimized Engine:** Uses the `realesr-animevideov3` model (via ncnn-vulkan), which is specifically designed to enhance stylized lines and colors common in Koikatsu media.
- **Smart Hardware Management:** The pipeline automatically detects NVIDIA GPUs via `nvidia-smi` to enable hardware acceleration. If no compatible GPU is found, it safely falls back to CPU-only processing.
- **Custom Resolution Targets:** Unlike standard upscalers, this tool allows you to choose a target output height (720p, 1080p, 1440p, or 4K). It upscales the media by 2x and then intelligently downscales it to your precise requirements using FFmpeg.
- **Optimized WebP/WebM Compression:** - Images: Uses `libwebp` with a balanced Quality/Effort ratio (Q90/M4), achieving up to 88% size reduction compared to raw PNG with no perceptible quality loss.
  - Videos: Uses `libvpx-vp9` in Constant Quality mode (`-crf 30`) with `-speed 2` and `-tile-columns` to ensure stable encoding times and modern file sizes.
- **Dynamic RPA Fallback:** Automatically detects loose files in the output root and bundles them into `root_files.rpa` to ensure no asset is left behind.
- **Resilient Execution:** Built to handle "dirty" data; if a file is corrupted or fails to process, the script logs the specific error to `error_log.txt` and continues to the next file without stopping the entire queue.
- **Real-time Progress Tracking:** The interactive CLI provides a visual progress bar, elapsed time, and a dynamic "Remaining Time" estimate based on your hardware's current performance.

---

## 🚀 Getting Started

### 1. Project Structure

For the script to function correctly, your directory must maintain the following layout:

```
KoikatsuForgeCLI/
├── KoikatsuForgeCLI.bat        # Recommended entry point
├── script.py                   # Main processing logic
├── rpatool.py                  # Archive generation tool
├── bin/                        # Video processing tools
│   ├── ffmpeg.exe
│   └── ffprobe.exe
├── realesrgan/                 # Upscaling engine
│   ├── realesrgan-ncnn-vulkan.exe
│   └── vcomp140.dll
├── models/                     # AI Model files
│   ├── realesr-animevideov3-x2.bin
│   └── realesr-animevideov3-x2.param
├── input/                      # Drop your original media here
└── output/                     # Your upscaled media ends up here
```

### 2. Basic Usage

1. **Prepare Media:** Place your images or videos into the `input/` folder.
2. **Launch:** Double-click **`KoikatsuForgeCLI.bat`** to start the environment (or run `python script.py`).
3. **Configure:** Follow the interactive menu to:
   - Select the media type (Images, Videos, or Both).
   - Choose your preferred output format (e.g., WebP for images or MP4 for videos).
   - Set your target resolution (from raw 2x up to 4K).

4. **Confirm:** Review the scan summary (total files found, GPU status) and press **1** to begin.

---

## 📂 Supported Formats

| Media Category | Supported Input Extensions       | Available Output Formats    |
| -------------- | -------------------------------- | --------------------------- |
| **Images**     | `.png`, `.jpg`, `.jpeg`, `.webp` | **PNG, WEBP**               |
| **Videos**     | `.mp4`, `.webm`, `.mkv`, `.mov`  | **MP4 (H.265), WEBM (VP9)** |

---

## ⚙️ Technical Specifications

- **Robust Video Workflow:** The script handles complex video files by accurately calculating fractional framerates using FFprobe. It extracts frames into process-safe temporary directories (using OS PIDs) to prevent conflicts if multiple instances are run.
- **Advanced Visual Enhancements:** AI upscaling can sometimes wash out colors. To counteract this, the pipeline applies a post-processing color correction filter (`gamma=0.8, contrast=1.1, saturation=1.05`) via FFmpeg to **both images and videos**, ensuring vibrant and punchy results.
- **Encoding Efficiency:** - **MP4:** Uses `hevc_nvenc` with the `p4` preset for fast, high-quality NVIDIA-accelerated H.265 encoding, or `libx265` for CPU encoding.
  - **WEBM:** Uses `libvpx-vp9` with variable bitrate (`-b:v 0`) and `libopus` audio for maximum web compatibility and quality retention.
- **Auto-Cleanup:** All temporary frame sequences (`tmp_in`, `tmp_out`) and intermediate image files are strictly managed and automatically deleted upon completion or failure to save disk space.

---

## 📄 License

This tool is open-source and free to use. Modify it, break it, or improve it as you see fit!
