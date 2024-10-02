from polyglotdb import CorpusContext
import polyglotdb.io as pgio

corpus_root = '/home/corpora/spade-SOTC/audio_and_transcripts'
corpus_name = 'spade-SOTC'

# Import
parser = pgio.inspect_labbcat(corpus_root)
parser.call_back = print

with CorpusContext(corpus_name) as c:
   print('IMPORT...')
   c.load(parser, corpus_root)
