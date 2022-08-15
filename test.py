import threading
from paddleocr import PaddleOCR
import time
from PIL import Image, ImageTk, ImageDraw, ImageGrab
import tkinter, win32api, win32con, pywintypes
import imagesize
import pyWinhook
import pythoncom
ocr = PaddleOCR(use_angle_cls=True, lang='en')
a = 0
next_img = 0
coordinate = [1, 1, 1, 1]
def output():
    global next_img 
    #t = time.time()
    #res = ocr.ocr('./example/images/test2.png', cls=True)
    #print(res)
    #print(time.time()-t)


    root = tkinter.Tk()

    #width, height = imagesize.get('./example/images/test2.png')
    img = Image.new('RGBA', (100, 100), (255, 0, 0, 0))

    #draw = ImageDraw.Draw(img)
    #for i in res:
    #    print(i[0][0])
    #    draw.text((i[0][0][0], i[0][0][1]), i[1][0], fill=(255, 0, 0))

    test = ImageTk.PhotoImage(img)
    label = tkinter.Label(image=test, bg='white')#text='Text on the screen', font=('Times New Roman','80'), fg='black', bg='white')
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
        #label.update()
        #time.sleep(1)
        
        if next_img:# and (coordinate[0]-coordinate[2]) > 4 and (coordinate[1]-coordinate[3]) > 4:
            print('--')
            label.configure(image=test)
            label.update()
            time.sleep(0.5)
            width, height = coordinate[0], coordinate[1]
            label.master.geometry("+"+str(width)+"+" +str(height))
            pic1 = ImageGrab.grab(coordinate)
            pic = pic1.resize((pic1.width//2, pic1.height//2))
            pic.save('temp.png', 'PNG')
            res = ocr.ocr('temp.png', cls=True)
            print(res)
            img3 = Image.new('RGBA', (pic1.width, pic1.height), (255, 0, 0, 0))
            draw = ImageDraw.Draw(img3)
            for i in res:
            #    print(i[0][0])
                draw.rectangle((i[0][0][0]*2, i[0][0][1]*2, i[0][2][0]*2, i[0][2][1]*2), fill="grey")
                draw.text((i[0][0][0]*2, i[0][0][1]*2), i[1][0], fill=(255, 0, 0))
            #draw.text((10,10), str(coordinate), fill=(255, 0, 0))
            img3 =  ImageTk.PhotoImage(img3)
            label.configure(image=img3)
            next_img=0
        #label.image = img3 
        #label.im = img.rotate(10)
        #label.master.geometry("+"+str(r) +"+"+str(r))
        #r +=5
        #print(r)
        label.update()
def change(e):
    global a
    global next_img
    if e.Key == 'Lcontrol':
        a =1
    elif e.Key == 'Z':
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
    #keyboard.hook(change)
    while True:
        pythoncom.PumpMessages()
        #keyboard.wait()
if __name__ == '__main__':
    thread1 = threading.Thread(target=select_data)
    thread2 = threading.Thread(target=output)
    thread1.start()
    thread2.start()