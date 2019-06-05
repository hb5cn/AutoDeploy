a=$1
kill -9 $(ps -ef|grep "$a"|gawk '$0 !~/grep/ {print $2}' |tr -s '\n' ' ')
