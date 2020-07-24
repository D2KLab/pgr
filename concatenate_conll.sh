#!/bin/sh

cat wikiner_tools/wikiner_conll/it/wikinerIT.conll.test wikiner_tools/wikiner_conll/en/wikinerEN.conll.test wikiner_tools/wikiner_conll/es_balanced/wikinerES.conll.test panacea_tools/panacea_conll_balanced/panaceaGR.conll.test > multilang_conll_balanced/mlang.conll.test
cat wikiner_tools/wikiner_conll/it/wikinerIT.conll.val wikiner_tools/wikiner_conll/en/wikinerEN.conll.val wikiner_tools/wikiner_conll/es_balanced/wikinerES.conll.val panacea_tools/panacea_conll_balanced/panaceaGR.conll.val > multilang_conll_balanced/mlang.conll.val
cat wikiner_tools/wikiner_conll/it/wikinerIT.conll.train wikiner_tools/wikiner_conll/en/wikinerEN.conll.train wikiner_tools/wikiner_conll/es_balanced/wikinerES.conll.train panacea_tools/panacea_conll_balanced/panaceaGR.conll.train > multilang_conll_balanced/mlang.conll.train
