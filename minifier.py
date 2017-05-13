#!/usr/bin/python

import sys


class BashFileIterator:
    def __init__(self, src):
        self.src = src
        self.reset()

    def reset(self):
        self.pos = 0
        self.insideString = False
        self.insideComment = False
        self.insideHereDoc = False
        self._CBE_counter = 0  # Curly Braces Expansion
        self._PBE_counter = 0  # Parenthesis Expansion
        self._stringBeginsWith = ""

    def getPreviousCharacters(self, n):
        return self.src[max(0, self.pos - n):self.pos]

    def getPreviousCharacter(self):
        return self.getPreviousCharacters(1)

    def getNextCharacters(self, n):
        return self.src[self.pos + 1:self.pos + n + 1]

    def getNextCharacter(self):
        return self.getNextCharacters(1)

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

    def getPartOfLineAfterPos(self):
        result = ''
        i = self.pos + 1
        while i < len(self.src) and self.src[i] != '\n':
            result += self.src[i]
            i += 1
        return result

    def getPartOfLineBeforePos(self):
        result = ''
        i = self.pos - 1
        while i >= 0 and self.src[i] != '\n':
            result = self.src[i] + result
            i -= 1
        return result

    def skipNextCharacters(self, n):
        self.pos += n

    def skipNextCharacter(self):
        self.skipNextCharacters(1)

    def charactersGenerator(self):
        self._stringBeginsWith = ""
        hereDocWord = ''
        _closeHereDocAfterYield = False
        escaped = False
        while self.pos < len(self.src):
            ch = self.src[self.pos]
            # handle strings and comments
            if ch == "\\":
                escaped = not escaped
            else:
                # if (ch in "\"'`") and not escaped and not self.insideComment:
                if (ch in "\"'") and not escaped and not self.isInsideCommentOrHereDoc():
                    if self.insideString and self._stringBeginsWith == ch:
                        self._stringBeginsWith = ""
                        self.insideString = False
                    elif not self.insideString:
                        self._stringBeginsWith = ch
                        self.insideString = True
                elif ch == "#" and not self.isInsideStringOrHereDocOrCBEOrPBE() and \
                        self.getPreviousCharacter() in "\n\t ;":
                    self.insideComment = True
                elif ch == '{' and self.getPreviousCharacter() == '$' and not self.isInsideCommentOrHereDoc() and \
                        not self.isInsideSingleQuotedString() and not self.isInsideCBE():
                    self._CBE_counter = 1
                elif ch == '{' and not self.isInsideSingleQuotedString() and self.isInsideCBE():
                    self._CBE_counter += 1
                elif ch == '}' and not self.isInsideSingleQuotedString() and self.isInsideCBE():
                    self._CBE_counter -= 1
                elif ch == '(' and self.getPreviousCharacter() == '$' and not self.isInsideCommentOrHereDoc() and \
                        not self.isInsideSingleQuotedString() and not self.isInsidePBE():
                    self._PBE_counter = 1
                elif ch == '(' and not self.isInsideSingleQuotedString() and self.isInsidePBE():
                    self._PBE_counter += 1
                elif ch == ')' and not self.isInsideSingleQuotedString() and self.isInsidePBE():
                    self._PBE_counter -= 1
                elif ch == '<' and self.getPreviousCharacter() == '<' and self.getPreviousCharacters(2) != '<<' and \
                        self.getNextCharacter() != '<' and \
                        not self.insideComment and not self.isInsideStringOrHereDocOrCBEOrPBE():
                    # heredoc
                    self.insideHereDoc = True
                    hereDocWord = self.getPartOfLineAfterPos()
                    if hereDocWord[0] == '-':
                        hereDocWord = hereDocWord[1:]
                    hereDocWord = hereDocWord.strip().replace('"', '').replace("'", '')
                elif ch == "\n":
                    if self.insideComment:
                        self.insideComment = False
                    elif self.insideHereDoc and self.getPartOfLineBeforePos() == hereDocWord:
                        _closeHereDocAfterYield = True
                escaped = False
            yield ch
            if _closeHereDocAfterYield:
                _closeHereDocAfterYield = False
                self.insideHereDoc = False
            self.pos += 1
        raise StopIteration

    def isInsideString(self):
        return self.insideString

    def isInsideHereDoc(self):
        return self.insideHereDoc

    def isInsideDoubleQuotedString(self):
        return self.insideString and self._stringBeginsWith == '"'

    def isInsideSingleQuotedString(self):
        return self.insideString and self._stringBeginsWith == "'"

    def isInsideComment(self):
        return self.insideComment

    def isInsideCommentOrHereDoc(self):
        return self.insideComment or self.insideHereDoc

    def isInsideCBE(self):
        return self._CBE_counter > 0

    def isInsidePBE(self):
        return self._PBE_counter > 0

    def isInsideStringOrHereDocOrCBEOrPBE(self):
        return self.insideString or self.insideHereDoc or self.isInsideCBE() or self.isInsidePBE()


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
        if it.isInsideStringOrHereDocOrCBEOrPBE():
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
        if it.isInsideStringOrHereDocOrCBEOrPBE() or ch != "\n":
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

    # finally remove spaces around semicolons
    it = BashFileIterator(src)
    src = ""  # result
    for ch in it.charactersGenerator():
        if it.isInsideStringOrHereDocOrCBEOrPBE():
            src += ch
        elif ch in ' \t' and (it.getPreviousCharacter() == ";" or it.getNextCharacter() == ";"):
            continue
        else:
            src += ch

    return src


if __name__ == "__main__":
    # TODO check all bash keywords and ensure that they are handled correctly
    # https://www.gnu.org/software/bash/manual/html_node/Reserved-Word-Index.html
    # http://pubs.opengroup.org/onlinepubs/009695399/utilities/xcu_chap02.html

    # get bash source from file or from stdin
    src = ""
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as ifile:
            src = ifile.read()
    else:
        src = sys.stdin.read()
    print minify(src)
