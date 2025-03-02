#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Indexing homework solution"""

import argparse
from timeit import default_timer as timer
import os
import json
from collections import defaultdict

def preprocess(text):
    # Tokenize
    tokenizer = tokenize.RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(text)

    # Normalize
    return [token.lower() for token in tokens]

def build_index(data_dir, index_dir):
    # Загружаем документы
    documents = []
    with open(os.path.join(data_dir, 'vkmarco-docs.tsv'), 'r', encoding='utf-8') as f:
        for line in f:
            document_id, url, title, body = line.strip().split('\t')
            documents.append((document_id, title + ' ' + body))

    # Создаем индекс
    index = defaultdict(lambda: defaultdict(set))
    for doc_id, text in documents:
        tokens = preprocess(text)
        for token in tokens:
            index[token][doc_id].add(doc_id)

    # Сохраняем индекс
    with open(os.path.join(index_dir, 'index.json'), 'w', encoding='utf-8') as f:
        json.dump(index, f)

def generate_submission(data_dir, submission_file):
    # Загружаем объекты и запросы
    objects = {}
    queries = {}
    with open(os.path.join(data_dir, 'objects.csv'), 'r', encoding='utf-8') as f:
        for line in f:
            objectId, queryId, documentId = line.strip().split(',')
            objects[objectId] = {'queryId': queryId, 'documentId': documentId}
    
    with open(os.path.join(data_dir, 'vkmarco-doceval-queries.tsv'), 'r', encoding='utf-8') as f:
        for line in f:
            queryId, query = line.strip().split('\t')
            queries[queryId] = preprocess(query)

    # Генерируем сабмишн
    submission = []
    with open(os.path.join(data_dir, 'sample_submission.csv'), 'r', encoding='utf-8') as f:
        next(f)  # Пропускаем заголовок
        for line in f:
            objectId, label = line.strip().split(',')
            queryId = objects[objectId]['queryId']
            documentId = objects[objectId]['documentId']
            
            # Проверяем, содержится ли все слова запроса в документе
            query_tokens = queries[queryId]
            document_text = get_document_text(documentId, data_dir)
            document_tokens = preprocess(document_text)
            
            if all(token in document_tokens for token in query_tokens):
                submission.append((objectId, 1))
            else:
                submission.append((objectId, 0))

    # Сохраняем сабмишн
    with open(submission_file, 'w', encoding='utf-8') as f:
        f.write('objectId,label\n')
        for obj_id, label in submission:
            f.write(f'{obj_id},{label}\n')

def get_document_text(documentId, data_dir):
    # Здесь нужно реализовать функцию для получения текста документа
    # Например, можно использовать URL для загрузки документа
    # Это упрощенная версия, которая может потребовать доработки
    return f"Document {documentId}"

def main():
    # Парсим опции командной строки
    parser = argparse.ArgumentParser(description='Indexing homework solution')
    parser.add_argument('--submission_file', help='output Kaggle submission file')
    parser.add_argument('--build_index', action='store_true', help='force reindexing')
    parser.add_argument('--index_dir', required=True, help='index directory')
    parser.add_argument('data_dir', help='input data directory')
    args = parser.parse_args()

    # Будем измерять время работы скрипта
    start = timer()

    if args.build_index:
        build_index(args.data_dir, args.index_dir)
    else:
        generate_submission(args.data_dir, args.submission_file)

    # Репортим время работы скрипта
    elapsed = timer() - start
    print(f"finished, elapsed = {elapsed:.3f}")

if __name__ == "__main__":
    main()
