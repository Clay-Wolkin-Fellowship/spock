grep "^0" raw/$1.mtrace | build/bin/compress >zip/$1.zmtrace
if [ $? == 0 ] ; then
        rm raw/$1.mtrace
else
        echo $?
fi
