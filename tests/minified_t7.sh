isql<<EOF
select count(*) from
table_A
where a=b
go
exit
EOF
echo \<<<true
  this
  is
     here doc!
true