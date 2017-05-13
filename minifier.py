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
        self._CBVE_counter = 0  # CurlyBracesVariableExpansion
        self._stringBeginsWith = ""

    def getPreviousCharacter(self):
        return self.previousCharacter

    def getNextCharacter(self):
        return self.src[self.pos + 1:self.pos + 2]

    def getPreviousCharacters(self, n):
        return self.src[max(0, self.pos - n):self.pos]

    def getNextCharacters(self, n):
        return self.src[self.pos + 1:self.pos + n + 1]

    def getPreviousWord(self):
        word = ''
        i = 1
        while i <= self.pos:
            newWord = self.getPreviousCharacters(i)
            if not newWord.isalpha():
                break
            word = newWord
            i += 1
        return word

    def getNextWord(self):
        word = ''
        i = 1
        while self.pos + i < len(self.src):
            newWord = self.getNextCharacters(i)
            if not newWord.isalpha():
                break
            word = newWord
            i += 1
        return word

    def skipNextCharacter(self):
        self.pos += 1

    def charactersGenerator(self):
        self._stringBeginsWith = ""
        escaped = False
        while self.pos < len(self.src):
            ch = self.src[self.pos]
            # handle strings and comments
            if ch == "\\":
                escaped = not escaped
            else:
                # if (ch in "\"'`") and not escaped and not self.insideComment:
                if (ch in "\"'") and not escaped and not self.insideComment:
                    if self.insideString and self._stringBeginsWith == ch:
                        self._stringBeginsWith = ""
                        self.insideString = False
                    elif not self.insideString:
                        self._stringBeginsWith = ch
                        self.insideString = True
                elif ch == "#" and not self.isInsideStringOrCBVE() and not self.previousCharacter == "$":
                    self.insideComment = True
                elif ch == "\n" and self.insideComment:
                    self.insideComment = False
                elif ch == '{' and self.previousCharacter == '$' and not self.insideComment and \
                        not self.isInsideSingleQuotedString() and not self.isInsideCBVE():
                    self._CBVE_counter = 1
                elif ch == '{' and not self.isInsideSingleQuotedString() and self.isInsideCBVE():
                    self._CBVE_counter += 1
                elif ch == '}' and not self.isInsideSingleQuotedString() and self.isInsideCBVE():
                    self._CBVE_counter -= 1
                escaped = False
            yield ch
            self.previousCharacter = ch
            self.pos += 1
        raise StopIteration

    def isInsideString(self):
        return self.insideString

    def isInsideDoubleQuotedString(self):
        return self.insideString and self._stringBeginsWith == '"'

    def isInsideSingleQuotedString(self):
        return self.insideString and self._stringBeginsWith == "'"

    def isInsideComment(self):
        return self.insideComment

    def isInsideCBVE(self):
        return self._CBVE_counter > 0

    def isInsideStringOrCBVE(self):
        return self.insideString or self.isInsideCBVE()


def minify(src):
    # first remove all comments
    it = BashFileIterator(src)
    src = ""  # result
    for ch in it.charactersGenerator():
        if not it.isInsideComment():
            src += ch

    # second remove empty strings and strip lines
    it = BashFileIterator(src)
    src = ""  # result
    emptyLine = True
    previousSpacePrinted = True
    for ch in it.charactersGenerator():
        if it.isInsideStringOrCBVE():
            src += ch
        elif ch == "\\" and it.getNextCharacter() == "\n":
            it.skipNextCharacter()
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
    src = ""  # result
    for ch in it.charactersGenerator():
        if it.isInsideStringOrCBVE() or ch != "\n":
            src += ch
        else:
            prevWord = it.getPreviousWord()
            nextWord = it.getNextWord()
            if prevWord in ("then", "do", "else", "in") or it.getPreviousCharacter() in ("{", "(") or \
                            it.getPreviousCharacters(2) in ("&&", "||"):
                src += " "
            elif nextWord in ("esac",) and it.getPreviousCharacters(2) != ';;':
                src += ';;'
            elif it.getNextCharacter() != "" and it.getPreviousCharacter() != ";":
                src += ";"

    # finaly remove spaces around semicolons
    it = BashFileIterator(src)
    src = ""  # result
    for ch in it.charactersGenerator():
        if it.isInsideStringOrCBVE():
            src += ch
        elif ch in ' \t' and (it.getPreviousCharacter() == ";" or it.getNextCharacter() == ";"):
            continue
        else:
            src += ch

    return src


if __name__ == "__main__":
    # get bash source from file or from stdin
    src = ""
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as ifile:
            src = ifile.read()
    else:
        src = sys.stdin.read()
    print minify(src)
