#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 18:42:41 2018

@author: arinzeokeke
"""
import Classes as C
import Settings as S
import requests
import PIL
import io

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

def getCardImage(card,imageIndex=0):
    imageURL = ""
    searchText = card.kanji
    if searchText=="":
        searchText = card.hiragana
    url = "https://www.google.com/search?q="+searchText+"&tbm=isch"
    response = requests.get(url)
    if not response.ok:
        print ("search response not ok")
        return response, False
    content = str(response.content)
    pieces = content.split("<img")[1:]
    imageURL = pieces[min(imageIndex,len(pieces)-1)].split("src=\"")[1].split("\"")[0]
    response = requests.get(imageURL)
    if not response.ok:
        print ("image response not ok")
        return response, False
    return response.content.hex(), True

def addImagesToAllCards(deck):
    count = 0
    for c in deck:
        print("{0} out of {1} done".format(count,len(deck.cards)))
        count += 1
        resp,successful = changeOnePicture(c)
        if not successful:
            return resp,successful
        
    print ("done")
    return deck,True

def changeOnePicture(card):
    if (card.imageIndex==card.desiredImageIndex):
        return card,True
    im,successful = getCardImage(card,card.desiredImageIndex)
    if not successful:
        return im,False
    card.image = im
    card.imageIndex = card.desiredImageIndex
    return card,True
    
    
