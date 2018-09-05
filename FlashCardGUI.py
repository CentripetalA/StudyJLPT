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
        
        #buttons
        self.buttonFrame = tkinter.Frame(master)
        self.buttonFrame.grid(row=2,column=0)
        
        self.showHideButton = tkinter.Button(self.buttonFrame,text="Show/Hide",command=self.showHide)
        self.showHideButton.grid(row=0,column=0, sticky=tkinter.EW)
        
        self.correctButton = tkinter.Button(self.buttonFrame,text="Correct",command=self.correct)
        self.correctButton.grid(row=0,column=1, sticky=tkinter.EW)
        
        self.incorrectButton = tkinter.Button(self.buttonFrame,text="Incorrect",command=self.incorrect)
        self.incorrectButton.grid(row=0,column=2, sticky=tkinter.EW)
        
        self.studyKanjiButton = tkinter.Button(self.buttonFrame,text="Study Kanji",command=self.studyKanji)
        self.studyKanjiButton.grid(row=1,column=0, sticky=tkinter.EW)
        
        self.studyVocabButton = tkinter.Button(self.buttonFrame,text="Study Vocab",command=self.studyVocab)
        self.studyVocabButton.grid(row=1,column=1, sticky=tkinter.EW)
        
#        self.preview = tkinter.IntVar()
#        self.previewCheckBox = tkinter.Checkbutton(self.buttonFrame, text="Preview",variable=self.preview)
#        self.previewCheckBox.grid(row=1,column=2, sticky=tkinter.EW)
#        
        self.summarizeButton = tkinter.Button(self.buttonFrame,text="Summarize",command=self.summarize)
        self.summarizeButton.grid(row=1,column=2, sticky=tkinter.EW)
        
        self.speakButton = tkinter.Button(self.buttonFrame,text="Speak",command=self.speak)
        self.speakButton.grid(row=2,column=0, sticky=tkinter.EW)
        
        self.doneButton = tkinter.Button(self.buttonFrame,text="Done",command=self.done)
        self.doneButton.grid(row=2,column=1, sticky=tkinter.EW)

        self.quitButton = tkinter.Button(self.buttonFrame,text="Quit",command=master.quit)
        self.quitButton.grid(row=2,column=2, sticky=tkinter.EW)
        
    def quitApp(self):
        self.done()
        self.master.quit()
    def showHide(self):
        if self.waiting:
            return
        if self.currentCard==None:
            return
        if self.isRevealed:
            self.mainLabelText.set(self.currentCard.eng)
        else:
            self.mainLabelText.set(str(self.currentCard))
        self.isRevealed = not self.isRevealed
    def correct(self):
        self.updateCard(1)
        
    def incorrect(self):
        self.updateCard(0)
        
    def updateCard(self,value):
        if self.waiting:
            return
        if self.currentCard==None:
            return
        if not self.isRevealed:
            return
        self.currentCard.updateCardSpacedRepetition(value)
        self.getAndDisplayNextCard()
    
    def countdown(self):
        if self.forceStopWait:
            self.waiting=False
            return
        timeRemaining = self.currentCard.getTimeToNext()
        if timeRemaining<=0:
            self.waiting = False
            self.mainLabelText.set(self.currentCard.eng)
            #display card
            return
        else:
            self.waiting = True
            self.mainLabelText.set("Next card will display after {0} seconds!".format(round(timeRemaining)))
            self.master.after(1000,self.countdown)

    def studyKanji(self):
        self.forceStopWait = True
        self.done()
        self.deck = U.getDeck("kanji")
        self.startStudy()
        
    def studyVocab(self):
        self.forceStopWait = True
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

        timeRemaining = self.currentCard.getTimeToNext()
        if timeRemaining>0:
            self.forceStopWait = False
            self.countdown()
        else:
            self.mainLabelText.set(self.currentCard.eng)
        
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
        return_code = subprocess.call(["afplay", audio_file])

    
if __name__=="__main__":
    root=tkinter.Tk()
    myApp=FlashCardApp(root)
    root.mainloop()
    try:
        root.destroy()
    except:
        pass