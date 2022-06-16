# Importing necessary packages
import tkinter as tk
from tkinter import *
from tkinter import messagebox, filedialog
from fake_useragent import UserAgent
from PIL import Image
from bs4 import BeautifulSoup
import shutil, requests, threading, string, random, os, re, traceback, cloudscraper, base64, io

#https://stackoverflow.com/questions/68772211/fake-useragent-module-not-connecting-properly-indexerror-list-index-out-of-ra

def logError(error):
    print(f"+++ Error : {error}")
    traceback.print_tb(error.__traceback__)

def validateUrl(text):
    regex = r'(?:(?:http|https):\/\/)?(?:www.)?(?:instagram.com|instagr.am|instagr.com)\/(\w+)'
    if re.match(regex, text):
        return True
    else:
        return False
 
def Widgets():
 
    head_label = Label(root, text = "Instagram Downloader", padx = 15, pady = 15, font = "SegoeUI 14", bg = "ivory3", fg = "blue")
    head_label.grid(row = 1, column = 1, pady = 10, padx = 5, columnspan = 3)
 
    link_label = Label(root, text = "Post link :", bg = "cyan", pady = 5, padx = 5)
    link_label.grid(row = 2, column = 0, pady = 5, padx = 5)
 
    root.linkText = Entry(root, width = 35, textvariable = link_post, font = "Arial 14")
    root.linkText.grid(row = 2, column = 1,pady = 5,padx = 5, columnspan = 2)
 
    destination_label = Label(root, text = "Destination :", bg = "cyan", pady = 5, padx = 9)
    destination_label.grid(row = 3, column = 0, pady = 5, padx = 5)
 
    root.destinationText = Entry(root, width = 27, textvariable = download_Path, font = "Arial 14")

    root.destinationText.grid(row = 3, column = 1, pady = 5,padx = 5)
 
    browse_B = Button(root, text = "Browse", command = Browse, width = 10, bg = "light goldenrod", relief = GROOVE)
    browse_B.grid(row = 3, column = 2, pady = 1, padx = 1)

    Download_B = Button(root, text = "Download", 
                        command = Download, width = 20, 
                        bg = "DodgerBlue2", pady = 10,
                        padx = 15, relief = GROOVE, font ="Georgia, 13")

    Download_B.grid(row=4, column=1, pady=20, padx=20)
 
def randomStr(count):
    tx = string.ascii_letters + string.digits
    ret = ''.join(random.choices(tx, k=count))
    return ret 

def Browse():
    download_Directory = filedialog.askdirectory(initialdir="YOUR DIRECTORY PATH", title="Save Video")
 
    download_Path.set(download_Directory)
 
def saveFile(path, raw):
    with open(path, 'wb') as f:
        shutil.copyfileobj(raw, f)

def saveImage(data, path):
    b64 = data[data.find("/9"):]
    Image.open(io.BytesIO(base64.b64decode(b64))).save(path)

def downloadFileWithURL(url, saveAs):
    r = requests.get(url, stream = True)
    if r.status_code != 404:
        saveFile(saveAs,r.raw)
        return saveAs
    else:
        raise Exception('Download file failure.')

def igdl(url):
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'android',
            'desktop': False
        }
    )
    ua = UserAgent()
    # r = requests.get("https://www.instagramsave.com", headers=headers)
    headers = {"User-Agent": ua.random}
    r = scraper.get("https://instagramsave.com", headers=headers)
    html = BeautifulSoup(r.content, 'lxml')
    token = html.findAll("input", {"name":"token"})[0].get("value")
    if "/reel/" in url or "/p/" in url or "/tv/" in url:
        typePost = "post"
    elif "/stories/" in url:
        typePost = "story"
        url = "https://instagram.com/" + url.split("/stories/")[1].split("/")[0]
    data = {"url":url, "action": typePost, "token": token}
    r2 = requests.post("https://www.instagramsave.com/system/action.php", data = data, headers = headers)
    return r2.json()

def igdl2(url):
    base = "https://sssinstagram.com/"
    api = f"{base}request"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
        "Accept": "*/*","Accept-Language": "en-US,en;q=0.5"
    }
    s = requests.session()
    s.get(url=base, headers=headers)
    response = s.post(url=api,headers={**headers,
        "Content-Type": "application/json;charset=utf-8",
        "X-XSRF-TOKEN": requests.utils.unquote(s.cookies["XSRF-TOKEN"]),
        },
        json={
            "link": url,
        })
    data = response.json()['data']
    return data

def downloadIg(url):
    global progress_done, total, path_list
    if download_Path.get() == "":
        download_Path.set(os.getcwd())
    try:
        dataJson = igdl(url)
        if dataJson['user']['username'] not in os.listdir(download_Path.get()):
            os.mkdir(download_Path.get()+"/"+dataJson['user']['username'])
        path = download_Path.get()+"/"+dataJson['user']['username']+"/"+typePost
        path_list = []
        if typePost not in os.listdir(download_Path.get()):
            os.mkdir(path)
        medias = dataJson['medias']
        total = 0
        for i in medias:
            ppath = downloadFileWithURL(i['url'], path+"/"+randomStr(10)+"."+i["fileType"])
            path_list.append(ppath)
            total += 1
        progress_done = True
    except Exception as e:
        logError(e)
        try:
            data = igdl2(url)
            if "/reel/" in url or "/p/" in url or "/tv/" in url:
                typePost = "post"
            elif "/stories/" in url:
                typePost = "story"

            if typePost not in os.listdir(download_Path.get()):
                os.mkdir(download_Path.get()+"/"+typePost)
            ppath = download_Path.get()+"/"+typePost
            path_list = []
            total = 0
            if data["type"] == "GraphImage":
                total += 1
                path = ppath+"/"+randomStr(10)+".jpg"
                saveImage(data["image"]["display_url"], path)
                path_list.append(path)
                progress_done = True
            elif data["type"] == "GraphVideo":
                total += 1
                path = ppath+"/"+randomStr(10)+".mp4"
                downloadFileWithURL(data["video"]["video_url"], path)
                path_list.append(path)
                progress_done = True
            elif data["type"] == "GraphSidecar":
                for i in data["items"]:
                    total += 1
                    if i["type"] == "GraphImage":
                        path = ppath+"/"+randomStr(10)+".jpg"
                        saveImage(i["image"]["display_url"], path)
                        path_list.append(path)
                    else:
                        path = ppath+"/"+randomStr(10)+".mp4"
                        downloadFileWithURL(i["video"]["video_url"], path)
                        path_list.append(path)
                progress_done = True

        except Exception as e:
            logError(e)
            messagebox.showerror("Error", str(e))
 
def Download():
    global progress_done

    
    post_link = link_post.get()
    if validateUrl(link_post.get()):
        progress_done = False
        t = threading.Thread(target=downloadIg(post_link), daemon=True)
        t.start()
        root.after(5000, tkinter_download_loop)
    else:
        return messagebox.showerror("Error", "Link tidak valid")

def tkinter_download_loop():
    global progress_done, path_list
    if not progress_done:
        root.after(1000, tkinter_download_loop)
    else:
        result = "\n - ".join(path_list)
        messagebox.showinfo("SUCCESSFULLY","DOWNLOADED AND SAVED IN\n - " + result)

 
root = tk.Tk()
 
root.geometry("520x280")
root.resizable(False, False)
root.title("Instagram Post Downloader")
root.config(background="ivory3")
 
# Creating the tkinter Variables
link_post = StringVar()
download_Path = StringVar()
 
# Calling the Widgets() function
Widgets()
 
# Defining infinite loop to run
# application
root.mainloop()