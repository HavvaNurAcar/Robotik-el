import cv2
import mediapipe
import pyttsx3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException
import os
import subprocess

class Browser:
    def __init__(self):
        self.options = Options()
        self.options.add_experimental_option("debuggerAddress", "localhost:9222")
        self.driver = webdriver.Chrome(options=self.options, executable_path="C:\\webdrivers\\chromedriver.exe")
        self.likeButton = None
        self.dislikeButton = None

    def likeVideo(self):
        try:
            if self.checkButtonsDefined() and self.likeButton.get_attribute("aria-pressed") == "false":
                self.likeButton.click()
        except ElementNotInteractableException:
            print("not interactable")

    def dislikeVideo(self):
        try:
            if self.checkButtonsDefined() and self.dislikeButton.get_attribute("aria-pressed") == "false":
                self.dislikeButton.click()
        except ElementNotInteractableException:
            print("not interactable")

    def defineButtons(self):
        self.likeButton = self.driver.find_element(By.CSS_SELECTOR, "div.style-scope.ytd-video-primary-info-renderer div div#menu-container div#menu button")
        self.dislikeButton = self.driver.find_element(By.CSS_SELECTOR, "div.style-scope.ytd-video-primary-info-renderer div div#menu-container div#menu ytd-toggle-button-renderer:nth-child(2) button")

    def checkButtonExists(self):
        if "watch" in self.driver.current_url:
            try:
                self.driver.find_element(By.CSS_SELECTOR, "div.style-scope.ytd-video-primary-info-renderer div div#menu-container div#menu button")
            except NoSuchElementException:
                return False
            return True

    def checkButtonsDefined(self):
        return self.likeButton is not None and self.dislikeButton is not None

# Kodun geri kalanı
browser = Browser()

camera = cv2.VideoCapture(0)

engine = pyttsx3.init()

mpHands = mediapipe.solutions.hands
hands = mpHands.Hands()
mpDraw = mediapipe.solutions.drawing_utils

checkThumbsUp = False

while True:
    if browser.checkButtonExists() and not browser.checkButtonsDefined():
        browser.defineButtons()

    success, img = camera.read()

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    hlms = hands.process(imgRGB)

    height, width, channel = img.shape

    if hlms.multi_hand_landmarks:
        for handlandmarks in hlms.multi_hand_landmarks:
            for fingerNum, landmark in enumerate(handlandmarks.landmark):
                positionX, positionY = int(landmark.x * width), int(landmark.y * height)

                if fingerNum > 4 and landmark.y < handlandmarks.landmark[2].y:
                    break

                if fingerNum == 20 and landmark.y > handlandmarks.landmark[2].y:
                    checkThumbsUp = True

            mpDraw.draw_landmarks(img, handlandmarks, mpHands.HAND_CONNECTIONS)

    cv2.imshow("Camera", img)

    if checkThumbsUp and browser.checkButtonExists():
        browser.likeVideo()
        checkThumbsUp = False

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
