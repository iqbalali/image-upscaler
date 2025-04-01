# Image Upscaler

A desktop application that uses AI to upscale images while maintaining quality. Built with Python and PyQt6, powered by the fal.ai Clarity Upscaler model.

## Features

- User-friendly graphical interface
- Batch processing of multiple images
- Supports common image formats (JPG, JPEG, PNG, BMP, GIF, WEBP)
- Creates a separate "upscaled" folder for processed images
- 2x upscaling with AI-powered enhancement

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/iqbalali/image-upscaler.git
   cd image-upscaler
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your FAL API key:
   - Create an account at [FAL.ai](https://fal.ai)
   - Get your API key from the dashboard
   - Create a `.env` file in the project root:
   ```
   FAL_KEY=your_fal_api_key_here
   ```

4. Run the application:
   ```
   python main.py
   ```

## Usage

1. Select a directory containing images to upscale.
2. High-res images will be saved in the `upscaled` folder.