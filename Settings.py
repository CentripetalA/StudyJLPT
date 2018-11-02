#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  1 20:12:20 2018

@author: arinzeokeke
"""

maxStudyGroup=2
labels     = ("5 seconds","25 seconds","2 minutes","10 minutes","1 hour","5 hours","1 day",   "5 days",   "10 days",   "25 days",   "2 months",    "4 months",     "1 years",     "2 years")
timeToNext = (5,          25,          2*60,       10*60,       1*60*60, 5*60*60,  1*24*60*60, 5*24*60*60, 10*24*60*60, 25*24*60*60, 2*30*24*60*60, 4*30*24*60*60, 1*365*24*60*60, 2*365*24*60*60)
yes = ["y","yes","1"]
no = ["n","no","0"]
stop = ["end","done","finish","finished","close","exit","quit"]

fullVocab="Vocab.tsv"
trimVocab="VocabTrim.tsv"
fullKanji="Kanji.tsv"
trimKanji="KanjiTrim.tsv"
wordList = {"vocab":trimVocab,"kanji":trimKanji}

studySet = {"vocab":range(91),"kanji":range(30),"kanji2":range(78)}

saveFileNames = {"vocab":"savedVocabDeck.json","kanji":"savedKanjiDeck.json","kanji2":"savedKanji2Deck.json"}


knownChars = "charactersShouldKnow.txt"