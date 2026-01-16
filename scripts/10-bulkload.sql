-- load every .rdf under /database/data into graph <http://makaao.inria.fr/kg>
ld_dir_all ('../database/data', '*.rdf', 'http://makaao.inria.fr/kg/');
rdf_loader_run();
checkpoint;