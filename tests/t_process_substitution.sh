# for details see
# https://superuser.com/questions/1059781/what-exactly-is-in-bash-and-in-zsh
# https://en.wikipedia.org/wiki/Process_substitution

cat < <(which wc)

cat <(which wc)

seq 1 10 | tee >(echo "# of lines:" `wc -l` 1>&2) | awk '{print $1*2}'

