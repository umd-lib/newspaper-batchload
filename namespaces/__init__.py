from rdflib import Namespace,Graph
from rdflib.namespace import NamespaceManager

# useful namespaces for use with RDFlib code

bibo     = Namespace('http://purl.org/ontology/bibo/')
carriers = Namespace('http://id.loc.gov/vocabulary/carriers/')
dc       = Namespace('http://purl.org/dc/elements/1.1/')
dcmitype = Namespace('http://purl.org/dc/dcmitype/')
dcterms  = Namespace('http://purl.org/dc/terms/')
ebucore  = Namespace('http://www.ebu.ch/metadata/ontologies/ebucore/ebucore#')
edm      = Namespace('http://www.europeana.eu/schemas/edm/')
ex       = Namespace('http://www.example.org/terms/')
fabio    = Namespace('http://purl.org/spar/fabio/')
foaf     = Namespace('http://xmlns.com/foaf/0.1/')
iana     = Namespace('http://www.iana.org/assignments/relation/')
ndnp     = Namespace('http://chroniclingamerica.loc.gov/terms/')
oa       = Namespace('http://www.w3.org/ns/oa#')
ore      = Namespace('http://www.openarchives.org/ore/terms/')
pcdm     = Namespace('http://pcdm.org/models#')
pcdmuse  = Namespace('http://pcdm.org/use#')
prov     = Namespace('http://www.w3.org/ns/prov#')
rdf      = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
sc       = Namespace('http://www.shared-canvas.org/ns/')

def get_manager(graph=None):
    if graph is None:
        graph = Graph()
    m = NamespaceManager(graph)
    m.bind('bibo', bibo)
    m.bind('carriers', carriers)
    m.bind('dc', dc)
    m.bind('dcmitype', dcmitype)
    m.bind('dcterms', dcterms)
    m.bind('ebucore', ebucore)
    m.bind('edm', edm)
    m.bind('ex', ex)
    m.bind('fabio', fabio)
    m.bind('foaf', foaf)
    m.bind('iana', iana)
    m.bind('ndnp', ndnp)
    m.bind('oa', oa)
    m.bind('ore', ore)
    m.bind('pcdm', pcdm)
    m.bind('pcdmuse', pcdmuse)
    m.bind('prov', prov)
    m.bind('rdf', rdf)
    m.bind('sc', sc)
    return m
