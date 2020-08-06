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


def run_nlp(path):
    title_metrics = []
    summary_metrics = []
    title_summary_metrics = []

    for fname in glob.iglob(path):
        df_1 = pd.read_csv(fname, encoding='windows-1252')

        # Parse Fields
        doc1 = df_1.title.T
        doc2 = df_1.summary.T
        doc3 = doc1 + doc2
        doc4 = pd.DataFrame(df_1.target_site.T)

        # Convert elements to strings
        docs1 = listToString(doc1)
        docs2 = listToString(doc2)
        docs3 = listToString(doc3)

        target_site = getTarget(doc4)

        # NLP metrics: Title
        doc_title = nlp(docs1)
        for p in doc_title._.phrases:
            print("{:.4f} {:5d} {} {} ".format(p.rank, p.count, p.text, target_site))
            title_metrics.append("{:.4f} {:5d} {} {} ".format(p.rank, p.count, p.text, target_site))

        # NLP metrics: Summary
        doc_summary = nlp(docs2)
        for p in doc_summary._.phrases:
            print("{:.4f} {:5d} {} {} ".format(p.rank, p.count, p.text, target_site))
            summary_metrics.append("{:.4f} {:5d} {} {} ".format(p.rank, p.count, p.text, target_site))

        # NLP metrics: Title plus Summary
        doc_title_summary = nlp(docs3)
        for p in doc_title_summary._.phrases:
            print("{:.4f} {:5d} {} {} ".format(p.rank, p.count, p.text, target_site))
            title_summary_metrics.append("{:.4f} {:5d} {} {} ".format(p.rank, p.count, p.text, target_site))

        # Combine indiviudal NLP metrics into one dataframe
        nlp_titles = pd.DataFrame({'Title': title_metrics})
        nlp_summaries = pd.DataFrame({'Summaries': summary_metrics})
        nlp_title_summaries = pd.DataFrame({'Title_Summary': title_summary_metrics})

        nlp_metrics = pd.concat([nlp_titles, nlp_summaries, nlp_title_summaries], ignore_index=True, axis=1)

    return nlp_metrics


run_nlp(path)
