# -*- coding: utf-8 -*-
import re

_REG_CMD = re.compile(r'{.*?}')


class SimpleTime(object):
    def __init__(self, string):
        """The string is like '19:89:06.04'."""
        h, m, s = string.split(':', 2)
        s, cs = s.split('.')
        self.hour = int(h)
        self.minute = int(m)
        self.second = int(s)
        # It's centisec in ASS
        self.microsecond = int(cs) * 10
        if self.microsecond < 0:
            self.microsecond = 0

    def sort_key(self):
        """Used by sort(key=...)."""
        return (self.hour, self.minute, self.second, self.microsecond)

    def __sub__(self, other):
        return (self.hour - other.hour) * 3600 + (self.minute - other.minute) * 60 + \
                (self.second - other.second) + (self.microsecond - other.microsecond) / 1000

    def __str__(self):  # SRT Format
        return '{:02d}:{:02d}:{:02d},{:03d}'.format(self.hour, self.minute, self.second, self.microsecond)
    __unicode__ = __str__


class StrDialogue(object):
    def __init__(self, time_from, time_to, text=''):
        self.time_from = time_from
        self.time_to = time_to
        self.text = text

    def __unicode__(self):
        return '{} --> {}\r\n{}\r\n'.format(self.time_from, self.time_to, self.text)
    __str__ = __unicode__


class AssDialogueFormater(object):
    def __init__(self, format_line):
        colums = format_line[7:].split(',')
        self._columns_names = [c.strip().lower() for c in colums]

    def format(self, dialogue_line):
        columns = dialogue_line[9:].split(',', len(self._columns_names) - 1)
        formated = {name: columns[idx] for idx, name in enumerate(self._columns_names)}
        formated['start'] = SimpleTime(formated['start'])
        formated['end'] = SimpleTime(formated['end'])
        return formated


def _preprocess_line(line):
    """Remove line endings and comments."""
    line = line.strip()
    if line.startswith(';'):
        return ''
    else:
        return line


def convert(file, translator=None, no_effect=False, only_first_line=False):
    """Convert a ASS subtitles to SRT format and return the content of SRT.

    Arguments:
    file            -- a file-like object which shoud handle decoding;
    translator      -- a instance of LangconvTranslator or OpenCCTranslator;
    no_effect       -- delete all effect dialogues;
    only_first_line -- only keep the first line of each dialogue.

    """
    for line in file:          # Locate the Events tag.
        line = _preprocess_line(line)
        if line.startswith('[Events]'):
            break
    formater = None
    for line in file:             # Find Format line.
        line = _preprocess_line(line)
        if line.startswith('Format:'):
            formater = AssDialogueFormater(line)
            break
    if formater is None:
        raise ValueError("Can't find Events tag or Foramt line in this file.")
    # Iterate and convert all Dialogue lines:
    srt_dialogues = []
    for line in file:
        line = _preprocess_line(line)
        if line.startswith('['):
            break  # Events ended.
        elif not line.startswith('Dialogue:'):
            continue
        dialogue = formater.format(line)
        if dialogue['end'] - dialogue['start'] < 0.2:
            continue          # Ignore duration < 0.2 second.
        if no_effect:
            if dialogue.get('effect', ''):
                continue
        if dialogue['text'].endswith('{\p0}'):  # TODO: Exact match drawing commands.
            continue
        text = ''.join(_REG_CMD.split(dialogue['text']))  # Remove commands.
        text = text.replace(r'\N', '\r\n').replace(r'\n', '\r\n')
        if only_first_line:
            text = text.split('\r\n', 1)[0]
        if translator is not None:
            text = translator.convert(text)
        srt_dialogues.append(StrDialogue(dialogue['start'], dialogue['end'], text))
    srt_dialogues.sort(key=lambda dialogue: dialogue.time_from.sort_key())
    srt_string = ''
    srt_set = set()      # 去重集合
    i = 0
    for index in range(len(srt_dialogues)):
        if (index == 0 or index == len(srt_dialogues) - 1) and \
                ('.tv' in str(srt_dialogues[index]) or '.com' in str(srt_dialogues[index]) or
                 '.org' in str(srt_dialogues[index])):     # 去除网址
            continue
        if str(srt_dialogues[index]) in srt_set:      # 遇到重复则跳过
            continue
        i += 1
        srt_string += '{}\r\n{}\r\n'.format(i, str(srt_dialogues[index]))
        srt_set.add(str(srt_dialogues[index]))
    return srt_string


if __name__ == '__main__':
    srt = convert(open('C:/Users/Administrator/Downloads/[HorribleSubs] Mahou Shoujo Site - 02 [720p].ass',
                       'r', encoding='utf-8'), None, True, False)
    print(srt)
