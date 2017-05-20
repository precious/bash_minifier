# line continuation
# it does not work inside comments and single quoted strings

# all next 4 echos should look identically after minification
echo "ab" "cd"

echo "ab" \
"cd"

echo "ab"\
 "cd"

echo "ab" \
 "cd"

echo "double quoted:"
echo "ab\
cd"

echo "single quoted:"
echo 'ab\
cd'

echo "parameter expansion \${}:"
a=abcd
echo ${a\
}

echo "command substitution \$():"
echo $(echo a\
b c d)

echo "command substitution \`\`:"
echo `echo a\
b c d`

echo "heredoc:"
cat << HD
HI!\
 I'm here doc
HD


echo "arithmetic expansion \$(()):"
echo 15 \* 99 = $((15\
*99))

echo "comment:"
# echo "if you THIS -- next statement is incorrect:";\
echo "line continuation does not work inside comments"