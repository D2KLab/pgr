# bash command to prepare the 3column format necessary to be processed by the conlleval script
# cat mlang.conll.test | cut -d' '  -f2 > column
# paste -d' ' /tmp/mlang.conll.test /tmp/colmn > /tmp/mlang.conll.test.3col

## breakdown entity/type & no. tokens
# perl /tmp/conlleval.pl < /tmp/mlang.conll.test.3col 

## count no. empty lines -> no. sentences
# cat mlang.conll.train | grep -e '^$' | wc -l (+ 1 if not last line)
