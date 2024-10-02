from polyglotdb import CorpusContext
import polyglotdb.io as pgio
from polyglotdb.query.base.func import Count, Average

corpus_root = '/home/mlipari/spade-SOTC/audio_and_transcripts'
corpus_name = 'spade-SOTC'

# Import
parser = pgio.inspect_labbcat(corpus_root)
parser.call_back = print

with CorpusContext(corpus_name) as c:
    c.reset()

    print('IMPORT...')
    c.load(parser, corpus_root)

    print('Speakers:', c.speakers)
    print('Discourses:', c.discourses)

    # Optional: Use order_by to enforce ordering on the output for easier comparison with the sample output.
    q = c.query_graph(c.phone).order_by(c.phone.label).group_by(c.phone.label.column_name('phone'))
    results = q.aggregate(Count().column_name('count'), Average(c.phone.duration).column_name('average_duration'))

    for r in results:
        print('The phone {} had {} occurrences and an average duration of {}.'.format(r['phone'], r['count'], r['average_duration']))

