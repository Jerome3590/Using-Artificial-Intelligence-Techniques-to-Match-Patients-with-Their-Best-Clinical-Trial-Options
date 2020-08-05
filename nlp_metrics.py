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


def run_nlp(path):
    title_metrics = []
    summary_metrics = []
    title_summary_metrics = []

    for fname in glob.iglob(path):
        df_1 = pd.read_csv(fname, encoding='windows-1252')

        #Parse Fields
        doc1 = df_1.title.T
        doc2 = df_1.summary.T
        doc3 = doc1 + doc2
        doc4 = df_1.target_site

        #Convert elements to strings
        docs1 = listToString(doc1)
        docs2 = listToString(doc2)
        docs3 = listToString(doc3)
        docs4 = listToString(doc4)

        #NLP metrics: Title
        doc_title = nlp(docs1, docs4)
        for p in doc_title._.phrases:
            #print("{} {:.4f} {:5d} {} {} ".format(p.rank, p.count, p.text, doc4))
            title_metrics.append("{:.4f} {:5d} {} {} ".format(p.rank, p.count, p.text, docs4))

        #NLP metrics: Summary
        doc_summary = nlp(docs2, docs4)
        for p in doc_summary._.phrases:
            #print("{} {:.4f} {:5d} {} {} ".format(p.rank, p.count, p.text, doc4))
            summary_metrics.append("{:.4f} {:5d} {} {} ".format(p.rank, p.count, p.text, docs4))

        #NLP metrics: Title plus Summary
        doc_title_summary = nlp(docs3, doc4)
        for p in doc_title_summary._.phrases:
            # print("{} {:.4f} {:5d} {} {} ".format(p.rank, p.count, p.text, docs4))
            title_summary_metrics.append("{:.4f} {:5d} {} {} ".format(p.rank, p.count, p.text, docs4))

        #Combine indiviudal NLP metrics into one dataframe
        nlp_metrics = pd.DataFrame(
            {'Title': title_metrics,
             'Summary': summary_metrics,
             'Title_Summary': title_summary_metrics
             })

    return nlp_metrics


run_nlp(path)
