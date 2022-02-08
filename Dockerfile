######### FROM nvcr.io/nvidia/pytorch:21.09-py3
######### WORKDIR /

######### RUN pip install jupyter seaborn thop pyyaml==5.4.1 onnx onnxruntime pycuda

#-------------------------------------------------------------------------------------------
FROM nvcr.io/nvidia/pytorch:21.09-py3

WORKDIR /workspace/service

COPY requirements.txt /usr/src/requirements.txt

RUN pip install --no-cache-dir -r /usr/src/requirements.txt

COPY ./service /workspace/service

# Use the ping endpoint as a healthcheck,
# so Docker knows if the API is still running ok or needs to be restarted
############################HEALTHCHECK --interval=21s --timeout=3s --start-period=10s CMD curl --fail http://localhost:8080/ping || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]


#RUN pip3 install https://mirror.sjtu.edu.cn/pytorch-wheels/cu113/torch-1.10.0+cu113-cp38-cp38-linux_x86_64.whl
#RUN pip3 install https://mirror.sjtu.edu.cn/pytorch-wheels/cu113/torchvision-0.11.0+cu113-cp38-cp38-linux_x86_64.whl
#RUN pip3 install torch-tensorrt -f https://github.com/NVIDIA/Torch-TensorRT/releases/tag/v1.1.0

#EXPOSE 8888

#docker run --gpus all --ipc=host --ulimit memlock=-1 
#--ulimit stack=67108864 -it -p "8888:8888" -v /home/neuralearn/pytorch-nvidia/notebooks:/workspace my-nvidia-container:latest