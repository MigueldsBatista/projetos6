import sys

from solve import run_pipeline

processo = sys.argv[0] if len(sys.argv) > 0 else "00011043820135060015"
grau = sys.argv[1] if len(sys.argv) > 1 else "1"

run_pipeline.delay(processo, grau)