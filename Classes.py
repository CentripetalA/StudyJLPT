#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 18:41:06 2018

@author: arinzeokeke
"""

import time
import csv
import random
import json
import Settings as S
import Utils as U
import PIL
import io

class Card:
    maxStudyGroup = S.maxStudyGroup
    def __init__(self,eng="",hiragana="",kanji="",cardType=""):
        if type(eng)==str:
            self.eng = eng
            self.hiragana = hiragana
            self.kanji = kanji
            self.cardType = cardType
            self.reset()
            self.image = None
            self.imageIndex = None
            self.desiredImageIndex = 0

        elif type(eng)==dict:
            self.reset()
            for key in eng:
                setattr(self,key,eng[key])
        
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if self.cardType=="kanji":
            output = self.kanji
        else:
            output = self.hiragana
            if self.kanji!="":
                output += " ["+self.kanji+"]"
        return output
    def __eq__(self,other):
        if type(self)!=type(other):
            return False
        return (self.eng==other.eng) and (self.hiragana==other.hiragana) and (self.kanji==other.kanji)
    def updateCardStudyGroup(self,correct=1):
        self.lastSeen = time.time()
        if correct>0:
            self.increaseStudyGroup()
        elif correct==0:
            self.resetStudyGroup()
        else:
            self.decreaseStudyGroup()
        self.lastSeen = time.time()
    def increaseStudyGroup(self):
        self.timesCorrect += 1
        self.totalCorrect += 1
        self.studyGroup = min(self.maxStudyGroup, self.studyGroup+1)
    def decreaseStudyGroup(self):
        self.ambiguous += 1
        self.studyGroup = max(0, self.studyGroup-1)
    def resetStudyGroup(self):
        self.misses += 1
        self.timesCorrect = 0
        self.studyGroup = 0
        
    def updateCardSpacedRepetition(self,correct):
        prevLastSeen = self.lastSeen
        self.lastSeen = time.time()
        if correct>0:
            if (self.totalCorrect+self.misses+self.almost==0):
                self.timesCorrect += 5 #if correct on first attempt bump it up a couple groups
                print("timesCorrect4:",self.timesCorrect)
            else:
                #if the real wait time for the card is more than the ideal wait time, 
                #bump the card to the bin it would have been for the real wait
                realBin = U.closestWaitLessThan(time.time()-prevLastSeen)
                if realBin>self.timesCorrect:
                    self.timesCorrect = realBin
            if correct==2:
                #easy
                self.timesCorrect += 1
            self.timesCorrect += 1
            self.totalCorrect += 1
        elif correct==-1:
            #almost
            self.almost += 1
            self.timesCorrect //= 2
        elif correct==-2:
            #correct but not confident
            #keep on the same wait scale except if it was a first attempt then bump 2
            if (self.totalCorrect+self.misses+self.almost==0):
                self.timesCorrect += 3 #if correct on first attempt bump it up a couple groups
            self.totalCorrect += 1
        else:
            #incorrect
            self.timesCorrect = 0
            self.misses += 1

    def getTimeToNext(self):
        #lowest numbers are most important
        #negative numbers equal cards past due
        
        #if we haven't seen the card yet, give wait time of 0 (this should prioritize review over new cards)
        if self.totalCorrect+self.misses+self.almost==0:
            return 0
        
        #time remaining = how long we should wait - how long we have waited
        #cap at -1 because all overdue cards should be treated equally and randomized to prevent memorized ordering
        timeIndex = min(self.timesCorrect,len(S.timeToNext))
        timeRemaining = S.timeToNext[timeIndex]-(time.time()-self.lastSeen)
        if timeRemaining<0:
            timeRemaining = -(len(S.timeToNext)-self.timesCorrect) - (1+(1/timeRemaining))
        return timeRemaining
        
    def getTimeSinceLastSeen(self):
        return U.convertSecondsToTimeString(time.time()-self.lastSeen)
    def reset(self):
        self.studyGroup = 0
        self.timesCorrect = 0
        self.misses = 0
        self.totalCorrect = 0
        self.ambiguous = 0
        self.almost = 0
        self.lastSeen = time.time()
    def viewImage(self):
        if self.image==None:
            return
        image = PIL.Image.open(io.BytesIO(bytes.fromhex(self.image)))
        image.show()
        
    def getImage(self):
        if self.image==None:
            return None
        return PIL.Image.open(io.BytesIO(bytes.fromhex(self.image)))
    
    def changePicture(self):
        if self.imageIndex==self.desiredImageIndex:
            self.image = None
            self.imageIndex = None
            self.desiredImageIndex += 1
        im,successful = U.changeOnePicture(self)
        if not successful:
            print ("unable to change the picture for this card.")
        else:
            print ("successfully changed picture")
            
    def revertPicture(self):
        if self.imageIndex==self.desiredImageIndex:
            self.image = None
            self.imageIndex = None
            self.desiredImageIndex = max(0,self.desiredImageIndex-1)
        im,successful = U.changeOnePicture(self)
        if not successful:
            print ("unable to change the picture for this card.")
        else:
            print ("successfully changed picture")
            
    def clearPicture(self):
        self.image = None
        self.imageIndex = None
            
class Deck:
    maxStudyGroup = S.maxStudyGroup
    def __init__(self,name,cards=[],binSize=20,randomize=False):
        self.name = name
        self.binSize = binSize
        self.reset()
        self.addCards(cards,randomize=randomize)
        
    def reset(self):
        self.bins = {}
        self.cards = []

    def __getitem__(self,key):
        return self.cards[key]
        
    def exportDeck(self):
        cardInfo = {}
        for k in self.bins:
            cards = self.bins[k]
            out = []
            for card in cards:
                out.append(vars(card))
            cardInfo[k] = out
        output = {
                "cards": cardInfo,
                "name" : self.name
                }
        return output
    
    def importDeck(self,cardsDict):
        self.reset()
        for k in cardsDict:
            cards = cardsDict[k]
            trueK = int(k)
            for card in cards:
                c = Card(card)
                self.cards.append(c)
                if trueK not in self.bins:
                    self.bins[trueK] = []
                self.bins[trueK].append(c)

    def addCard(self,card):
        self.cards.append(card)
        i = 0
        if i not in self.bins:
            self.bins[i] = []
        while len(self.bins[i])>=self.binSize:
            i += 1
            if i not in self.bins:
                self.bins[i] = []
        self.bins[i].append(card)
    def addCards(self,cards,randomize=True):
        if randomize:
            random.shuffle(cards)
        i = 0
        for card in cards:
            if i not in self.bins:
                self.bins[i] = []
            while len(self.bins[i])>=self.binSize:
                i += 1
                if i not in self.bins:
                    self.bins[i] = []
            self.bins[i].append(card)
            self.cards.append(card)

    def removeCard(self,card):
        if card in self.cards:
            self.cards.remove(card)
            for k in self.bins:
                if card in self.bins[k]:
                    self.bins[k].remove(card)
        
    def importCardsFromFile(self,filename,append=True,randomize=False):
        if not append:
            self.reset()
        cards = []
        fileContent = csv.reader(open(filename,newline='',encoding='utf-8'),delimiter="\t")
        isFirst = True
        for row in fileContent:
            if isFirst:
                isFirst = False
                continue
            if self.name=="vocab":
                cards.append(Card(row[2],row[1],row[0],"vocab"))
            elif self.name=="kanji":
                reading = row[1]+"/"+row[2]
                reading = reading.replace(" ",",")
                cards.append(Card(row[3],reading,row[0],"kanji"))
            else:
                print("cannot import file for this kind of deck")
        self.addCards(cards,randomize=randomize)

    def doneStudying(self,maxScore=10,stack=-1):
        if stack<0:
            for card in self.cards:
                if (card.studyGroup!=self.maxStudyGroup):
                    return False
            return True
        else:
            for card in self.bins[stack]:
                if (card.studyGroup!=self.maxStudyGroup):
                    return False
            return True

    def doneStudyingSpacedRep(self,cards,maxWait=60):
        #the cards should be sorted in order of importance
        if len(cards)>0:
            if cards[0].getTimeToNext()>=maxWait:
                return True
            return False
        return True
        
    def getCardsBelowStudyGroup(self,cards,studyGroup):
        output = []
        for card in cards:
            if card.studyGroup<=studyGroup:
                output.append(card)
        random.shuffle(output)
        return output
    
    def studyStudyGroup(self,stack=-1,show="jpn"):
        if stack<0:
            allCards = self.cards
            line = "Studying {0} cards from full deck.".format(len(allCards))
            print (line)
        else:
            allCards = self.bins[stack]
            line = "Studying {0} cards from stack {1}.".format(len(allCards),stack)
            print (line)
            
        #preview cards:
        for card in allCards:
            print (card,"\t",card.eng)
        for i in range(5):
            print ("-----------")

        session = 0
        done = False
        while not (self.doneStudying(stack=stack) or done):
            sessionCards = self.getCardsBelowStudyGroup(allCards,session%(self.maxStudyGroup+1))
            for currCard in sessionCards:
                if show=="jpn":
                    print (currCard)
                else:
                    print (currCard.eng)
                res = input ("Press enter to show translation...")
                while res in ["summarize"]:
                    if res=="summarize":
                        print ("Session: ",session)
                        self.summarizeStack(stack)
                    res = input ("Press enter to show translation...")
                if res in ["end","done","finish","finished","close","exit"]:
                    done = True
                    break
                else:
                    if show=="jpn":
                        print (currCard,"=",currCard.eng)
                    else:
                        print (currCard.eng,"=",currCard)
                    res = input ("Did you know this word (y/n)? ")
                    while res not in ["y","n","yes","no","0","1","remove","-1"]:
                        res = input ("Did you know this word (y/n)? ")
                    if res=="remove":
                        self.removeCard(currCard)
                    elif res=="-1":
                        val = -1
                        currCard.updateCardStudyGroup(val)
                    else:
                        val = 0
                        if res in ["y","yes","1"]:
                            val = 1
                        currCard.updateCardStudyGroup(val)
            session += 1
        self.summarizeStack(stack)
        
    def studySpacedRep(self,stack=-1,show="eng",maxWait=60,saveWhenDone=True,preview=True):
        allCards = []
        if type(stack)==int:
            if stack<0:
                allCards.extend(self.cards)
                line = "Studying {0} cards from full deck.".format(len(allCards))
                print (line)
            else:
                allCards.extend(self.bins[stack])
                line = "Studying {0} cards from stack {1}.".format(len(allCards),stack)
                print (line)
        elif type(stack)==list or type(stack)==tuple or type(stack)==range:
            for s in stack:
                allCards.extend(self.bins[s])
            line = "Studying {0} cards from stack {1}.".format(len(allCards),stack)
            print (line)
        else:
            print ("Cannot study stack:",stack)
            return
            
        
        #preview cards (more relavant ones toward the top):
        if preview:
            allCards.sort(key=lambda c: c.getTimeToNext())
            for card in allCards:
                if card.getTimeToNext()>5*maxWait:
                    continue
                print (card,"\t",card.eng)
                
            res = input ("Are you ready to start? (y/n)")
            while res not in S.yes:
                res = input ("Are you ready to start? (y/n)")
            U.clear()
        
        random.shuffle(allCards)
        allCards.sort(key=lambda c: c.getTimeToNext())
        while not self.doneStudyingSpacedRep(cards=allCards,maxWait=maxWait):
            currCard = allCards[0]
            waitTime = currCard.getTimeToNext()
            waitCounter = 1
            while waitTime>0:
                print("Next card has a wait time of {0} seconds".format(round(waitTime)),flush=True)
                time.sleep(min(2*waitCounter,waitTime))
                waitTime = currCard.getTimeToNext()
                waitCounter = min(waitCounter+1,5)
            if show=="jpn":
                visible = currCard
            else:
                visible = currCard.eng
            res = input ("Press enter to show translation for '{0}'...".format(visible))
            while res in ["summarize"]:
                if res=="summarize":
                    self.summarizeSpacedRep(stack=stack,cards=allCards)
                    res = input ("Done? (y/n)")
                    while res not in S.yes:
                        res = input ("Done? (y/n)")
                    U.clear()
                res = input ("Press enter to show translation for '{0}'...".format(visible))
            if res in S.stop:
                break
            if show=="jpn":
                print (currCard,"=",currCard.eng)
            else:
                print (currCard.eng,"=",currCard)
            res = input ("Did you know this word (y/n)? ")
            while res not in S.yes+S.no+S.stop+["remove"]:
                res = input ("Did you know this word (y/n)? ")
            if res=="remove":
                self.removeCard(currCard)
            else:
                if res in S.stop:
                    break
                val = 0
                if res in S.yes:
                    val = 1
                currCard.updateCardSpacedRepetition(val)
            allCards.sort(key=lambda c: c.getTimeToNext())
            U.clear()
        self.summarizeSpacedRep(stack=stack,cards=allCards)
        if saveWhenDone:
            print("Saving...")
            self.save()
            print("Done saving.")
        
    def summarize(self,maxShow=-1):
        output = ""
        line = "{0} stacks of cards. At most {1} cards allowed per stack".format(len(self.bins), self.binSize)
        output += line + "\n"
        
        line = "{0} cards in {1} deck. Showing {2} cards".format(len(self.cards),self.name, maxShow)
        output += line + "\n"

        count = 0
        over8hours = 0
        for card in self.cards:
            count += 1
            if maxShow>=0 and count>maxShow:
                break
            if card.getTimeToNext()>=28800:
                over8hours += 1
                continue
            content = (card,card.totalCorrect,card.timesCorrect,card.misses,card.studyGroup,round(card.getTimeToNext(),2))
            line = "{0} \ttotal correct:{1} \tconsecutive correct:{2} \tmisses:{3} \tstudy group:{4}. \t{5} seconds until next appearance.".format(*content)
            output += line + "\n"
        line = "plus "+over8hours+" items with a wait time over 8 hours"
        output += line + "\n"
    def summarizeStack(self,stack):
        if stack<0:
            return
        line = "{0} stacks of cards. At most {1} cards allowed per stack. Max study group is {2}".format(len(self.bins), self.binSize,self.maxStudyGroup)
        print (line)
        
        line = "Showing cards from stack {0}".format(stack)
        print (line)
        cards = self.bins[stack]
        count = 0
        for card in cards:
            count += 1
            content = (card,card.totalCorrect,card.timesCorrect,card.misses,card.studyGroup)
            line = "{0} \tstudy group:{4} \ttotal correct:{1} \tconsecutive correct:{2} \tmisses:{3} \t".format(*content)
            print (line)
    def summarizeSpacedRep(self,stack,cards=None):
        if cards==None:
            cards = []
            if type(stack)==int:
                if stack<0:
                    cards.extend(self.cards)
                else:
                    cards.extend(self.bins[stack])
            elif type(stack)==list:
                for s in stack:
                    cards.extend(self.bins[s])
            else:
                print ("Cannot study stack:",stack)
                return
        output = "Studying {0} cards using spaced repetition technique. These include cards from stack(s) {1}.\n".format(len(cards),stack)
        extra = 0
        due = 0
        for card in cards:
            if card.getTimeToNext()>=28800:
                extra += 1
                continue
            if card.getTimeToNext()<=0:
                due += 1
            content = (card.eng,round(card.getTimeToNext(),2))
            output += "{0} \t{1} seconds until next appearance.\n".format(*content)
        output += "plus {0} extra items with more than 8 hour wait time.\n".format(extra)
        output += "{0} cards due for study.\n".format(due)
        print (output)
        return output
        
    
    def save(self):
        filename = S.saveFileNames[self.name]
        content = self.exportDeck()
        with open(filename, 'w', encoding='utf-8') as outfile:
            json.dump(content, outfile, ensure_ascii=False, indent=2)
        
    def load(self):
        filename = S.saveFileNames[self.name]
        with open(filename, 'r', encoding="utf-8") as outfile:
            content = json.load(outfile)
        self.name = content["name"]
        self.importDeck(content["cards"])