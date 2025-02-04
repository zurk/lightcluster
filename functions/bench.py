#experiment


def make_experiment(algorithms=None, datasets=None, **kwargs):
	
	if algorithms == None:
		raise TypeError("Algorithms are not given\n")
	if datasets == None:
		raise TypeError("Datasets are not given\n")

	recognized = ['n_clusters', 'neighbours_threshold', 'similarity_threshold', 'n_steps', 'clique_size']

	n_clusters=None
	neighbours_threshold=None
	similarity_threshold=None
	n_steps=None
	clique_size=None

	for key, value in kwargs.items():
		if key not in recognized:
			 raise TypeError(("Keyword argument '%s' is not recognized!\nAvailable keywords are:\n'"
												 + "', '".join(recognized)  + "'") % key)

		if key == recognized[0]:
			n_clusters = value
		elif key == recognized[1]:
			neighbours_threshold = value
		elif key == recognized[2]:
			similarity_threshold = value
		elif key == recognized[3]:
			n_steps = value
		elif key == recognized[4]:
			clique_size = value

	for algorithm in algorithms:
		if algorithm not in ['Spectral', 'SCAN', 'GreedyNewman', 'Walktrap', 'LPA', 'CFinder', 'Clauset-Newman', 'Bigclam']:
			print 'Algorithm '+algorithm+' is unavailable!\n'

	for dataset in datasets:
			if dataset not in ['football.txt', 'polbooks.txt', 'protein_new.txt', 'amazon.txt', 'scientists_new.txt', 'karate.txt', 
													'facebook.txt', 'cliques.txt', 'nested.txt', 'stars.txt', 'cycles.txt']:
				print 'Dataset '+dataset+' is unavailable!\n'

	result = {}

	for algorithm in algorithms:
		if algorithm not in ['Spectral', 'SCAN', 'GreedyNewman', 'Walktrap', 'LPA', 'CFinder', 'Clauset-Newman', 'Bigclam']:
			continue

		fit, n_clusters, similarity_threshold, neighbours_threshold, n_steps, clique_size = fit_algo_params(algorithm, n_clusters, 
																										 similarity_threshold, neighbours_threshold, n_steps, clique_size)
		if not fit:
			continue

		for dataset in datasets:
			if dataset not in ['football.txt', 'polbooks.txt', 'protein_new.txt', 'amazon.txt', 'scientists_new.txt', 'karate.txt', 
													'facebook.txt', 'cliques.txt', 'nested.txt', 'stars.txt', 'cycles.txt']:
				continue

			from load_data import download_graph
			n_vertex, edge_list = download_graph('data\\'+dataset)

			from model_builder import clustering
			#try:
			lbls, clrs, exectime = clustering(algorithm, n_vertex, edge_list, n_clusters, neighbours_threshold,  similarity_threshold, n_steps, clique_size)
			#except:
			#	continue

			from load_data import write_labels, write_clusters
			if lbls != None:
				write_labels(algorithm, dataset, lbls)
			if clrs != None:
				write_clusters(algorithm, dataset, clrs)

			result[algorithm, dataset, 'Time'] = exectime

			from cluster_metrics import compute_my_modularity, compute_overlapping_modularity, compute_modularity, compute_ratio_cut, compute_normalized_cut
			if algorithm in ['LPA', 'Walktrap', 'GreedyNewman', 'Clauset-Newman', 'Spectral']:
				result[algorithm, dataset, 'My modularity'] = compute_overlapping_modularity(clrs, n_vertex, edge_list)
				result[algorithm, dataset, 'Modularity'] = compute_modularity(lbls, edge_list)
				result[algorithm, dataset, 'RatioCut'] = compute_ratio_cut(lbls, clrs, edge_list)
				result[algorithm, dataset, 'NormCut'] = compute_normalized_cut(lbls, clrs, edge_list)

			elif algorithm in ['Bigclam', 'CFinder']:
				result[algorithm, dataset, 'My modularity'] = compute_overlapping_modularity(clrs, n_vertex, edge_list)
			elif algorithm in ['SCAN']:
				result[algorithm, dataset, 'My modularity'] = compute_overlapping_modularity(clrs, n_vertex, edge_list)
				result[algorithm, dataset, 'RatioCut'] = compute_ratio_cut(lbls, clrs, edge_list)
				result[algorithm, dataset, 'NormCut'] = compute_normalized_cut(lbls, clrs, edge_list)

			lbls_true = None
			clrs_true = None
			import os
			if os.path.isfile('data\\'+dataset[:-4]+'_labels.txt'):
				from load_data import download_labels
				lbls_true = download_labels('data\\'+dataset[:-4]+'_labels.txt')
				from transform_functions import compute_clusters_from_labels
				clrs_true = compute_clusters_from_labels(lbls_true)

			elif os.path.isfile('data\\'+dataset[:-4]+'_clusters.txt'):
				from load_data import download_clusters
				clrs_true = download_clusters('data\\'+dataset[:-4]+'_clusters.txt')
			
			if clrs_true == None:
				result[algorithm, dataset, 'Precision'] = None
				result[algorithm, dataset, 'Recall'] = None
				result[algorithm, dataset, 'Average F1'] = None
			else:
				from cluster_metrics import compute_recall, compute_precision, compute_avg_f1
				result[algorithm, dataset, 'Precision'] = compute_precision(clrs_true, clrs)
				result[algorithm, dataset, 'Recall'] = compute_recall(clrs_true, clrs)
				result[algorithm, dataset, 'Average F1'] = compute_avg_f1(clrs_true, clrs)

			if algorithm != 'SCAN':
				if lbls_true == None:
					result[algorithm, dataset, 'NMI'] = None
					result[algorithm, dataset, 'ARS'] = None	
				elif lbls != None:
					from cluster_metrics import compute_nmi, compute_ars
					result[algorithm, dataset, 'NMI'] = compute_nmi(lbls_true, lbls)
					result[algorithm, dataset, 'ARS'] = compute_ars(lbls_true, lbls)
	
	return result

def make_optimal_experiment(algorithms=None, datasets=None):
	
	if algorithms == None:
		raise TypeError("Algorithms are not given\n")
	if datasets == None:
		raise TypeError("Datasets are not given\n")

	for algorithm in algorithms:
		if algorithm not in ['Spectral', 'SCAN', 'GreedyNewman', 'Walktrap', 'LPA', 'CFinder', 'Clauset-Newman', 'Bigclam']:
			print 'Algorithm '+algorithm+' is unavailable!\n'

	for dataset in datasets:
			if dataset not in ['football.txt', 'polbooks.txt', 'protein_new.txt', 'amazon.txt', 'scientists_new.txt', 'karate.txt', 
													'facebook.txt', 'cliques.txt', 'nested.txt', 'stars.txt', 'cycles.txt']:
				print 'Dataset '+dataset+' is unavailable!\n'

	result = {}

	for dataset in datasets:
		if dataset not in ['football.txt', 'polbooks.txt', 'protein_new.txt', 'amazon.txt', 'scientists_new.txt', 'karate.txt', 
													'facebook.txt', 'cliques.txt', 'nested.txt', 'stars.txt', 'cycles.txt']:
			continue
		from get_parameters import get_optimal_parameters
		parameters = get_optimal_parameters(dataset, recompute=False)
		n_clusters = parameters['n_clusters']
		n_steps = parameters['n_steps']
		clique_size = parameters['clique_size']
		neighbours_threshold = parameters['neighbours_threshold']
		similarity_threshold = parameters['similarity_threshold']

		for algorithm in algorithms:
			if algorithm not in ['Spectral', 'SCAN', 'GreedyNewman', 'Walktrap', 'LPA', 'CFinder', 'Clauset-Newman', 'Bigclam']:
				continue

			from load_data import download_graph
			n_vertex, edge_list = download_graph('data\\'+dataset)

			from model_builder import clustering
			#try:
			lbls, clrs, exectime = clustering(algorithm, n_vertex, edge_list, n_clusters, neighbours_threshold,  similarity_threshold, n_steps, clique_size)
			#except:
			#	continue

			from load_data import write_labels, write_clusters
			if lbls != None:
				write_labels(algorithm, dataset, lbls)
			if clrs != None:
				write_clusters(algorithm, dataset, clrs)

			result[algorithm, dataset, 'Time'] = exectime

			from cluster_metrics import compute_my_modularity, compute_overlapping_modularity, compute_modularity, compute_ratio_cut, compute_normalized_cut
			if algorithm in ['LPA', 'Walktrap', 'GreedyNewman', 'Clauset-Newman', 'Spectral']:
				result[algorithm, dataset, 'My modularity'] = compute_overlapping_modularity(clrs, n_vertex, edge_list)
				result[algorithm, dataset, 'Modularity'] = compute_modularity(lbls, edge_list)
				result[algorithm, dataset, 'RatioCut'] = compute_ratio_cut(lbls, clrs, edge_list)
				result[algorithm, dataset, 'NormCut'] = compute_normalized_cut(lbls, clrs, edge_list)

			elif algorithm in ['Bigclam', 'CFinder']:
				result[algorithm, dataset, 'My modularity'] = compute_overlapping_modularity(clrs, n_vertex, edge_list)
			elif algorithm in ['SCAN']:
				result[algorithm, dataset, 'My modularity'] = compute_overlapping_modularity(clrs, n_vertex, edge_list)
				result[algorithm, dataset, 'RatioCut'] = compute_ratio_cut(lbls, clrs, edge_list)
				result[algorithm, dataset, 'NormCut'] = compute_normalized_cut(lbls, clrs, edge_list)

			lbls_true = None
			clrs_true = None
			import os
			if os.path.isfile('data\\'+dataset[:-4]+'_labels.txt'):
				from load_data import download_labels
				lbls_true = download_labels('data\\'+dataset[:-4]+'_labels.txt')
				from transform_functions import compute_clusters_from_labels
				clrs_true = compute_clusters_from_labels(lbls_true)

			elif os.path.isfile('data\\'+dataset[:-4]+'_clusters.txt'):
				from load_data import download_clusters
				clrs_true = download_clusters('data\\'+dataset[:-4]+'_clusters.txt')
			
			if clrs_true == None:
				result[algorithm, dataset, 'Precision'] = None
				result[algorithm, dataset, 'Recall'] = None
				result[algorithm, dataset, 'Average F1'] = None
			else:
				from cluster_metrics import compute_recall, compute_precision, compute_avg_f1
				result[algorithm, dataset, 'Precision'] = compute_precision(clrs_true, clrs)
				result[algorithm, dataset, 'Recall'] = compute_recall(clrs_true, clrs)
				result[algorithm, dataset, 'Average F1'] = compute_avg_f1(clrs_true, clrs)

			if algorithm != 'SCAN':
				if lbls_true == None:
					result[algorithm, dataset, 'NMI'] = None
					result[algorithm, dataset, 'ARS'] = None	
				elif lbls != None:
					from cluster_metrics import compute_nmi, compute_ars
					result[algorithm, dataset, 'NMI'] = compute_nmi(lbls_true, lbls)
					result[algorithm, dataset, 'ARS'] = compute_ars(lbls_true, lbls)
	
	return result


def fit_algo_params(algorithm, n_clusters, similarity_threshold, neighbours_threshold, n_steps, clique_size):

	fit = True

	if algorithm == 'Spectral':
		if n_clusters == None:
			print "Argument n_clusters must be given for Srectral algorithm!\n"
			fit = False
		if neighbours_threshold != None:
			print "Argument neighbours_threshold is ignored for Spectral algorithm.\n"
		if similarity_threshold != None:
			print "Argument similarity_threshold is ignored for Spectral algorithm.\n"
		if n_steps != None:
			print "Argument n_steps is ignored for Spectral algorithm.\n"
		if clique_size != None:
			print "Argument clique_size is ignored for Spectral algorithm.\n"

	elif algorithm == 'SCAN':
		if n_clusters != None:
			print "Argument n_clusters is ignored for SCAN algorithm.\n"
		if neighbours_threshold == None:
			print "Argument neighbours_threshold was not given for SCAN algorithm. Launching with default neighbours_threshold=2.\n"
			neighbours_threshold = 2
		if similarity_threshold == None:
			print "Argument similarity_threshold was not given for SCAN algorithm. Launching with default similarity_threshold=0.7.\n"
			similarity_threshold = 0.7
		if n_steps != None:
			print "Argument n_steps is ignored for SCAN algorithm.\n"
		if clique_size != None:
					print "Argument clique_size is ignored for SCAN algorithm.\n"

	elif algorithm == 'GreedyNewman':
		if n_clusters != None:
			print "Argument n_clusters is ignored for GreedyNewman algorithm.\n"
		if neighbours_threshold != None:
			print "Argument neighbours_threshold is ignored for GreedyNewman algorithm.\n"
		if similarity_threshold != None:
			print "Argument similarity_threshold is ignored for GreedyNewman algorithm.\n"
		if n_steps != None:
			print "Argument n_steps is ignored for GreedyNewman algorithm.\n"
		if clique_size != None:
					print "Argument clique_size is ignored for GreedyNewman algorithm.\n"

	elif algorithm == 'Walktrap':
		if n_clusters == None:
			print "Argument n_clusters will be choosen automatically for Walktrap algorithm.\n"
		if neighbours_threshold != None:
			print "Argument neighbours_threshold is ignored for Walktrap algorithm.\n"
		if similarity_threshold != None:
			print "Argument similarity_threshold is ignored for Walktrap algorithm.\n"
		if n_steps == None:
			print "Argument n_steps was not given for Walktrap algorithm. Launching with default n_steps=4.\n"
			n_steps = 4
		if clique_size != None:
					print "Argument clique_size is ignored for Walktrap algorithm.\n"

	elif algorithm == 'LPA':
		if n_clusters == None:
			print "Argument n_clusters is ignored for LPA algorithm.\n"
		if neighbours_threshold != None:
			print "Argument neighbours_threshold is ignored for LPA algorithm.\n"
		if similarity_threshold != None:
			print "Argument similarity_threshold is ignored for LPA algorithm.\n"
		if n_steps != None:
			print "Argument n_steps is ignored for LPA algorithm.\n"
		if clique_size != None:
					print "Argument clique_size is ignored for LPA algorithm.\n"

	elif algorithm == 'CFinder':
			if n_clusters != None:
					print "Argument n_clusters is ignored for CFinder algorithm!\n"
			if neighbours_threshold != None:
					print "Argument neighbours_threshold is ignored for CFinder algorithm.\n"
			if similarity_threshold != None:
					print "Argument similarity_threshold is ignored for CFinder algorithm.\n"
			if n_steps != None:
					print "Argument n_steps is ignored for CFinder algorithm.\n"
			if clique_size == None:
					print "Argument clique_size was not given for CFinder algorithm. Launching with default clique_size=3.\n"
					clique_size = 3

	elif algorithm == 'Clauset-Newman':
		if n_clusters == None:
			print "Argument n_clusters will be choosen automatically for Clauset-Newman algorithm.\n"
		if neighbours_threshold != None:
			print "Argument neighbours_threshold is ignored for Clauset-Newman algorithm.\n"
		if similarity_threshold != None:
			print "Argument similarity_threshold is ignored for Clauset-Newman algorithm.\n"
		if n_steps == None:
			print "Argument n_steps is ignored for Clauset-Newman algorithm.\n"
		if clique_size != None:
					print "Argument clique_size is ignored for Clauset-Newman algorithm.\n"

	elif algorithm == 'Bigclam':
		if n_clusters == None:
			print "Argument n_clusters must be given for Bigclam algorithm!\n"
			fit = False
		if neighbours_threshold != None:
			print "Argument neighbours_threshold is ignored for Bigclam algorithm.\n"
		if similarity_threshold != None:
			print "Argument similarity_threshold is ignored for Bigclam algorithm.\n"
		if n_steps != None:
			print "Argument n_steps is ignored for Bigclam algorithm.\n"
		if clique_size != None:
			print "Argument clique_size is ignored for Bigclam algorithm.\n"

	return [fit, n_clusters, similarity_threshold, neighbours_threshold, n_steps, clique_size]

