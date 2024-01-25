#pylint:disable= C0114, C0115, C0116, W0401, W0614, W0621, W0108, W0212, W0201, W0613, C0209, R0915, W0122
#pylint:disable= E1101

import pytest
import natlink
# from natlinkcore import gramparser
from natlinkcore import natlinkutils

def setup():
    natlink.natConnect()
def teardown():
    natlink.natDisconnect()


class MYTESTError(Exception):
    """test error"""


def doTestRecognition(words, shouldWork=1):
    if shouldWork:
        natlink.recognitionMimic(words)
        return True
    if doTestForException(natlink.MimicFailed,"natlink.recognitionMimic(words)",locals()):
        return True
    return False

def doTestForException(exceptionType,command,localVars=None):
    if localVars is None:
        localVars = {}
    try:
        exec(command,globals(),localVars)
    except exceptionType:
        return True
    raise MYTESTError('Expecting an exception to be raised calling %s'% repr(command))

def doTestActiveRules(gram, expected):
    """gram must be a grammar instance, sort the rules to be expected and got
    """
    got = gram.activeRules
    if not isinstance(got, dict):
        raise MYTESTError('doTestActiveRules, activeRules should be a dict, not: %s (%s)'% (repr(got), type(got)))
    if not isinstance(expected, dict):
        raise MYTESTError('doTestActiveRules, expected should be a dict, not: %s (%s)'% (repr(expected), type(expected)))
    
    assert expected == got, 'Active rules not as expected:\nexpected: %s, got: %s'%(expected, got)

def doTestValidRules(self, gram, expected):
    """gram must be a grammar instance, sort the rules to be expected and got
    """
    got = gram.validRules
    if not isinstance(got, list):
        raise MYTESTError('doTestValidRules, activeRules should be a list: %s (%s)'% (repr(got), type(got)))
    if not isinstance(expected, list):
        raise MYTESTError('doTestValidRules, expected should be a list, not: %s (%s)'% (repr(expected), type(expected)))
    got.sort()
    expected.sort()
    
    assert expected == got, 'Valid rules not as expected:\nexpected: %s, got: %s'%(expected, got)

class TTTestGrammar(natlinkutils.GrammarBase):
    """Create a simple command grammar.  This grammar simply gets the results
       of the recognition and saves it in member variables.  It also contains
       code to check for the results of the recognition.
    """

    def __init__(self):
        natlinkutils.GrammarBase.__init__(self)
        self.resetExperiment()

    def resetExperiment(self):
        self.sawBegin = 0
        self.recogType = None
        self.words = []
        self.fullResults = []
        self.error = None
        self.nTries = 0

    def gotBegin(self,moduleInfo):
        if self.sawBegin > self.nTries:
            self.error = 'Command grammar called gotBegin twice'
        self.sawBegin += 1
        if moduleInfo != natlink.getCurrentModule():
            self.error = 'Invalid value for moduleInfo in GrammarBase.gotBegin'

    def gotResultsObject(self,recogType,resObj):
        if self.recogType:
            self.error = 'Command grammar called gotResultsObject twice'
        self.recogType = recogType

    def gotResults(self,words,fullResults):
        if self.words:
            self.error = 'Command grammar called gotResults twice'
        self.words = words
        self.fullResults = fullResults

    def checkExperiment(self,sawBegin,recogType,words,fullResults):
        if self.error:
            raise MYTESTError(self.error)
        if self.sawBegin != sawBegin:
            raise MYTESTError('Unexpected result for GrammarBase.sawBegin\n  Expected %d\n  Saw %d'%(sawBegin,self.sawBegin))
        if self.recogType != recogType:
            raise MYTESTError('Unexpected result for GrammarBase.recogType\n  Expected %s\n  Saw %s'%(recogType,self.recogType))
        if self.words != words:
            raise MYTESTError('Unexpected result for GrammarBase.words\n  Expected %s\n  Saw %s'%(repr(words),repr(self.words)))
        if self.fullResults != fullResults:
            raise MYTESTError('Unexpected result for GrammarBase.fullResults\n  Expected %s\n  Saw %s'%(repr(fullResults),repr(self.fullResults)))
        self.resetExperiment()


def test_grammarrules():
    testGram = TTTestGrammar()
    testRecognition = doTestRecognition

    # Activate the grammar and try a test recognition
    testGram.load('<Start> exported = hello there;')
    testGram.activateAll()
    testRecognition(['hello','there'])
    testGram.checkExperiment(1,'self',['hello','there'],[('hello','Start'),('there','Start')])

    # With the grammar deactivated, we should see nothing.  But to make this
    # work we need another grammar active to catch the recognition.
    otherGram = TTTestGrammar()
    otherGram.load('<Start> exported = hello there;')
    otherGram.activateAll(window=0)

    testGram.deactivateAll()
    testRecognition(['hello','there'])
    testGram.checkExperiment(1,None,[],[])

    testGram.unload()

   #This fails testGram.checkExperiment(1,'other',[],[])
   
    testGram.resetExperiment()
            
if __name__ == "__main__":
    pytest.main(['test_grammarrules.py'])
