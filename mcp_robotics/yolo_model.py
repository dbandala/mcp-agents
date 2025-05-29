#!/usr/bin/env python3
import argparse
import cv2
from ultralytics import YOLO

def run_detection(model_name: str, image_path: str, device: str = 'cpu'):
    # Load the model
    model = YOLO(model_name)

    # Inference
    results = model.predict(source=image_path, device=device, imgsz=640, conf=0.4, verbose=False)
    # Results[0] holds detections for the first (and here only) image

    # Draw boxes on image
    img = cv2.imread(image_path)
    for r in results:
        boxes = r.boxes
        for box in boxes:
            coords = box.xyxy[0].cpu().numpy().astype(int)
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            label = f"{model.names[cls]}:{conf:.2f}"
            cv2.rectangle(img, tuple(coords[:2]), tuple(coords[2:]), (255,0,0), 2)
            cv2.putText(img, label, (coords[0], coords[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)

    # Save image
    cv2.imwrite("detection.png", img)

    # Show result
    # win = "YOLO11n Detection"
    # cv2.imshow(win, img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

def export_model(model_name: str, fmt: str = 'onnx', dynamic: bool = True, device: str = 'cuda'):
    model = YOLO(model_name)
    model.export(format=fmt, dynamic=dynamic, device=device)
    print(f"Exported {model_name} as {fmt}")

def main():
    parser = argparse.ArgumentParser(description="YOLO11n Fast Inference")
    parser.add_argument("image", help="Path to the input image")
    parser.add_argument("--model", default="yolo11n.pt", help="Model name or .pt file (e.g. yolo11n.pt)")
    parser.add_argument("--device", default="cpu", help="Inference device: cpu or cuda")
    parser.add_argument("--export", choices=["onnx","tensorrt","torch"], help="Export model format")
    args = parser.parse_args()

    if args.export:
        export_model(args.model, fmt=args.export, device=args.device)
    else:
        run_detection(args.model, args.image, device=args.device)

if __name__ == "__main__":
    main()
