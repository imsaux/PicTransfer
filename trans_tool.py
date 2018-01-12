# coding=utf-8
import os.path
from tkinter import *
from tkinter.filedialog import *
from tkinter.ttk import *

class pic_base():
    def __init__(self):
        self.search_keys = []
        self.limitDate = ''
        self.src_dir = ''
        self.dst_dir = ''
        self.in_use = False
        self.stats = dict()

    def _filter(self, x):
        _x = str(x).upper()
        for key in self.search_keys:
            if key.upper() in x:
                return True
        if self.search_keys == '':
            return True
        return False

    def readIndex(self, filename, lst):
        try:
            _return = list()
            with open(filename, 'r') as f:
                for line in f.readlines():
                    # print(line)
                    _split = line.strip().split('\t')
                    if _split[0] != '0':
                        _kind = ''
                        # print(_split)
                        if _split[3][0] == 'K':
                            _kind = _split[3][:6]
                        if _split[3][0] in ('T', 'Q'):
                            _kind = _split[3][1:7]
                        if _split[3][0] == 'J':
                            _kind = _split[3][:4]

                        if self._filter(_kind) is True and _kind != '':
                            _return.append((_split[0], _kind))
        except:
            pass
        return _return

    def ui_init(self):
        m = Tk()
        m.title('车型图片提取工具')
        win_width = 500
        win_height = 300
        m.maxsize(width=win_width, height=win_height)
        m.minsize(width=win_width, height=win_height)

        lbSrcDirectory = Label(m, text='基准目录：')
        lbSrcDirectory.place(x=5, y=5)
        self.entSrc = Entry(m, width=50)
        self.entSrc.place(x=65, y=5)
        btnOpenSrcDirectory = Button(
            m, width=10, command=self.btn_open_src_directory, text='打开目录')
        btnOpenSrcDirectory.place(x=375, y=5)
        lbDstDirectory = Label(m, text='存放目录：')
        lbDstDirectory.place(x=5, y=40)
        self.entDst = Entry(m, width=50)
        self.entDst.place(x=65, y=40)
        btnOpenDstDirectory = Button(
            m, width=10, command=self.btn_open_dst_directory, text='打开目录')
        btnOpenDstDirectory.place(x=375, y=40)
        lbDate = Label(m, text='起止日期：')
        lbDate.place(x=5, y=75)
        self.entStartDate = Entry(m, width=15)
        self.entStartDate.place(x=65, y=75)
        Label(m, text=' <  日期  < ').place(x=165, y=75)
        self.entEndDate = Entry(m, width=15)
        self.entEndDate.place(x=255, y=75)
        lbSearchKey = Label(m, text='检索车型：')
        lbSearchKey.place(x=5, y=105)
        self.entSearchKey = Entry(m, width=50)
        self.entSearchKey.place(x=65, y=105)
        Label(m, text='检索多个用,分隔').place(x=375, y=105)
        Label(m, text='数量：').place(x=5, y=135)
        self.entMountLimit = Entry(m, width=15)
        self.entMountLimit.place(x=65, y=135)
        Label(m, text=' 0：不限').place(x=165, y=135)

        self.lbInfo = Label(m)
        self.lbInfo.place(x=5, y=165)

        btn_proc = Button(m, text='提取', width=10, command=self._do)
        btn_proc.place(x=265, y=195)
        btn_detail = Button(m, text='明细', width=10, command=self.showDetail)
        btn_detail.place(x=355, y=195)

        m.mainloop()

    def btn_open_src_directory(self):
        self.src_dir = os.path.normpath(askdirectory(
            initialdir=os.path.join(sys.path[0]), title='请选择源文件夹'))
        self.entSrc.insert(0, self.src_dir)

    def btn_open_dst_directory(self):
        self.dst_dir = os.path.normpath(askdirectory(
            initialdir=os.path.join(sys.path[0]), title='请选择存储文件夹'))
        self.entDst.insert(0, self.dst_dir)

    def showDetail(self):
        def _getLineName(name):
            return '202.202.202.%s' % (str(int(name)+1),)
        
        top = Toplevel(width=420, height=500)
        top.title('明细')
        _side_frame = Frame(top, width=420, height=30)
        _info_frame = Frame(top, width=420, height=570)
        _info_frame.place(x=0, y=5)
        tree = Treeview(_info_frame, height=20)
        tree["columns"]=("left","right")
        tree.column("left", width=100 )
        tree.column("right", width=100)
        tree.heading("left", text="左侧")
        tree.heading("right", text="右侧")
        lst = sorted(list(self.stats.keys()), key=lambda s:s[0])
        for _keys in lst:
            tree.insert('', 'end', text=_keys, values=(
                self.getFilesCount(os.path.join(self.dst_dir, _keys), isLeft=True),
                self.getFilesCount(os.path.join(self.dst_dir, _keys), isLeft=False)))
        tree.pack(side=LEFT)
        trinfo = Scrollbar(_info_frame, orient=VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=trinfo.set)
        trinfo.pack(side=RIGHT, fill=Y)
        def _close():
            top.destroy()
        btnClose = Button(top, text='确定', command=_close, width=10)
        btnClose.place(x=230, y=465)

    

    def _do(self):
        import threading
        if self.in_use is True: return
        self.in_use = True
        _t = threading.Thread(target=self.btn_Process2)
        _t.setDaemon(True)
        _t.start()

    def btn_Process(self):
        self.src_dir = self.entSrc.get()
        self.dst_dir = self.entDst.get()
        self.startDate = self.entStartDate.get() if self.entStartDate.get() != '' else '00010101000000'
        self.endDate = self.entEndDate.get() if self.entEndDate.get() != '' else '99999999999999'
        self.search_keys = self.entSearchKey.get().split(',') if self.entSearchKey.get() != '' else ''
        self.amountlimit = int(self.entMountLimit.get()) if self.entMountLimit.get() != '' else 0
        if self.src_dir == '' or self.dst_dir  == '': return

        for x, y, z in os.walk(self.src_dir):
            
            if len(y) > 0 and len(z) > 0:
                _s = x.split('\\')
                if not self.startDate < _s[len(_s) - 1] < self.endDate:
                    continue
                if 'index.txt' not in z:
                    continue
                else:
                    # 1> 处理 index.txt 获取车型及顺位
                    # 2> 按相应规则拷贝并重命名图片文件
                    self.lbInfo.config(text='Searching ...')
                    valid = self.readIndex(os.path.join(
                        x, 'index.txt'), self.search_keys)
                    self.lbInfo.config(text='Copying ...')
                    for idx, kd in valid:
                        print(idx, ' > ', kd)
                        self.stats[kd] = list()
                        srcName_L = os.path.join(
                            x, 'L' + str(idx).zfill(3) + '_' + str(idx) + '.jpg')
                        if os.path.exists(srcName_L): 
                            self.stats[kd].append('√')
                        else:
                            self.stats[kd].append('x')
                        srcName_R = os.path.join(
                            x, 'R' + str(idx).zfill(3) + '_' + str(idx) + '.jpg')
                        if os.path.exists(srcName_R): 
                            self.stats[kd].append('√')
                        else:
                            self.stats[kd].append('x')
                        dstName_L = '%s_%s_%s_L%s_%s.jpg' % (
                            kd.strip(), _s[len(_s) - 1], _s[len(_s) - 2], str(idx).zfill(3), str(idx))
                        dstName_R = '%s_%s_%s_R%s_%s.jpg' % (
                            kd.strip(), _s[len(_s) - 1], _s[len(_s) - 2], str(idx).zfill(3), str(idx))
                        if os.path.exists(os.path.join(self.dst_dir, kd.strip())) is False:
                            os.mkdir(os.path.join(self.dst_dir, kd.strip()))
                        try:

                            if not (self.amountlimit > 0 and self.getFilesCount(os.path.join(self.dst_dir, kd.strip()), isLeft=True) == self.amountlimit):
                                self.lbInfo.config(
                                    text=srcName_L + ' >>> ' + os.path.join(self.dst_dir, kd.strip(), dstName_L))
                                __import__('shutil').copy(srcName_L, os.path.join(
                                    self.dst_dir, kd.strip(), dstName_L))
                            if not (self.amountlimit > 0 and self.getFilesCount(os.path.join(self.dst_dir, kd.strip()), isLeft=False) == self.amountlimit):
                                self.lbInfo.config(
                                    text=srcName_R + ' >>> ' + os.path.join(self.dst_dir, kd.strip(), dstName_R))
                                __import__('shutil').copy(srcName_R, os.path.join(
                                    self.dst_dir, kd.strip(), dstName_R))
                        except FileNotFoundError:
                            pass
        self.lbInfo.config(text='完成')
        self.in_use = False

    def btn_Process2(self):
        self.src_dir = self.entSrc.get()
        self.dst_dir = self.entDst.get()
        self.startDate = self.entStartDate.get() if self.entStartDate.get() != '' else '00010101000000'
        self.endDate = self.entEndDate.get() if self.entEndDate.get() != '' else '99999999999999'
        self.search_keys = self.entSearchKey.get().split(',') if self.entSearchKey.get() != '' else ''
        self.amountlimit = int(self.entMountLimit.get()) if self.entMountLimit.get() != '' else 0
        if self.src_dir == '' or self.dst_dir  == '': return

        def _f(f):
            return self.startDate <= f <= self.endDate and f.isdigit()
        _tmp = list()
        for x, y, z in os.walk(self.src_dir):
            _tmp = [os.path.join(x, _y) for _y in list(filter(_f, y))]
            break
        print(_tmp)
        for _path in _tmp:
            for x, y, z in os.walk(_path):
                _s = x.split('\\')
                if 'index.txt' not in z:
                    continue
                else:
                    self.lbInfo.config(text='Searching ...')
                    valid = self.readIndex(os.path.join(
                        x, 'index.txt'), self.search_keys)
                    self.lbInfo.config(text='Copying ...')
                    for idx, kd in valid:
                        print(idx, ' > ', kd)
                        self.stats[kd] = list()
                        srcName_L = os.path.join(
                            x, 'L' + str(idx).zfill(3) + '_' + str(idx) + '.jpg')
                        if os.path.exists(srcName_L): 
                            self.stats[kd].append('√')
                        else:
                            self.stats[kd].append('x')
                        srcName_R = os.path.join(
                            x, 'R' + str(idx).zfill(3) + '_' + str(idx) + '.jpg')
                        if os.path.exists(srcName_R): 
                            self.stats[kd].append('√')
                        else:
                            self.stats[kd].append('x')
                        dstName_L = '%s_%s_%s_L%s_%s.jpg' % (
                            kd.strip(), _s[len(_s) - 1], _s[len(_s) - 2], str(idx).zfill(3), str(idx))
                        dstName_R = '%s_%s_%s_R%s_%s.jpg' % (
                            kd.strip(), _s[len(_s) - 1], _s[len(_s) - 2], str(idx).zfill(3), str(idx))
                        if os.path.exists(os.path.join(self.dst_dir, kd.strip())) is False:
                            os.mkdir(os.path.join(self.dst_dir, kd.strip()))
                        try:

                            if not (self.amountlimit > 0 and self.getFilesCount(os.path.join(self.dst_dir, kd.strip()), isLeft=True) == self.amountlimit):
                                self.lbInfo.config(
                                    text=srcName_L + ' >>> ' + os.path.join(self.dst_dir, kd.strip(), dstName_L))
                                __import__('shutil').copy(srcName_L, os.path.join(
                                    self.dst_dir, kd.strip(), dstName_L))
                            if not (self.amountlimit > 0 and self.getFilesCount(os.path.join(self.dst_dir, kd.strip()), isLeft=False) == self.amountlimit):
                                self.lbInfo.config(
                                    text=srcName_R + ' >>> ' + os.path.join(self.dst_dir, kd.strip(), dstName_R))
                                __import__('shutil').copy(srcName_R, os.path.join(
                                    self.dst_dir, kd.strip(), dstName_R))
                        except FileNotFoundError:
                            pass

        self.lbInfo.config(text='完成')
        self.in_use = False



    def getFilesCount(self, dir, isLeft=True):
        _count = 0
        for x,y,z in os.walk(dir.strip()):
            for _file in z:
                if isLeft:
                    if _file.split('_')[3][0] == 'L': 
                        _count += 1
                else:
                    if _file.split('_')[3][0] == 'R': 
                        _count += 1
            break
        return _count


def start():
    p = pic_base()
    p.ui_init()
    

if __name__ == '__main__':
    start()
