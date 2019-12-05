#%% Imports
from imports import *
import numpy as np
from stretch_time import stretch_time
from scipy.optimize import least_squares
from scipy.optimize import minimize_scalar
from sklearn.neighbors import RadiusNeighborsRegressor
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.stats import iqr, variation

#%% Read in the protein data
# Idea: read in the protein data to compare with the RNA seq data
# Exec: pandas
# Output: fucci plot from the immunofluorescence data
print("reading protein IF data")
#plate = np.load("output/pickles/plate.npy", allow_pickle=True)
u_plate = np.load("output/pickles/u_plate.npy", allow_pickle=True)
well_plate=np.load("output/pickles/well_plate.npy", allow_pickle=True)
well_plate_imgnb=np.load("output/pickles/well_plate_imgnb.npy", allow_pickle=True)
#imgnb=np.load("output/pickles/imgnb.npy", allow_pickle=True)
u_well_plates=np.load("output/pickles/u_well_plates.npy", allow_pickle=True)
#ab_objnum=np.load("output/pickles/ab_objnum.npy", allow_pickle=True)
ab_nuc=np.load("output/pickles/ab_nuc.npy", allow_pickle=True)
ab_cyto=np.load("output/pickles/ab_cyto.npy", allow_pickle=True)
ab_cell=np.load("output/pickles/ab_cell.npy", allow_pickle=True)
mt_cell=np.load("output/pickles/mt_cell.npy", allow_pickle=True)
green_fucci=np.load("output/pickles/green_fucci.npy", allow_pickle=True)
red_fucci=np.load("output/pickles/red_fucci.npy", allow_pickle=True)
log_green_fucci_zeroc=np.load("output/pickles/log_green_fucci_zeroc.npy", allow_pickle=True)
log_red_fucci_zeroc=np.load("output/pickles/log_red_fucci_zeroc.npy", allow_pickle=True)
log_green_fucci_zeroc_rescale=np.load("output/pickles/log_green_fucci_zeroc_rescale.npy", allow_pickle=True)
log_red_fucci_zeroc_rescale=np.load("output/pickles/log_red_fucci_zeroc_rescale.npy", allow_pickle=True)
wp_cell_kruskal_gaussccd_adj = np.load("output/pickles/wp_cell_kruskal_gaussccd_adj.npy", allow_pickle=True)
wp_nuc_kruskal_gaussccd_adj = np.load("output/pickles/wp_nuc_kruskal_gaussccd_adj.npy", allow_pickle=True)
wp_cyto_kruskal_gaussccd_adj = np.load("output/pickles/wp_cyto_kruskal_gaussccd_adj.npy", allow_pickle=True)
wp_pass_gaussccd_bh_cell = np.load("output/pickles/wp_pass_gaussccd_bh_cell.npy", allow_pickle=True)
wp_pass_gaussccd_bh_nuc = np.load("output/pickles/wp_pass_gaussccd_bh_nuc.npy", allow_pickle=True)
wp_pass_gaussccd_bh_cyto = np.load("output/pickles/wp_pass_gaussccd_bh_cyto.npy", allow_pickle=True)
fucci_data = np.load("output/pickles/fucci_data.npy", allow_pickle=True)

wp_ensg = np.load("output/pickles/wp_ensg.npy", allow_pickle=True) 
wp_prev_ccd = np.load("output/pickles/wp_prev_ccd.npy", allow_pickle=True) 
wp_prev_notccd = np.load("output/pickles/wp_prev_notccd.npy", allow_pickle=True) 
wp_prev_negative = np.load("output/pickles/wp_prev_negative.npy", allow_pickle=True) 
prev_ccd_ensg = np.load("output/pickles/prev_ccd_ensg.npy", allow_pickle=True) 
prev_notccd_ensg = np.load("output/pickles/prev_notccd_ensg.npy", allow_pickle=True) 
prev_negative_ensg = np.load("output/pickles/prev_negative_ensg.npy", allow_pickle=True)

u_well_plates_old = np.load("output/pickles/u_well_plates.devin.npy", allow_pickle=True)
perc_var_compartment_old = np.load("output/pickles/perc_var_compartment.devin.npy", allow_pickle=True)
perc_var_cell_old = np.load("output/pickles/perc_var_cell.devin.npy", allow_pickle=True)
perc_var_nuc_old = np.load("output/pickles/perc_var_nuc.devin.npy", allow_pickle=True)
perc_var_cyto_old = np.load("output/pickles/perc_var_cyto.devin.npy", allow_pickle=True)

mean_mean_comp = np.load("output/pickles/mean_mean_comp.npy", allow_pickle=True)
cv_comp = np.load("output/pickles/cv_comp.npy", allow_pickle=True)
gini_comp = np.load("output/pickles/gini_comp.npy", allow_pickle=True)
var_comp = np.load("output/pickles/var_comp.npy", allow_pickle=True)

pol_sort_well_plate = np.load("output/pickles/pol_sort_well_plate.npy", allow_pickle=True)
pol_sort_norm_rev = np.load("output/pickles/pol_sort_norm_rev.npy", allow_pickle=True)
pol_sort_ab_nuc = np.load("output/pickles/pol_sort_ab_nuc.npy", allow_pickle=True)
pol_sort_ab_cyto = np.load("output/pickles/pol_sort_ab_cyto.npy", allow_pickle=True)
pol_sort_ab_cell = np.load("output/pickles/pol_sort_ab_cell.npy", allow_pickle=True)
pol_sort_mt_cell = np.load("output/pickles/pol_sort_mt_cell.npy", allow_pickle=True)


wp_iscell = np.load("output/pickles/wp_iscell.npy", allow_pickle=True)
wp_isnuc = np.load("output/pickles/wp_isnuc.npy", allow_pickle=True)
wp_iscyto = np.load("output/pickles/wp_iscyto.npy", allow_pickle=True)
print("loaded")


    

#%%
# Idea: process the well data
# Exec: use Devin's code
# Output: the moving average plots for each gene studied
PSIN_INIT = [np.nan,1,1,np.nan] 
PSIN_BOUNDS = ((0, 1/6, 1/2, 0), (1, 100, 100, 1))
OUTLIER_NAMES = ['KIAA2026_HPA002109',
                'FEN1_HPA006581',
                'FASN_HPA006461',
                'EMP2_HPA014711',
                'CYTIP_HPA007191',
                'KREMEN2_HPA003223',
                'NXNL2_HPA045526',
                'CTU2_HPA041894',
                'GMNN_HPA054597']
PERCVAR_CUT = 0.1 #Min % of the variance explained by the cell cycle.
FDR_CUT = 0.05 #False discovery rate we will tolerate
WINDOW = 20 #Number of points for moving average window, arbitrary choice
DO_PLOTS = True #flag of whether to plot each well and save the plot
TPLOT_MODE = 'avg' #can have values of: 'avg', 'psin'
HIGHLIGHTS = ['ORC6','DUSP19','BUB1B','DPH2', 'FLI1']

def mvavg_perc_var(yvals,mv_window):
    yval_avg = np.convolve(yvals,np.ones((mv_window,))/mv_window, mode='valid')
    return np.var(yval_avg)/np.var(yvals), yval_avg

def temporal_mov_avg(curr_pol, curr_ab_norm, curr_mt_norm, outname, outsuff):
    plt.close()
    outfile = os.path.join(outname,outsuff+'_mvavg.pdf')
    if os.path.exists(outfile): return
    #plot data
    bin_size = WINDOW
    df = pd.DataFrame({
            "time" : curr_pol, 
            "intensity" : curr_ab_norm,
            "mt_intensity": curr_mt_norm})
    plt.figure(figsize=(5,5))
    plt.plot(
            df["time"],
            df["intensity"].rolling(bin_size).mean(),
            color="blue")
    plt.plot(
            df["time"],
            df["mt_intensity"].rolling(bin_size).mean(),
            color="red")
    plt.fill_between(
            df["time"], 
            df["intensity"].rolling(bin_size).quantile(0.10),
            df["intensity"].rolling(bin_size).quantile(0.90),
            color="lightsteelblue",
            label="10th & 90th Percentiles")
    plt.scatter(
            curr_pol,
            curr_ab_norm,
            c='c')
#    plt.ylim([0,1])
#    plt.xlim([0,1])
    plt.xlabel('Pseudotime')
    plt.ylabel(outsuff.split('_')[0] + ' Protein Expression')
    plt.xticks(size=14)
    plt.yticks(size=14)
    # plt.legend(fontsize=14)
    plt.tight_layout()
    if not os.path.exists(os.path.dirname(outfile)):
        os.mkdir(os.path.join(os.getcwd(), os.path.dirname(outfile)))
    plt.savefig(outfile)
    plt.close()

def _ecdf(x):
    '''no frills empirical cdf used in fdrcorrection'''
    nobs = len(x)
    return np.arange(1,nobs+1)/float(nobs)

def benji_hoch(alpha, pvals):
    pvals = np.nan_to_num(pvals, nan=1) # fail the ones with not enough data
    pvals_sortind = np.argsort(pvals)
    pvals_sorted = np.take(pvals, pvals_sortind)
    ecdffactor = _ecdf(pvals_sorted)
    reject = pvals_sorted <= ecdffactor*alpha
    reject = pvals_sorted <= ecdffactor*alpha
    if reject.any():
        rejectmax = max(np.nonzero(reject)[0])
        reject[:rejectmax] = True
    pvals_corrected_raw = pvals_sorted / ecdffactor
    pvals_corrected = np.minimum.accumulate(pvals_corrected_raw[::-1])[::-1]
    del pvals_corrected_raw
    pvals_corrected[pvals_corrected>1] = 1
    pvals_corrected_BH = np.empty_like(pvals_corrected)

    # deal with sorting
    pvals_corrected_BH[pvals_sortind] = pvals_corrected
    del pvals_corrected
    reject_BH = np.empty_like(reject)
    reject_BH[pvals_sortind] = reject
    return pvals_corrected_BH, reject_BH

# bonferroni MTC
def bonf(alpha, pvals):
    pvals = np.nan_to_num(pvals, nan=1) # fail the ones with not enough data
    pvals_sortind = np.argsort(pvals)
    pvals_sorted = np.take(pvals, pvals_sortind)
    alphaBonf = alpha / float(len(pvals))
    rejectBonf = pvals_sorted <= alphaBonf
    pvals_correctedBonf = pvals_sorted * float(len(pvals))
    pvals_correctedBonf_unsorted = np.empty_like(pvals_correctedBonf) 
    pvals_correctedBonf_unsorted[pvals_sortind] = pvals_correctedBonf
    rejectBonf_unsorted = np.empty_like(rejectBonf)
    rejectBonf_unsorted[pvals_sortind] = rejectBonf
    return pvals_correctedBonf_unsorted, rejectBonf_unsorted

def values_comp(values_cell, values_nuc, values_cyto, wp_iscell, wp_isnuc, wp_iscyto):
    '''Get the values for the annotated compartment'''
    values_comp = np.empty_like(values_cell)
    values_comp[wp_iscell] = np.array(values_cell)[wp_iscell]
    values_comp[wp_isnuc] = np.array(values_nuc)[wp_isnuc]
    values_comp[wp_iscyto] = np.array(values_cyto)[wp_iscyto]
    return np.array(values_comp)

x_fit = np.linspace(0,1,num=200)
ccd_coeff_list = []
not_ccd_coeff_list = []
xvals = np.linspace(0,1,num=21)
ccd_pvals = []
not_ccd_pvals = []

use_log_ccd = True
perc_var_cell, perc_var_nuc, perc_var_cyto, perc_var_mt = [],[],[],[] # percent variance attributed to cell cycle (mean POI intensities)
mvavgs_cell, mvavgs_nuc, mvavgs_cyto, mvavgs_mt = [],[],[],[] # moving average y values
ccd_var_cell_levenep, ccd_var_nuc_levenep, ccd_var_cyto_levenep = [],[],[] # two-tailed p values for equal variance of mvavg and raw values
cell_counts = []

for i, well in enumerate(u_well_plates):
#    print(well)
    plt.close('all')
#    well = 'H05_55405991'#GMNN well, used for testing
    curr_well_inds = pol_sort_well_plate==well
    curr_pol = pol_sort_norm_rev[curr_well_inds]
    curr_ab_cell = pol_sort_ab_cell[curr_well_inds] if not use_log_ccd else np.log10(pol_sort_ab_cell[curr_well_inds])
    curr_ab_nuc = pol_sort_ab_nuc[curr_well_inds] if not use_log_ccd else np.log10(pol_sort_ab_nuc[curr_well_inds])
    curr_ab_cyto = pol_sort_ab_cyto[curr_well_inds] if not use_log_ccd else np.log10(pol_sort_ab_cyto[curr_well_inds])
    curr_mt_cell = pol_sort_mt_cell[curr_well_inds] if not use_log_ccd else np.log10(pol_sort_mt_cell[curr_well_inds])
    
    # Normalize mean intensities, normalized for display
    curr_ab_cell_norm = curr_ab_cell / np.max(curr_ab_cell) 
    curr_ab_nuc_norm = curr_ab_nuc / np.max(curr_ab_nuc)
    curr_ab_cyto_norm = curr_ab_cyto / np.max(curr_ab_cyto) 
    curr_mt_cell_norm  = curr_mt_cell / np.max(curr_mt_cell)
    
    # Original method from Devin's work
    perc_var_cell_val, mvavg_cell = mvavg_perc_var(curr_ab_cell_norm, WINDOW)
    perc_var_nuc_val, mvavg_nuc = mvavg_perc_var(curr_ab_nuc_norm, WINDOW)
    perc_var_cyto_val, mvavg_cyto = mvavg_perc_var(curr_ab_cyto_norm, WINDOW)
    perc_var_mt_val, mvavg_mt = mvavg_perc_var(curr_mt_cell_norm, WINDOW)
    perc_var_xvals_val, mvavg_xvals = mvavg_perc_var(curr_pol, WINDOW)
    
    # Levene test for different variance over cell cycle compared to mt (one-tailed)
    # Tried it on the natural intensities, but the variation is probably in the log scale, since it's normal in the log scale
    # So comparing the microtubule to antibody intensities in the log scale may make more sense
    w, p = scipy.stats.levene(np.asarray(mvavg_cell), np.asarray(mvavg_mt), center="mean" if use_log_ccd else "median")
    ccd_var_cell_levenep.append(2*p)
    w, p = scipy.stats.levene(np.asarray(mvavg_nuc), np.asarray(mvavg_mt), center="mean" if use_log_ccd else "median")
    ccd_var_nuc_levenep.append(2*p)
    w, p = scipy.stats.levene(np.asarray(mvavg_cyto), np.asarray(mvavg_mt), center="mean" if use_log_ccd else "median")
    ccd_var_cyto_levenep.append(2*p)
    
    # What about testing for percent variance being higher for each well than the microtubules?
    # What about testing if the variances of the residuals is less than the variance overall (the fit is adding something...)
    
    # Test for equal variances of the moving averages and raw values
    perc_var_cell.append(perc_var_cell_val)
    perc_var_nuc.append(perc_var_nuc_val)
    perc_var_cyto.append(perc_var_cyto_val)
    perc_var_mt.append(perc_var_mt_val)
    
    mvavgs_cell.append(mvavg_cell)
    mvavgs_nuc.append(mvavg_nuc)
    mvavgs_cyto.append(mvavg_cyto)
    mvavgs_mt.append(mvavg_mt)
    
    cell_counts.append(len(curr_pol))
    percvar = perc_var_cell_val if wp_iscell[i] else perc_var_nuc_val if wp_isnuc[i] else perc_var_cyto_val
    if wp_prev_ccd[i] and percvar < 0.16:
        outname = "figures/191101CCDProteins"
        outstuff = wp_ensg[i]
        outfile = os.path.join(outname,outstuff+'_mvavg.pdf')
#        if os.path.exists(outfile): return
        df = pd.DataFrame({
                "time" : curr_pol, 
                "intensity" :  curr_ab_cell_norm if wp_iscell[i] else curr_ab_nuc_norm if wp_isnuc[i] else curr_ab_cyto_norm,
                "mt_intensity": curr_mt_cell_norm})
        plt.figure(figsize=(5,5))
        plt.plot(
                df["time"],
                df["intensity"].rolling(WINDOW).mean(),
                color="blue")
        plt.plot(
                df["time"],
                df["mt_intensity"].rolling(WINDOW).mean(),
                color="red")
        plt.fill_between(
                df["time"], 
                df["intensity"].rolling(WINDOW).quantile(0.10),
                df["intensity"].rolling(WINDOW).quantile(0.90),
                color="lightsteelblue",
                label="10th & 90th Percentiles")
        plt.scatter(
                curr_pol,
                curr_ab_cell_norm)
    #    plt.ylim([0,1])
    #    plt.xlim([0,1])
        plt.xlabel('Pseudotime')
        plt.ylabel(outstuff.split('_')[0] + ' Protein Expression')
        plt.xticks(size=14)
        plt.yticks(size=14)
        # plt.legend(fontsize=14)
        plt.tight_layout()
        if not os.path.exists(os.path.dirname(outfile)):
            os.mkdir(os.path.join(os.getcwd(), os.path.dirname(outfile)))
        plt.savefig(outfile)
        plt.close()
    
alpha_ccd = 0.01
perc_var_cell, perc_var_nuc, perc_var_cyto, perc_var_mt = np.array(perc_var_cell),np.array(perc_var_nuc),np.array(perc_var_cyto),np.array(perc_var_mt) # percent variance attributed to cell cycle (mean POI intensities)
mean_mean_cell, mean_mean_nuc, mean_mean_cyto, mean_mean_mt = np.array(mean_mean_cell), np.array(mean_mean_nuc), np.array(mean_mean_cyto), np.array(mean_mean_mt)
wp_cell_levene_eq_ccdvariability_adj, wp_pass_eq_ccdvariability_levene_bh_cell = benji_hoch(alpha_ccd, ccd_var_cell_levenep)
wp_nuc_levene_eq_ccdvariability_adj, wp_pass_eq_ccdvariability_levene_bh_nuc = benji_hoch(alpha_ccd, ccd_var_nuc_levenep)
wp_cyto_levene_eq_ccdvariability_adj, wp_pass_eq_ccdvariability_levene_bh_cyto = benji_hoch(alpha_ccd, ccd_var_cyto_levenep)


eqccdvariability_levene_comp_p = values_comp(ccd_var_cell_levenep, ccd_var_nuc_levenep, ccd_var_cyto_levenep, wp_iscell, wp_isnuc, wp_iscyto)
wp_comp_levene_eq_ccdvariability_adj, wp_pass_eq_ccdvariability_levene_bh_comp = benji_hoch(alpha_ccd, eqccdvariability_levene_comp_p)

# BenjiHoch is actually pretty liberal for this dataset. What about bonferroni?
wp_comp_levene_eq_ccdvariability_bonfadj, wp_bonfpass_eq_ccdvariability_levene_bh_comp = bonf(alpha_ccd, eqccdvariability_levene_comp_p)


#%% Do the percent variance values match up with what we measured before for the genes?
# Idea: take the perc var values from Devin's analysis and compare them to the ones now
# Execution: run old code and save the data
# Output: plot of percvar vs percvar
perc_var_comp = values_comp(perc_var_cell, perc_var_nuc, perc_var_cyto, wp_iscell, wp_isnuc, wp_iscyto)
var_comp = values_comp(var_cell, var_nuc, var_cyto, wp_iscell, wp_isnuc, wp_iscyto)
wp_comp_kruskal_adj = values_comp(wp_cell_kruskal_gaussccd_adj, wp_nuc_kruskal_gaussccd_adj, wp_cyto_kruskal_gaussccd_adj, wp_iscell, wp_isnuc, wp_iscyto)
wp_comp_mean_mean = values_comp(mean_mean_cell, mean_mean_nuc, mean_mean_cyto, wp_iscell, wp_isnuc, wp_iscyto)
wp_comp_levene_gtvariability_adj = values_comp(wp_cell_levene_gtvariability_adj, wp_nuc_levene_gtvariability_adj, wp_cyto_levene_gtvariability_adj, wp_iscell, wp_isnuc, wp_iscyto)

u_plates_old_idx = np.array([u_well_plates_list.index(wp) for wp in u_well_plates_old if wp in u_well_plates])
old_notfiltered = np.isin(u_well_plates_old, u_well_plates)

plt.scatter(perc_var_compartment_old[old_notfiltered], perc_var_comp[u_plates_old_idx], c=-np.log10(wp_comp_kruskal_adj[u_plates_old_idx]))
plt.xlabel("percent variance old")
plt.ylabel("percent variance new")
cb = plt.colorbar()
cb.set_label("-log10 FDR for Cell Cycle Dependence")
plt.savefig(f"figures/PercVarAgreement_comp.png")
plt.show()
plt.close()

plt.scatter(perc_var_comp, wp_comp_mean_mean)
plt.xlabel("percent variance new")
plt.ylabel("mean mean intensity")
plt.savefig(f"figures/PercVarVsMeanMeanIntensity_comp.png")
plt.show()
plt.close()

plt.scatter(perc_var_comp, -np.log10(wp_comp_levene_eq_ccdvariability_adj))
plt.xlabel("percent variance new")
plt.ylabel("-log10 FDR for CCD")
plt.hlines(-np.log10(alphaa), np.min(perc_var_comp), np.max(perc_var_comp))
plt.savefig(f"figures/PercVarVsLog10FdrCCD_comp.png")
plt.show()
plt.close()

plt.scatter(wp_comp_mean_mean, -np.log10(wp_comp_levene_eq_ccdvariability_adj))
plt.xlabel("mean mean intensity")
plt.ylabel("-log10 FDR for CCD")
plt.hlines(-np.log10(alphaa), np.min(wp_comp_mean_mean), np.max(wp_comp_mean_mean))
plt.savefig(f"figures/IntensityVsLog10FdrCCD_comp.png")
plt.show()
plt.close()

    
#%% Calculate the cutoffs for total intensity and percent variance attributed to the cell cycle
# Idea: create cutoffs for percent variance and 
# Execution: create cutoffs for perc_var and total variance per compartment and for integrated intensity and mean intensity
# Output: Graphs that illustrate the cutoffs (integrated, mean)
# Output: Overlap of the total variance cutoffs with the original filtering done manually

alphaa = 0.05
perc_var_mt_valid = perc_var_mt[~np.isinf(perc_var_mt) & ~np.isnan(perc_var_mt)]
percent_var_cutoff = 0.1#np.mean(perc_var_mt_valid) + 1 * np.std(perc_var_mt_valid)
print(f"{percent_var_cutoff}: cutoff for percent of total variance due to cell cycle")

wp_cell_ccd = perc_var_cell >= percent_var_cutoff
wp_nuc_ccd = perc_var_nuc >= percent_var_cutoff
wp_cyto_ccd = perc_var_cyto >= percent_var_cutoff

eqccdvariability_levene_comp = values_comp(wp_cell_levene_eq_ccdvariability_adj, wp_nuc_levene_eq_ccdvariability_adj, wp_cyto_levene_eq_ccdvariability_adj, wp_iscell, wp_isnuc, wp_iscyto)
ccd_levene_comp = values_comp(wp_pass_eq_ccdvariability_levene_bh_cell, wp_pass_eq_ccdvariability_levene_bh_nuc, wp_pass_eq_ccdvariability_levene_bh_cyto, wp_iscell, wp_isnuc, wp_iscyto)

wp_comp_ccd = perc_var_comp >= percent_var_cutoff
print(f"{sum(wp_cell_ccd)}: # proteins showing CCD variation, cell, percvar")
print(f"{sum(wp_nuc_ccd)}: # proteins showing CCD variation, nuc, percvar")
print(f"{sum(wp_cyto_ccd)}: # proteins showing CCD variation, cyto, percvar")
print(f"{sum(wp_comp_ccd)}: # proteins showing CCD variation, comp, percvar")
    
wp_comp_ccd_levene = eqccdvariability_levene_comp < alphaa
print(f"{sum(wp_comp_ccd_levene)}: # proteins showing CCD variation, comp, levene")
print(f"{sum(wp_comp_ccd_levene) / len(wp_comp_ccd_levene)}: fraction of variable proteins showing CCD variation, comp, levene")

#wp_any_ccd_kruskal_adj = (wp_cell_kruskal_gaussccd_adj < alphaa) | (wp_nuc_kruskal_gaussccd_adj < alphaa) | (wp_cyto_kruskal_gaussccd_adj < alphaa)
#plt.scatter(var_comp[var_pass_comp], perc_var_comp[var_pass_comp], c=wp_comp_kruskal_adj[var_pass_comp])
## plt.vlines(total_var_cutoff, 0, 0.9)
#plt.hlines(percent_var_cutoff, 0, 0.1)
#plt.xlabel("Total Variance of Protein Expression")
#plt.ylabel("Fraction of Variance Due to Cell Cycle")
#cb = plt.colorbar()
#cb.set_label("FDR for Cell Cycle Dependence")
#plt.title("Compartment - Fraction of Variance Due to Cell Cycle")
#plt.savefig("figures/CompartmentProteinFractionVariance.png")
#plt.show()
#plt.close()
#wp_comp_ccd_percvaronly = var_pass_comp & (perc_var_comp >= percent_var_cutoff)
#print(f"{sum(wp_comp_ccd_percvaronly)}: # proteins showing CCD variation (mvavg), respective compartment")
#wp_comp_ccd = var_pass_comp & (perc_var_comp >= percent_var_cutoff) & (wp_comp_kruskal_adj < alphaa)
#print(f"{sum(wp_comp_ccd)}: # proteins showing CCD variation (mvavg & gauss), respective compartment")

#plt.scatter(var_comp[var_pass_comp], -np.log10(wp_comp_levene_eq_ccdvariability_bonfadj[var_pass_comp]), c=wp_comp_kruskal_adj[var_pass_comp])
## plt.vlines(total_var_cutoff, 0, 0.9)
#plt.hlines(-np.log10(0.01), 0, 0.1)
#plt.xlabel("Total Variance of Protein Expression")
#plt.ylabel("FDR")
#cb = plt.colorbar()
#cb.set_label("FDR for Cell Cycle Dependence")
#plt.title("Compartment - Fraction of Variance Due to Cell Cycle")
#plt.savefig("figures/CompartmentProteinFractionVariance.png")
#plt.show()
#plt.close()

# Output a list of the genes that show variation
name_df = pd.read_csv("input/processed/excel/Fucci_staining_summary_first_plates.csv")
wppp1, ensggg1, abbb1 = list(name_df["well_plate"]), list(name_df["ENSG"]), list(name_df["Antibody"])
name_df2 = pd.read_csv("input/processed/excel/Fucci_staining_review_variation_check.csv")
wppp2, ensggg2, abbb2 = list(name_df2["well_plate"]), list(name_df2["ENSG"]), list(name_df2["Antibody"])
wppp, ensggg, abbb = wppp1 + wppp2, ensggg1 + ensggg2, abbb1 +  abbb2

ensg_dict = dict([(wppp[i], ensggg[i]) for i in range(len(wppp))])
ab_dict = dict([(wppp[i], abbb[i]) for i in range(len(wppp))])
ENSG = np.asarray([ensg_dict[wp] if wp in ensg_dict else "" for wp in well_plate])
antibody = np.asarray([ab_dict[wp] if wp in ab_dict else "" for wp in well_plate])

alpha = 0.05
does_perc_vary_cell = np.array(perc_var_cell) >= percent_var_cutoff
does_perc_vary_nuc = np.array(perc_var_nuc) >= percent_var_cutoff
does_perc_vary_cyto = np.array(perc_var_cyto) >= percent_var_cutoff
does_perc_vary_any = does_perc_vary_cell | does_perc_vary_nuc | does_perc_vary_cyto
ccd_cell = does_perc_vary_cell & (wp_cell_kruskal_gaussccd_adj < alpha)
ccd_cyto = does_perc_vary_cyto & (wp_cyto_kruskal_gaussccd_adj < alpha)
ccd_nuc = does_perc_vary_nuc & (wp_nuc_kruskal_gaussccd_adj < alpha)
ccd_any = ccd_cell | ccd_cyto | ccd_nuc
ccd_comp = wp_comp_ccd
nonccd_cell = ~ccd_cell
nonccd_cyto = ~ccd_cyto
nonccd_nuc = ~ccd_nuc
nonccd_any = nonccd_cell | nonccd_cyto | nonccd_nuc
nonccd_comp = var_pass_comp & ~ccd_comp

n_tot_variable = sum(wp_pass_gtvariability_levene_bh_cell|wp_pass_gtvariability_levene_bh_nuc|wp_pass_gtvariability_levene_bh_cyto)
n_tot_variable_comp = sum(wp_cell_var_and_loc|wp_nuc_var_and_loc|wp_cyto_var_and_loc)
print(f"{n_tot_variable}: # total proteins showing variation")
print(f"{n_tot_variable_comp}: # total proteins showing variation in compartment")
print(f"{len([ensg for ensg in ensggg1 if ensg in wp_ensg[wp_pass_gtvariability_levene_bh_cell|wp_pass_gtvariability_levene_bh_nuc|wp_pass_gtvariability_levene_bh_cyto]]) / len(ensggg1)}: # fraction of proteins annotated as variable still annotated as such")
print(f"{len([ensg for ensg in ensggg1 if ensg in wp_ensg[wp_cell_var_and_loc|wp_nuc_var_and_loc|wp_cyto_var_and_loc]]) / len(ensggg1)}: # fraction of proteins annotated as variable still annotated as such in selected metacompartment")

print(f"{sum(wp_prev_ccd & ccd_any) / len(prev_ccd_ensg)}: fraction of previously annotated CCD genes called CCD (mvavg & gauss, any)")
print(f"{sum(wp_prev_ccd & wp_any_ccd_kruskal_adj) / len(prev_ccd_ensg)}: fraction of previously annotated CCD genes called CCD (gauss, any)")
print(f"{sum(wp_prev_ccd & wp_logany_var_and_loc & does_perc_vary_any) / len(prev_ccd_ensg)}: fraction of previously annotated CCD genes called CCD (mvavg, any)")
print(f"{sum(wp_prev_ccd & ccd_comp) / len(prev_ccd_ensg)}: fraction of previously annotated CCD genes called CCD (mvavg & gauss, comp)")
print(f"{sum(wp_prev_ccd & (wp_comp_kruskal_adj < alphaa)) / len(prev_ccd_ensg)}: fraction of previously annotated CCD genes called CCD (gauss, comp)")
print(f"{sum(wp_prev_ccd & (perc_var_comp >= percent_var_cutoff)) / len(prev_ccd_ensg)}: fraction of previously annotated CCD genes called CCD (mvavg, comp)")

print(f"{sum(wp_prev_ccd & ccd_any) / len(prev_ccd_ensg)}: fraction of previously annotated CCD genes called CCD (mvavg & gauss, any)")
print(f"{sum(wp_prev_ccd & wp_any_ccd_kruskal_adj) / len(prev_ccd_ensg)}: fraction of previously annotated CCD genes called CCD (gauss, any)")
print(f"{sum(wp_prev_ccd & wp_logany_var_and_loc & does_perc_vary_any) / len(prev_ccd_ensg)}: fraction of previously annotated CCD genes called CCD (mvavg, any)")
print(f"{sum(wp_prev_ccd & ccd_comp) / len(prev_ccd_ensg)}: fraction of previously annotated CCD genes called CCD (mvavg & gauss, comp)")
print(f"{sum(wp_prev_ccd & (wp_comp_kruskal_adj < alphaa)) / len(prev_ccd_ensg)}: fraction of previously annotated CCD genes called CCD (gauss, comp)")
print(f"{sum(wp_prev_ccd & (var_pass_comp & (perc_var_comp >= percent_var_cutoff))) / len(prev_ccd_ensg)}: fraction of previously annotated CCD genes called CCD (mvavg, comp)")

print(f"{sum(wp_prev_ccd & (var_pass_comp & (perc_var_comp >= percent_var_cutoff))) / len(prev_ccd_ensg)}: fraction of previously annotated CCD genes called CCD (mvavg)")
print(f"{len([ensg for ensg in wp_ensg[wp_comp_ccd] if ensg in ensggg1 and ensg in prev_ccd_ensg]) / len(wp_ensg[wp_comp_ccd])}: fraction of CCD genes that are previously annotated CCD genes (mvavg & gauss)")
print(f"{len([ensg for ensg in wp_ensg[wp_comp_kruskal_adj < alphaa] if ensg in ensggg1 and ensg in prev_ccd_ensg]) / len(wp_ensg[wp_comp_kruskal_adj < alphaa])}: fraction of CCD genes that are previously annotated CCD genes (gauss)")
print(f"{len([ensg for ensg in wp_ensg[var_pass_comp & (perc_var_comp >= percent_var_cutoff)] if ensg in ensggg1 and ensg in prev_ccd_ensg]) / len(wp_ensg[var_pass_comp & (perc_var_comp >= percent_var_cutoff)])}: fraction of CCD genes that are previously annotated CCD genes (mvavg)")
print(f"{sum(ccd_comp)}: CCD variable proteins (mvavg & gauss)")
print(f"{sum(wp_comp_kruskal_adj < alphaa)}: CCD variable proteins (gauss)")
print(f"{sum(var_pass_comp & (perc_var_comp >= percent_var_cutoff))}: CCD variable proteins (mvavg)")
print(f"{len(prev_ccd_ensg)}: CCD variable proteins (previous)")
print(f"{sum(nonccd_comp)}: non-CCD variable proteins")

examples=np.loadtxt("input/processed/manual/ensgexamplesfrompaper.txt", dtype=str)
print(f"{sum(~np.isin(examples,wp_ensg[ccd_any]))}: number of examples missing of {len(examples)}, which includes 1 negative control (mvavg & gauss, any)")
print(f"{sum(~np.isin(examples,wp_ensg[wp_any_ccd_kruskal_adj]))}: number of examples missing of {len(examples)}, which includes 1 negative control (gauss, any)")
print(f"{sum(~np.isin(examples,wp_ensg[wp_logany_var_and_loc & does_perc_vary_any]))}: number of examples missing of {len(examples)}, which includes 1 negative control (mvavg, any)")
print(f"{sum(~np.isin(examples,wp_ensg[ccd_any]))}: number of examples missing of {len(examples)}, which includes 1 negative control (mvavg & gauss, any)")
print(f"{sum(~np.isin(examples,wp_ensg[ccd_comp]))}: number of examples missing of {len(examples)}, which includes 1 negative control, (mvavg & gauss, comp)")
print(examples[~np.isin(examples,wp_ensg[ccd_comp])])

pd.DataFrame({
    "well_plate" : u_well_plates, 
    "ENSG": wp_ensg,
    "var_cell":var_cell,
    "var_cyto":var_cyto,
    "var_nuc":var_nuc,
    "perc_var_cell":perc_var_cell,
    "perc_var_cyto":perc_var_cyto,
    "perc_var_nuc":perc_var_nuc,
    "perc_var_comp":perc_var_comp,
    "wp_cell_kruskal_gaussccd_adj":wp_cell_kruskal_gaussccd_adj,
    "wp_cyto_kruskal_gaussccd_adj":wp_cyto_kruskal_gaussccd_adj,
    "wp_nuc_kruskal_gaussccd_adj":wp_nuc_kruskal_gaussccd_adj,
    "ccd_cell":ccd_cell,
    "ccd_cyto":ccd_cyto,
    "ccd_nuc":ccd_nuc,
    "ccd_any":ccd_any,
    "ccd_comp":ccd_comp,
    "nonccd_cell":nonccd_cell,
    "nonccd_cyto":nonccd_cyto,
    "nonccd_nuc":nonccd_nuc,
    "nonccd_any":nonccd_any,
    "nonccd_comp":nonccd_comp,
    "in_firstbatch":np.isin(wp_ensg, ensggg1),
    "in_secondbatch":np.isin(wp_ensg, ensggg2),
    "is_variable":wp_pass_gtvariability_levene_bh_cell|wp_pass_gtvariability_levene_bh_nuc|wp_pass_gtvariability_levene_bh_cyto,
    "is_variable_comp":wp_cell_var_and_loc|wp_nuc_var_and_loc|wp_cyto_var_and_loc,
    "wp_prev_ccd":wp_prev_ccd,
    "is_newccd":ccd_comp,
    }).to_csv("output/CellCycleVariationSummary.csv")
    
pd.DataFrame({"ENSG":wp_ensg[wp_prev_ccd & ~ccd_comp]}).to_csv("output/DianaCCDMissingProteins.csv")
pd.DataFrame({"ENSG":wp_ensg[~wp_prev_ccd & ccd_comp]}).to_csv("output/NewToDianaCCDProteins.csv")


#%% Pickle the results needed later
def np_save_overwriting(fn, arr):
    with open(fn,"wb") as f:    
        np.save(f, arr, allow_pickle=True)

np_save_overwriting("output/pickles/ccd_comp.npy", ccd_comp)
np_save_overwriting("output/pickles/nonccd_comp.npy", nonccd_comp)
np_save_overwriting("output/pickles/wp_ensg.npy", wp_ensg)

np.savetxt("output/picklestxt/ccd_compartment_ensg.txt", wp_ensg[ccd_comp], fmt="%s", delimiter="\t")
np.savetxt("output/picklestxt/nonccd_compartment_ensg.txt", wp_ensg[nonccd_comp], fmt="%s", delimiter="\t")
