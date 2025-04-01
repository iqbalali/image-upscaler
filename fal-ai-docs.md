About
Generate Image

1. Calling the API
#
Install the client
#
The client provides a convenient way to interact with the model API.


pip install fal-client
Setup your API Key
#
Set FAL_KEY as an environment variable in your runtime.


export FAL_KEY="YOUR_API_KEY"
Submit a request
#
The client API handles the API submit protocol. It will handle the request status updates and return the result when the request is completed.

Python
Python (async)

import fal_client

def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
           print(log["message"])

result = fal_client.subscribe(
    "fal-ai/clarity-upscaler",
    arguments={
        "image_url": "https://storage.googleapis.com/falserverless/gallery/NOCA_Mick-Thompson.resized.resized.jpg"
    },
    with_logs=True,
    on_queue_update=on_queue_update,
)
print(result)
2. Authentication
#
The API uses an API Key for authentication. It is recommended you set the FAL_KEY environment variable in your runtime when possible.

API Key
#
Protect your API Key
When running code on the client-side (e.g. in a browser, mobile app or GUI applications), make sure to not expose your FAL_KEY. Instead, use a server-side proxy to make requests to the API. For more information, check out our server-side integration guide.

3. Queue
#
Long-running requests
For long-running requests, such as training jobs or models with slower inference times, it is recommended to check the Queue status and rely on Webhooks instead of blocking while waiting for the result.

Submit a request
#
The client API provides a convenient way to submit requests to the model.

Python
Python (async)

import fal_client

handler = fal_client.submit(
    "fal-ai/clarity-upscaler",
    arguments={
        "image_url": "https://storage.googleapis.com/falserverless/gallery/NOCA_Mick-Thompson.resized.resized.jpg"
    },
    webhook_url="https://optional.webhook.url/for/results",
)

request_id = handler.request_id
Fetch request status
#
You can fetch the status of a request to check if it is completed or still in progress.

Python
Python (async)

status = fal_client.status("fal-ai/clarity-upscaler", request_id, with_logs=True)
Get the result
#
Once the request is completed, you can fetch the result. See the Output Schema for the expected result format.

Python
Python (async)

result = fal_client.result("fal-ai/clarity-upscaler", request_id)
4. Files
#
Some attributes in the API accept file URLs as input. Whenever that's the case you can pass your own URL or a Base64 data URI.

Data URI (base64)
#
You can pass a Base64 data URI as a file input. The API will handle the file decoding for you. Keep in mind that for large files, this alternative although convenient can impact the request performance.

Hosted files (URL)
#
You can also pass your own URLs as long as they are publicly accessible. Be aware that some hosts might block cross-site requests, rate-limit, or consider the request as a bot.

Uploading files
#
We provide a convenient file storage that allows you to upload files and use them in your requests. You can upload files using the client API and use the returned URL in your requests.

Python
Python (async)

url = fal_client.upload_file("path/to/file")
Read more about file handling in our file upload guide.

5. Schema
#
Input
#
image_url string
The URL of the image to upscale.

prompt string
The prompt to use for generating the image. Be as descriptive as possible for best results. Default value: "masterpiece, best quality, highres"

upscale_factor float
The upscale factor Default value: 2

negative_prompt string
The negative prompt to use. Use it to address details that you don't want in the image. Default value: "(worst quality, low quality, normal quality:2)"

creativity float
The creativity of the model. The higher the creativity, the more the model will deviate from the prompt. Refers to the denoise strength of the sampling. Default value: 0.35

resemblance float
The resemblance of the upscaled image to the original image. The higher the resemblance, the more the model will try to keep the original image. Refers to the strength of the ControlNet. Default value: 0.6

guidance_scale float
The CFG (Classifier Free Guidance) scale is a measure of how close you want the model to stick to your prompt when looking for a related image to show you. Default value: 4

num_inference_steps integer
The number of inference steps to perform. Default value: 18

seed integer
The same seed and the same prompt given to the same version of Stable Diffusion will output the same image every time.

enable_safety_checker boolean
If set to false, the safety checker will be disabled. Default value: true


{
  "image_url": "https://storage.googleapis.com/falserverless/gallery/NOCA_Mick-Thompson.resized.resized.jpg",
  "prompt": "masterpiece, best quality, highres",
  "upscale_factor": 2,
  "negative_prompt": "(worst quality, low quality, normal quality:2)",
  "creativity": 0.35,
  "resemblance": 0.6,
  "guidance_scale": 4,
  "num_inference_steps": 18,
  "enable_safety_checker": true
}
Output
#
image Image
The URL of the generated image.

seed integer
The seed used to generate the image.

timings Timings
The timings of the different steps in the workflow.


{
  "image": {
    "url": "",
    "content_type": "image/png",
    "file_name": "z9RV14K95DvU.png",
    "file_size": 4404019,
    "width": 1024,
    "height": 1024
  }
}
Other types
#
Image
#
url string
The URL where the file can be downloaded from.

content_type string
The mime type of the file.

file_name string
The name of the file. It will be auto-generated if not provided.

file_size integer
The size of the file in bytes.

width integer
The width of the image in pixels.

height integer
The height of the image in pixels.