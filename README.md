
# 🔨 KoikatsuForge CLI `v0.3-public`

> **An advanced AI upscaling pipeline specifically tuned for Koikatsu media.**
>
> KoikatsuForge CLI is a high-performance tool that leverages the **RealESR-AnimeVideoV3** engine to transform standard images and videos into high-definition assets. Designed for stability and massive workloads, it automates the entire upscaling workflow while providing a clean, interactive user experience.

## ✨ Key Features

- **Intelligent Batch Processing:** The script performs recursive folder scanning, allowing you to process hundreds of files across nested directories while preserving your original folder hierarchy in the output.
- **Anime-Optimized Engine:** Uses the `realesr-animevideov3` model (via ncnn-vulkan), which is specifically designed to enhance stylized lines and colors common in Koikatsu media.
- **Smart Hardware Management:** The pipeline automatically detects NVIDIA GPUs via `nvidia-smi` to enable hardware acceleration. If no compatible GPU is found, it safely falls back to CPU-only processing.
- **Custom Resolution Targets:** Allows you to choose a target output height (720p, 1080p, 1440p, or 4K). It upscales the media by 2x and then intelligently downscales it to your precise requirements using FFmpeg.
- **Optimized WebP/WebM Compression:**
  - **Images:** Uses `libwebp` with a balanced Quality/Effort ratio (Q90/M4), achieving massive size reduction compared to raw PNG with no perceptible quality loss.
  - **Videos:** Uses `libvpx-vp9` in Constant Quality mode (`-crf 30`) with `-speed 2` and `-tile-columns` to ensure stable encoding times and modern file sizes.
- **Automated Ren'Py Archive (.rpa) Generation:** The tool can automatically compile your processed assets into production-ready `.rpa` archives, dynamically organizing them by top-level folders for effortless game integration.
  - **Dynamic RPA Fallback:** Automatically detects loose files in the output root and bundles them into `root_files.rpa` to ensure no asset is left behind.
- **Resilient Execution:** Built to handle "dirty" data; if a file is corrupted or fails to process, the script logs the specific error to `error_log.txt` and continues to the next file.
- **Real-time Progress Tracking:** The interactive CLI provides a visual progress bar, elapsed time, and a dynamic "Remaining Time" estimate based on your hardware's current performance.

## 🖼️ Visual Comparison (Before vs. After)

<table>
  <tr>
    <th width="50%">ORIGINAL (Input)</th>
    <th width="50%">KOIKATSUFORGE CLI (Output)</th>
  </tr>
  <tr>
    <td><img src="https://i.imgur.com/cneQ6HW.jpeg" width="100%"></td>
    <td><img src="https://i.imgur.com/TFJaAwv.jpeg" width="100%"></td>
  </tr>
  <tr>
    <td><img src="https://i.imgur.com/LFPROWI.jpeg" width="100%"></td>
    <td><img src="https://i.imgur.com/Z8A2wpt.jpeg" width="100%"></td>
  </tr>
  <tr>
    <td><img src="https://i.imgur.com/nGOyvU9.jpeg" width="100%"></td>
    <td><img src="https://i.imgur.com/OyPUPw0.jpeg" width="100%"></td>
  </tr>
</table>

## 🚀 Getting Started

### 1. Project Structure

For the script to function correctly, your directory must maintain the following layout:

```
KoikatsuForgeCLI/
├── KoikatsuForgeCLI.bat        # Recommended entry point
├── script.py                   # Main processing logic
├── rpatool.py                  # Archive generation tool (required for RPA)
├── bin/                        # Video processing tools
│   ├── ffmpeg.exe
│   └── ffprobe.exe
├── realesrgan/                 # Upscaling engine
│   ├── realesrgan-ncnn-vulkan.exe
│   └── vcomp140.dll
├── models/                     # AI Model files
│   ├── realesr-animevideov3-x2.bin
│   └── realesr-animevideov3-x2.param
├── input/                      # Drop your original media here
└── output/                     # Final media and .rpa files will be here
````

### 2. Basic Usage

1. **Prepare Media:** Place your images or videos into the `input/` folder (subfolders are supported).
2. **Launch:** Double-click **`KoikatsuForgeCLI.bat`** (or run `python script.py`).
3. **Configure:** Follow the interactive menu to:
    - Select the media type (Images, Videos, or Both).
    - Choose output format (WebP/PNG for images, MP4/WebM for videos).
    - Set target resolution.
    - **Enable RPA Creation:** Choose if you want to bundle the results into Ren'Py archives.

5. **Confirm:** Review the summary (total files, GPU status, RPA settings) and press **1** to begin.

## 📂 Supported Formats

| Media Category | Supported Input Extensions       | Available Output Formats    |
| -------------- | -------------------------------- | --------------------------- |
| **Images**     | `.png`, `.jpg`, `.jpeg`, `.webp` | **PNG, WEBP**               |
| **Videos**     | `.mp4`, `.webm`, `.mkv`, `.mov`  | **MP4 (H.265), WEBM (VP9)** |

## ⚙️ Technical Specifications

- **Robust Video Workflow:** Uses FFprobe for framerate calculation and extracts frames into process-safe temporary directories (using OS PIDs) to prevent conflicts.
- **Advanced Visual Enhancements:** Applies a specific color correction filter (`gamma=0.8, contrast=1.1, saturation=1.05`) via FFmpeg to ensure vibrant results post-upscale.
- **Encoding Efficiency:** - **MP4:** `hevc_nvenc` (NVIDIA) or `libx265` (CPU) with `p4` preset.
  - **WEBM:** `libvpx-vp9` with `-crf 30` and `libopus` audio.
  - **WEBP:** `libwebp` with `-q:v 85` and `-compression_level 4`.
- **RPA Automation:** Archives are generated directly inside the `output/` folder. To save disk space, the script automatically deletes the processed loose images/folders after they are successfully packed into their respective `.rpa` files.
- **Auto-Cleanup:** All temporary frames (`tmp_in`, `tmp_out`) are strictly managed and deleted upon completion or failure.

## 📄 License

This tool is open-source and free to use. Modify it, break it, or improve it as you see fit!

