import glob, sys
from rdflib import Graph

PFX = """
PREFIX conf: <https://w3id.org/scholarlydata/ontology/conference-ontology.owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbo:  <http://dbpedia.org/ontology/>
PREFIX dbp:  <http://dbpedia.org/property/>
"""
CONSULTAS = {
"1. Articulos aceptados por track con sus autores": """
SELECT ?track ?titulo (GROUP_CONCAT(DISTINCT ?autor; separator=", ") AS ?autores)
WHERE {
  ?paper a conf:InProceedings ; conf:title ?titulo ; conf:relatesToEvent ?talk ;
         <http://purl.org/dc/elements/1.1/creator> ?a .
  ?talk conf:isSubEventOf ?t . ?t a conf:Track ; rdfs:label ?track .
  ?a conf:name ?autor .
}
GROUP BY ?track ?titulo ORDER BY ?track ?titulo
""",
"2. Ponencias con articulo, horas, sala, sesion y track": """
SELECT ?titulo ?inicio ?fin ?sala ?sesion ?track
WHERE {
  ?talk a conf:Talk ; conf:isEventRelatedTo ?paper ; conf:startDate ?inicio ; conf:endDate ?fin ;
        conf:isSubEventOf ?ses , ?t .
  ?ses a conf:Session ; rdfs:label ?sesion .
  OPTIONAL { ?ses conf:location ?sala }
  ?t a conf:Track ; rdfs:label ?track .
  ?paper conf:title ?titulo .
}
ORDER BY ?inicio ?sala
""",
"3. Personas con algun rol": """
SELECT DISTINCT ?nombre ?rol
WHERE {
  ?p a conf:Person ; conf:name ?nombre ; conf:holdsRole ?r .
  ?r conf:withRole ?rolURI .
  BIND (REPLACE(STR(?rolURI), "^.*/", "") AS ?rol)
}
ORDER BY ?rol ?nombre
""",
"4. Afiliaciones de personas involucradas": """
SELECT DISTINCT ?organizacion
WHERE {
  ?p a conf:Person ; conf:hasAffiliation/conf:withOrganisation ?o .
  ?o conf:name ?organizacion .
}
ORDER BY ?organizacion
""",
"5. Pausas de cafe y comidas": """
SELECT DISTINCT ?evento ?inicio ?fin
WHERE {
  { ?e a conf:Break } UNION { ?e a conf:Meal }
  ?e rdfs:label ?evento ; conf:startDate ?inicio ; conf:endDate ?fin .
}
ORDER BY ?inicio
""",
}

if __name__ == "__main__":
    g = Graph()
    for f in glob.glob((sys.argv[1] if len(sys.argv) > 1 else "DatosPractica18") + "/*.ttl"):
        g.parse(f, format="turtle")
    print(len(g), "tripletas cargadas")

    for nombre, q in CONSULTAS.items():
        res = list(g.query(PFX + q))
        print(f"\n {nombre}: ({len(res)} filas)")
        print("-------------------------------------------------------")
        for fila in res[:5]:
            print("  " + " | ".join(str(x)[:70] for x in fila))
        print(" ------------------------------------------------------- ")