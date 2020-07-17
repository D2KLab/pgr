#!/bin/sh

cat wikiner_tools/wikiner_conll/it/wikinerIT.conll.test wikiner_tools/wikiner_conll/en/wikinerEN.conll.test wikiner_tools/wikiner_conll/es/wikinerES.conll.test panacea_tools/panacea_conll/panaceaGR.conll.test > multilang_conll/mlang.conll.test
cat wikiner_tools/wikiner_conll/it/wikinerIT.conll.val wikiner_tools/wikiner_conll/en/wikinerEN.conll.val wikiner_tools/wikiner_conll/es/wikinerES.conll.val panacea_tools/panacea_conll/panaceaGR.conll.val > multilang_conll/mlang.conll.val
cat wikiner_tools/wikiner_conll/it/wikinerIT.conll.train wikiner_tools/wikiner_conll/en/wikinerEN.conll.train wikiner_tools/wikiner_conll/es/wikinerES.conll.train panacea_tools/panacea_conll/panaceaGR.conll.train > multilang_conll/mlang.conll.train