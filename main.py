import os
import fal_client
from pathlib import Path
from time import sleep
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QLabel
import sys

# Load environment variables from .env file
load_dotenv()

# Get FAL_KEY from environment variables
fal_key = os.getenv('FAL_KEY')
if not fal_key:
    raise ValueError("FAL_KEY not found in environment variables. Please add it to your .env file.")

# Initialize fal client with the key
fal_client.api_key = fal_key

def is_image_file(filename):
    # Common image file extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
    return any(filename.lower().endswith(ext) for ext in image_extensions)

def upscale_image(image_path):
    try:
        # Upload the image to fal.ai
        print(f"Uploading {image_path}...")
        image_url = fal_client.upload_file(str(image_path))
        
        print(f"Processing {image_path}...")
        result = fal_client.subscribe(
            "fal-ai/clarity-upscaler",
            arguments={
                "image_url": image_url,
                "upscale_factor": 2,  # You can adjust this factor
                "creativity": 0.35,
                "resemblance": 0.6,
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
        
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Upscaler")
        self.setMinimumSize(400, 200)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Add label
        self.status_label = QLabel("Select a directory containing images to upscale")
        layout.addWidget(self.status_label)

        # Add browse button
        browse_button = QPushButton("Browse Directory")
        browse_button.clicked.connect(self.browse_directory)
        layout.addWidget(browse_button)

    def browse_directory(self):
        source_dir = QFileDialog.getExistingDirectory(self, "Select Directory")
        if source_dir:
            source_path = Path(source_dir)
            image_files = [f for f in source_path.iterdir() if f.is_file() and is_image_file(f.name)]
            
            if not image_files:
                self.status_label.setText("No image files found in the selected directory!")
                return
            
            self.status_label.setText(f"Processing {len(image_files)} images...")
            
            # Process each image
            for image_file in image_files:
                upscale_image(image_file)
                sleep(1)  # Small delay between requests to avoid rate limiting
            
            self.status_label.setText("Processing complete!")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 