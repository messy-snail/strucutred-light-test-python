from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic

import os
import cv2

############### 이게 있어야 rs와 QFileDialog conflict 안남
import sys
sys.coinit_flags = 2
import pythoncom

import camera_manager
import pattern_manager
import structured_light_system
import common as com

from _thread import*

form_class = uic.loadUiType("mainwindow.ui")[0]

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        if not os.path.exists('captured'):
            os.mkdir('captured')

        com.TE_LOG = self.TE_LOG
        com.LABEL_ORIGINAL = self.LB_CAMERA_VIEW
        com.LABEL_TARGET = self.LB_TARGET_VIEW

        self.cm = camera_manager.camera_manager()
        self.sls = structured_light_system.structured_light_system()

        self.total_imgs = []
        self.current_index = 0
        self.total_index = 0

        ## Slots
        self.BTN_CAM_OPEN.clicked.connect(self.btn_cam_oepn_clicked)
        self.BTN_GENERATE_PATTERN.clicked.connect(self.btn_generate_pattern_clicked)
        self.BTN_AUTO_CAPTURE.clicked.connect(self.btn_auto_capture_clicked)
        self.BTN_MANUAL_CAPTURE.clicked.connect(self.btn_manual_capture_clicked)
        self.BTN_EXTRACT_STRIPE.clicked.connect(self.btn_extract_stripe_clicked)
        self.BTN_EXIT.clicked.connect(self.btn_exit_clicked)
        self.BTN_PREV_IMAGE.clicked.connect(self.btn_prev_image_clicked)
        self.BTN_NEXT_IMAGE.clicked.connect(self.btn_next_image_clicked)

        self.BTN_OPEN_CAPTURE_IMAGE.clicked.connect(self.btn_open_capture_image_clicked)
        self.BTN_OPEN_EXTRACTED_IMAGE.clicked.connect(self.btn_open_extracted_image_clicked)
        self.BTN_OPEN_GRAY_CODE.clicked.connect(self.btn_open_gray_code_clicked)
        self.BTN_OPEN_BINARY_CODE.clicked.connect(self.btn_open_binary_code_clicked)

        self.BTN_CALIBRATION.clicked.connect(self.btn_calibration_clicked)

        self.RB_GRAY_CODE.clicked.connect(self.radio_clicked)
        self.RB_BINARY_CODE.clicked.connect(self.radio_clicked)

        # 전체화면
        self.shortcutFull = QShortcut(self)
        self.shortcutFull.setKey(QKeySequence('F11'))
        self.shortcutFull.setContext(Qt.ApplicationShortcut)
        self.shortcutFull.activated.connect(self.toggle_full_screen)

        # 종료
        self.shortcutQuit = QShortcut(self)
        self.shortcutQuit.setKey(QKeySequence('Ctrl+Q'))
        self.shortcutQuit.setContext(Qt.ApplicationShortcut)
        self.shortcutQuit.activated.connect(self.close)

        self.btn_cam_oepn_clicked()
        self.toggle_full_screen()


    ###소멸자
    def __del__(self):
        pass

    #풀스크린
    def toggle_full_screen(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()



    def btn_cam_oepn_clicked(self):
        ret = self.cm.cam_open()
        if ret ==False:
            com.log.print_log("카메라 연결 상태를 확인하세요", self.TE_LOG, "red")
            return
        com.log.print_log("카메라 열기", self.TE_LOG)

    def btn_generate_pattern_clicked(self):
        com.PATTERN_WIDTH =  int(self.LE_PATTERN_WIDTH.text())
        com.PATTERN_HEIGHT =  int(self.LE_PATTERN_HEIGHT.text())
        com.log.print_log(f'가로: {com.PATTERN_WIDTH}, 세로: {com.PATTERN_HEIGHT}의 패턴을 생성합니다', com.TE_LOG)
        com.pm.start()

        ret = start_new_thread(com.pm.label_thread, (0,))
        # com.log.print_log('생성을 완료했습니다', com.TE_LOG)

        # thread = threading.Thread(target=self.pm.label_thread, args=(1, ))
        # thread.start()
        # thread.join()

    def btn_auto_capture_clicked(self):
        if self.cm.THREAD_RUN == True:
            self.cm.CAPTURE_FLAG =True

    def btn_manual_capture_clicked(self):
        date = QDateTime.currentDateTime().toString("yy-MM-dd-hh-mm-ss")
        if not os.path.exists('manual'):
            os.mkdir('manual')
        cv2.imwrite(f'manual/{date}.png', self.cm.cv_image1)
        com.log.print_log('캡쳐되었습니다', self.TE_LOG)

    def btn_extract_stripe_clicked(self):
        self.sls.line_extarct()
        pass

    def btn_exit_clicked(self):
        self.close()

    def btn_prev_image_clicked(self):
        self.current_index-=1
        if self.current_index<0:
            self.current_index = 0          
        self.change_view()

    def btn_next_image_clicked(self):
        self.current_index+=1
        if self.current_index>=self.total_index:
            self.current_index = self.total_index
        self.change_view()

    def change_view(self):
        self.LB_CURRENT_INDEX.setNum(self.current_index)
        com.lm.view_original_image(com.LABEL_TARGET, self.total_imgs[self.current_index], True)

    def btn_open_capture_image_clicked(self):
        self.total_imgs = []
        self.current_index = 0
        left_imgs, right_imgs, white_imgs, black_imgs =com.read_captured_imgs()
        self.total_imgs = left_imgs + right_imgs + white_imgs + black_imgs
        self.total_index = len(self.total_imgs)-1
        self.LB_TOTAL_INDEX.setNum(self.total_index)
        self.change_view()

    def btn_open_extracted_image_clicked(self):
        self.total_imgs = []
        self.total_imgs = com.read_extracted_imgs()
        self.total_index = len(self.total_imgs)-1
        self.LB_TOTAL_INDEX.setNum(self.total_index)
        self.change_view()

    def btn_open_gray_code_clicked(self):
        pass
    def btn_open_binary_code_clicked(self):
        pass

    def btn_calibration_clicked(self):
        pass

    def radio_clicked(self):
        if self.RB_GRAY_CODE.isChecked():
            com.pm.OPTION = 'g'
            com.log.print_log('그레이 코드', com.TE_LOG, 'yellow')
        elif self.RB_BINARY_CODE.isChecked():
            com.pm.OPTION = 'b'
            com.log.print_log('바이너리 코드', com.TE_LOG, 'yellow')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
    myWindow = None





