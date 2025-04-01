import os
import fal_client
import google.generativeai as genai
import json
from pathlib import Path
from time import sleep
from dotenv import load_dotenv
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, 
    QFileDialog, QLabel, QGroupBox, QFormLayout, QHBoxLayout, 
    QSlider, QLineEdit, QCheckBox, QComboBox, QTextEdit, QTabWidget
)
from PyQt6.QtCore import Qt
import sys
from google.generativeai import types

# Load environment variables from .env file
load_dotenv()

# Get FAL_KEY from environment variables
fal_key = os.getenv('FAL_KEY')
if not fal_key:
    raise ValueError("FAL_KEY not found in environment variables. Please add it to your .env file.")

# Initialize fal client with the key
fal_client.api_key = fal_key

# After loading FAL_KEY, add Gemini configuration
gemini_key = os.getenv('GOOGLE_API_KEY')
if not gemini_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please add it to your .env file.")

genai.configure(api_key=gemini_key)
client = genai.GenerativeModel('gemini-2.0-flash')

def is_image_file(filename):
    # Common image file extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
    return any(filename.lower().endswith(ext) for ext in image_extensions)

def upscale_image(image_path, **kwargs):
    try:
        # Check for JSON file and load prompt if it exists
        json_path = image_path.with_suffix('.json')
        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    kwargs['prompt'] = json_data.get('prompt', kwargs.get('prompt'))
                    print(f"Loaded prompt from {json_path}: {kwargs['prompt']}")
            except Exception as e:
                print(f"Error loading JSON file {json_path}: {str(e)}")
        
        # Upload the image to fal.ai
        print(f"Uploading {image_path}...")
        image_url = fal_client.upload_file(str(image_path))
        
        print(f"Processing {image_path}...")
        print(f"Using settings: {json.dumps(kwargs, indent=2)}")
        
        result = fal_client.subscribe(
            "fal-ai/clarity-upscaler",
            arguments={
                "image_url": image_url,
                "upscale_factor": kwargs.get("upscale_factor", 2),
                "creativity": kwargs.get("creativity", 0.35),
                "resemblance": kwargs.get("resemblance", 0.6),
                "prompt": kwargs.get("prompt", "masterpiece, best quality, highres"),
                "negative_prompt": kwargs.get("negative_prompt", "(worst quality, low quality, normal quality:2)"),
                "guidance_scale": 4,
                "num_inference_steps": kwargs.get("num_inference_steps", 18),
                "enable_safety_checker": kwargs.get("enable_safety_checker", True)
            }
        )
        
        # Create output filename
        output_dir = image_path.parent / "upscaled"
        output_dir.mkdir(exist_ok=True)
        output_filename = f"upscaled_{image_path.name}"
        output_path = output_dir / output_filename
        
        # Download the result
        import requests
        response = requests.get(result['image']['url'])
        with open(output_path, 'wb') as f:
            f.write(response.content)
            
        print(f"Saved upscaled image to {output_path}")
        return True
        
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return False

def describe_image(image_path):
    """Describe an image using Gemini API and save the result as JSON"""
    try:
        # Read the image file
        with open(image_path, 'rb') as img_file:
            image_data = img_file.read()
        
        # Prompt for Gemini
        prompt = """Describe this image and give me a prompt suitable for stable diffusion use. Output in JSON format:
        {
            "description":"detailed description of the image, create sections if necessary, use markdown. include style, lighting, mood, description of actions, convert text",
            "prompt":"prompt to generate in stable diffusion"
        }"""
        
        # Create content for the request
        response = client.generate_content([
            {
                "mime_type": "image/jpeg",
                "data": image_data
            },
            prompt
        ])
            
        # Parse the response to get just the JSON part
        json_str = response.text
        if '```json' in json_str:
            json_str = json_str.split('```json')[1].split('```')[0]
        elif '```' in json_str:
            json_str = json_str.split('```')[1].split('```')[0]
            
        # Parse and validate JSON
        result = json.loads(json_str)
        
        # Save JSON file
        output_path = image_path.with_suffix('.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
            
        return True
        
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Processing Tool")
        self.setMinimumSize(800, 600)  # Increased size to accommodate debug output

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Create tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Create tabs
        self.describe_tab = QWidget()
        self.upscale_tab = QWidget()
        
        # Add tabs to widget
        self.tabs.addTab(self.describe_tab, "Describe Images")
        self.tabs.addTab(self.upscale_tab, "Upscale Images")

        # Setup both tabs
        self.setup_describe_tab()
        self.setup_upscale_tab()

        # Add debug output
        self.debug_output = QTextEdit()
        self.debug_output.setReadOnly(True)
        self.debug_output.setMinimumHeight(150)
        main_layout.addWidget(QLabel("Debug Output:"))
        main_layout.addWidget(self.debug_output)

        # Redirect stdout to debug output
        sys.stdout = DebugStream(self.debug_output)

    def setup_describe_tab(self):
        layout = QVBoxLayout(self.describe_tab)
        
        # Status label
        self.describe_status_label = QLabel("Select a directory containing images to describe")
        layout.addWidget(self.describe_status_label)

        # Add browse button
        browse_button = QPushButton("Browse Directory")
        browse_button.clicked.connect(self.browse_directory_describe)
        layout.addWidget(browse_button)

    def setup_upscale_tab(self):
        layout = QVBoxLayout(self.upscale_tab)
        
        # Add settings group
        settings_group = QGroupBox("Upscaling Settings")
        settings_layout = QFormLayout()

        # Upscale factor combo box
        self.upscale_factor = QComboBox()
        self.upscale_factor.addItems(['2x', '4x'])
        settings_layout.addRow("Scale Factor:", self.upscale_factor)

        # Sliders with value labels
        self.creativity_slider = QSlider(Qt.Orientation.Horizontal)
        self.creativity_slider.setRange(0, 100)
        self.creativity_slider.setValue(35)
        self.creativity_label = QLabel("0.35")
        self.creativity_slider.valueChanged.connect(
            lambda v: self.creativity_label.setText(f"{v/100:.2f}")
        )
        creativity_layout = QHBoxLayout()
        creativity_layout.addWidget(self.creativity_slider)
        creativity_layout.addWidget(self.creativity_label)
        settings_layout.addRow("Creativity:", creativity_layout)

        self.resemblance_slider = QSlider(Qt.Orientation.Horizontal)
        self.resemblance_slider.setRange(0, 100)
        self.resemblance_slider.setValue(60)
        self.resemblance_label = QLabel("0.60")
        self.resemblance_slider.valueChanged.connect(
            lambda v: self.resemblance_label.setText(f"{v/100:.2f}")
        )
        resemblance_layout = QHBoxLayout()
        resemblance_layout.addWidget(self.resemblance_slider)
        resemblance_layout.addWidget(self.resemblance_label)
        settings_layout.addRow("Resemblance:", resemblance_layout)

        self.steps_slider = QSlider(Qt.Orientation.Horizontal)
        self.steps_slider.setRange(1, 50)
        self.steps_slider.setValue(18)
        self.steps_label = QLabel("18")
        self.steps_slider.valueChanged.connect(
            lambda v: self.steps_label.setText(str(v))
        )
        steps_layout = QHBoxLayout()
        steps_layout.addWidget(self.steps_slider)
        steps_layout.addWidget(self.steps_label)
        settings_layout.addRow("Inference Steps:", steps_layout)

        # Prompt inputs with more space
        self.prompt = QTextEdit()
        self.prompt.setPlainText("masterpiece, best quality, highres")
        self.prompt.setMinimumWidth(300)
        self.prompt.setMaximumHeight(60)
        settings_layout.addRow("Prompt:", self.prompt)

        self.negative_prompt = QTextEdit()
        self.negative_prompt.setPlainText("(worst quality, low quality, normal quality:2)")
        self.negative_prompt.setMinimumWidth(300)
        self.negative_prompt.setMaximumHeight(60)
        settings_layout.addRow("Negative Prompt:", self.negative_prompt)

        # Safety checker
        self.safety_checker = QCheckBox()
        self.safety_checker.setChecked(True)
        settings_layout.addRow("Safety Checker:", self.safety_checker)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Status label
        self.upscale_status_label = QLabel("Select a directory containing images to upscale")
        layout.addWidget(self.upscale_status_label)

        # Add browse button
        browse_button = QPushButton("Browse Directory")
        browse_button.clicked.connect(self.browse_directory_upscale)
        layout.addWidget(browse_button)

    def get_settings(self):
        """Get current settings as a dictionary"""
        return {
            "upscale_factor": int(self.upscale_factor.currentText()[0]),
            "creativity": self.creativity_slider.value() / 100,
            "resemblance": self.resemblance_slider.value() / 100,
            "num_inference_steps": self.steps_slider.value(),
            "prompt": self.prompt.toPlainText(),
            "negative_prompt": self.negative_prompt.toPlainText(),
            "enable_safety_checker": self.safety_checker.isChecked(),
            "guidance_scale": 4  # Keeping this fixed for now
        }

    def browse_directory_describe(self):
        source_dir = QFileDialog.getExistingDirectory(self, "Select Directory")
        if source_dir:
            source_path = Path(source_dir)
            image_files = [f for f in source_path.iterdir() if f.is_file() and is_image_file(f.name)]
            
            if not image_files:
                self.describe_status_label.setText("No image files found in the selected directory!")
                return
            
            self.describe_status_label.setText(f"Processing {len(image_files)} images...")
            
            # Process each image
            success_count = 0
            for image_file in image_files:
                if describe_image(image_file):
                    success_count += 1
                sleep(1)  # Small delay between requests
            
            self.describe_status_label.setText(f"Processing complete! Successfully described {success_count} images.")

    def browse_directory_upscale(self):
        source_dir = QFileDialog.getExistingDirectory(self, "Select Directory")
        if source_dir:
            source_path = Path(source_dir)
            image_files = [f for f in source_path.iterdir() if f.is_file() and is_image_file(f.name)]
            
            if not image_files:
                self.upscale_status_label.setText("No image files found in the selected directory!")
                return
            
            self.upscale_status_label.setText(f"Processing {len(image_files)} images...")
            
            # Get current settings
            settings = self.get_settings()
            
            # Process each image with current settings
            success_count = 0
            for image_file in image_files:
                if upscale_image(image_file, **settings):
                    success_count += 1
                sleep(1)  # Small delay between requests
            
            self.upscale_status_label.setText(f"Processing complete! Successfully upscaled {success_count} images.")

# Add DebugStream class to handle stdout redirection
class DebugStream:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, text):
        self.text_widget.append(text)

    def flush(self):
        pass

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 