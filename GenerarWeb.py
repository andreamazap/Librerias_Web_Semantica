import glob, os, sys
from html import escape
from rdflib import Graph, Namespace

CONF = Namespace("https://w3id.org/scholarlydata/ontology/conference-ontology.owl#")

class ResumenISWC2019:
    QUERY = """
    PREFIX conf: <https://w3id.org/scholarlydata/ontology/conference-ontology.owl#>
    PREFIX dbo:  <http://dbpedia.org/ontology/>
    PREFIX dbp:  <http://dbpedia.org/property/>
    SELECT DISTINCT ?paper ?titulo ?track ?pais
    WHERE {
      ?paper a conf:InProceedings ;
             conf:title ?titulo ;
             conf:hasAuthorList/conf:hasFirstItem/conf:next*/conf:hasContent ?autor .
      ?autor conf:hasAffiliation/conf:withOrganisation ?org .
      ?org dbo:country ?c .
      ?c dbp:name ?pais .
      BIND (REPLACE(STR(?paper), "^.*/iswc-2019-([a-z-]+)-[0-9]+$", "$1") AS ?track)
      FILTER (?track IN ("research", "in-use", "resource"))
    }
    """
    ETIQUETA = {"research": "(IN)", "in-use": "(EU)", "resource": "(RC)"}

    def __init__(self, directorio):
        self.g = Graph()
        for f in sorted(glob.glob(os.path.join(directorio, "*.ttl"))):
            self.g.parse(f, format="turtle")

    def autores_ordenados(self, paper):
        nombres = []
        lista = self.g.value(paper, CONF.hasAuthorList)
        item = self.g.value(lista, CONF.hasFirstItem)
        while item is not None:
            autor = self.g.value(item, CONF.hasContent)
            nombres.append(str(self.g.value(autor, CONF.name)))
            item = self.g.value(item, CONF.next)
        return nombres

    @staticmethod
    def formatear_autores(n):
        if len(n) <= 1:
            return "".join(n)
        return ", ".join(n[:-1]) + " y " + n[-1]

    def agrupar(self):
        por_pais = {}
        for paper, titulo, track, pais in self.g.query(self.QUERY):
            por_pais.setdefault(str(pais), {})[paper] = (str(titulo), str(track))
        return por_pais

    def generar_html(self, salida="index.html"):
        datos = self.agrupar()
        h = ["<!DOCTYPE html>", "<html>", "<head>", '<meta charset="utf-8">',
             "<title>Publicaciones ISWC 2019 por país</title>", "</head>", "<body>",
             "<h1>Publicaciones de ISWC 2019 agrupadas por país</h1>"]
        for pais in sorted(datos):
            h.append(f"<h2>{escape(pais)}</h2>")
            for paper, (titulo, track) in sorted(datos[pais].items(), key=lambda kv: kv[1][0].lower()):
                autores = self.formatear_autores(self.autores_ordenados(paper))
                h.append(f'{self.ETIQUETA[track]} "{escape(titulo)}" por {escape(autores)}<br/>')
        h += ["</body>", "</html>"]
        with open(salida, "w", encoding="utf-8") as f:
            f.write("\n".join(h))
        return datos

if __name__ == "__main__":
    d = sys.argv[1] if len(sys.argv) > 1 else "DatosPractica18"
    datos = ResumenISWC2019(d).generar_html()
    print(len(datos), "países;", sum(len(v) for v in datos.values()), "entradas")