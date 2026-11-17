"""Prepara offline el índice TF-IDF de fuentes públicas de la demostración."""
import hashlib
import json
from pathlib import Path
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT=Path(__file__).resolve().parents[1]


def indexar():
    ruta=ROOT/'ml/corpus_optica.json'
    documentos=[d for d in json.loads(ruta.read_text(encoding='utf8')) if d['activo'] and d['audiencia']=='publica']
    if not documentos:raise ValueError('No hay fuentes públicas activas')
    vectorizador=TfidfVectorizer(ngram_range=(1,2),strip_accents='unicode',sublinear_tf=True)
    matriz=vectorizador.fit_transform([d['titulo']+' '+d['contenido'] for d in documentos])
    salida=ROOT/'backend/optica/modelo/indice_corpus.joblib'
    joblib.dump({'documentos':documentos,'matriz':matriz,'vectorizador':vectorizador,'hash_corpus':hashlib.sha256(ruta.read_bytes()).hexdigest()},salida)
    print(f'Índice preparado: {len(documentos)} fuentes públicas; {matriz.shape[1]} términos/ngramas.')


if __name__=='__main__':indexar()
