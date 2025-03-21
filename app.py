import streamlit as st
import cv2
from ultralytics import YOLO
import os
import time

def model_yolo():
    MODEL_PATH = "yolov8s_ppe.pt"
    model = YOLO(MODEL_PATH)
    model.fuse()
    return model
    
def detect_ppe(model, frame, conf):
    CLASS_NAMES_DICT = model.model.names
    class_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]

    detections = model(frame, conf=conf, verbose=False)
    for result in detections[0]:
        x_min, y_min, x_max, y_max = result.boxes.xyxy[0].cpu().numpy()
        confidence = result.boxes.conf[0]
        cls = int(result.boxes.cls[0])

        color = class_colors[cls % len(class_colors)]

        frame = cv2.rectangle(frame, (int(x_min), int(y_min)),(int(x_max), int(y_max)), color, 3)

        (w, h), _ = cv2.getTextSize(f'{CLASS_NAMES_DICT[cls]}', cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
        frame = cv2.rectangle(frame, (int(x_min), int(y_min)-20), (int(x_min)+w, int(y_min)), color, -1)
        frame = cv2.putText(frame, f'{CLASS_NAMES_DICT[cls]}', (int(x_min), int(y_min)-4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), thickness=2)
    return frame

def display_video_detection(model, video_source, conf):
    start_time = time.time()

    video = cv2.VideoCapture(video_source)

    video_container = st.empty()

    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break

        processed_frame = detect_ppe(model, frame, conf)

        rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)

        video_container.image(rgb_frame, channels="RGB")

    video.release()
    end_time = time.time()
    processing_time = end_time - start_time
    st.write(f"Processing Time: {processing_time:.2f} seconds")

def display_image_detection(model, image_source, conf):
    start_time = time.time()

    image_container = st.empty()

    frame = cv2.imread(image_source)
    
    processed_frame = detect_ppe(model, frame, conf)

    rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)

    image_container.image(rgb_frame, channels="RGB")

    end_time = time.time()

    processing_time = end_time - start_time
    st.write(f"Processing Time: {processing_time:.2f} seconds")
    
def main(model):
    UPLOAD_FOLDER = os.getcwd()

    st.title("Personal Protective Equipment Detection")

    media_option = st.radio("Choose Media Type", ("Upload Image", "Upload Video"))

    if media_option == "Upload Image":
        uploaded_image = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], 
                                        accept_multiple_files=False, 
                                        key="image_uploader", 
                                        help="Upload an image from your local system.")
        if uploaded_image is not None:
            image_source = f"temp.{uploaded_image.name.split('.')[-1]}"
            with open(os.path.join(UPLOAD_FOLDER, image_source), "wb") as f:
                f.write(uploaded_image.read())
        else:
            st.write("Please upload an image.")
            return
        
        conf = st.slider("Select Confidence Threshold", 0.1, 1.0, 0.5, 0.1)

        st.write(f"Image Processing ({image_source}) with Confidence: {conf}")
        display_image_detection(model, image_source, conf)

    else:
        video_option = st.radio("Choose Video Source", ("Upload Video", "Default Video"))

        if video_option == "Default Video":
            video_source = st.selectbox("Choose Source", ("Default Video 1", "Default Video 2"))
            if video_source == "Default Video 1":
                video_source = "test.mov"
            else:
                video_source = "test2.mp4"
        else:
            uploaded_video = st.file_uploader("Upload Video", type=["mp4", "avi", "mov"])
            if uploaded_video is not None:
                video_source = f"temp.{uploaded_video.name.split('.')[-1]}"
                with open(os.path.join(UPLOAD_FOLDER, video_source), "wb") as f:
                    f.write(uploaded_video.read())
            else:
                st.write("Please upload a video file.")
                return

        conf = st.slider("Select Confidence Threshold", 0.1, 1.0, 0.5, 0.1)

        st.write(f"Video Processing ({video_source}) with Confidence: {conf}")
        display_video_detection(model, video_source, conf)

if __name__ == "__main__":
    model = model_yolo()
    main(model)
