#import pygame;  
import socket;  
import threading;  
#from PIL import Image;  
import struct;  
import os;  
import time;  
import json
import numpy
import cv2

class webCamConnect:
    def __init__(self, resolution = [640,480], remoteAddress = ("115.216.215.130", 7999), windowName = "video"):
        self.remoteAddress = remoteAddress
        self.resolution = resolution
        self.name = windowName
        self.mutex = threading.Lock()
        self.interval=0
        self.path=os.getcwd()
        self.img_quality = 15
        self.src=911+self.img_quality
        
    def _setSocket(self):  
        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        #self.socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);  
  
    def connect(self):  
        self._setSocket();  
        self.socket.connect(self.remoteAddress);  
      
  
    def _processImage(self):
        self.socket.send(struct.pack("lhh",self.src,self.resolution[0],self.resolution[1]));
        while(1):
            info = struct.unpack("lhh",self.socket.recv(8));
            bufSize = info[0];
            if bufSize:
                try:  
                    self.mutex.acquire();
                    self.buf=b''
                    tempBuf=self.buf;
                    while(bufSize):                 #循环读取到一张图片的长度  
                        tempBuf = self.socket.recv(bufSize);
                        bufSize -= len(tempBuf);
                        self.buf += tempBuf;
                    #print("收到数据")
                    #self.buf = zlib.decompress(self.buf)
                    #print(len(self.buf))
                    data = numpy.fromstring(self.buf,dtype='uint8')
                    #print("转换data")
                    self.image=cv2.imdecode(data,1)
                    #blur=cv2.GaussianBlur(self.image,(3,3),0)
                    #cv2.imshow("blur",blur)
                    #print(len(self.buf))
                    #print("转换图像")
                    cv2.imshow(self.name,self.image)
                except:
                    print("接收失败")
                    pass;  
                finally:
                    self.mutex.release();
                    if cv2.waitKey(10) == 27:
                        self.socket.close()
                        cv2.destroyAllWindows()
                        print("放弃连接")
                        break
  
    def getData(self, interval):    
        showThread=threading.Thread(target=self._processImage);  
        showThread.start();  
        if interval != 0:   # 非0则启动保存截图到本地的功能  
            saveThread=threading.Thread(target=self._savePicToLocal,args = (interval, ));  
            saveThread.setDaemon(1);  
            saveThread.start();  
  
    def setWindowName(self, name):  
        self.name = name;  
  
    def setRemoteAddress(remoteAddress):  
        self.remoteAddress = remoteAddress;  
  
    def _savePicToLocal(self, interval):  
        while(1):  
            try:  
                self.mutex.acquire();  
                path=os.getcwd() + "\\" + "savePic";  
                if not os.path.exists(path):  
                    os.mkdir(path);
                cv2.imwrite(path + "\\" + time.strftime("%Y%m%d-%H%M%S", time.localtime(time.time())) + ".jpg",self.image)
            except:  
                pass;  
            finally:  
                self.mutex.release();  
                time.sleep(interval);

    def check_config(self):
        path=os.getcwd()
        path = path+'\\'+"client_init.jason"

        if os.path.isfile(path) is False:
            with open(path, 'w') as json_file:
                data = {
                    "w":self.resolution[0],
                    "h":self.resolution[1],
                    "ip":self.remoteAddress[0],
                    "port":self.remoteAddress[1],
                    "save_flag":self.interval,
                    "quality":self.img_quality,
                }
                json_file.write(json.dumps(data))
                print("初始化配置...")
        else:
            with open(path, 'r') as json_file:
                data = json.load(json_file)
                self.resolution[0] = int(data["w"])
                self.resolution[1] = int(data["h"])
                self.remoteAddress = (data["ip"], int(data["port"]))
                self.interval = data["save_flag"]
                self.img_quality = data["quality"]
            print("读取配置...")

def main():
    print("创建连接...")
    cam = webCamConnect();
    cam.check_config()
    print("像素为:%d * %d"%(cam.resolution[0],cam.resolution[1]))
    print("目标ip为%s:%d"%(cam.remoteAddress[0],cam.remoteAddress[1]))
    cam.connect();  
    cam.getData(cam.interval);  
if __name__ == "__main__":  
    main();  
