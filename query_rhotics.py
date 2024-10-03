def main():
    from polyglotdb import CorpusContext
    import time

    corpus_name = 'spade-SOTC'

    rhotics = ['ar', 'or', 'our', '@r', 'aer', 'oir', 'owr', 'ir', 'er', 'eir', 'ur']
    r = ['r', 'R', 'r\\']
    csv_path = '/home/mlipari/test.csv'

    print('Exporting rhotic tokens for {}'.format(corpus_name))
    beg = time.time()

    with CorpusContext(corpus_name) as c:
        q = c.query_graph(c.phone)

        print('Applying filters...')
        q = q.filter(c.phone.label.in_(r),
                    #  c.phone.syllable.word.unisynprimstressedvowel1.in_(rhotics),
                    # c.phone.duration >= 0.05,
                    # c.phone.end == c.phone.word.end,
                     )
        
        print('Querying...')
        q = q.columns(c.phone.speaker.name.column_name('speaker'),
                      c.phone.discourse.name.column_name('discourse'),
                      c.phone.id.column_name('phone_id'),
                      c.phone.label.column_name('phone_label'),
                      c.phone.begin.column_name('phone_begin'),
                      c.phone.end.column_name('phone_end'),
                      c.phone.duration.column_name('phone_duration'),
                      c.phone.syllable.stress.column_name('syllable_stress'),
                      c.phone.word.stresspattern.column_name('word_stresspattern'),
                      c.phone.syllable.position_in_word.column_name('syllable_position_in_word'),
                      c.phone.following.label.column_name('following_phone'),
                      c.phone.previous.label.column_name('previous_phone'),
                      c.phone.word.label.column_name('word_label'),
                      c.phone.word.unisynprimstressedvowel1.column_name('unisyn_vowel'),
                      c.phone.utterance.speech_rate.column_name('speech_rate'),
                      c.phone.syllable.label.column_name('syllable_label'),
                      c.phone.syllable.duration.column_name('syllable_duration'),
                      c.phone.syllable.begin.column_name('syllable_begin'),
                      c.phone.syllable.end.column_name('syllable_end'),
                      c.phone.word.duration.column_name('word_duration'),
                      c.phone.word.begin.column_name('word_begin'),
                      c.phone.word.end.column_name('word_end'),
                      c.phone.utterance.duration.column_name('utterance_duration'),
                      c.phone.utterance.begin.column_name('utterance_begin'),
                      c.phone.utterance.end.column_name('utterance_end'),
                      c.phone.word.transcription.column_name('word_transcription'),
                      c.phone.word.num_syllables.column_name('word_num_syllables'),
                      c.phone.utterance.num_syllables.column_name('utterance_num_syllables'),
                      c.phone.utterance.num_words.column_name('utterance_num_words'),
                      )
        for sp, _ in c.hierarchy.speaker_properties:
            if sp == 'name':
                continue
            q = q.columns(getattr(c.phone.speaker, sp).column_name(sp))

        print(f'Writing to file: {csv_path}...')
        q.to_csv(csv_path)

        end = time.time()
        print('Export took: {}'.format(end - beg))

if __name__ == '__main__':
    main()