cat << EOF

Working dir "$PWD" `pwd`


line 2

EOF
ls /home/;cat << EOF

line 1


Working dir "$PWD" `pwd`

EOF
echo $((1<<5));echo 1;echo 2;tr a-z A-Z << END_TEXT
one two three
four five six
END_TEXT
tr a-z A-Z <<- END_TEXT
 one two three
 four five six
END_TEXT
cat << EOF
Working dir "$PWD" `pwd`
EOF
cat << 'EOF'
Working dir "$PWD" `pwd`
EOF
tr a-z A-Z <<< one;tr a-z A-Z <<< 'one two three';FOO='one two three';tr a-z A-Z <<< $FOO;tr a-z A-Z <<< 'one
two three';tr a-z A-Z <<< '
one
two three
';tr a-z A-Z <<< "
one
two three
";bc <<< 2^10
