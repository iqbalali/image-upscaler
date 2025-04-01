# Image Processing Tool

A desktop application that uses AI to upscale and describe images. Built with Python and PyQt6, powered by the fal.ai Clarity Upscaler model and Google's Gemini AI.

## Features

- User-friendly graphical interface with tabbed interface
- **Image Description (Gemini AI)**
  - Analyzes images and generates detailed descriptions
  - Creates JSON files with structured descriptions and stable diffusion prompts
  - Batch processing of multiple images
- **Image Upscaling (fal.ai)**
  - 2x or 4x upscaling with AI-powered enhancement
  - Customizable settings for creativity and resemblance
  - Creates a separate "upscaled" folder for processed images
- Supports common image formats (JPG, JPEG, PNG, BMP, GIF, WEBP)

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

3. Set up your API keys:
   - Create an account at [FAL.ai](https://fal.ai)
   - Get your Google API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a `.env` file in the project root:
   ```
   FAL_KEY=your_fal_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   ```

4. Run the application:
   ```
   python main.py
   ```

## Usage

### Image Description
1. Select the "Describe Images" tab
2. Choose a directory containing images
3. The tool will create JSON files with descriptions next to each image

### Image Upscaling
1. Select the "Upscale Images" tab
2. Adjust upscaling settings as needed
3. Choose a directory containing images
4. Upscaled images will be saved in an "upscaled" subfolder