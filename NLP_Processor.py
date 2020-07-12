import pandas
import pytextrank
import spacy
import networkx as nx
import math
import matplotlib.pyplot as plt
import operator

nlp = spacy.load("en_core_web_sm")

text = "Compatibility of systems of linear constraints over the set of natural numbers. Criteria of compatibility of " \
       "a system of linear Diophantine equations, strict inequations, and nonstrict inequations are considered. Upper " \
       "bounds for components of a minimal set of solutions and algorithms of construction of minimal generating sets " \ 
       "of solutions for all types of systems are given. These criteria and the corresponding algorithms for " \
       "constructing a minimal supporting set of solutions can be used in solving all the considered types systems " \
       "and systems of mixed types. "

doc = nlp(text)

POS_KEPT = ["ADJ", "NOUN", "PROPN", "VERB"]


def increment_edge(graph, node0, node1):
    print("link {} {}".format(node0, node1))

    if graph.has_edge(node0, node1):
        graph[node0][node1]["weight"] += 1.0
    else:
        graph.add_edge(node0, node1, weight=1.0)


def link_sentence(doc, lemma_graph, seen_lemma):
    visited_tokens = []
    visited_nodes = []

    for sent in doc.sents:
        print(">", sent.start, sent.end)

    for i in range(sent.start, sent.end):
        token = doc[i]

        if token.pos_ in POS_KEPT:
            key = (token.lemma_, token.pos_)

            if key not in seen_lemma:
                seen_lemma[key] = set([token.i])
            else:
                seen_lemma[key].add(token.i)

            node_id = list(seen_lemma.keys()).index(key)

            if not node_id in lemma_graph:
                lemma_graph.add_node(node_id)

            print("visit {} {}".format(visited_tokens, visited_nodes))
            print("range {}".format(list(range(len(visited_tokens) - 1, -1, -1))))

            for prev_token in range(len(visited_tokens) - 1, -1, -1):
                print("prev_tok {} {}".format(prev_token, (token.i - visited_tokens[prev_token])))

                if (token.i - visited_tokens[prev_token]) <= 3:
                    lemma_graph.add_edge(lemma_graph, node_id, visited_nodes[prev_token])
                else:
                    break

            print(" -- {} {} {} {} {} {}".format(token.i, token.text, token.lemma_, token.pos_, visited_tokens,
                                                 visited_nodes))

            visited_tokens.append(token.i)
            visited_nodes.append(node_id)


def draw_network_graph(doc):
    lemma_graph = nx.Graph()
    seen_lemma = {}

    for sent in doc.sents:
        link_sentence(doc, sent, lemma_graph, seen_lemma)

    print(seen_lemma)

    labels = {}
    keys = list(seen_lemma.keys())

    for i in range(len(seen_lemma)):
        labels[i] = keys[i][0].lower()


def view_graph(lemma_graph, labels):
    fig = plt.figure(figsize=(9, 9))
    pos = nx.spring_layout(lemma_graph)

    nx.draw(lemma_graph, pos=pos, with_labels=False, font_weight="bold")
    nx.draw_networkx_labels(lemma_graph, pos, labels)

    plt.show(fig)


def calculate_word_rank(lemma_graph, labels):
    ranks = nx.pagerank(lemma_graph)
    for node_id, rank in sorted(ranks.items(), key=lambda x: x[1], reverse=True):
        print(node_id, rank, labels[node_id])


def calculate_phrases(chunk, phrases, counts, seen_lemma, ranks, doc):
    chunk_len = chunk.end - chunk.start + 1
    sq_sum_rank = 0.0
    non_lemma = 0
    compound_key = set([])

    for i in range(chunk.start, chunk.end):
        token = doc[i]
        key = (token.lemma_, token.pos_)

        if key in seen_lemma:
            node_id = list(seen_lemma.keys()).index(key)
            rank = ranks[node_id]
            sq_sum_rank += rank
            compound_key.add(key)

            print(" {} {} {} {}".format(token.lemma_, token.pos_, node_id, rank))
        else:
            non_lemma += 1

    non_lemma_discount = chunk_len / (chunk_len + (2.0 * non_lemma) + 1.0)

    # use root mean square (RMS) to normalize the contributions of all the tokens
    phrase_rank = math.sqrt(sq_sum_rank / (chunk_len + non_lemma))
    phrase_rank *= non_lemma_discount

    # remove spurious punctuation
    phrase = chunk.text.lower().replace("'", "")

    # create a unique key for the the phrase based on its lemma components
    compound_key = tuple(sorted(list(compound_key)))

    if not compound_key in phrases:
        phrases[compound_key] = set([(phrase, phrase_rank)])
        counts[compound_key] = 1
    else:
        phrases[compound_key].add((phrase, phrase_rank))
        counts[compound_key] += 1

    print("{} {} {} {} {} {}".format(phrase_rank, chunk.text, chunk.start, chunk.end, chunk_len, counts[compound_key]))


def collect_phrases(doc, labels, ranks):
    phrases = {}
    counts = {}
    min_phrases = {}

    for chunk in doc.noun_chunks:
        collect_phrases(chunk, phrases, counts)

    for compound_key, rank_tuples in phrases.items():
        l = list(rank_tuples)
        l.sort(key=operator.itemgetter(1), reverse=True)

        phrase, rank = l[0]
        count = counts[compound_key]

        min_phrases[phrase] = (rank, count)

    for phrase, (rank, count) in sorted(min_phrases.items(), key=lambda x: x[1][0], reverse=True):
        print(phrase, count, rank)

    for node_id, rank in sorted(ranks.items(), key=lambda x: x[1], reverse=True):
        print(labels[node_id], rank)

    for node_id, rank in sorted(ranks.items(), key=lambda x: x[1], reverse=True):
        keywords = labels[node_id], rank
        return keywords


def run_nlp(doc_to_process):
    doc = nlp(doc_to_process)
    for sent in doc.sents:
        print(">", sent.start, sent.end)
    for chunk in doc.noun_chunks:
        print(chunk.text)
    for ent in doc.ents:
        print(ent.text, ent.label_, ent.start, ent.end)
    increment_edge()
    link_sentence()
    draw_network_graph()
    view_graph()
    calculate_word_rank()
    calculate_phrases()
    collect_phrases()


run_nlp(text)
