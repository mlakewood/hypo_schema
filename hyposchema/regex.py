#
# Copy and pasta from PR https://github.com/HypothesisWorks/hypothesis-python/pull/393/files
#

# coding=utf-8
#
# This file is part of Hypothesis, which may be found at
# https://github.com/HypothesisWorks/hypothesis-python
#
# Most of this work is copyright (C) 2013-2016 David R. MacIver
# (david@drmaciver.com), but it contains contributions by others. See
# CONTRIBUTING.rst for a full list of people who may hold copyright, and
# consult the git log if you need to determine who owns an individual
# contribution.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.
#
# END HEADER

from __future__ import division, print_function, absolute_import

import re
import sys
import string
from itertools import chain

import hypothesis.strategies as strats
from hypothesis.strategies import defines_strategy
from hypothesis.searchstrategy import SearchStrategy
from hypothesis.internal.compat import hunichr, hrange


def strategy_concat(strategies):
    """given a list of strategies yielding strings return a strategy yielding
    their concatenation."""
    return strats.tuples(*strategies).map(lambda x: u"".join(x))


class RegexStrategy(SearchStrategy):
    """Strategy for generating strings matching a regular expression.

    Currently does not support \B, positive and negative lookbehind
    assertions and conditional matching.

    """


    CATEGORY_DIGIT = string.digits
    CATEGORY_NOT_DIGIT = string.ascii_letters + string.punctuation
    CATEGORY_SPACE = string.whitespace
    CATEGORY_NOT_SPACE = string.printable.strip()
    CATEGORY_WORD = string.ascii_letters + string.digits + '_'
    CATEGORY_NOT_WORD = ''.join(set(string.printable)
                                .difference(string.ascii_letters +
                                            string.digits + '_'))

    def __init__(self, pattern):
        parsed = re.sre_parse.parse(pattern)
        self.cache = {}
        self.strategies = [self._handle_state(state) for state in parsed]

    def do_draw(self, data):
        self.cache = {}
        temp = [data.draw(strat) for strat in self.strategies]
        return "".join(temp)

    def _categories(self, category):
        if category == re.sre_parse.CATEGORY_DIGIT:
            return self.CATEGORY_DIGIT
        elif category == re.sre_parse.CATEGORY_NOT_DIGIT:
            return self.CATEGORY_NOT_DIGIT
        elif category == re.sre_parse.CATEGORY_SPACE:
            return self.CATEGORY_SPACE
        elif category == re.sre_parse.CATEGORY_NOT_SPACE:
            return self.CATEGORY_NOT_SPACE
        elif category == re.sre_parse.CATEGORY_WORD:
            return self.CATEGORY_WORD
        elif category == re.sre_parse.CATEGORY_NOT_WORD:
            return self.CATEGORY_NOT_WORD
        else:
            raise NotImplementedError("Unable to find category: {0}".format(category))

    def _handle_character_sets(self, state):
        opcode, value = state
        if opcode == re.sre_parse.RANGE:
            return [hunichr(val) for val in hrange(value[0], value[1] + 1)]
        elif opcode == re.sre_parse.LITERAL:
            return [hunichr(value)]
        elif opcode == re.sre_parse.CATEGORY:
            return self._categories(value)
        else:
            raise NotImplementedError("Unable to find character set: {0}".format(opcode))

    def _handle_state(self, state):
        opcode, value = state
        if opcode == re.sre_parse.LITERAL:
            return strats.just(hunichr(value))
        elif opcode == re.sre_parse.NOT_LITERAL:
            return strats.characters(blacklist_characters=hunichr(value))
        elif opcode == re.sre_parse.AT:
            return strats.just('')
        elif opcode == re.sre_parse.IN:
            if value[0][0] == re.sre_parse.NEGATE:
                candidates = []
                for v in value[1:]:
                    candidates.extend(chain(*(self._handle_character_sets(v))))
                return strats.characters(blacklist_characters=candidates)
            else:
                candidates = []
                for v in value:
                    candidates.extend(chain(*(self._handle_character_sets(v))))
                return strats.sampled_from(candidates)
        elif opcode == re.sre_parse.ANY:
            return strats.characters()
        elif opcode == re.sre_parse.BRANCH:
            branches = []
            for val in value[1]:
                branch = [self._handle_state(v) for v in val]
                branches.append(strategy_concat(branch))
            return strats.one_of(branches)
        elif opcode == re.sre_parse.SUBPATTERN:
            parts = []
            for part in value[1]:
                parts.append(self._handle_state(part))
            result = strategy_concat(parts)
            if value[0]:
                self.cache[value[0]] = result
                result = strats.shared(result, key=value[0])
            return result
        elif opcode == re.sre_parse.ASSERT:
            result = []
            for part in value[1]:
                result.append(self._handle_state(part))
            return strategy_concat(result)
        elif opcode == re.sre_parse.ASSERT_NOT:
            return strats.just('')
        elif opcode == re.sre_parse.GROUPREF:
            return strats.shared(self.cache[value], key=value)
        elif opcode == re.sre_parse.MIN_REPEAT:
            start_range, end_range, val = value
            result = []
            for v in val:
                part = strats.lists(
                    self._handle_state(v),
                    min_size=start_range,
                    max_size=end_range
                ).map(lambda x: u"".join(x))
                result.append(part)
            return strategy_concat(result)
        elif opcode == re.sre_parse.MAX_REPEAT:
            start_range, end_range, val = value
            result = []
            for v in val:
                part = strats.lists(
                    self._handle_state(v),
                    min_size=start_range,
                    max_size=end_range
                ).map(lambda x: u"".join(x))
                result.append(part)
            return strats.tuples(*result).map(lambda x: u"".join(x))
        else:
            import ipdb; ipdb.set_trace()
            raise NotImplementedError(opcode)


# From hypothesis.strategies.py
@defines_strategy
def regex(pattern):
#    from hypothesis.searchstrategy.regex import RegexStrategy
    return RegexStrategy(pattern)
