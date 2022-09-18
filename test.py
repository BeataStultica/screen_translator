import threading
from paddleocr import PaddleOCR
import time
import re
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

dist_limit = 30


#Generate two text boxes a larger one that covers them
def merge_boxes(box1, box2):
    return [min(box1[0], box2[0]), 
         min(box1[1], box2[1]), 
         max(box1[2], box2[2]),
         max(box1[3], box2[3])]



#Computer a Matrix similarity of distances of the text and object
def calc_sim(text, obj):
    # text: ymin, xmin, ymax, xmax
    # obj: ymin, xmin, ymax, xmax
    text_ymin, text_xmin, text_ymax, text_xmax = text
    obj_ymin, obj_xmin, obj_ymax, obj_xmax = obj

    x_dist = min(abs(text_xmin-obj_xmin), abs(text_xmin-obj_xmax), abs(text_xmax-obj_xmin), abs(text_xmax-obj_xmax))
    y_dist = min(abs(text_ymin-obj_ymin), abs(text_ymin-obj_ymax), abs(text_ymax-obj_ymin), abs(text_ymax-obj_ymax))

    dist = x_dist + y_dist
    return dist

#Principal algorithm for merge text 
def merge_algo(texts, texts_boxes):
    for i, (text_1, text_box_1) in enumerate(zip(texts, texts_boxes)):
        for j, (text_2, text_box_2) in enumerate(zip(texts, texts_boxes)):
            if j <= i:
                continue
            # Create a new box if a distances is less than disctance limit defined 
            if calc_sim(text_box_1, text_box_2) < dist_limit:
            # Create a new box  
                new_box = merge_boxes(text_box_1, text_box_2)            
             # Create a new text string 
                new_text = text_1 + ' ' + text_2

                texts[i] = new_text
                #delete previous text 
                del texts[j]
                texts_boxes[i] = new_box
                #delete previous text boxes
                del texts_boxes[j]
                #return a new boxes and new text string that are close
                return True, texts, texts_boxes

    return False, texts, texts_boxes



def deeptr(text):
    br = browser.find_element('xpath','//textarea[@dl-test="translator-source-input"]')
    br.clear()
    pyperclip.copy(text)
    br.send_keys(Keys.CONTROL + "v")
    c = text.count('~')
    count = 0
    while True:

        time.sleep(0.1)
        b = browser.find_element('id', 'target-dummydiv')
        res = b.get_attribute('innerHTML')
        if res.count('~') >= c:
            pyperclip.copy(text)
            return res.split('~')#replace('~', '')
        print(res.count('~'))
        print(c)
def output(scale=1, fontsize = 15):
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

    while True:
        if next_img:
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
            
            texts_copied = []
            texts_boxes_copied = []
            for c, i in enumerate(res):
                texts_copied.append(i[1][0])
                texts_boxes_copied.append([i[0][0][0], i[0][0][1], i[0][2][0], i[0][2][1]])
            need_to_merge = True
            print(texts_copied)

            while need_to_merge:
                need_to_merge, texts_copied, texts_boxes_copied = merge_algo(texts_copied, texts_boxes_copied)
            print(len(texts_copied))
            print(len(texts_boxes_copied))
            tran_str = ''
            for r in texts_copied:
                tran_str +=r + ' ~ '
            tr_res = deeptr(tran_str)
            while len(tr_res) < len(texts_copied):
                tr_res.append('')
            #print(tr_res)
            tr_res=tr_res[:-1]
            #print(tr_res)
            #print(texts_boxes_copied)
            #print(len(tr_res))
            #print(len(texts_boxes_copied))
            check_len = min(len(tr_res), len(texts_boxes_copied))
            tr_res.append('')
            texts_boxes_copied.append('')
            tr_res = tr_res[:check_len]
            texts_boxes_copied = texts_boxes_copied[:check_len]
            #print(tr_res)
            #print(texts_boxes_copied)
            for c, i in enumerate(tr_res):
                i = i.strip()
                y0=texts_boxes_copied[c][1]
                y1=texts_boxes_copied[c][3]
                x0=texts_boxes_copied[c][0]
                x1=texts_boxes_copied[c][2]
                if len(i)>0:
                    sq = ((y1-y0)*(x1-x0))/len(i)
                    fs = int((sq/0.8)**(1/2))-1
                    font = ImageFont.truetype('arial.ttf', fs)
                    len_t = (x1-x0)/(fs*0.7)
                    texts = re.findall('(.{%s}|.+$)'%int(len_t), i)
                    draw.rectangle(tuple(texts_boxes_copied[c]), fill="grey")
                    add = 0
                    for te in texts:
                        draw.text((x0+fs/4, y0+add+fs/4), te, fill=(0, 0, 0), font = font )
                        add+=fs
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