def basic_enrichment(corpus, syllabics, pauses):
    """Enrich the corpus database with syllable and utterance information."""
    from polyglotdb import CorpusContext
    import time

    with CorpusContext(corpus) as g:
        if not 'utterance' in g.annotation_types:
            ## encode utterances based on presence of an intervening pause
            ## default 150ms
            print('encoding utterances')
            begin = time.time()
            g.encode_pauses(pauses)
            g.encode_utterances(min_pause_length=0.15)
            time_taken = time.time() - begin
            print('Utterance enrichment took: {}'.format(time_taken))

        if syllabics and 'syllable' not in g.annotation_types:
            ## encode syllabic information using maxmimum-onset principle
            print('encoding syllables')
            begin = time.time()
            g.encode_syllabic_segments(syllabics)
            g.encode_syllables('maxonset')
            time_taken = time.time() - begin
            print('Syllable enrichment took: {}'.format(time.time() - begin))

        print('enriching utterances')
        if syllabics and not g.hierarchy.has_token_property('utterance', 'speech_rate'):
            begin = time.time()
            g.encode_rate('utterance', 'syllable', 'speech_rate')
            time_taken = time.time() - begin
            print('Speech rate encoding took: {}'.format(time.time() - begin))

        if not g.hierarchy.has_token_property('utterance', 'num_words'):
            begin = time.time()
            g.encode_count('utterance', 'word', 'num_words')
            time_taken = time.time() - begin
            print('Word count encoding took: {}'.format(time.time() - begin))

        if syllabics and not g.hierarchy.has_token_property('utterance', 'num_syllables'):
            begin = time.time()
            g.encode_count('utterance', 'syllable', 'num_syllables')
            time_taken = time.time() - begin
            print('Syllable count encoding took: {}'.format(time.time() - begin))

        if syllabics and not g.hierarchy.has_token_property('syllable', 'position_in_word'):
            print('enriching syllables')
            begin = time.time()
            g.encode_position('word', 'syllable', 'position_in_word')
            time_taken = time.time() - begin
            print('Syllable position encoding took: {}'.format(time.time() - begin))

        if syllabics and not g.hierarchy.has_token_property('syllable', 'num_phones'):
            begin = time.time()
            g.encode_count('syllable', 'phone', 'num_phones')
            time_taken = time.time() - begin
            print('Phone count encoding took: {}'.format(time.time() - begin))

        if syllabics and not g.hierarchy.has_token_property('word', 'num_syllables'):
            begin = time.time()
            g.encode_count('word', 'syllable', 'num_syllables')
            time_taken = time.time() - begin
            print('Syllable count encoding took: {}'.format(time.time() - begin))

        print('enriching syllables')
        ## generate the word-level stress pattern, either from an external pronunciation dictionary
        ## or by the presence of numeric values on the vowel phones
        if syllabics and g.hierarchy.has_type_property('word', 'stresspattern') and not g.hierarchy.has_token_property(
                'syllable',
                'stress'):
            begin = time.time()
            g.encode_stress_from_word_property('stresspattern')
            time_taken = time.time() - begin
            print("encoded stress")
        elif syllabics and re.search(r"\d", syllabics[0]) and not g.hierarchy.has_type_property('syllable',
                                                                                                'stress'):  # If stress is included in the vowels
            begin = time.time()
            g.encode_stress_to_syllables("[0-9]", clean_phone_label=False)
            time_taken = time.time() - begin
            print("encoded stress")

def lexicon_enrichment(corpus, unisyn_spade_directory, dialect_code):
    """Enrich the database with lexical information, such as stress position and UNISYN phone labels."""
    from polyglotdb import CorpusContext
    import time
    import os
    from polyglotdb.io.enrichment import enrich_lexicon_from_csv

    enrichment_dir = os.path.join(unisyn_spade_directory, 'enrichment_files')
    if not os.path.exists(enrichment_dir):
        print('Could not find enrichment_files directory from {}, skipping lexical enrichment.'.format(
            unisyn_spade_directory))
        return
    
    with CorpusContext(corpus) as g:
        for lf in os.listdir(enrichment_dir):
            path = os.path.join(enrichment_dir, lf)
            if lf == 'rule_applications.csv':
                if g.hierarchy.has_type_property('word', 'UnisynPrimStressedVowel1'.lower()):
                    print('Dialect independent enrichment already loaded, skipping.')
                    continue
            elif lf.startswith(dialect_code):
                if g.hierarchy.has_type_property('word', 'UnisynPrimStressedVowel2_{}'.format(
                        dialect_code).lower()):
                    print('Dialect specific enrichment already loaded, skipping.')
                    continue
            else:
                continue
            begin = time.time()
            enrich_lexicon_from_csv(g, path)
            time_taken = time.time() - begin
            print('Lexicon enrichment took: {}'.format(time.time() - begin))


def speaker_enrichment(corpus, speaker_file):
    """Enrich the database with speaker information (e.g. age, dialect) from a speaker metadata file."""
    from polyglotdb import CorpusContext
    import time
    import os
    from polyglotdb.io.enrichment import enrich_speakers_from_csv

    if not os.path.exists(speaker_file):
        print('Could not find {}, skipping speaker enrichment.'.format(speaker_file))
        return
    with CorpusContext(corpus) as g:
        if not g.hierarchy.has_speaker_property('gender'):
            begin = time.time()
            enrich_speakers_from_csv(g, speaker_file)
            time_taken = time.time() - begin
            print('Speaker enrichment took: {}'.format(time.time() - begin))
        else:
            print('Speaker enrichment already done, skipping.')


def main():
    corpus_root = '/home/mlipari/spade-SOTC/audio_and_transcripts'
    corpus_name = 'spade-SOTC'

    unisyn_spade_directory = '/home/mlipari/unisyn_spade'
    speaker_enrichment_file = '/home/corpora/spade-SOTC/corpus-data/enrichment/speaker_info.csv'
    dialect_code = 'edi'
    pauses = '^<SIL>$'

    vowel_inventory = ["I", "E", "{", "V", "Q", "U", "@", "i","#", "$", "u", "3", "1", "2","4", "5", "6", "7", "8", "9", "c","q", "O", "~"]
    extra_syllabic_segments = ["B","F","H","L", "P", "C"]

    ## Perform linguistic, speaker, and acoustic enrichment
    lexicon_enrichment(corpus_name, unisyn_spade_directory, dialect_code)
    speaker_enrichment(corpus_name, speaker_enrichment_file)
    basic_enrichment(corpus_name, vowel_inventory['vowel_inventory'] + extra_syllabic_segments, pauses)

    print('Enrichment complete!')

if __name__ == '__main__':
    main()