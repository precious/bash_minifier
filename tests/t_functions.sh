function f1()   {   echo 1;   }

f1


function f2   {   echo 2;   }

f2



function f3()

{

echo 3

return

}


f3




function f4

{

local aa=aa
bb=bb

echo 4

return 12

}


f4

echo $?
echo aa=$aa
echo bb=$bb

# declarations without "function" keyword

f11  ()   {   echo 11;   }

f11


f33  ()

{

echo 33

return

}


f33

# redirects

function xx()
{
    echo xx;
    echo 'redireced!' 1>&2
} > ./xx$(date +'%T').txt

xx

# function that invokes subshell
e () (
var0=20
echo 'i am "e" func'
)

e

echo var0=$var0 # should be empty

# single command function

function no_braces () if true
then
echo 'i am func without braces';
fi

no_braces
