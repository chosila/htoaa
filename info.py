## file namesQCDType = 'QCD_BGenFilter/'#QCDType = 'QCD_bEnriched/'fileNames = [     'GGH_HPT',     QCDType + 'QCD_HT200to300',     QCDType + 'QCD_HT300to500',     QCDType + 'QCD_HT500to700',     QCDType + 'QCD_HT700to1000',     QCDType + 'QCD_HT1000to1500',     QCDType + 'QCD_HT1500to2000',     QCDType + 'QCD_HT2000toInf'    ]## QCD_BGenFilter# weight = [#     1, #     1, #     0.259, #     0.0515, #     0.01666, #     0.00905, #     0.003594, #     0.001401#     ]## QCD_bEnrichedweight = [    1,     1,     0.33,     0.034,     0.034,     0.0024,     0.00024,     0.00044    ]weightDict = dict(zip(fileNames, weight))## vars for training and cutting datatrainVars = [    'FatJet_pt',     'FatJet_eta',     'FatJet_mass',     'FatJet_btagCSVV2',     'FatJet_btagDeepB',     'FatJet_msoftdrop',     'FatJet_btagDDBvL',    'FatJet_deepTagMD_H4qvsQCD'    ]cutVars = [    'FatJet_btagDDBvL',     'FatJet_btagDeepB',     'FatJet_mass',     'FatJet_msoftdrop',     'FatJet_pt'    ]allVars = list(set(cutVars + trainVars))## making cuts, in order of cutVars. should I make this a dict instead? is## it safer?cutValues = [0.8, 0.4184, 90, 90, 240]cutDict = dict(zip(cutVars, cutValues))