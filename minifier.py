#!/usr/bin/python

import sys

class BashFileIterator:
    def __init__(self, src):
        self.src = src
        self.reset()

    def reset(self):
        self.pos = 0
        self.previousCharacter = ""
        self.insideString = False
        self.insideComment = False

    def getPreviousCharacter(self):
        return self.previousCharacter

    def getNextCharacter(self):
        return self.src[self.pos+1:self.pos+2]

    def getPreviousCharacters(self,n):
        return self.src[max(0,self.pos - n):self.pos]

    def getNextCharacters(self,n):
        return self.src[self.pos+1:self.pos+n+1]

    def getPreviousWord(self):
        word = ''
        i = 1
        while i <= self.pos:
            newWord = self.getPreviousCharacters(i)
            if newWord.isalpha():
                word = newWord
            else:
                return word
            i += 1

    def charactersGenerator(self):
        stringBeginsWith = ""
        escaped = False
        while self.pos < len(self.src):
            ch = self.src[self.pos]
            # handle strings and comments
            if ch == "\\":
                escaped = not escaped
            else:
                if (ch in "\"'`") and not escaped and not self.insideComment:
                    if self.insideString and stringBeginsWith == ch:
                        stringBeginsWith = ""
                        self.insideString = False
                    elif not self.insideString:
                        stringBeginsWith = ch
                        self.insideString = True
                elif ch == "#" and not self.insideString and \
                        not self.previousCharacter == "$" and not self.getPreviousCharacters(2) == "${":
                    self.insideComment = True
                elif ch == "\n" and self.insideComment:
                    self.insideComment = False
                escaped = False
            yield ch
            self.previousCharacter = ch
            self.pos += 1
        raise StopIteration

    def isInsideString(self):
        return self.insideString

    def isInsideComment(self):
        return self.insideComment


def minify(src):
    # first remove all comments
    it = BashFileIterator(src)
    src = "" # result
    for ch in it.charactersGenerator():
        if not it.isInsideComment():
            src += ch

    # second remove empty strings and strip lines
    it = BashFileIterator(src)
    src = "" # result
    emptyLine = True
    previousSpacePrinted = True
    for ch in it.charactersGenerator():
        if it.isInsideString():
            src += ch
        elif ch == "\\" and it.getNextCharacter() == "\n":
            continue
        elif ch in " \t" and not previousSpacePrinted and not emptyLine and \
                not it.getNextCharacter() in " \t\n" and not it.getNextCharacters(2) == "\\\n":
            src += " "
            previousSpacePrinted = True
        elif ch == "\n" and it.getPreviousCharacter() != "\n" and not emptyLine:
                src += ch
                previousSpacePrinted = True
                emptyLine = True
        elif ch not in " \t\n":
            src += ch
            previousSpacePrinted = False
            emptyLine = False

    # third get rid of newlines
    it = BashFileIterator(src)
    src = "" # result
    for ch in it.charactersGenerator():
        if it.isInsideString() or ch != "\n":
            src += ch
        else:
            prevWord = it.getPreviousWord()
            if prevWord in ("then", "do", "else", "in") or it.getPreviousCharacter() in ("{", "(") or \
                it.getPreviousCharacters(2) in ("&&", "||"):
                src += " "
            elif it.getNextCharacter() != "" and it.getPreviousCharacter() != ";":
                src += ";"

    # finaly remove spaces around semicolons
    it = BashFileIterator(src)
    src = "" # result
    for ch in it.charactersGenerator():
        if it.isInsideString():
            src += ch
        elif ch in ' \t' and (it.getPreviousCharacter() == ";" or it.getNextCharacter() == ";"):
            continue
        else:
            src += ch
    
    return src


if __name__ == "__main__":
    # get bash source from file or fron stdin
    src = ""
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as ifile:
            src = ifile.read()
    else:
        src = sys.stdin.read()
    print minify(src)


