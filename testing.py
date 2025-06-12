from ultralytics import YOLO
import cv2

model = YOLO('models/my_model.pt')  

image_path = 'test_image.jpg'
results = model(image_path)

for r in results:
    annotated_frame = r.plot()
    cv2.imshow("Hasil Deteksi YOLOv8n", annotated_frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
