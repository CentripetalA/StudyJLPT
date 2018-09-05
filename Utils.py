#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 18:42:41 2018

@author: arinzeokeke
"""
import Classes as C
import Settings as S

def clear():
    print ("\n"*50)
    
def getDeck(name):
    deck = C.Deck(name)
    deck.load()
    return deck

def initializeDeck(name):
    deck = C.Deck(name)
    filename = S.wordList[name]
    deck.importCardsFromFile(filename,append=False,randomize=True)
    return deck

def study(deck,preview=True):
    deck.studySpacedRep(S.studySet[deck.name],show="eng",maxWait=60,saveWhenDone=True,preview=preview)
    
def printCardsSortedByTrouble(deckname):
    deck = getDeck(deckname)
    allCards = []
    for s in S.studySet[deck.name]:
        allCards.extend(deck.bins[s])
        
    allCards.sort(key=lambda c: (c.totalCorrect/(c.misses+c.totalCorrect)), reverse=False)
    
    output = "Kanji\tHiragana\tEnglish\tSuccessRate\n"
    
    for c in allCards:
        content = (c.kanji,c.hiragana,c.eng,round(c.totalCorrect/(c.misses+c.totalCorrect),2))
        output += "{0}\t{1}\t{2}\t{3}\n".format(*content)
        
    fileName = "trouble"+deckname+".tsv"
    with open(fileName,"w", encoding="utf-8") as f:
        f.write(output)
        
    print (output)
    return output