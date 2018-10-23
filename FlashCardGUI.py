#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  3 11:51:43 2018

@author: arinzeokeke
"""

import tkinter
import Utils as U
import Settings as S
import random
import subprocess
from gtts import gTTS
import threading
import PIL.Image,PIL.ImageTk
import time
import playsound,os,random

class FlashCardApp:
    def __init__(self,master):
        self.master = master
        master.title("勉強しましょう!")
        self.mode = None
        self.deck = None
        self.studySet = None
        self.currentCard = None
        self.isRevealed = False
        self.waiting = False
        
        
        #where the cards and summaries will appear
        master.grid_rowconfigure(1,minsize=400)
        master.grid_columnconfigure(0,minsize=600)
        self.displayFrame = tkinter.Frame(master)
        self.displayFrame.grid(row=1,column=0, sticky=tkinter.EW)
        
        self.mainLabelText = tkinter.StringVar()
        
        self.mainLabel = tkinter.Label(self.displayFrame, textvariable=self.mainLabelText,wraplength=600)
        self.mainLabel.pack()
        self.mainLabel.config(font=("Courier", 40))
        self.mainLabelText.set("Click 'Study Kanji' or 'Study Vocab' to begin!")
        
        self.img = None
        self.secondaryLabel = tkinter.Label(self.displayFrame, image=self.img)
        self.secondaryLabel.pack()
        
        #status panel
        self.statusFrame = tkinter.Frame(master)
        self.statusFrame.grid(row=0,column=0, sticky=tkinter.EW)
        
        self.timeSinceLastLabelText = tkinter.StringVar()
        self.timeSinceLastLabel = tkinter.Label(self.statusFrame, textvariable=self.timeSinceLastLabelText)
        self.timeSinceLastLabel.grid(row=0,column=0, sticky=tkinter.EW,columnspan=3)
        
        self.cardsRemainingLabelText = tkinter.StringVar()
        self.cardsRemainingLabel = tkinter.Label(self.statusFrame, textvariable=self.cardsRemainingLabelText)
        self.cardsRemainingLabel.grid(row=1,column=0, sticky=tkinter.EW,columnspan=3)
        
        self.binLabels = []
        self.binLabelTexts = []
        self.binCountLabels = []
        self.binCountLabelTexts = []
        self.binCountLabels2 = []
        self.binCountLabelTexts2 = []
        for i in range(len(S.timeToNext)):
            b = S.timeToNext[i]
            binLabelText = tkinter.StringVar()
            binLabel = tkinter.Label(self.statusFrame, textvariable=binLabelText)
            binLabel.grid(row=2,column=i, sticky=tkinter.EW)
            binLabelText.set(U.convertSecondsToTimeString(b,1))
            self.binLabels.append(binLabel)
            self.binLabelTexts.append(binLabelText)
            
            binCountLabelText = tkinter.StringVar()
            binCountLabel = tkinter.Label(self.statusFrame, textvariable=binCountLabelText)
            binCountLabel.grid(row=3,column=i, sticky=tkinter.EW)
            binCountLabelText.set("0")
            self.binCountLabels.append(binCountLabel)
            self.binCountLabelTexts.append(binCountLabelText)
            
            binCountLabelText2 = tkinter.StringVar()
            binCountLabel2 = tkinter.Label(self.statusFrame, textvariable=binCountLabelText2)
            binCountLabel2.grid(row=4,column=i, sticky=tkinter.EW)
            binCountLabelText2.set("0")
            self.binCountLabels2.append(binCountLabel2)
            self.binCountLabelTexts2.append(binCountLabelText2)
            
        #buttons
        self.buttonFrame = tkinter.Frame(master)
        self.buttonFrame.grid(row=2,column=0)
        
        self.showHideButton = tkinter.Button(self.buttonFrame,text="Show/Hide",command=self.showHide)
        self.showHideButton.grid(row=0,column=0, sticky=tkinter.EW)
        
        self.correctButton = tkinter.Button(self.buttonFrame,text="Correct",command=self.correct)
        self.correctButton.grid(row=0,column=1, sticky=tkinter.EW)
        
        self.incorrectButton = tkinter.Button(self.buttonFrame,text="Incorrect",command=self.incorrect)
        self.incorrectButton.grid(row=0,column=2, sticky=tkinter.EW)

        self.correctButton = tkinter.Button(self.buttonFrame,text="Shaky",command=self.shaky)
        self.correctButton.grid(row=1,column=0, sticky=tkinter.EW)

        self.correctButton = tkinter.Button(self.buttonFrame,text="Easy",command=self.easy)
        self.correctButton.grid(row=1,column=1, sticky=tkinter.EW)

        self.correctButton = tkinter.Button(self.buttonFrame,text="Almost",command=self.almost)
        self.correctButton.grid(row=1,column=2, sticky=tkinter.EW)
        
        self.studyKanjiButton = tkinter.Button(self.buttonFrame,text="Study Kanji",command=self.studyKanji)
        self.studyKanjiButton.grid(row=2,column=0, sticky=tkinter.EW)
        
        self.studyVocabButton = tkinter.Button(self.buttonFrame,text="Study Vocab",command=self.studyVocab)
        self.studyVocabButton.grid(row=2,column=1, sticky=tkinter.EW)
                
        self.studyKanji2Button = tkinter.Button(self.buttonFrame,text="Study Applied Kanji",command=self.studyKanji2)
        self.studyKanji2Button.grid(row=2,column=2, sticky=tkinter.EW)
                        
        self.summarizeButton = tkinter.Button(self.buttonFrame,text="Summarize",command=self.summarize)
        self.summarizeButton.grid(row=2,column=3, sticky=tkinter.EW)
        
        self.speakButton = tkinter.Button(self.buttonFrame,text="Change Picture",command=self.changeCardPicture)
        self.speakButton.grid(row=3,column=0, sticky=tkinter.EW)
        
        self.doneButton = tkinter.Button(self.buttonFrame,text="Revert Picture",command=self.revertCardPicture)
        self.doneButton.grid(row=3,column=1, sticky=tkinter.EW)

        self.quitButton = tkinter.Button(self.buttonFrame,text="Clear Picture",command=self.clearCardPicture)
        self.quitButton.grid(row=3,column=2, sticky=tkinter.EW)
        
        self.speakButton = tkinter.Button(self.buttonFrame,text="Speak",command=self.speak)
        self.speakButton.grid(row=4,column=0, sticky=tkinter.EW)
        
        self.doneButton = tkinter.Button(self.buttonFrame,text="Done",command=self.done)
        self.doneButton.grid(row=4,column=1, sticky=tkinter.EW)

        self.quitButton = tkinter.Button(self.buttonFrame,text="Quit",command=self.quitApp)
        self.quitButton.grid(row=4,column=2, sticky=tkinter.EW)
        
    def nothing(self):
        pass
    
    def quitApp(self):
        self.done()
        self.master.quit()
        
    def showHide(self):
        if self.waiting:
            return
        if self.currentCard==None:
            return
        if self.isRevealed:
            if self.deck.name=="kanji2":
                self.mainLabelText.set(self.currentCard.kanji)
            else:
                self.mainLabelText.set(self.currentCard.eng)
        else:
            if self.deck.name=="kanji2":
                display = self.currentCard.hiragana+"\n"+self.currentCard.eng
                self.mainLabelText.set(display)
            else:
                self.mainLabelText.set(str(self.currentCard))
        
        self.isRevealed = not self.isRevealed
        self.wasRevealed = True
    def correct(self):
        self.updateCard(1)
        
    def incorrect(self):
        self.updateCard(0)
        
    def easy(self):
        self.updateCard(2)
        
    def shaky(self):
        self.updateCard(-2)
        
    def almost(self):
        self.updateCard(-1)
        
    def updateCard(self,value):
        if self.waiting:
            return
        if self.currentCard==None:
            return
        if not self.wasRevealed:
            return
        self.currentCard.updateCardSpacedRepetition(value)
        self.getAndDisplayNextCard()
        
    def changeCardPicture(self):
        if self.waiting:
            return
        if self.currentCard==None:
            return
        self.currentCard.changePicture()
        
        if self.currentCard.image==None:
            self.img = None
        else:
            print ("updating image")
            self.img = PIL.ImageTk.PhotoImage(self.currentCard.getImage())
        self.secondaryLabel.configure(image=self.img)
        self.secondaryLabel.image = self.img
        
    def revertCardPicture(self):
        if self.waiting:
            return
        if self.currentCard==None:
            return
        self.currentCard.revertPicture()
        
        if self.currentCard.image==None:
            self.img = None
        else:
            print ("updating image")
            self.img = PIL.ImageTk.PhotoImage(self.currentCard.getImage())
        self.secondaryLabel.configure(image=self.img)
        self.secondaryLabel.image = self.img
        
    def clearCardPicture(self):
        if self.waiting:
            return
        if self.currentCard==None:
            return
        self.currentCard.clearPicture()
        self.img = None
        self.secondaryLabel.configure(image=self.img)
        self.secondaryLabel.image = self.img
    
    def updateTimeSinceLastSeen(self):
        if self.waiting:
            return
        if self.currentCard==None:
            return
        timeString = self.currentCard.getTimeSinceLastSeen()
        self.timeSinceLastLabelText.set(timeString)
        realWait = U.closestWaitLessThan(time.time()-self.currentCard.lastSeen)
        for i in range(len(self.binLabels)):
            if (realWait>self.currentCard.timesCorrect) and (i==realWait):
                self.binLabels[i].config(fg="blue")
            elif i==self.currentCard.timesCorrect:
                self.binLabels[i].config(fg="red")
            else:
                self.binLabels[i].config(fg="black")
    def updateCardsRemaining(self):
        if self.studySet==None:
            return
        cardsRemaining = 0
        binCount = {}
        binCount2 = {}
        for i in range(len(self.binCountLabelTexts)):
            binCount[i] = 0
            binCount2[i] = 0
        
        for c in self.studySet:
            if c.getTimeToNext()<=0:
                cardsRemaining += 1
                binCount2[c.timesCorrect] += 1
            else:
                binCount[c.timesCorrect] += 1
        self.cardsRemainingLabelText.set("{0} cards remaining to study".format(cardsRemaining))
        
        for i in range(len(self.binCountLabelTexts)):
            self.binCountLabelTexts[i].set(str(binCount[i]))
            self.binCountLabelTexts2[i].set(str(binCount2[i]))
            
    def cleanStatusFrame(self):
        self.updateCardsRemaining()
        self.timeSinceLastLabelText.set("")
        for i in range(len(self.binLabels)):
            self.binLabels[i].config(fg="black")
    
    def countdown(self):
        if self.forceStopWait:
            self.waiting=False
            return
        timeRemaining = self.currentCard.getTimeToNext()
        if timeRemaining<=0:
            self.waiting = False

            #display card
            return self.getAndDisplayNextCard()
        else:
            self.waiting = True
            timeRemainingStr = U.convertSecondsToTimeString(timeRemaining)
            self.mainLabelText.set("Next card will display in {0}!".format(timeRemainingStr))
            self.master.after(1000,self.countdown)
            

    def studyKanji(self):
        self.forceStopWait = True
        self.waiting = False
        self.done()
        self.deck = U.getDeck("kanji")
        self.startStudy()
        
    def studyKanji2(self):
        self.forceStopWait = True
        self.waiting = False
        self.done()
        self.deck = U.getDeck("kanji2")
        self.startStudy()
        
    def studyVocab(self):
        self.forceStopWait = True
        self.waiting = False
        self.done()
        self.deck = U.getDeck("vocab")
        self.startStudy()
    
    def startStudy(self):
        stacks = S.studySet[self.deck.name]
        self.studySet = []
        for s in stacks:
            self.studySet.extend(self.deck.bins[s])
        line = "Studying {0} cards from stack {1}.".format(len(self.studySet),stacks)
        print (line)
        
        self.getAndDisplayNextCard()
        
    def getAndDisplayNextCard(self):
        random.shuffle(self.studySet)
        self.studySet.sort(key=lambda c: c.getTimeToNext())
        self.currentCard = self.studySet[0]
        self.isRevealed = False
        self.wasRevealed = False
        self.cleanStatusFrame()
        
        timeRemaining = self.currentCard.getTimeToNext()
        if timeRemaining>0:
            self.img = None
            self.forceStopWait = False
            self.countdown()
        else:
            if self.deck.name=="kanji2":
                self.mainLabelText.set(self.currentCard.kanji)
            else:
                self.mainLabelText.set(self.currentCard.eng)
            if self.currentCard.image==None:
                self.img = None
            else:
                self.img = PIL.ImageTk.PhotoImage(self.currentCard.getImage())
            self.updateTimeSinceLastSeen()
        self.secondaryLabel.configure(image=self.img)
        self.secondaryLabel.image = self.img

    def summarize(self):
        if self.deck==None:
            return
        self.deck.summarizeSpacedRep(stack=S.studySet[self.deck.name],cards=self.studySet)
        
    def done(self):
        self.forceStopWait = True
        if self.deck != None:
            self.deck.save()
        self.mode = None
        self.deck = None
        self.studySet = None
        self.currentCard = None
        self.mainLabelText.set("Click 'Study Kanji' or 'Study Vocab' to begin!")
        self.img = None
        self.secondaryLabel.configure(image=self.img)
        self.secondaryLabel.image = self.img
        
        self.cleanStatusFrame()
        
    def speak(self):
        if self.currentCard==None:
            return
        if self.deck.name=="kanji":
            return
        t = threading.Thread(target=self.speakThread)
        t.start()
        
    def speakThread(self):
        audio_file = "temp.mp3"
        lang = "en"
        text = self.currentCard.eng
        if self.isRevealed:
            lang = "ja"
            text = self.currentCard.hiragana
        tts = gTTS(text=text, lang=lang)
        tts.save(audio_file)
#        return_code = subprocess.call(["afplay", audio_file])
        playsound.playsound(audio_file)

    
if __name__=="__main__":
    root=tkinter.Tk()
    myApp=FlashCardApp(root)
    root.mainloop()
    try:
        root.destroy()
    except:
        pass