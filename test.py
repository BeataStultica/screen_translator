import threading
from paddleocr import PaddleOCR
import time
from PIL import Image, ImageTk, ImageDraw, ImageGrab, ImageFont
import tkinter, win32api, win32con, pywintypes
import pyWinhook
import pythoncom
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pyperclip

ocr = PaddleOCR(use_angle_cls=True, lang='en')
a = 0
next_img = 0
coordinate = [1, 1, 1, 1]

chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument('user-data-dir=C:\\Users\\dimon\\AppData\\Local\\Google\\Chrome\\User Data')
browser = webdriver.Chrome(chrome_options=chrome_options) 
browser.get('https://www.deepl.com/translator#en/ru/')
def deeptr(text):
    br = browser.find_element('xpath','//textarea[@dl-test="translator-source-input"]')
    br.clear()
    pyperclip.copy(text)
    #time.sleep(5)
    br.send_keys(Keys.CONTROL + "v")
    c = text.count('999909')
    count = 0
    while True:

        time.sleep(0.1)
        b = browser.find_element('id', 'target-dummydiv')
        res = b.get_attribute('innerHTML')
        if res.count('999909') >= c:
            pyperclip.copy(text)
            return res.split('999909')#replace('999909', '')
        print(res.count('999909'))
        print(c)
def output(scale=2, fontsize = 15):
    global next_img 

    root = tkinter.Tk()
    img = Image.new('RGBA', (100, 100), (255, 0, 0, 0))
    test = ImageTk.PhotoImage(img)
    label = tkinter.Label(image=test, bg='white')
    label.master.overrideredirect(True)
    label.master.geometry("+250+250")
    label.master.lift()
    label.master.wm_attributes("-topmost", True)
    label.master.wm_attributes("-disabled", True)
    label.master.wm_attributes("-transparentcolor", "white")

    hWindow = pywintypes.HANDLE(int(label.master.frame(), 16))

    # The WS_EX_TRANSPARENT flag makes events (like mouse clicks) fall through the window.
    exStyle = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT
    win32api.SetWindowLong(hWindow, win32con.GWL_EXSTYLE, exStyle)

    label.pack()
    print('-')

    while True:
        if next_img:
            print('--')
            label.configure(image=test)
            label.update()
            time.sleep(0.5)
            width, height = coordinate[0], coordinate[1]
            label.master.geometry("+"+str(width)+"+" +str(height))
            pic1 = ImageGrab.grab(coordinate)
            pic = pic1.resize((pic1.width//scale, pic1.height//scale))
            pic.save('temp.png', 'PNG')
            res = ocr.ocr('temp.png', cls=True)
            print(res)
            img3 = Image.new('RGBA', (pic1.width, pic1.height), (255, 0, 0, 0))
            draw = ImageDraw.Draw(img3)
            font = ImageFont.truetype('arial.ttf', fontsize)
            tran_str = ''
            for r in res:
                tran_str +=r[1][0] + ' 999909 '
            tr_res = deeptr(tran_str)
            while len(tr_res) < len(res):
                tr_res.append('')
            for c, i in enumerate(res):
                draw.rectangle((i[0][0][0]*scale, i[0][0][1]*scale, i[0][2][0]*scale, i[0][2][1]*scale), fill="grey")
                draw.text((i[0][0][0]*scale, i[0][0][1]*scale), tr_res[c], fill=(0, 0, 0), font = font)
            img3 =  ImageTk.PhotoImage(img3)
            label.configure(image=img3)
            next_img=0
        label.update()
def change(e):
    global a
    global next_img
    if e.Key == 'Lcontrol':
        a =1
    elif e.Key == 'P':
        next_img =1
    else:
        print(e.Key)
    return 1
def on_mouse_event(event):
    global a
    if event.MessageName == 'mouse left down' and a >=1:
        coordinate[0:2] = event.Position
    elif event.MessageName == 'mouse left up' and a>=1:
        coordinate[2:4] = event.Position
        win32api.PostQuitMessage()
        a = 0
    return True
def select_data():
    hm = pyWinhook.HookManager()
    hm.MouseAll = on_mouse_event
    hm.KeyDown = change
    hm.HookMouse()
    hm.HookKeyboard()
    while True:
        pythoncom.PumpMessages()
if __name__ == '__main__':
    thread1 = threading.Thread(target=select_data)
    thread2 = threading.Thread(target=output)
    thread1.start()
    thread2.start()