SEQUENCE = "Sequence"
SELECTOR = "Selector"
PARALLEL = "Parallel"
ACTION = "Action"
INVERTER = "Inverter"
CONDITION = "Condition"
PARSEL = "Parallel Selector"
REPEAT = "Repeater"
LATSEQ = "LAT Sequence"

RE_NOTHINGORWHITESPACESTART = "(?<!\S)"
RE_NOTHINGORWHITESPACEEND = "(?!\S)"
RE_ANY = "*"

# [regular expression] -> node_type_str
#TODO: should pull some regex constants from the pipeline constants, hard coded for now
regex_dict = {
        RE_NOTHINGORWHITESPACESTART + SEQUENCE + RE_ANY : SEQUENCE,
        RE_NOTHINGORWHITESPACESTART + SELECTOR + RE_ANY : SELECTOR,
        RE_NOTHINGORWHITESPACESTART + "\|\|" + RE_ANY : PARALLEL,
        RE_NOTHINGORWHITESPACESTART + "A->" + RE_ANY : ACTION,
        RE_NOTHINGORWHITESPACESTART + INVERTER + RE_ANY : INVERTER,
        RE_NOTHINGORWHITESPACESTART + "Selector \/ Parallel Replaceable" + RE_ANY : PARSEL,
        RE_NOTHINGORWHITESPACESTART + "Repeat<>" + RE_ANY : REPEAT,
        RE_NOTHINGORWHITESPACESTART + "LAT Sequence" + RE_ANY : LATSEQ,
        "*": CONDITION # catch all, needs to stay in this order as conditions do not have a good identifier
}

def get_node_regex_dict():
    return regex_dict


def unique_node_set():
    return get_node_regex_dict().values()

def unique_node_freq_counter():
    return dict.fromkeys(unique_node_set(), 0)


