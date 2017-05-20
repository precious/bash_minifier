echo "ab" "cd";echo "ab" "cd";echo "ab" "cd";echo "ab" "cd";echo "double quoted:";echo "abcd";echo "single quoted:";echo 'ab\
cd';echo "parameter expansion \${}:";a=abcd;echo ${a};echo "command substitution \$():";echo $(echo ab c d);echo "command substitution \`\`:";echo `echo ab c d`;echo "heredoc:";cat<< HD
HI! I'm here doc
HD
echo "arithmetic expansion \$(()):";echo 15 \* 99 = $((15*99));echo "comment:";echo "line continuation does not work inside comments"