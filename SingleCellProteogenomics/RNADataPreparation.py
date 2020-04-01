# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 18:52:36 2020

@author: antho
"""

import pandas as pd
import numpy as np
import scanpy as sc
import matplotlib.pyplot as plt
import os, shutil
import seaborn as sbn

def read_counts_and_phases(dd, count_or_rpkm, use_spike_ins, biotype_to_use):
    '''
    Read data into scanpy; Read phases and FACS intensities
    * dd: "All", "355", "356", "357"
    * count_or_rpkm: "Counts" or "Tpms"
    '''
    read_file = f"input/processed/scanpy/{count_or_rpkm}.csv" + (".ercc.csv" if use_spike_ins else "")
    if biotype_to_use != None and len(biotype_to_use) > 0:
        print(f"filtering for biotype: {biotype_to_use}")
        biotype_file = f"{read_file}.{biotype_to_use}.csv"
        if not os.path.exists(biotype_file):
            gene_info = pd.read_csv("input/processed/python/IdsToNames.csv", index_col=False, header=None, names=["gene_id", "name", "biotype", "description"])
            biotyped = gene_info[gene_info["biotype"] == biotype_to_use]["gene_id"]
            pd.read_csv(read_file)[biotyped ].to_csv(biotype_file, index=False)
        read_file = biotype_file

    adata = sc.read_csv(read_file)
    print(f"data shape: {adata.X.shape}")
    # adata.raw = adata

    phases = pd.read_csv("input/processed/WellPlatePhasesLogNormIntensities.csv").sort_values(by="Well_Plate")
    
    # Assign phases and log intensities; require log intensity
    adata.obs["phase"] = np.array(phases["Stage"])
    adata.obs["Green530"] = np.array(phases["Green530"])
    adata.obs["Red585"] = np.array(phases["Red585"])
    adata = adata[pd.notnull(adata.obs["Green530"]) & pd.notnull(adata.obs["Red585"])] # removes dark mitotic cells
    
    # Read in fucci pseudotime from previous analysis
    if os.path.isfile("output/fucci_time.csv"):
        adata.obs["fucci_time"] = np.array(pd.read_csv("output/fucci_time.csv")["fucci_time"])

    # Get info about the genes
    gene_info = pd.read_csv("input/processed/python/IdsToNames.csv", header=None, names=["name", "biotype", "description"], index_col=0)
    adata.var["name"] = gene_info["name"]
    adata.var["biotype"] = gene_info["biotype"]
    adata.var["description"] = gene_info["description"]

    return adata, phases

def qc_filtering(adata, do_log_normalize, do_remove_blob):
    '''QC and filtering; remove cluster of cells in senescent G0'''
    sc.pp.filter_cells(adata, min_genes=500)
    sc.pp.filter_genes(adata, min_cells=100)
    sc.pp.normalize_per_cell(adata, counts_per_cell_after=1e4)
    if do_log_normalize: sc.pp.log1p(adata)
    louvain = np.load("input/processed/python/louvain.npy", allow_pickle=True)
    adata.obs["louvain"] = louvain
    if do_remove_blob: adata = adata[adata.obs["louvain"] != "5",:]
    phases = pd.read_csv("input/processed/WellPlatePhasesLogNormIntensities.csv").sort_values(by="Well_Plate")
    phases_filt = phases[phases["Well_Plate"].isin(adata.obs_names)]
    phases_filt = phases_filt.reset_index(drop=True) # remove filtered indices
    print(f"data shape after filtering: {adata.X.shape}")
    return adata, phases_filt

def ccd_gene_lists(adata):
    '''Read in the published CCD genes / Diana's CCD / Non-CCD genes'''
    gene_info = pd.read_csv("input/processed/python/IdsToNames.csv", index_col=False, header=None, names=["gene_id", "name", "biotype", "description"])
    ccd_regev=pd.read_csv("input/processed/manual/ccd_regev.txt")   
    wp_ensg = np.load("output/pickles/wp_ensg.npy", allow_pickle=True)
    ccd_comp = np.load("output/pickles/ccd_comp.npy", allow_pickle=True)
    nonccd_comp = np.load("output/pickles/nonccd_comp.npy", allow_pickle=True)
    ccd=wp_ensg[ccd_comp]
    nonccd=wp_ensg[nonccd_comp]
    ccd_regev_filtered = list(gene_info[(gene_info["name"].isin(ccd_regev["gene"])) & (gene_info["gene_id"].isin(adata.var_names))]["gene_id"])
    ccd_filtered = list(ccd[np.isin(ccd, adata.var_names)])
    nonccd_filtered = list(nonccd[np.isin(nonccd, adata.var_names)])
    return ccd_regev_filtered, ccd_filtered, nonccd_filtered

def is_ccd(adata, wp_ensg, ccd_comp, nonccd_comp, bioccd, ccd_regev_filtered):
    '''Return whether the genes in RNA-Seq analysis are 1) CCD by present protein analysis 2) non-CCD by present protein analysis, 3) curated published CCD'''
    ccdprotein = np.isin(adata.var_names, np.concatenate((wp_ensg[ccd_comp], bioccd)))
    nonccdprotein = np.isin(adata.var_names, wp_ensg[nonccd_comp]) & ~np.isin(adata.var_names, bioccd)
    regevccdgenes = np.isin(adata.var_names, ccd_regev_filtered)
    return ccdprotein, nonccdprotein, regevccdgenes

def general_plots():
    '''Make plots to illustrate the results of the scRNA-Seq analysis'''
    plate, valuetype, use_spikeins, biotype_to_use = "All", "Tpms", False, "protein_coding"
    adata, phases = read_counts_and_phases(plate, valuetype, use_spikeins, biotype_to_use)

    # QC plots before filtering
    sc.pl.highest_expr_genes(adata, n_top=20, show=True, save=True)
    shutil.move("figures/highest_expr_genes.pdf", f"figures/highest_expr_genes_{plate}Cells.pdf")

    # Post filtering QC
    do_log_normalization = True
    do_remove_blob = False
    adata, phasesfilt = qc_filtering(adata, do_log_normalization, do_remove_blob)
    sc.pp.highly_variable_genes(adata, min_mean=0.0125, max_mean=3, min_disp=0.5)
    sc.pl.highly_variable_genes(adata, show=True, save=True)
    shutil.move("figures/filter_genes_dispersion.pdf", f"figures/filter_genes_dispersion{plate}Cells.pdf")

    # UMAP plots
    # Idea: based on the expression of all genes, do the cell cycle phases cluster together?
    # Execution: scanpy methods: UMAP statistics first, then make UMAP
    # Output: UMAP plots
    sc.pp.neighbors(adata, n_neighbors=10, n_pcs=40)
    sc.tl.umap(adata)
    plt.rcParams['figure.figsize'] = (10, 10)
    sc.pl.umap(adata, color=["phase"], show=True, save=True)
    shutil.move("figures/umap.pdf", f"figures/umap{plate}CellsSeqCenterPhase.pdf")

    # General display of RNA abundances in TPMs
    sbn.distplot(np.concatenate(adata.X), color="tab:orange", hist=False)
    plt.xlabel("TPM")
    plt.ylabel("Density")
    plt.savefig("figures/rna_abundance_density.pdf")
    plt.show()
    plt.close()

def analyze_noncycling_cells():
    '''The raw UMAP shows a group of cells that appear sequestered from cycling; investigate those'''
    plate, valuetype, use_spikeins, biotype_to_use = "All", "Tpms", False, "protein_coding"
    do_log_normalization = True
    do_remove_blob = False
    adata, phases = read_counts_and_phases(plate, valuetype, use_spikeins, biotype_to_use)
    adata, phasesfilt = qc_filtering(adata, do_log_normalization, do_remove_blob) 

    # Unsupervised clustering and generate the gene list for the uncycling cells, aka the unknown blob
    sc.pp.neighbors(adata, n_neighbors=10, n_pcs=40)
    sc.tl.umap(adata)
    sc.pl.umap(adata, color="louvain", show=True, save=True)
    shutil.move("figures/umap.pdf", f"figures/umap_louvain_clusters_before.pdf")
    sc.tl.rank_genes_groups(adata, groupby="louvain")
    p_blob=[a[5] for a in adata.uns["rank_genes_groups"]["pvals_adj"]]
    p_blob_sig = np.array(p_blob) < 0.01
    ensg_blob_sig=np.array([a[5] for a in adata.uns["rank_genes_groups"]["names"]])[p_blob_sig]
    np.savetxt("output/blob_genes.csv", ensg_blob_sig, fmt="%s", delimiter=",")

    # Remove the blob
    do_remove_blob = True
    adata, phases = read_counts_and_phases(plate, valuetype, use_spikeins, biotype_to_use)
    adata, phasesfilt = qc_filtering(adata, do_log_normalization, do_remove_blob)
    sc.pp.neighbors(adata, n_neighbors=10, n_pcs=40)
    sc.tl.umap(adata)
    sc.pl.umap(adata, color="louvain", show=True, save=True)
    shutil.move("figures/umap.pdf", f"figures/umap_louvain_clusters_after.pdf")

def demonstrate_umap_cycle_without_ccd(adata):
    '''
    Idea: We should expect that the UMAP does not recognize a cycle when cycling transcripts are removed.
    Removing the CCD genes from the 93 curated genes or the 300-or-so CCD proteins identified in this work lead to UMAPs that are not cyclical. 
    '''
    ccd_regev_filtered, ccd_filtered, nonccd_filtered = ccd_gene_lists(adata)
    adata_ccdregev = adata[:, [x for x in adata.var_names if x not in ccd_regev_filtered]]
    sc.pp.neighbors(adata_ccdregev, n_neighbors=10, n_pcs=40)
    sc.tl.umap(adata_ccdregev)
    sc.pl.umap(adata_ccdregev, color="fucci_time", show=True, save=True)
    shutil.move("figures/umap.pdf", f"figures/umapAllCellsPhaseNonCcdCurated.pdf")

    adata_ccdregev = adata[:, [x for x in adata.var_names if x in nonccd_filtered]]
    sc.pp.neighbors(adata_ccdregev, n_neighbors=10, n_pcs=40)
    sc.tl.umap(adata_ccdregev)
    sc.pl.umap(adata_ccdregev, color="fucci_time", show=True, save=True)
    shutil.move("figures/umap.pdf", f"figures/umapAllCellsPhaseNonCcd.pdf")

def readcount_and_genecount_over_pseudotime():
    '''
    To demonstrate why we normalize read counts per cell, these plots show the increase in read count over the cell cycle as the cell grows.
    We also show the resulting increase in the number of genes detected.
    '''
    plate, valuetype, use_spikeins, biotype_to_use = "All", "Counts", False, "protein_coding"
    adata, phases = RNADataPreparation.read_counts_and_phases(plate, valuetype, use_spikeins, biotype_to_use)
    expression_data = adata.X
    fucci_time_inds = np.argsort(adata.obs["fucci_time"])
    fucci_time_sort = np.take(np.array(adata.obs["fucci_time"]), fucci_time_inds)
    exp_sort = np.take(expression_data, fucci_time_inds, axis=0)

    # Total counts per cell, moving average
    exp = exp_sort.sum(axis=1)
    df = pd.DataFrame({"fucci_time" : fucci_time_sort, "total_counts" : exp})
    bin_size = 100
    plt.figure(figsize=(10,10))
    plt.plot(df["fucci_time"], 
            df["total_counts"].rolling(bin_size).mean(), 
            color="blue", 
            label=f"Moving Average by {bin_size} Cells")
    plt.xlabel("Fucci Pseudotime",size=36,fontname='Arial')
    plt.ylabel("Total RNA-Seq Counts",size=36,fontname='Arial')
    plt.xticks(size=14)
    plt.yticks(size=14)
    # plt.title("Total Counts",size=36,fontname='Arial')
    plt.legend(fontsize=14)
    plt.tight_layout()
    plt.savefig(f"figures/TotalCountsPseudotime.png")
    plt.show()
    plt.close()

    # Total genes detected per cell, moving average
    gene_ct = np.count_nonzero(exp_sort, axis=1)
    df = pd.DataFrame({"fucci_time" : fucci_time_sort, "total_genes" : gene_ct})
    plt.figure(figsize=(10,10))
    plt.plot(df["fucci_time"], 
            df["total_genes"].rolling(bin_size).mean(), 
            color="blue", 
            label=f"Moving Average by {bin_size} Cells")
    plt.xlabel("Fucci Pseudotime",size=36,fontname='Arial')
    plt.ylabel("Total Genes Detected By RNA-Seq",size=36,fontname='Arial')
    plt.xticks(size=14)
    plt.yticks(size=14)
    # plt.title("Total Genes ",size=36,fontname='Arial')
    plt.legend(fontsize=14)
    plt.tight_layout()
    plt.savefig(f"figures/TotalGenesPseudotime.png")
    plt.show()
    plt.close()