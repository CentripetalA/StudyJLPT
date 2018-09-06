import Utils as U
        
if __name__=="__main__":
    print ("勉強しましょう!")
    vocabDeck = U.getDeck("vocab")
    kanjiDeck = U.getDeck("kanji")
    
#    vocabDeck.summarize(20)
#    kanjiDeck.summarize(20)
    
    studyVocab = False
    studyKanji = False

    if studyVocab:
        U.study(vocabDeck,preview=False)
    if studyKanji:
        U.study(kanjiDeck,preview=False)

