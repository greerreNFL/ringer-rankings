import sys
from .ringer_rankings import update_qb_ranks

if sys.argv[1] == 'run':
    update_qb_ranks()
    