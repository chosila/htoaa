import pickle
import numpy as np
import pandas as pd
from analib import PhysObj, Event
import dataVsMC_DataManager as DM
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import mplhep as hep
import uproot
import os
import multiprocessing as mp
import time 



pool = mp.Pool(mp.cpu_count())

#np.seterr(divide='ignore', invalid='ignore')

## get that sweet CMS style plots
plt.style.use(hep.style.CMS)


## if reading from rootfiles, set true. if already have pickle of dataframe, set false
root = True

## function to add a BDTScore column to each of the background/signal/data DF
# loadedModel = pickle.load(open('BDTModels/Htoaa_BDThigh disc.pkl', 'rb'))
#def analyze(dataDf):
#    prediction = loadedModel.predict_proba(dataDf[trainVars])
#    dataDf = dataDf.assign(BDTScore=prediction[:,1])
#    return dataDf




histranges = {           'FatJet_btagCSVV2' :   ((0,1), 20), 
                       'FatJet_btagDDBvLV2' :   ((0,1), 20), 
                         'FatJet_btagDeepB' :   ((0,1), 20), 
                'FatJet_deepTagMD_H4qvsQCD' :   ((0,1), 20), 
                               'FatJet_eta' :   ((-2.4, 2.4), 20), 
                              'FatJet_mass' :   ((90, 250), 32), 
                         'FatJet_msoftdrop' :   ((90, 200), 22), 
                              'FatJet_n2b1' :   ((0, 0.5), 10), 
                                'FatJet_pt' :   ((180, 1500), 40), 
                                   'LHE_HT' :   ((500, 2500), 50),
                 'FatJet_particleNetMD_Xbb' :   ((0,1), 20),
              'FatJet_particleNet_H4qvsQCD' :   ((0,1), 20),
              'FatJet_particleNet_HbbvsQCD' :   ((0,1),20),
                 'FatJet_particleNetMD_QCD' :   ((0,1),20),
                   'FatJet_particleNet_QCD' :   ((0,1),20),
                         'FatJet_particleNet_mass' :   ((0,250), 20),
                'FatJet_deepTagMD_HbbvsQCD' :   ((0,1), 20),
               'FatJet_deepTagMD_ZHbbvsQCD' :   ((0,1), 20),
               'FatJet_deepTagMD_bbvsLight' :   ((0,1), 20), 
                         'FatJet_deepTag_H' :   ((0,1), 20),
                       'FatJet_deepTag_QCD' :   ((0,1), 20),
                           'FatJet_btagHbb' :   ((-1,1), 20),

              #'Muon_eta' : (-2.4, 2.4), 
              #'Muon_ip3d' : (0, 0.5), 
              #'Muon_pt' : (0, 300), 
              #'Muon_softId' : (0,1), 
              'PV_npvs' : ((1,90), 10), 
                         'PV_npvsGood': ((0,70), 10)} 

nphists = {col:[0.0, 0.0] for col in histranges}
cols = histranges.keys()

## function to get center of ins given binedges as np array
def getBinCenter(arr):
    arrCen = list()
    for i in range(len(arr)-1):
        arrCen.append((arr[i+1]+arr[i])/2)
    return arrCen


## get all rootfiles from a given folder 
# def getFileNames(directory):
#     filelist = []
#     for root, dirs, files in os.walk(directory):
#         for name in files:
#             filelist.append(os.path.join(root, name))
#     return filelist


## make dict of np.histogram given maxPtData df 
def makeNpHist(df):
    toremove = ['final_weights', 'LHE_weights']

    for i in toremove:
        if i in cols: cols.remove(i)

    nphistdict = {}

    for var in cols:
        nbins = histranges[var][1]
        
        nphistdict[var] = np.histogram(df[var], bins=nbins, range=histranges[var][0], weights=df['final_weights'])

    return nphistdict


## main 
def main():

    # read the bgenfile from txt
    with open('BGenFiles.txt') as f:
        #BGenPaths = filter(None, (line.rstrip() for line in f_in))
    #with open('BGenFiles.txt') as f: 
        BGenPaths = [line.rstrip() for line in f]#filter(None, (line.rstrip() for line in f)) #f.read().split('\n')

    BGenPaths = ['root://xrootd-cms.infn.it/' + x for x in BGenPaths]
    
    chunksize = 40
    BGenPathsChunks = [BGenPaths[i:i+chunksize] for i in range(0, len(BGenPaths), chunksize)]

    for filedirs in BGenPathsChunks:#DM.BGenPaths:#DM.TunCP5Path
        ## better to parallel across the files than folders since more files than folders exist
        
        resultObj = [pool.apply_async(DM.processData, args=(filedir, 'BGen', 'UL', True)) for filedir in filedirs]
        results = [r.get() for r in resultObj]

        # for filedir in filedirs:
        #     df = DM.processData(filedir, tag='TunCP5', dataSet='UL', MC=True)
            
        ## this needs to become it's own loop over the result objects 
        for df in results:
            
            if df.empty:
                print('df empty')
                continue
            tmpdict = makeNpHist(df)
        
            for col in nphists:
                nphists[col][0] += tmpdict[col][0] # histograms need to be appended 
                nphists[col][1] = tmpdict[col][1] # the edges stay the same throughout. can be done outside loop but i don't want to loop twice 
        

    print(nphists)
    
    ## save nphists so that it can be loaded and plotted without running the whole thing again
    import pickle 
    pickle.dump(open('pickles/nphists.py', 'wb'), nphists)

    ## plot. maybe this can be a function?? 
    for col in nphists: 
        fig, ax = plt.subplots(figsize=(11,7))
        bincen = getBinCenter(nphists[col][1])
        bar = nphists[col][0]
        width = (bincen[1] - bincen[0])
        ax.bar(bincen, bar, width=width)
        ax.set_title('BGenFilter_TuneCP5')
        ax.set_xlabel(col)
        plt.savefig(f'ULPlots/{col}.png', bbox_inches='tight')
        plt.close(fig)
        
        if 'LHE' in col: 
            fig, ax = plt.subplots(figsize=(11,7))
            bincen = getBinCenter(nphists[col][1])
            bar = nphists[col][0]
            width = (bincen[1] - bincen[0])
            ax.bar(bincen, bar, width=width)
            ax.set_title('BGenFilter_TuneCP5')
            ax.set_xlabel(col + ' LogY Scale')
            ax.set_yscale('log')
            plt.savefig(f'ULPlots/{col}-logY.png', bbox_inches='tight')
            plt.close(fig)



if __name__ == "__main__":
    start = time.time()
    main()
    print(f'time taken: {time.time() - start}')
