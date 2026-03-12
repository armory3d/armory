#!/usr/bin/env python3
"""
生成蓝噪声纹理用于 SSSR
64x64 蓝噪声纹理，每帧旋转使用
"""

import numpy as np
from PIL import Image
import os

def generate_blue_noise(width=64, height=64):
    """
    使用 Mitchell's best-candidate 算法生成蓝噪声
    """
    # 初始化
    points = []
    
    # 第一个点随机
    points.append((np.random.rand() * width, np.random.rand() * height))
    
    # 生成剩余点
    num_points = width * height // 4  # 稀疏采样
    for _ in range(num_points - 1):
        best_candidate = None
        best_dist = 0
        
        # 生成 k 个候选点
        for _ in range(30):
            candidate = (np.random.rand() * width, np.random.rand() * height)
            
            # 计算到最近点的距离
            min_dist = min(
                np.sqrt((candidate[0] - p[0])**2 + (candidate[1] - p[1])**2)
                for p in points
            )
            
            if min_dist > best_dist:
                best_dist = min_dist
                best_candidate = candidate
        
        points.append(best_candidate)
    
    # 创建纹理
    texture = np.zeros((height, width), dtype=np.float32)
    
    # 高斯模糊每个点
    for x, y in points:
        xx, yy = np.meshgrid(np.arange(width), np.arange(height))
        dist = np.sqrt((xx - x)**2 + (yy - y)**2)
        texture += np.exp(-dist**2 / (2 * 3**2))
    
    # 归一化到 0-1
    texture = (texture - texture.min()) / (texture.max() - texture.min())
    
    return texture

def save_texture(texture, filepath):
    """保存为 PNG"""
    # 转换为 0-255
    img_array = (texture * 255).astype(np.uint8)
    
    # 创建 RGB 图像
    img_array_rgb = np.stack([img_array, img_array, img_array], axis=-1)
    img = Image.fromarray(img_array_rgb, 'RGB')
    img.save(filepath)
    print(f"Saved: {filepath}")

if __name__ == "__main__":
    output_dir = "armory/Assets/sssr"
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成主纹理
    texture = generate_blue_noise(64, 64)
    save_texture(texture, f"{output_dir}/blue_noise_64.png")
    
    # 生成多帧旋转版本 (可选)
    for i in range(4):
        # 旋转 90 度
        rotated = np.rot90(texture, k=i)
        save_texture(rotated, f"{output_dir}/blue_noise_64_rot{i}.png")
    
    print("✅ 蓝噪声纹理生成完成!")
