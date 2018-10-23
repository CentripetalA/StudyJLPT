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

def printCardsSortedByTrouble2(deckname):
    deck = getDeck(deckname)
    allCards = []
    for s in S.studySet[deck.name]:
        allCards.extend(deck.bins[s])
        
    allCards.sort(key=lambda c: c.timesCorrect, reverse=False)
    
    output = "Kanji\tHiragana\tEnglish\tSuccessRate\n"
    
    for c in allCards:
        content = (c.kanji,c.hiragana,c.eng,round(c.totalCorrect/(c.misses+c.totalCorrect),2))
        output += "{0}\t{1}\t{2}\t{3}\n".format(*content)
        
    fileName = "trouble2"+deckname+".tsv"
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
    
def convertSecondsToTimeString(timeSeconds,valuesToShow=3):
    
    timeBoxes = [1,60,60,24,30,12]
    timeBoxesString = ["second(s)","minute(s)","hour(s)","day(s)","month(s)","year(s)"]
    timeVal = timeSeconds
    finalTimes = []
    for i in range(len(timeBoxes)):
        isDone = False
        if (i==(len(timeBoxes)-1)) or (not timeVal//timeBoxes[i+1]):
            timeVal2 = timeVal
            isDone = True
        elif timeVal//timeBoxes[i+1]:
            timeVal2 = timeVal%timeBoxes[i+1]
            timeVal = timeVal//timeBoxes[i+1]
        timeVal2 = round(timeVal2)
        timeString = ("{0} "+timeBoxesString[i]).format(timeVal2)
        finalTimes.append(timeString)
        
        if isDone:
            break
    finalTimes.reverse()
    return " ".join(finalTimes[0:valuesToShow])

def closestWaitLessThan(timeSeconds):
    for i in range(len(S.timeToNext)):
        if timeSeconds<S.timeToNext[i]:
            return max(0,i-1)
    return i

def prepareKanjiDict2():
    hiraganaSet = set()
    kanjiSet = set()
    
    with open(S.knownChars,encoding="utf-8") as f:
        lineIndex = 0
        for line in f:
            for c in line:
                if lineIndex<=17:
                    hiraganaSet.add(c)
                else:
                    kanjiSet.add(c)
            lineIndex += 1
                
    words = []
    with open(S.fullVocab,encoding="utf-8") as f:
        for line in f:
            words.append(line[:-1].split("\t"))
    words = words[1:]
    print (len(words),"words at the loaded.")
    size = list(range(len(words)))
    size.reverse()
    for i in size:
        w = words[i]
        if w[0]=="":
            words.pop(i)
            continue
        
        wordOk = True
        for c in w[0]:
            if (c not in hiraganaSet) and (c not in kanjiSet):
                wordOk = False
                break
        if not wordOk:
            words.pop(i)
            continue
        
        wordOk = False
        for c in w[0]:
            if c in kanjiSet:
                wordOk = True
                break
        if not wordOk:
            words.pop(i) 
            continue
    print (len(words),"words remaining.")
    
    #make cards
    cards = []
    for w in words:
        c = C.Card(eng=w[2],hiragana=w[1],kanji=w[0],cardType="kanji2")
        cards.append(c)
    
    #make deck
    deck = C.Deck("kanji2",cards=cards,binSize=20,randomize=True)
    deck.save()
    return deck