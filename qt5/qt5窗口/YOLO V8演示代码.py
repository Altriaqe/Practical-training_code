import torch
import cv2
import numpy as np
from ultralytics import YOLO
import matplotlib.pyplot as plt
from PIL import Image
import requests
from io import BytesIO

class YOLOv8Demo:
    """YOLOv8教学演示类"""
    
    #初始化YOLOv8模型,模型名称（yolov8n.pt
    def __init__(self, model_name='best.pt'):
        
        print(f"正在加载模型: {model_name}")
        self.model = YOLO(model_name)
        print("模型加载成功！")
        
        # COCO数据集类别名称（YOLOv8默认使用的80个类别）
        self.classes = [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat',
            'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat',
            'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack',
            'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
            'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
            'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
            'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair',
            'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
            'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator',
            'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
        ]
        
    def detect_image(self, image_path, conf_threshold=0.25, save_result=True):
        """
        对单张图片进行目标检测
        
        参数:
            image_path: 图片路径或URL
            conf_threshold: 置信度阈值
            save_result: 是否保存结果图片
        """
        # 读取图片
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 进行推理
        results = self.model(image, conf=conf_threshold)[0]
        
        # 获取检测结果
        boxes = results.boxes
        if boxes is not None:
            print(f"检测到 {len(boxes)} 个物体")
            
            # 绘制检测结果
            plotted_image = results.plot()
            
            # 打印检测信息
            for box in boxes:
                # 获取边界框坐标
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                # 获取置信度
                confidence = float(box.conf[0])
                # 获取类别
                class_id = int(box.cls[0])
                class_name = self.classes[class_id]
                
                print(f"物体: {class_name}, 置信度: {confidence:.3f}, 位置: [{int(x1)}, {int(y1)}, {int(x2)}, {int(y2)}]")
            
            # 显示结果
            plt.figure(figsize=(12, 8))
            plt.imshow(plotted_image)
            plt.axis('off')
            plt.title(f'YOLOv8 目标检测结果 (置信度阈值: {conf_threshold})')
            plt.show()
            
            # 保存结果
            if save_result:
                result_path = 'detection_result.jpg'
                Image.fromarray(plotted_image).save(result_path)
                print(f"结果已保存到: {result_path}")
                
            return results
        else:
            print("未检测到任何物体")
            return None
    
    def get_model_info(self):
        """获取模型信息"""
        print("\n=== 模型信息 ===")
        print(f"模型类型: {self.model.__class__.__name__}")
        print(f"模型路径: {self.model.model.model_name if hasattr(self.model.model, 'model_name') else '默认模型'}")
        print(f"类别数量: {len(self.classes)}")
        print(f"可用类别: {', '.join(self.classes[:10])}...")  # 显示前10个类别
        
    

# 主函数
def main():
    """主函数，演示各种功能"""
    print("=== YOLOv8 目标检测教学演示 ===")
    
    # 1. 初始化模型
    demo = YOLOv8Demo('yolov8n.pt') 
    
    # 2. 显示模型信息
    demo.get_model_info()
    
    # 3. 图片检测演示
    print("\n=== 图片检测演示 ===")
    # 使用在线图片进行演示
    demo.detect_image(r"qt5\qt5窗口\images\lLD9016.jpg", conf_threshold=0.3)

if __name__ == "__main__":

    main()
    