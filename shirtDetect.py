import io
import boto3
import operator
import webbrowser
from pprint import pprint
import webcolors
from os.path import basename
import matplotlib
import base64
import Tkinter as tk
from bs4 import BeautifulSoup
import urllib2
import PIL.Image
from PIL import Image, ImageTk
from urlparse import urlsplit
from google.cloud import vision
from amazon.api import AmazonAPI
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types 
from google.cloud.vision import types as tp2
from tkinter import *
from itertools import combinations
from tkinter.filedialog import askopenfilename
import six
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "My Project 34134-0ba01989fe78.json"
vision_client = vision.Client()
amazon = AmazonAPI("AKIAINAN7KXLIGYAWEAA", "...", "akhily-20")

#home page to upload image                               
class Home():
                def __init__(self, master):
                                self.window = tk.Toplevel(root)
                                self.window.geometry("300x120")
                                self.window.title("Homepage")
                                button1 = Button(self.window, text="Upload file", width=15, height=3, command = self.uploadInfo)
                                button1.pack(ipadx=10)

                def uploadInfo(self):
                                self.window.update()
                                filePath = askopenfilename()
                                self.window.destroy()
                                detect = detectInfo(root, filePath)

#Creates pop up window for invalid search
class newPopUp():
                def __init__(self, master, message):
                                self.window = tk.Toplevel(root)
                                self.window.geometry("600x200")
                                self.window.title("Invalid Search")
                                label2 = tk.Label(self.window, text = message)
                                label2.pack()
                                button1 = Button(self.window, text="Ok", width=15, height=3, command = self.homePage)
                                button1.pack()

                def homePage(self):
                                self.window.withdraw()
                                home = Home(root)

#searches keywords in Amazon Product Advertising API
#match is displayed in a new tkinter window
class searchAmazon():
                def __init__(self, master, searchInfo, color, category):
                                self.window = tk.Toplevel(root)
                                self.window.geometry("815x825")
                                self.window.title("Info Page")
                                self.searchInfo(searchInfo, color, category)
                                
                def openUrl(self, url):
                                webbrowser.open_new(url)
                                                
                def searchInfo(self, searchInfo, color, category):
                                url = ""
                                price = ""
                                title = ""
                                img = ""
                                endLoop = False
                                products = amazon.search(Keywords=searchInfo, SearchIndex='All')
                                print(type(products))
                                for i, product in enumerate(products):
                                                imgUrl = product.large_image_url
                                                imgData = urllib2.urlopen(imgUrl).read()
                                                fileName = basename(urlsplit(imgUrl)[2])
                                                output = open(fileName,'wb')
                                                output.write(imgData)
                                                output.close()
                                                with io.open(fileName, 'rb') as imageFile:
                                                                content = imageFile.read()
                                                                image = vision_client.image(content = content)
                                                checkLabels = image.detect_labels()
                                                for eachLabel in checkLabels:
                                                                if category in eachLabel.description:
                                                                                url = product.offer_url
                                                                                price = product.price_and_currency
                                                                                title = product.title
                                                                                img = ImageTk.PhotoImage(PIL.Image.open(fileName))
                                                                                endLoop = True
                                                if endLoop == True:
                                                                break
                                                
                                label = tk.Label(self.window, image = img)
                                label.pack()
                                label2 = tk.Label(self.window, text = title)
                                label2.pack()
                                label3 = tk.Label(self.window, text = price)
                                label3.pack()
                                label4 = tk.Label(self.window, text = url)
                                label4.pack()
                                self.openUrl(url)
                                self.window.mainloop()

#takes the inputted image and uses Amazon Rekognition to detext text
#Google Cloud vision is used to detext logos, color and category
#if image is not classified as shirt, hat, sweatshirt, shorts, or pants, a pop up window
#will ask user to input a valid image
class detectInfo():
                def __init__(self, master, path):
                                description = ""
                                logos = self.detect_logos(path)
                                color, category = self.detectLabels(path)
                                name = self.detectText(path)
                                if type(color) == str and color:
                                                newWindow = newPopUp(root, color)
                                else:
                                                if logos == "":
                                                                description = color +  " " + name + " " + "sports " + category
                                                else:
                                                                description = color + " " + logos + " " + name + " "+  category
                                                print(description)
                                                searchCheck = searchAmazon(root, description, color, category)
                               
                def detectText(self, path):
                                client = boto3.client('rekognition')
                                content = ""
                                with io.open(path, 'rb') as imageFile:
                                                content = imageFile.read()
                                rekresp = client.detect_text(Image={'Bytes': content})
                                detections = rekresp['TextDetections']
                                word = ""
                                if detections:
                                                firstDetection = detections[0]
                                                secondDetection = detections[1]
                                                if firstDetection['Confidence'] > 93:
                                                                word = firstDetection['DetectedText']
                                                elif secondDetection['Confidence'] > 93:
                                                                word = secondDetection['DetectedText']
                                return word
                                      
                def detect_logos(self, path):
                                client = vision.ImageAnnotatorClient()
                                with io.open(path, 'rb') as image_file:
                                                content = image_file.read()
                                image = tp2.Image(content=content)
                                response = client.logo_detection(image=image)
                                logos = response.logo_annotations
                                print('Logos:')
                                word = ""
                                for logo in logos:
                                                print(logo.description)
                                                word += logo.description
                                return word

                def detectLabels(self, filePath):
                                with io.open(filePath, 'rb') as imageFile:
                                                content = imageFile.read()
                                                image = vision_client.image(content = content)
                                labels = image.detect_labels()
                                colors, tracker = [], {}
                                category = ""
                                shirts, jerseys, shorts, pants, headgear, sweatshirt = 0, 0, 0, 0, 0, 0
                                for label in labels:
                                                if "sweatshirt" in label.description or "hoodie" in label.description:
                                                                sweatshirt += 1
                                                                tracker["sweatshirt"] = sweatshirt
                                                elif "shirt" in label.description:
                                                                shirts += 1
                                                                tracker["shirt"] = shirts
                                                elif "jersey" in label.description:
                                                                jerseys += 1
                                                                tracker["jersey"] = jerseys
                                                elif "shorts" in label.description:
                                                                shorts += 1
                                                                tracker["shorts"] = shorts
                                                elif "pants" in label.description:
                                                                pants += 1
                                                                tracker["pants"] = sports
                                                elif "cap" in label.description or "hat" in label.description:
                                                                headgear += 1
                                                                tracker["cap"] = headgear
                                color = ""
                                print(max(tracker.iteritems(), key=operator.itemgetter(1))[0])
                                if all(value == 0 for value in tracker.values()):
                                                message = "Please input a search that contains shirts, jerseys, shorts, pants, or hats"
                                                return message, None
                                if 'shirt' in tracker.keys() and 'jersey' in tracker.keys():
                                                if tracker['shirt'] == tracker['jersey']:
                                                                category = "jersey"
                                                                print(category)
                                                else:
                                                                category = category = max(tracker.iteritems(), key=operator.itemgetter(1))[0]
                                else:
                                                category = max(tracker.iteritems(), key=operator.itemgetter(1))[0]
                                                print(category)
                                                
                                for label in labels:
                                                data = []
                                                if " " in label.description:
                                                                data = label.description.split()
                                                for item in data:
                                                                if item in webcolors.CSS3_NAMES_TO_HEX:
                                                                                colors.append(item)
                                                                                break
                                                if not colors and label.description in webcolors.CSS3_NAMES_TO_HEX:
                                                                colors.append(label.description)
                                if colors:
                                                color = colors[0]
                                return color, category
                                                               
if __name__ == '__main__':
                root = tk.Tk()
                first = Home(root)
                root.mainloop()
