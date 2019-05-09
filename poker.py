from random import randint   
from random import shuffle
from collections import defaultdict
from copy import deepcopy
from enum import Enum

VALS = '23456789TJQKA'
SUITS = 'SCDH'
HANDSIZE = 5
BOARDSIZE = 5
SIMNUM = 20000
PAD = " "*150


# hand strength
STRAIGHTFLUSH = 8
QUADS = 7
FULLHOUSE = 6
FLUSH = 5
STRAIGHT = 4
TRIPS = 3
TWOPAIR = 2
PAIR = 1
HIGHCARD = 0



class hStrength(Enum):
    STRAIGHTFLUSH = 8
    QUADS = 7
    FULLHOUSE = 6
    FLUSH = 5
    STRAIGHT = 4
    TRIPS = 3
    TWOPAIR = 2
    PAIR = 1
    HIGHCARD = 0

class card:

    def __init__(self, cardString):
        if len(cardString) != 2 or cardString[0] not in VALS or \
           cardString[1] not in SUITS:
            print("Invalid card!")
            exit(0)
        self.value = cardString[0]
        self.suit = cardString[1]
        
    def __str__(self):
        return self.value + self.suit
    def __repr__(self):
        return self.value + self.suit
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    
class deck:
    cards = []
    
    def __init__(self):
        for i in VALS:
            for j in SUITS:
                self.cards.append(card(i+j))
        #shuffle(cards)
        
    def deal(self, cardString=None):
        if cardString is not None:
            myCard = card(cardString)
            for i in range(len(self.cards)):
                if self.cards[i] == myCard:
                    return self.cards.pop(i)
            print("Card duplicate")
            exit(0)
        # this can pop out of range somehow FIX
        return self.cards.pop(randint(0,len(self.cards)-1))

    def simulate(self, num):
        '''returns list of cards which have been "dealt randomly"'''
        shuffle(deck.cards)
        return deck.cards[:num]
        




def getValOrder(card):
    return valOrder(card.value)

def isFlush(cards):
    returnCards = calcFlush(cards)
    if not returnCards:
        return False
    return list(map(getValOrder, returnCards))[:HANDSIZE] #what a meme

def calcFlush(cards):
    '''returns the 5 cards used to make a flush, if a flush is made. Used within isFlush which returns consistent output type.
       Assumes no two flushes of different suits can be made'''
    suits = defaultdict(int)
    flushSuit = None
    for card in cards:
        suits[card.suit] += 1
        if suits[card.suit] >= HANDSIZE:
            flushSuit = card.suit
    if flushSuit == None:
        return False
    returnCards = list(filter(lambda x: x.suit == flushSuit, cards))
    returnCards.sort(key=getValOrder, reverse=True)
    return returnCards
    
def makeValDict(cards):
    valDict = defaultdict(int)
    for i in cards:
        valDict[i.value] += 1
    return valDict

def isOfaKind(valDict, dups):
    ''' '''
    paired = []
    kickers = []
    for val, freq in valDict.items():
        if freq >= dups:
            paired.append(val)
        else:
            kickers.append(val)
    if not paired:
        return False
    paired.sort(key=valOrder, reverse=True)
    kickers.sort(key=valOrder, reverse=True)
    cardVals = paired[:1] + kickers[:HANDSIZE-dups]
    '''return list(map(valOrder, cards))''' #converts vals into ints for comparison
    return list(map(valOrder, cardVals))  # do this to everything!!!
    

def isFull(valDict):
    '''returns a tuple of the value of three of a kind then two of a kind
    if full house is valid, else returns false'''
    threes = []
    twos = []
    for val, freq in valDict.items():
        if freq >= 3:
            threes.append(val)
        if freq == 2:
            twos.append(val)
    if len(threes) < 1:
        return False
    cardVals = sorted(threes, key=valOrder, reverse=True) + sorted(twos, key=valOrder, reverse=True)
    if len(cardVals) < 2:
        return False
    return list(map(valOrder, cardVals[:2]))
    
def is2Pair(valDict):
    '''returns a sorted tuple of the two highest pairs available 
    if two pair is valid, else returns false'''
    twos = []
    kickers = []
    for val, freq in valDict.items():
        if freq >= 2:
            twos.append(val)
        else:
            kickers.append(val)
    if len(twos) < 2:
        return False
    twos.sort(key=valOrder, reverse=True)
    kickers = twos[2:] + kickers
    kickers.sort(key=valOrder, reverse=True) 
    cardVals = twos[:2] + kickers
    return list(map(valOrder, cardVals[:3]))
            
def valOrder(val):
    return VALS.index(val)
    

def isStraight(valDict):
    vals = list(valDict.keys())
    vals.sort(key=valOrder, reverse=True)
    if vals and vals[0] == 'A':
        vals.append('A')
    for i in range(len(vals)-HANDSIZE+1):
        if isSeq(vals[i:i+HANDSIZE]):
            return list(map(valOrder, vals[i:i+HANDSIZE]))
        
    return False
        
def isSeq(vals):
    '''identifies whether or not a list of values are in susequent order (a straight)'''
    valString = ''
    for i in vals:
        valString = i + valString
        #print(valString)
    if valString in VALS or valString == '5432A':
        return True
    return False
    
def isStraightFlush(cards):
    flushedCards = calcFlush(cards)
    if not flushedCards:
        return False
    return isStraight(makeValDict(flushedCards))


def isHigh(vals):

    return list(map(valOrder, sorted(vals.keys(), key=valOrder, reverse=True)[:HANDSIZE]))

def rankHand(cards):
    '''returns a list of numbers which represents the strength of the best possible hand made out of all of cards
       first number represents hand strength, the rest reperesent values of cards/kickers'''
    vals = makeValDict(cards)
    #print(vals)
    # checks for straight flush
    handType = isStraightFlush(cards)
    if handType:
        handType.insert(0, STRAIGHTFLUSH)
        return handType

    # checks for quads
    handType = isOfaKind(vals, 4)
    if handType:
        handType.insert(0, QUADS)
        return handType
    
    # checks for full house
    handType = isFull(vals)
    if handType:
        handType.insert(0, FULLHOUSE)
        return handType
    
    # checks for flush
    handType = isFlush(cards)
    if handType:
        handType.insert(0, FLUSH)
        return handType
    
    # checks for straight
    handType = isStraight(vals)
    if handType:
        handType.insert(0, STRAIGHT)
        return handType
    
    # checks for trips
    handType = isOfaKind(vals, 3)
    if handType:
        handType.insert(0, TRIPS)
        return handType
    
    # checks for two pair
    handType = is2Pair(vals)
    if handType:
        handType.insert(0, TWOPAIR)
        return handType


    # checks for pair
    handType = isOfaKind(vals, 2)
    if handType:
        handType.insert(0, PAIR)
        return handType

    # must be high card
    handType = isHigh(vals)
    handType.insert(0, HIGHCARD)
    print(handType)
    return handType
    







deck = deck()
hands = []

input("Before we begin, put caps lock on or you'll screw yourself over (trust me)")
input("You ready?")

handNum = int(input("how many players would you like? "))
print(f"Type in the hands you want for each player.\nType two characters: a value chosen from '{VALS}' then a suit chosen from '{SUITS}'. Note that for a ten write 'T'")

for i in range(handNum):
    print(f"Player {i+1}:")
    card1 = deck.deal(input())
    card2 = deck.deal(input())
    hands.append([card1, card2])

print("Would you like a flop? type Y/N")
while True:
    flop = input()
    if flop in 'yYnN' and len(flop) == 1:
        break
    print("uhhhhhh try typing Y or N maybe?")

if flop in 'Yy':
    print("Type the three flop cards separated by an enter")
    comCards = []
    for i in range(3):
        comCards.append(deck.deal(input()))
    turn = input("If you also want the turn entered in, type another card. Otherwise press enter ")
    if turn:
        comCards.append(deck.deal(turn))
        river = input("If you also want the river entered in, type another card. Otherwise press enter ")
        if river:
            comCards.append(deck.deal(river))
            input("Really?? This is not a very interesting exercise if you want a river in too, but I guess if you need help telling who has what hand I guess that's fine")
else:
    comCards = []

print("\nthe layout: ")
for hand in hands:
    print(f"{hand[0]} {hand[1]} ")

print("\nCommunity cards:")
for card in comCards:
    print(card, end=' ')
if not comCards:
    print("None", end='')
print("\n")

freqDicts = []
for i in range(handNum):
    freqDicts.append(defaultdict(int))
winTally = [0] * (handNum + 1)



if len(comCards) == BOARDSIZE:
    SIMNUM = 1
#print(f"com cards {comCards}")
for i in range(SIMNUM):
    comCardsTemp = comCards + deck.simulate(BOARDSIZE - len(comCards))
    handStrengths = []
    for j in range(handNum):
        hand = hands[j]
        strength = rankHand(hand + comCardsTemp)
        handStrengths.append(strength)
        freqDicts[j][strength[0]] += 1
    if handNum > 1 and sorted(handStrengths, reverse=True)[0] == sorted(handStrengths, reverse=True)[1]:
        winTally[-1] += 1
    else:
        winTally[handStrengths.index(max(handStrengths))] += 1

'''for i in range(handNum):
    print(freqDicts[i])
print(f"win tally : {winTally}")'''

print("              ", end="")
for i in range(STRAIGHTFLUSH+1):
    print("{:<15}".format(hStrength(i).name), end ='')
print("  win %")
for i in range(handNum):
    print(f"Player {i+1}:     ", end="")
    for j in range(STRAIGHTFLUSH+1):
        print("{:<15}".format(freqDicts[i][j]*100/SIMNUM), end="")
    print(" ", winTally[i]*100/SIMNUM)

print(f"{PAD} {winTally[-1]*100/SIMNUM} (tie %)")
# print(hands)

print("")

input("\n\nPlease comment on your experience. Or just say it aloud, no one's reading it. \nLots of Love. Luca xx ")
