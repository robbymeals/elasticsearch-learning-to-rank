from __future__ import print_function
import re


class Judgment:
    """
    Class to represent rows in the judgement file, to be used as inputs to ranklib algorithms

    A row of the judgement file contains a judgement score, a query id,
    the searched keywords, and a list of features.

    When printed out to Ranklib format, it looks like the line below:

    "3 qid:1 1:1 2:1 3:0 4:0.2 5:0 # 1A"

    """
    def __init__(self, grade, qid, keywords, docId):
        self.grade = grade
        self.qid = qid
        self.keywords = keywords
        self.docId = docId
        self.features = []

    def __str__(self):
        return "grade:%s qid:%s (%s) docid:%s" % (self.grade, self.qid, self.keywords, self.docId)

    def toRanklibFormat(self):
        featuresAsStrs = ["%s:%s" % (idx+1, feature) for idx, feature in enumerate(self.features)]
        comment = "# %s\t%s" % (self.docId, self.keywords)
        return "%s\tqid:%s\t%s %s" % (self.grade, self.qid, "\t".join(featuresAsStrs), comment)


def _queriesFromHeader(lines):
    """ Parses out mapping between, query id and user keywords
        from header comments, ie:
        # qid:523: First Blood
        returns dict mapping all query ids to search keywords"""
    # Regex can be debugged here:
    # http://www.regexpal.com/?fam=96564
    regex = re.compile('#\sqid:(\d+?):\s+?(.*)')
    rVal = {}
    for line in lines:
        if line[0] != '#':
            break
        m = re.match(regex, line)
        if m:
            rVal[int(m.group(1))] = m.group(2)

    return rVal

def _judgmentsFromBody(lines):
    """ Parses out judgment/grade, query id, and docId in line such as:
         4  qid:523   # a01  Grade for Rambo for query Foo
        <judgment> qid:<queryid> # docId <rest of comment ignored...)"""
    # Regex can be debugged here:
    # http://www.regexpal.com/?fam=96565
    regex = re.compile('^(\d)\s+qid:(\d+)\s+#\s+(\w+).*')
    for line in lines:
        print(line)
        m = re.match(regex, line)
        if m:
            print("%s,%s,%s" % (m.group(1), m.group(2), m.group(3)))
            yield int(m.group(1)), int(m.group(2)), m.group(3)


def judgmentsFromFile(filename):
    with open(filename) as f:
        qidToKeywords = _queriesFromHeader(f)
        for grade, qid, docId in _judgmentsFromBody(f):
            yield Judgment(grade=grade, qid=qid, keywords=qidToKeywords[qid], docId=docId)

def judgmentsByQid(judgments):
    rVal = {}
    for judgment in judgments:
        try:
            rVal[judgment.qid].append(judgment)
        except KeyError:
            rVal[judgment.qid] = [judgment]
    return rVal


if __name__ == "__main__":
    from sys import argv
    for judgment in judgmentsFromFile(argv[1]):
        print(judgment)


