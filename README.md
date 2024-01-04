# 🌟 Introduction

Welcome to my advanced computer vision project! Here, I leverage the power of YOLOv8, the latest in the YOLO (You Only Look Once) series, combined with ZeroMQ, to create a dynamic real-time object tracking and logging system.

# 📖 About the Project

In this project, I integrate the cutting-edge YOLOv8 model for object detection with a robust ZeroMQ messaging framework. This setup is ideal for scenarios that demand efficient and real-time processing such as surveillance systems, traffic monitoring, or advanced retail analytics.

# 🔧 Installation

To start using this project:

1. Clone the repository:

    ```bash
    git clone https://github.com/your-repository.git
    cd your-repository
    ```

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

# 🚀 Inferencing

Harness the capabilities of YOLOv8 for real-time object detection. Make sure to adjust the `config.json` file to meet your specific requirements. For more information about YOLOv8 and Ultralytics, visit [their GitHub page](https://github.com/ultralytics/ultralytics).

# 🖥️ Server Side (`main.py`)

The server script is responsible for real-time video processing:

```python
# Execute the server script
python main.py
```

It captures video frames, processes them for object detection, and sends the relevant data to the client for logging purposes.

# 📡 Client Side (`receiver.py`)

The client script handles data logging:

```python
# Start the client script
python receiver.py
```

It listens for incoming messages from the server and diligently logs each event into `crossing_log.csv`.

# ✅ Conclusion

This project is a testament to the amazing potential of combining advanced computer vision techniques with efficient data communication systems. It's versatile and can be adapted to a variety of real-time data processing and analytics applications.
