import pytextrank
import spacy
import pandas as pd
import glob

path = "data//nlp/*.csv"

nlp = spacy.load("en_core_web_sm")

tr = pytextrank.TextRank()
nlp.add_pipe(tr.PipelineComponent, name="textrank", last=True)


def listToString(s):
    str1 = ""
    for ele in s:
        str1 += ele

    return str1


def getTarget(doc4):
    for index, row in doc4.iterrows():
        target_site = str(row['target_site'])

    return target_site


def run_nlp_summaries(path):

    eigencentrality = []
    counts = []
    key_words = []
    targets = []

    for fname in glob.iglob(path):
        df_1 = pd.read_csv(fname, encoding='windows-1252')

        # Parse Fields
        doc1 = df_1.summary.T
        doc2 = pd.DataFrame(df_1.target_site.T)

        # Convert elements to strings
        docs1 = listToString(doc1)
        target_site = getTarget(doc2)

        # NLP metrics: Summary
        doc_summary = nlp(docs1)
        for p in doc_summary._.phrases:
            eigencentrality.append("{:.4f}".format(p.rank))
            counts.append("{:5d}".format(p.count))
            key_words.append("{}".format(p.text))
            targets.append("{}".format(target_site))

        # Combine indiviudal NLP metrics into one dataframe
        nlp_eigencentrality = pd.DataFrame({'eigencentrality': eigencentrality})
        nlp_counts = pd.DataFrame({'counts': counts})
        nlp_key_words = pd.DataFrame({'key_words': key_words})
        nlp_target_sites = pd.DataFrame({'target_site': targets})

        nlp_summaries = pd.concat([nlp_eigencentrality, nlp_counts, nlp_key_words, nlp_target_sites],
                                   ignore_index=True,
                                axis=1)

    print(nlp_summaries)



    return nlp_summaries


run_nlp_summaries(path)
