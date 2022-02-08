# -*- coding: UTF-8 -*-
import argparse
import time
from pathlib import Path
from tracemalloc import start
#from turtle import width

import numpy as np
import cv2
import torch
import torch.backends.cudnn as cudnn
from numpy import random
import copy
#import torch_tensorrt

from core.logic.yolov5face.models.experimental import attempt_load
from core.logic.yolov5face.utils.datasets import letterbox
from core.logic.yolov5face.utils.general import check_img_size, non_max_suppression_face, apply_classifier, scale_coords, xyxy2xywh, \
    strip_optimizer, set_logging, increment_path
from core.logic.yolov5face.utils.plots import plot_one_box
from core.logic.yolov5face.utils.torch_utils import select_device, load_classifier, time_synchronized

import main

def load_model(weights, device):
    model = attempt_load(weights, map_location=device)  # load FP32 model
    return model


def scale_coords_landmarks(img1_shape, coords, img0_shape, ratio_pad=None):
    # Rescale coords (xyxy) from img1_shape to img0_shape
    if ratio_pad is None:  # calculate from img0_shape
        gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])  # gain  = old / new
        pad = (img1_shape[1] - img0_shape[1] * gain) / 2, (img1_shape[0] - img0_shape[0] * gain) / 2  # wh padding
    else:
        gain = ratio_pad[0][0]
        pad = ratio_pad[1]

    coords[:, [0, 2, 4, 6, 8]] -= pad[0]  # x padding
    coords[:, [1, 3, 5, 7, 9]] -= pad[1]  # y padding
    coords[:, :10] /= gain
    #clip_coords(coords, img0_shape)
    coords[:, 0].clamp_(0, img0_shape[1])  # x1
    coords[:, 1].clamp_(0, img0_shape[0])  # y1
    coords[:, 2].clamp_(0, img0_shape[1])  # x2
    coords[:, 3].clamp_(0, img0_shape[0])  # y2
    coords[:, 4].clamp_(0, img0_shape[1])  # x3
    coords[:, 5].clamp_(0, img0_shape[0])  # y3
    coords[:, 6].clamp_(0, img0_shape[1])  # x4
    coords[:, 7].clamp_(0, img0_shape[0])  # y4
    coords[:, 8].clamp_(0, img0_shape[1])  # x5
    coords[:, 9].clamp_(0, img0_shape[0])  # y5
    return coords

def show_results(img, xywh, conf, landmarks, class_num):
    h,w,c = img.shape
    tl = 1 or round(0.002 * (h + w) / 2) + 1  # line/font thickness
    x1 = int(xywh[0] * w - 0.5 * xywh[2] * w)
    y1 = int(xywh[1] * h - 0.5 * xywh[3] * h)
    x2 = int(xywh[0] * w + 0.5 * xywh[2] * w)
    y2 = int(xywh[1] * h + 0.5 * xywh[3] * h)
    cv2.rectangle(img, (x1,y1), (x2, y2), (0,255,0), thickness=tl, lineType=cv2.LINE_AA)

    clors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(0,255,255)]

    for i in range(5):
        point_x = int(landmarks[2 * i] * w)
        point_y = int(landmarks[2 * i + 1] * h)
        cv2.circle(img, (point_x, point_y), tl+1, clors[i], -1)

    tf = max(tl - 1, 1)  # font thickness
    label = str(conf)[:5]
    cv2.putText(img, label, (x1, y1 - 2), 0, tl / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)
    return img


# def detect_one(orgimg, device):
#     # Load model
#     img_size = 640
#     conf_thres = 0.3
#     iou_thres = 0.5




# def detect_one(orgimg, device):
#     # Load model
#     img_size = 640
#     conf_thres = 0.3
#     iou_thres = 0.5

#     img0 = copy.deepcopy(orgimg)
#     assert orgimg is not None, 'Image Not Found '
#     h0, w0 = orgimg.shape[:2]  # orig hw
#     r = img_size / max(h0, w0)  # resize image to img_size
#     if r != 1:  # always resize down, only resize up if training with augmentation
#         interp = cv2.INTER_AREA if r < 1  else cv2.INTER_LINEAR
#         img0 = cv2.resize(img0, (int(w0 * r), int(h0 * r)), interpolation=interp)

#     imgsz = img_size# check_img_size(img_size, s=model.stride.max())  # check img_size
#     print("firsttttttttttttttttttttttttt", img0.shape)
#     img = letterbox(img0, new_shape=imgsz)[0]
#     print("secondssssssssssssssssss", img.shape)
#     img = cv2.resize(orgimg, (640,640))
#     # Convert
#     img = img[:, :, ::-1].transpose(2, 0, 1).copy()  # BGR to RGB, to 3x416x416

#     # Run inference
#     t0 = time.time()

#     #img = torch.from_numpy(img).to(device)
#     img = img.astype(np.float32)
#     #img = img.float()  # uint8 to fp16/32
#     img /= 255.0  # 0 - 255 to 0.0 - 1.0
#     print("+++++++++++++++imgshape", img.shape)

#     img = np.expand_dims(img, 0)

#     # Inference
#     t1 = time_synchronized()


#     import onnxruntime as ort

#     ort_session = ort.InferenceSession("core/logic/yolov5face/weights/yolov5n-face.onnx")
    
#     outputs = ort_session.run(
#         None,
#         {"input": img},
#     )
#     print(outputs[0].shape)

#     #pred = model(img)[0]
#     # Apply NMS
#     pred = non_max_suppression_face(torch.from_numpy(outputs[0]), conf_thres, iou_thres)
#     print(pred[0].shape)
#     for i, det in enumerate(pred):  # detections per image
#         gn = torch.tensor(orgimg.shape)[[1, 0, 1, 0]].to(device)  # normalization gain whwh
#         gn_lks = torch.tensor(orgimg.shape)[[1, 0, 1, 0, 1, 0, 1, 0, 1, 0]].to(device)  # normalization gain landmarks
#         xywh_list = []
#         conf_list = []
#         if len(det):
#             # Rescale boxes from img_size to im0 size
#             det[:, :4] = scale_coords(img.shape[2:], det[:, :4], orgimg.shape).round()

#             # Print results
#             for c in det[:, -1].unique():
#                 n = (det[:, -1] == c).sum()  # detections per class

#             det[:, 5:15] = scale_coords_landmarks(img.shape[2:], det[:, 5:15], orgimg.shape).round()

#             for j in range(det.size()[0]):

#                 print(det[j, :4].get_device())
#                 print(det[j, :4].view(1,4).get_device())
#                 print(gn.get_device())
#                 print(xyxy2xywh(det[j, :4].view(1, 4)).get_device())

#                 xywh = (xyxy2xywh(det[j, :4].view(1, 4)) / gn).view(-1).tolist()
#                 im_width, im_height = orgimg.shape[1], orgimg.shape[0]
#                 xywh_list.append([xywh[0]*im_width - xywh[2]*im_width/2,xywh[1]*im_height - xywh[3]*im_height/2,xywh[0]*im_width + xywh[2]*im_width/2,
#                     xywh[1]*im_height + xywh[3]*im_height/2])

#                 conf = det[j, 4].cpu().numpy()
#                 conf_list.append(conf.item())
#                 landmarks = (det[j, 5:15].view(1, 10) / gn_lks).view(-1).tolist()
#                 class_num = det[j, 15].cpu().numpy()
#                 orgimg = show_results(orgimg, xywh, conf, landmarks, class_num)
    
#     cv2.imwrite('result.jpg', orgimg)
    
#     return {"xywh_list":xywh_list, "conf_list":conf_list}

def img_process(orgimg,long_side=640,stride_max=32):
    
    img0 = copy.deepcopy(orgimg)
    h0, w0 = orgimg.shape[:2]  # orig hw
    r = long_side/ max(h0, w0)  # resize image to img_size
    if r != 1:  # always resize down, only resize up if training with augmentation
        interp = cv2.INTER_AREA if r < 1 else cv2.INTER_LINEAR
        img0 = cv2.resize(img0, (int(w0 * r), int(h0 * r)), interpolation=interp)

    imgsz = check_img_size(long_side, s=stride_max)  # check img_size

    img = letterbox(img0, new_shape=imgsz,auto=False)[0] # auto True最小矩形   False固定尺度
    # Convert
    img = img[:, :, ::-1].transpose(2, 0, 1).copy()  # BGR to RGB, to 3x416x416
    img = torch.from_numpy(img)
    img = img.float()  # uint8 to fp16/32
    img /= 255.0  # 0 - 255 to 0.0 - 1.0
    if img.ndimension() == 3:
        img = img.unsqueeze(0)
    return img,orgimg
def detect_one_trt(orgimg, device):
    # Load model
    img_size = 640
    conf_thres = 0.3
    iou_thres = 0.5
    

    img,orgimg=img_process(orgimg)
    print("Start timing ...")
    timings = []
    nruns = 1
    
    for i in range(nruns):

        start_time = time.time()

        pred=main.model_trt(img.numpy()).reshape([1,25200,16]) # forward





        print("the prediction is ", pred)
        #model.destroy()

        # Apply NMS
        pred = non_max_suppression_face(torch.from_numpy(pred), conf_thres=0.3, iou_thres=0.5)



        for i, det in enumerate(pred):  # detections per image
            gn = torch.tensor(orgimg.shape)[[1, 0, 1, 0]]#.to(device)  # normalization gain whwh
            gn_lks = torch.tensor(orgimg.shape)[[1, 0, 1, 0, 1, 0, 1, 0, 1, 0]]#.to(device)  # normalization gain landmarks
            xywh_list = []
            conf_list = []
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], orgimg.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class

                det[:, 5:15] = scale_coords_landmarks(img.shape[2:], det[:, 5:15], orgimg.shape).round()

                for j in range(det.size()[0]):

                    print(det[j, :4].get_device())
                    print(gn.get_device())
                    print(xyxy2xywh(det[j, :4].view(1, 4)).get_device())

                    xywh = (xyxy2xywh(det[j, :4].view(1, 4)) / gn).view(-1).tolist()
                    im_width, im_height = orgimg.shape[1], orgimg.shape[0]
                    xywh_list.append([xywh[0]*im_width - xywh[2]*im_width/2,xywh[1]*im_height - xywh[3]*im_height/2,xywh[0]*im_width + xywh[2]*im_width/2,
                        xywh[1]*im_height + xywh[3]*im_height/2])

                    conf = det[j, 4].cpu().numpy()
                    conf_list.append(conf.item())
                    landmarks = (det[j, 5:15].view(1, 10) / gn_lks).view(-1).tolist()
                    class_num = det[j, 15].cpu().numpy()
                    orgimg = show_results(orgimg, xywh, conf, landmarks, class_num)
        
        cv2.imwrite('result.jpg', orgimg)




        
        end_time = time.time()
        timings.append(end_time - start_time)
        if(i%100==0):
            print(i)
        
    print("Average speed", np.mean(timings))
    print("Total time", np.sum(timings))

    
    return {"xywh_list":xywh_list, "conf_list":conf_list}
