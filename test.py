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
import requests
from translate import Translator
import json
import numpy as np
from webdriver_manager.chrome import ChromeDriverManager
with open('translate_log.json') as f:
    content = f.read()
    log = json.loads(content)
    log_key = list(log)
    if len(log_key)>300000:
        log_key = log_key[:len(log_key)-250000]
        for i in log_key:
            log.pop(i)
a = 0
full_screen = 0
next_img = 0
coordinate = [1, 1, 20, 20]
coordinate_copy = None
clear_img=0
chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument('user-data-dir=C:\\Users\\dimon\\AppData\\Local\\Google\\Chrome\\User Data')
# browser = webdriver.Chrome(chrome_options=chrome_options) 
browser = webdriver.Chrome(ChromeDriverManager().install())
browser.get('https://www.deepl.com/translator#en/ru/')
history = True
dist_limit = 100
stop_trans=False
bw_mod = True
threshold = 200
lang = 'en'
ocr = None
automatic = {'mode':False, 'freq':2}
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
    y_abs = abs((text_xmin+text_xmax)/2 -(obj_xmin+obj_xmax)/2) > max(abs(text_xmax-text_xmin)/2, abs(obj_xmax-obj_xmin)/2) 
    #print('Center_x dist ',y_abs)
    dist = x_dist + y_dist
    return dist#x_dist, y_dist, y_abs
   
#Principal algorithm for merge text 
def merge_algo(texts, texts_boxes):
    for i, (text_1, text_box_1) in enumerate(zip(texts, texts_boxes)):
        for j, (text_2, text_box_2) in enumerate(zip(texts, texts_boxes)):
            if j <= i:
                continue            # Create a new box if a distances is less than disctance limit defined 
            #if calc_sim(text_box_1, text_box_2)[0]+calc_sim(text_box_1, text_box_2)[1] < dist_limit and calc_sim(text_box_1, text_box_2)[2]:
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

from bs4 import BeautifulSoup

def get_text_between_tags(html):
    soup = BeautifulSoup(html, 'html.parser')

    def get_text_from_element(element):
        if element.string:
            return element.string.strip()
        else:
            result = ''
            for child in element.children:
                if child.name and child.name != 'script':  # Ігноруємо скрипти
                    child_text = get_text_from_element(child)
                    if child_text:
                        result += child_text + ' '
            return result.strip()

    text = get_text_from_element(soup)
    return text


from difflib import SequenceMatcher

def deeptr(text):
    br = browser.find_element('xpath','//d-textarea[@data-testid="translator-source-input"]')
    try:
        browser.find_element('xpath','//button[@data-testid="translator-source-clear-button"]').click()
    except:
        print('almost clear')
    #br.clear()
    pyperclip.copy(text)
    #time.sleep(0.1)
    trans = True
    while trans:
        try:
            br.send_keys(Keys.CONTROL + "v")
            trans=False
        except:
            print('ctrl+v error')
    c = text.count('\n')
    print(text)
    print(c)
    # if c == 1:
    #     c+=1
    #     text+='\n'
    count = 0
    stop = 30
    while True:
        res = ''
        time.sleep(0.1)
        #html = browser.find_element('xpath','//d-textarea[@data-testid="translator-target-input"]').get_attribute('innerHTML')
        try:
            browser.find_element('xpath','//button[@data-testid="translator-target-toolbar-copy"]').click()
        except:
            print('no copy button')
            stop -=1
            if not stop:
                return res.split('\n')
            continue
        res = pyperclip.paste()
        #print(html)
        #print('\n')
        #res = get_text_between_tags(html)
        print(res)
        #b = browser.find_element('id', 'target-dummydiv')
        #res = b.get_attribute('innerHTML')
        if res.count('\n') >= c:
            #pyperclip.copy(text)
            # print(res)
            if SequenceMatcher(None, text, res).ratio()<0.8:
                return res.split('\n')#replace('\n', '')
            else:
                if stop <=0:
                    return res.split('\n')
                stop = 0
                continue
        print(res.count('\n'))
        print(c)
        stop -=1
        if stop<=0:
            return res.split('\n')
def output(scale=1, fontsize = 15, server_mode=False, padding_scale=0, translator='deepl--'):
    global next_img 
    global clear_img
    global coordinate
    global coordinate_copy
    global full_screen
    global log
    global history
    global stop_trans
    global threshold
    global bw_mod
    global lang
    global ocr
    root = tkinter.Tk()
    img = Image.new('RGBA', (100, 100), (255, 0, 0, 0))
    test = ImageTk.PhotoImage(img)
    label = tkinter.Label(image=test, bg='white')
    label.master.overrideredirect(True)
    #label.master.geometry("+250+250")
    label.master.lift()
    label.master.wm_attributes("-topmost", True)
    label.master.wm_attributes("-disabled", True)
    label.master.wm_attributes("-transparentcolor", "white")

    hWindow = pywintypes.HANDLE(int(label.master.frame(), 16))

    # The WS_EX_TRANSPARENT flag makes events (like mouse clicks) fall through the window.
    exStyle = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT
    win32api.SetWindowLong(hWindow, win32con.GWL_EXSTYLE, exStyle)

    label.pack()
    if server_mode is False:
        ocr = PaddleOCR(use_angle_cls=True, lang=lang, gpu_enable=True, gpu_mem=4000, det_db_unclip_ratio=2.5, det_db_box_thresh=0.2) #det_db_unclip_ratio=2.5, det_db_box_thresh=0.2)#use_dilation=True)#, det_db_unclip_ratio=1, use_space_char=True)
    while True:
        if stop_trans:
            label.configure(image=test)
            label.update()
            clear_img=0
            next_img=0
            stop_trans=False
        if clear_img:
            label.configure(image=test)
            label.update()
            clear_img=0
            #time.sleep(0.4)
            next_img=1
        if next_img:
            
            #label.configure(image=test)
            label.update()
            time.sleep(0.1)
            
            res = []
            while not res and not stop_trans:
                time.sleep(0.3)
                t = time.time()
                if full_screen:
                    pic1 = ImageGrab.grab()
                    coordinate_copy=coordinate[:]
                    coordinate=[1,1,2,2]
                else:
                    try:
                        pic1 = ImageGrab.grab(coordinate)
                    except ValueError:
                        print('Coordinate error')
                print('time screenshot=',time.time()-t)
                width, height = coordinate[0], coordinate[1]
                label.master.geometry("+"+str(int(width/2))+"+" +str(int(height/2)))

                t1 = time.time()
                pic = pic1.resize((pic1.width//scale, pic1.height//scale))
                print('time resize=',time.time()-t1)
                
                #pic.save('temp.png', 'PNG')
                #print('time save=',time.time()-t1)
                t2 = time.time()
                if server_mode:
                    url = 'http://9727-34-66-21-36.ngrok.io/img'
                    files={'file':open('temp.png','rb')}
                    r = requests.post(url, files=files)
                    res = r.json()['res']
                    
                else:
                    if bw_mod:
                        gpic = pic.convert('L')
                        bw = gpic.point(lambda x: 0 if x < threshold else 255, '1')
                        pic = bw.convert('RGB')
                        #pic.save('temp.png', 'PNG')
                    res = ocr.ocr(np.array(pic), cls=True)
                print('time recognize=',time.time()-t2)
                print(res)
            t3 = time.time()
            # print(res)
            # print(len(res))
            img3 = Image.new('RGBA', (pic.width, pic.height), (255, 0, 0, 0))
            draw = ImageDraw.Draw(img3)
            font = ImageFont.truetype('arial.ttf', fontsize)
            
            texts_copied = []
            texts_boxes_copied = []
            for c, i in enumerate(res):
                texts_copied.append(i[1][0])
                # print('+++++++++++++')
                # print(i[1][0])
                # print('+++++++++++++')
                # print(i[0][0])
                texts_boxes_copied.append([i[0][0][0], i[0][0][1], i[0][2][0], i[0][2][1]])
            need_to_merge = True
            # print(texts_copied)

            while need_to_merge:
                need_to_merge, texts_copied, texts_boxes_copied = merge_algo(texts_copied, texts_boxes_copied)
            # print(len(texts_copied))
            # print(len(texts_boxes_copied))

            tran_str = ''
            rep_tran = ['+']*len(texts_copied)
            tr_str = []
            for r in range(len(texts_copied)):
                if texts_copied[r] in log and history:
                    rep_tran[r]=log[texts_copied[r]]
                else:
                    tran_str +=texts_copied[r] + ' \n '
                    tr_str.append(texts_copied[r])
            # print('\n')
            # print(texts_copied)
            # print(rep_tran)
            # # print(list(log)[-10:])
            # print('\n')
            print('time merge=',time.time()-t3)
            t4 = time.time()
            if translator=='deepl' and len(tran_str)>0:
                tr_res = deeptr(tran_str)
            elif len(tran_str)>0: # google translate
                l = lang
                if lang == "japan":
                    l = "ja"
                
                url = f"https://translate.google.com/m?sl={l}&tl=ru&q={tran_str}"
                headers = {"User-Agent": "Mozilla/5.0 Screen Translator"}
                t = time.time()
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    print(tran_str)
                    start = response.text.find("result-container\">") + 18
                    end = response.text.find("<", start)
                    tr_res = response.text[start:end].split('\n')
                    print(tr_res)
            else:
                tr_res = []
            try:
                for i in range(len(tr_str)):
                    log[tr_str[i]] = tr_res[i] 
            except:
                print('log error')
            if history:
                for i in tr_res:
                    for r in range(len(rep_tran)):
                        if rep_tran[r] =='+':
                            rep_tran[r] = i
                            break
                tr_res=rep_tran

            # print(log)
            print('time translate=',time.time()-t4)
            t5 = time.time()
            while len(tr_res) < len(texts_copied):
                tr_res.append('')
            # print(tr_res)
            # tr_res=tr_res[:-1]
            #print(tr_res)
            #print(texts_boxes_copied)
            #print(len(tr_res))
            #print(len(texts_boxes_copied))
            check_len = min(len(tr_res), len(texts_boxes_copied))
            # if check_len==0:
            #     check_len=1
            tr_res.append('')
            texts_boxes_copied.append('')
            tr_res = tr_res[:check_len]
            texts_boxes_copied = texts_boxes_copied[:check_len]

            for c, i in enumerate(tr_res):
                i = i.strip()
                y0=texts_boxes_copied[c][1]
                y1=texts_boxes_copied[c][3]
                x0=texts_boxes_copied[c][0]
                x1=texts_boxes_copied[c][2]
                if y1-y0 <=10:
                    y1+=20
                    texts_boxes_copied[c][3]+=20
                if len(i)>0:
                    sq = ((y1-y0)*(x1-x0))/len(i)
                    
                    try:
                        fs = int((sq/0.8)**(1/2))-1
                    except:
                        print(sq)
                        fs = 10
                    # print('----')
                    # print(fs)
                    if fs<=0:
                        fs=10
                    # print(fs)
                    font = ImageFont.truetype('arial.ttf', int(fs))
                    len_t = (x1-x0)/(fs*0.65)
                    texts = re.findall('(.{%s}|.+$)'%int(len_t-1), i)
                    try:
                        for i in range(len(texts)-1):
                            if texts[i][-1]!=' ' and texts[i+1][0]!=' ':
                                texts[i]+='-'
                    except:
                        print('error wrap')
                    draw.rectangle(tuple(texts_boxes_copied[c]), fill=(128, 128, 128, 128))#fill="grey")
                    add = 0
                    for te in texts:
                        draw.text((x0+padding_scale*fs/4, y0+add+padding_scale*fs/4), te, fill=(0, 0, 0), font = font )
                        add+=fs
            img3=img3.resize((int(img3.width*scale/2), int(img3.height*scale/2)))
            img3 =  ImageTk.PhotoImage(img3)
            label.configure(image=img3)
            if not automatic['mode']:
                next_img=0
            print('time show=',time.time()-t5)
            if full_screen:
                coordinate=coordinate_copy[:]
                full_screen=0
        label.update()
import sys
def change(e):
    global a
    global next_img
    global clear_img
    global full_screen
    global dist_limit
    global stop_trans
    global threshold
    global bw_mod
    global lang
    global ocr
    if e.Key == 'Oem_3':
        a =1
    elif e.Key == 'P':
        next_img =1
    elif e.Key == 'O':
        next_img =1
        full_screen=1
    elif e.Key=='Delete':
        with open('translate_log.json', 'w') as f:
            f.write(json.dumps(log))
        browser.quit()
        sys.exit('--')
    elif e.Key == 'Return':
        clear_img=1
    elif e.Key == 'I':
        dist_limit-=20
    elif e.Key == 'U':
        dist_limit+=20
    elif e.Key == 'L':
        stop_trans = True
    elif e.Key == 'A':
        automatic['mode'] = not automatic['mode']
    elif e.Key == 'K':
        bw_mod = not bw_mod
        print(bw_mod)
    elif e.Key == 'M':
        threshold -=10
        print(threshold)
    elif e.Key == 'N':
        threshold +=10
        print(threshold)
    elif e.Key == 'Z':
        if lang == "en":
            lang = "japan"
        else:
            lang="en"
        ocr = PaddleOCR(use_angle_cls=True, lang=lang, gpu_enable=True, gpu_mem=4000, det_db_unclip_ratio=2.5)#use_dilation=True)#, det_db_unclip_ratio=1, use_space_char=True)

        print(lang)
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
