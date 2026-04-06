# 🔨 KoikatsuForge CLI

> **An advanced AI upscaling pipeline specifically tuned for Koikatsu media.**
>
> KoikatsuForge CLI is a high-performance tool that leverages the **RealESR-AnimeVideoV3** engine to transform standard images and videos into high-definition assets. Designed for stability and massive workloads, it automates the entire upscaling workflow while providing a clean, interactive user experience.

---

## ✨ Key Features

- **Intelligent Batch Processing:** The script performs recursive folder scanning, allowing you to process hundreds of files across nested directories while preserving your original folder hierarchy in the output.
- **Anime-Optimized Engine:** Uses the `realesr-animevideov3` model, which is specifically designed to enhance stylized lines and colors common in Koikatsu media.
- **Smart Hardware Management:** The pipeline automatically detects NVIDIA GPUs via `nvidia-smi` to enable hardware acceleration. If no compatible GPU is found, it safely falls back to CPU-only processing.
- **Custom Resolution Targets:** Unlike standard upscalers, this tool allows you to choose a target output height (720p, 1080p, 1440p, or 4K). It upscales the media by 2x and then intelligently downscales it to your precise requirements using FFmpeg.
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
2. **Launch:** Double-click **`KoikatsuForgeCLI.bat`** to start the environment.
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

- **Video Processing Workflow:** The script extracts frames into a temporary directory, upscales them individually, and then re-assembles them with the original audio using FFmpeg.
- **Visual Enhancements:** A `gamma=0.8` correction filter is applied during video encoding to counteract the slight "washing out" that can occur during AI upscaling, ensuring vibrant results.
- **Encoding Efficiency:** \* **MP4:** Uses `hevc_nvenc` for NVIDIA-accelerated H.265 encoding or `libx265` for high-quality CPU encoding.
  - **WEBM:** Uses `libvpx-vp9` with a variable bitrate (CRF 32) and Opus audio for maximum web compatibility.
- **Auto-Cleanup:** All temporary frame sequences and intermediate folders are automatically deleted upon completion to save disk space.

---

## 📄 License

This tool is open-source and free to use. Modify it, break it, or improve it as you see fit!
