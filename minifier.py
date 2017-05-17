#!/usr/bin/python

import sys


class BashFileIterator:
    def __init__(self, src):
        self.src = src
        self.reset()

    def reset(self):
        self.pos = 0
        self.insideComment = False
        self.insideHereDoc = False
        self._escaped = False

        # possible characters in stack:
        # (, ) -- means Arithmetic Expansion or Command Substitution
        # {, } -- means Parameter Expansion
        # ` -- means Command Substitution
        # ' -- means single-quoted string
        # " -- means double-quoted string
        self._delimiters_stack = []

    def getLastDelimiter(self):
        return self._delimiters_stack[-1] if not self.isStackEmpty() else ''

    def pushDelimiter(self, delimiter):
        if delimiter == ')' and self.getLastDelimiter() == '(':
            self._delimiters_stack.pop()
        elif delimiter == '}' and self.getLastDelimiter() == '{':
            self._delimiters_stack.pop()
        elif delimiter in ('{', '}', '(', ')'):
            self._delimiters_stack.append(delimiter)
        elif delimiter == "'" and self.getLastDelimiter() != '"' or \
                                delimiter == '"' and self.getLastDelimiter() != "'" or \
                        delimiter == '`':
            if delimiter == self.getLastDelimiter():
                self._delimiters_stack.pop()
            else:
                self._delimiters_stack.append(delimiter)

    def isStackEmpty(self):
        return len(self._delimiters_stack) == 0

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

    def getPartOfLineAfterPos(self, skip=0):
        result = ''
        i = self.pos + 1 + skip
        while i < len(self.src) and self.src[i] != '\n':
            result += self.src[i]
            i += 1
        return result

    def getPartOfLineBeforePos(self, skip=0):
        result = ''
        i = self.pos - 1 - skip
        while i >= 0 and self.src[i] != '\n':
            result = self.src[i] + result
            i -= 1
        return result

    def skipNextCharacters(self, n):
        """
        be vary careful with skipping -- keep in mind possible escaping, quotes, substitution and expansions
          DO NOT skip escape characters, single/double quotes, curly braces and parenthesis
        """
        self._escaped = False
        self.pos += n

    def skipNextCharacter(self):
        self.skipNextCharacters(1)

    def charactersGenerator(self):
        hereDocWord = ''
        _closeHereDocAfterYield = False
        _yieldNextNCharactersAsIs = 0

        while self.pos < len(self.src):
            ch = self.src[self.pos]

            if _yieldNextNCharactersAsIs > 0:
                _yieldNextNCharactersAsIs -= 1
            elif ch == "\\":
                self._escaped = not self._escaped
            else:
                if ch == "\n" and not self.isInsideSingleQuotedString() and not self.isInsideDoubleQuotedString():
                    # handle end of comments and heredocs
                    if self.insideComment:
                        self.insideComment = False
                    elif self.insideHereDoc and self.getPartOfLineBeforePos() == hereDocWord:
                        _closeHereDocAfterYield = True
                elif not self.isInsideCommentOrHereDoc():
                    if ch in ('"', "'"):
                        # single quote can't be escaped inside single-quoted string
                        if not self._escaped or ch == "'" and self.isInsideSingleQuotedString():
                            self.pushDelimiter(ch)
                    elif not self.isInsideSingleQuotedString():
                        if not self._escaped:
                            if ch == "#" and not self.isInsideStringOrExpOrSubst() and \
                                            self.getPreviousCharacter() in "\n\t ;":  # handle comments
                                self.insideComment = True
                            elif ch == '`':
                                self.pushDelimiter(ch)
                            elif ch == '$':
                                next_char = self.getNextCharacter()
                                if next_char in ('{', '('):
                                    self.pushDelimiter(next_char)
                                    _yieldNextNCharactersAsIs = 1
                            elif ch in ('{', '}') and self.getLastDelimiter() in ('{', '}'):
                                self.pushDelimiter(ch)
                            elif ch in ('(', ')') and self.getLastDelimiter() in ('(', ')'):
                                self.pushDelimiter(ch)
                            elif ch == '<' and self.getNextCharacter() == '<' and not self.isInsideStringOrExpOrSubst():
                                _yieldNextNCharactersAsIs = 1

                                # we should handle correctly heredocs and herestrings like this one:
                                # echo <<< one

                                if self.getNextCharacters(2) != '<<':
                                    # heredoc
                                    self.insideHereDoc = True
                                    hereDocWord = self.getPartOfLineAfterPos(skip=1)
                                    if hereDocWord[0] == '-':
                                        hereDocWord = hereDocWord[1:]
                                    hereDocWord = hereDocWord.strip().replace('"', '').replace("'", '')

            yield ch

            if ch != "\\":
                self._escaped = False

            if _closeHereDocAfterYield:
                _closeHereDocAfterYield = False
                self.insideHereDoc = False

            self.pos += 1

        assert self.isStackEmpty(), 'Invalid syntax'
        raise StopIteration

    def isInsideDoubleQuotedString(self):
        return self.getLastDelimiter() == '"'

    def isInsideSingleQuotedString(self):
        return self.getLastDelimiter() == "'"

    def isInsideComment(self):
        return self.insideComment

    def isInsideCommentOrHereDoc(self):
        return self.insideComment or self.insideHereDoc

    def isInsideStringOrCommentOrHereDoc(self):
        return self.isInsideSingleQuotedString() or self.isInsideDoubleQuotedString() or self.isInsideCommentOrHereDoc()

    def isInsideStringOrExpOrSubst(self):
        return not self.isStackEmpty()

    def isInsideStringOrExpOrSubstOrHereDoc(self):
        return self.isInsideStringOrExpOrSubst() or self.insideHereDoc


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
        if it.isInsideStringOrExpOrSubstOrHereDoc():
            src += ch
        elif ch == "\\" and it.getNextCharacter() == "\n":
            # backslash at the very end of line means line continuation
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
        if it.isInsideStringOrExpOrSubstOrHereDoc() or ch != "\n":
            src += ch
        else:
            prevWord = it.getPreviousWord()
            nextWord = it.getNextWord()
            if it.getNextCharacter() in '{':  # functions declaration, see test t8.sh
                if it.getPreviousCharacter() == ')':
                    continue
                else:
                    src += ' '
            elif prevWord in ("until", "while", "then", "do", "else", "in", "elif", "if") or \
                            nextWord in ("in",) or \
                            it.getPreviousCharacter() in ("{", "(") or \
                            it.getPreviousCharacters(2) in ("&&", "||"):
                src += " "
            elif nextWord in ("esac",) and it.getPreviousCharacters(2) != ';;':
                src += ';;'
            elif it.getNextCharacter() != "" and it.getPreviousCharacter() != ";":
                src += ";"

    # finally remove spaces around semicolons and pipes
    it = BashFileIterator(src)
    src = ""  # result
    other_delimiters = "|&;<>()"  # characters that may not be surrounded by whitespaces
    for ch in it.charactersGenerator():
        if it.isInsideStringOrCommentOrHereDoc():
            src += ch
        elif ch in ' \t' and (it.getPreviousCharacter() in other_delimiters or
                                      it.getNextCharacter() in other_delimiters):
            continue
        else:
            src += ch

    return src


if __name__ == "__main__":
    # https://www.gnu.org/software/bash/manual/html_node/Reserved-Word-Index.html
    # http://pubs.opengroup.org/onlinepubs/009695399/utilities/xcu_chap02.html
    # http://pubs.opengroup.org/onlinepubs/9699919799/

    # get bash source from file or from stdin
    src = ""
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as ifile:
            src = ifile.read()
    else:
        src = sys.stdin.read()
    print minify(src)


# important rules:
# 1. A single-quote cannot occur within single-quotes.
# 2. The input characters within the double-quoted string that are also enclosed between "$(" and the matching ')'
#    shall not be affected by the double-quotes, but rather shall define that command whose output replaces the "$(...)"
#    when the word is expanded.
# 3. Within the double-quoted string of characters from an enclosed "${" to the matching '}', an even number of
#    unescaped double-quotes or single-quotes, if any, shall occur. A preceding <backslash> character shall be used
#    to escape a literal '{' or '}'
# 4.
