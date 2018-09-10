#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  1 20:12:20 2018

@author: arinzeokeke
"""

maxStudyGroup=2
# 5 seconds, 25 seconds, 2 minutes, 10 minutes, 1 hour, 5 hours, 1 day, 5 days, 25 days, 4 months, and 2 years
timeToNext = (5,25,2*60,10*60,1*60*60,5*60*60,1*24*60*60,5*24*60*60,25*24*60*60,4*30*24*60*60,2*365*24*60*60)
yes = ["y","yes","1"]
no = ["n","no","0"]
stop = ["end","done","finish","finished","close","exit","quit"]

fullVocab="Vocab.tsv"
trimVocab="VocabTrim.tsv"
fullKanji="Kanji.tsv"
trimKanji="KanjiTrim.tsv"
wordList = {"vocab":trimVocab,"kanji":trimKanji}

studySet = {"vocab":range(12),"kanji":range(10)}

saveFileNames = {"vocab":"savedVocabDeck.json","kanji":"savedKanjiDeck.json"}