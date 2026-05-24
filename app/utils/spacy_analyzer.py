from app.utils.nlp import nlp
import re

def process_text(text):
    doc = nlp(text)
    return doc

def compress_text(doc):
    important_sentences = []
    for sent in doc.sents:
        has_verb = any(token.pos_ == "VERB" for token in sent)
        has_entity = len(sent.ents) > 0
        if has_verb and has_entity:
            important_sentences.append(sent.text.strip())
    return " ".join(important_sentences)

def extract_keywords(doc):
    keywords = set()
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop:
            keywords.add(token.lemma_.lower())
    return sorted(list(keywords))

def extract_entities(doc):
    entities = {}
    for ent in doc.ents:
        if ent.label_ not in entities:
            entities[ent.label_] = []
        entities[ent.label_].append(ent.text)
    return entities

def run_analysis(resume_text, job_text):
    # Process both texts
    resume_doc = process_text(resume_text)
    job_doc = process_text(job_text)

    # Compress both texts to important sentences only
    compressed_resume = compress_text(resume_doc)
    compressed_job = compress_text(job_doc)

    # Extract keywords from both
    resume_keywords = set(extract_keywords(resume_doc))
    job_keywords = set(extract_keywords(job_doc))

    # Find matching and missing keywords
    matching = resume_keywords & job_keywords
    missing = job_keywords - resume_keywords

    # Calculate match percentage
    match_percentage = round(
        (len(matching) / len(job_keywords)) * 100
    ) if job_keywords else 0

    return {
        "compressed_resume": compressed_resume,
        "compressed_job": compressed_job,
        "comparison": {
            "matching_skills": sorted(list(matching)),
            "missing_skills": sorted(list(missing)),
            "match_percentage": match_percentage
        }
    }