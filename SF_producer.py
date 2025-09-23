# Load the setup
# source /cvmfs/sft.cern.ch/lcg/views/LCG_106a/x86_64-el9-gcc13-opt/setup.sh
import ROOT as rt
from copy import deepcopy
import pandas as pd
from math import sqrt
import os

rt.gStyle.SetOptStat(0)
rt.gROOT.SetBatch()

# Lists of functions needed to produce the SFs
def geteff(h_total, h_pass, var):
    #heff = rt.TEfficiency(h_pass, h_total)
    heff = h_pass.Clone()
    heff.SetTitle(var.replace("mujet_pt_", ""))
    heff.Divide(h_pass, h_total, 1, 1, "B")
    return deepcopy(heff)

def sumhist(infil, histn):
    tmp = infil.Get(histn[0]).Clone()
    tmp.GetXaxis().SetTitle("p_{T} [GeV]")
    #print(tmp.Integral())
    tmp.Reset("ICES")
    sumh = tmp.Clone("MC_sum")
    for h in histn:
        #print(h)
        tmp = infil.Get(h).Clone()
        #print(tmp.Integral)
        sumh.Add(tmp, 1)
        #print(sumh.Integral())
    return deepcopy(sumh)

def getc_data(data, fullMC, cW):
    hdata = data.Clone()
    hdata.Add(fullMC, -scale)
    hdata.Add(cW, scale)
    return deepcopy(hdata)

def drawandsave(h, var, lep, era):
    c1 = rt.TCanvas('','', 0, 0, 700, 600)
    c1.Draw()
    h.Draw()
    rt.gPad.Modified()
    rt.gPad.Update()
    h.GetLowerRefYaxis().SetTitle("SF")
    h.GetUpperRefYaxis().SetTitle("Efficiency")
    p = h.GetUpperPad()
    #leg = p.BuildLegend()
    legend = rt.TLegend(0.65,0.78,0.89,0.89)
    legend.AddEntry("Data","Data","l")
    legend.AddEntry("MC","MC","le")
    legend.Draw()
    Tl = rt.TLatex()
    Tl.SetTextAlign(12)
    Tl.SetTextSize(0.04)
    Tl.DrawLatex(0.15,0.8, f"Summer {era}")
    p.Modified()
    p.Update()    #c1.BuildLegend()
    c1.Update()
    c1.Print(f"v1_fix_SF_{var}_{lep}_{era}.png")
    c1.Print(f"v1_fix_SF_{var}_{lep}_{era}.pdf")

def ratio(h1, h2, var, lep, era, syst):
    print(var)
    var_r = var.split('_')[-1]
    c1 = rt.TCanvas('','', 0, 0, 700, 600)
    c1.Draw()
    h1.SetLineColor(rt.kRed)
    h1.SetName("Data")
    h1.SetTitle(var.replace("mujet_pt_", ""))
    h1.SetMaximum(1.6)
    h1.SetMinimum(0.2)
    h1.GetXaxis().SetTitle("p_{T} [GeV]")
    h2.SetName("MC")
    h_ratio = rt.TRatioPlot(h1, h2)
    out = deepcopy(h_ratio)
    drawandsave(out, var, lep, era)
    h_ratio.Draw()
    graph = h_ratio.GetLowerRefGraph()
    xaxis = h1.GetXaxis()
    npoi = graph.GetN()
    y_values = [0.0]*npoi
    ptmin = [0.0]*npoi
    ptmax = [0.0]*npoi
    erryh_values = [0.0]*npoi
    erryl_values = [0.0]*npoi
    wp = [[*var_r][-1]]*npoi
    if [*var_r][-2] == 'X' and [*var_r][-1] == 'T':
        wp = ['XT']*npoi
    syst_name = [syst]*npoi
    if syst == 'nominal':
        syst_name = ['central']*npoi
        syst_nameup = ['up_stat']*npoi
        syst_namedown = ['down_stat']*npoi    
    for i in range(npoi):
        ptmin[i] = xaxis.GetBinLowEdge(i+1)
        ptmax[i] = xaxis.GetBinUpEdge(i+1)
        y_values[i] = graph.GetY()[i]
        erryh_values[i] = graph.GetY()[i] + graph.GetEYhigh()[i]
        erryl_values[i] = graph.GetY()[i] - graph.GetEYlow()[i]

    nom_values = {
        "wp": wp,
        "type": ['wc']*npoi,
        "syst": syst_name,
        "flav": [4]*npoi,
        "etaMin": [0]*npoi,
        "etaMax": [2.4]*npoi,
        "ptMin": ptmin,
        "ptMax": ptmax,
        "discrMin": [0]*npoi,             
        "discrMax": [1]*npoi,
        "formula": y_values
    }
    data = pd.DataFrame(data=nom_values)
    if syst == 'nominal':
        up_values = {
            "wp": wp,
            "type": ['wc']*npoi,
            "syst": syst_nameup,
            "flav": [4]*npoi,
            "etaMin": [0]*npoi,
            "etaMax": [2.4]*npoi,
            "ptMin": ptmin,
            "ptMax": ptmax,
            "discrMin": [0]*npoi,             
            "discrMax": [1]*npoi,
            "formula": erryh_values
        }
        data_up = pd.DataFrame(data=up_values)
        down_values = {
            "wp": wp,
            "type": ['wc']*npoi,
            "syst": syst_namedown,
            "flav": [4]*npoi,
            "etaMin": [0]*npoi,
            "etaMax": [2.4]*npoi,
            "ptMin": ptmin,
            "ptMax": ptmax,
            "discrMin": [0]*npoi,             
            "discrMax": [1]*npoi,
            "formula": erryl_values
        }
        data_down = pd.DataFrame(data=down_values)
        data = pd.concat([data, data_up, data_down])
    return data

def get_final_dataframe(dict_dataframes, vars):
    final_dataframe_dict = {}
    for var in vars:
        final_dataframe = dict_dataframes['nominal'+var]
        only_nominal = final_dataframe[final_dataframe['syst'] == 'central']
        systup_dict = only_nominal.to_dict()
        systdown_dict = only_nominal.to_dict()
        systup_values = {}
        systdown_values = {}
        for i in range(len(only_nominal['formula'])):
            systup_values[i] = only_nominal['formula'][i] + sqrt(sum([(dict_dataframes[key]['formula'][i] - only_nominal['formula'][i])**2 for key in dict_dataframes.keys() if 'Up' in key and var in key and not 'nominal' in key]))
            systdown_values[i] = only_nominal['formula'][i] - sqrt(sum([(dict_dataframes[key]['formula'][i] - only_nominal['formula'][i])**2 for key in dict_dataframes.keys() if 'Down' in key and var in key and not 'nominal' in key]))
        systup_dict['formula'] = systup_values
        systdown_dict['formula'] = systdown_values
        dataframe_systup = pd.DataFrame(data=systup_dict)
        dataframe_systup.replace('central', 'up_syst', inplace=True)
        dataframe_systdown = pd.DataFrame(data=systdown_dict)
        dataframe_systdown.replace('central', 'down_syst', inplace=True)
        final_dataframe_dict[var.replace('mujet_pt_', '')] = pd.concat([final_dataframe, dataframe_systup, dataframe_systdown])
    return final_dataframe_dict

# Main part of the code
# Definition of the variables
path = {}
path["mu"] = "/eos/user/a/adeiorio/btv_ctag_SF/v1EE/histo/"
path["e"] = "/eos/user/a/adeiorio/btv_ctag_SF/v1eEE/histo/"
path["mue"] = "/eos/user/a/adeiorio/btv_ctag_SF/sum_v1/"
#path["mue"] = "/eos/user/a/adeiorio/btv_ctag_SF/23/sum_v1/"
era = "22EE"  # Change this to the desired era, e.g., "22EE", "23", "23BP"
scale = 7

bvar = "mujet_pt"
allvar = []
c_algos = ["DeepFlav", "RobustParTAK4", "PNet"]
c_WPs = {'22':["L", "M", "T"],
         '23':["L", "M", "T", "XT"]
        }
for c_algo in c_algos:
    for c_WP in c_WPs[era[:2]]:
        allvar.append(f"{bvar}_{c_algo}{c_WP}")

histn = ["WJets",
         "ZJets",
         "VV",
         "TT",
         "ST"]
#allvar.remove(bvar)

systs = {
        '22': ['nominal', 'puweightUp', 'puweightDown', 'mu_IDUp', 'mu_IDDown', 'mu_IsoUp', 'mu_IsoDown', 'JESUp', 'JESDown', 'UESUp', 'UESDown', 'JERUp', 'JERDown'],
        '22EE': ['nominal', 'puweightUp', 'puweightDown', 'ele_IDUp', 'ele_IDDown', 'ele_Reco_medDown', 'ele_Reco_medUp', 'mu_IDUp', 'mu_IDDown', 'mu_IsoUp', 'mu_IsoDown', 'JESUp', 'JESDown', 'UESUp', 'UESDown', 'JERUp', 'JERDown'],
        '23': ['nominal', 'puweightUp', 'ele_RecoDown', 'scalevar_muFUp', 'scalevar_muRUp', 'UEPS_FSRUp', 'ele_IDUp', 'scalevar_muFDown', 'scalevar_muR_muFUp', 'UEPS_ISRDown', 'PDFaS_weightUp', 'ele_IDDown', 'PDF_weightUp', 'scalevar_muRDown', 'aS_weightUp', 'ele_RecoUp', 'puweightDown', 'PDF_weightDown', 'UEPS_FSRDown', 'PDFaS_weightDown', 'UEPS_ISRUp', 'scalevar_muR_muFDown', 'aS_weightDown', 'JESUp', 'JESDown', 'UESUp', 'UESDown', 'JERUp', 'JERDown'],
        '23BP': ['nominal', 'UEPS_ISRDown', 'ele_RecoDown', 'scalevar_muRDown', 'aS_weightDown', 'PDF_weightUp', 'puweightDown', 'UEPS_FSRDown', 'PDFaS_weightUp', 'PDFaS_weightDown', 'scalevar_muFUp', 'ele_IDUp', 'scalevar_muR_muFUp', 'ele_IDDown', 'PDF_weightDown', 'ele_RecoUp', 'scalevar_muR_muFDown', 'scalevar_muFDown', 'aS_weightUp', 'puweightUp', 'scalevar_muRUp', 'UEPS_ISRUp', 'UEPS_FSRUp', 'JESUp', 'JESDown', 'JERUp', 'JERDown']
    }
lep = "mue"
dict_dataframes = {}

for syst in systs[era]:
    single_MC = {}
    print(f"******* Opening file {path[lep]}{bvar}_{era}_histMC_{syst}.root *******")
    inf_MC = rt.TFile.Open(f"{path[lep]}{bvar}_{era}_histMC_{syst}.root", "R")
    full_MC = sumhist(inf_MC, histn)
    for hnm in histn:
        single_MC[hnm] = deepcopy(inf_MC.Get(hnm))
        print(scale*single_MC[hnm].Integral())
        
    inf_MC.Close()

    single_MC_c = {}
    inf_MC_c = rt.TFile.Open(f"{path[lep]}{bvar}_{era}_c_histMC_{syst}.root", "R")
    full_MC_c = sumhist(inf_MC_c, histn)
    for hnm in histn:
        single_MC_c[hnm] = deepcopy(inf_MC_c.Get(hnm))
        print(scale*single_MC_c[hnm].Integral())
    inf_MC_c.Close()

    inf_data = rt.TFile.Open(f"{path[lep]}{bvar}_{era}_histdata.root")
    full_h_data = deepcopy(inf_data.Get('data'))

    print(scale*full_MC.Integral(), full_h_data.Integral())

    print("W+c & ", round(single_MC_c["WJets"].Integral()/full_MC.Integral()*100, 1),"\% \\\\")
    for hnm in histn:
        print(hnm, " & ", round(single_MC[hnm].Integral()/full_MC.Integral()*100, 1),"\% \\\\")

    eff_c_MC = {}
    eff_c_data = {}
    full_c_data = getc_data(full_h_data, full_MC, single_MC_c["WJets"])
    print("Algorithm & WP & Efficiency \\")
    print(" &  & MC & Data\\")
    for var in allvar:
        inf_c = rt.TFile.Open(f"{path[lep]}{var}_{era}_c_histMC_{syst}.root")
        var_c_WJ = deepcopy(inf_c.Get("WJets").Clone())
        eff_c_MC[var] = geteff(single_MC_c["WJets"], var_c_WJ, var)
        inf_c.Close()
        inf_data = rt.TFile.Open(f"{path[lep]}{var}_{era}_histdata.root")
        h_pass = inf_c.Get('data')
        inf_MC = rt.TFile.Open(f"{path[lep]}{var}_{era}_histMC_{syst}.root")
        #print("data integral ", h_pass.Integral())
        data_c = getc_data(inf_data.Get('data').Clone(), sumhist(inf_MC, histn), var_c_WJ)
        eff_c_data[var] = geteff(full_c_data, data_c, var)
        print(var.replace("mujet_pt_", ""), " & ", round(var_c_WJ.Integral()/single_MC_c["WJets"].Integral()*100, 1), " & " , round(data_c.Integral()/full_c_data.Integral()*100, 1))
        inf_c.Close()

        dict_dataframes[syst + var] = ratio(eff_c_data[var].Clone(), eff_c_MC[var].Clone(), var, lep, era, syst)
    print(dict_dataframes)

print("This is the final dataframe")
final_dataframes = get_final_dataframe(dict_dataframes, allvar)
print(final_dataframes)
taggerName = {
    "DeepFlav": "deepJet",
    "RobustParTAK4": "robustParticleTransformer",
    "PNet": "particleNet"
}
if not os.path.exists(era):
    os.system(f"mkdir {era}")
for c_algo in c_algos:
    writable_dataframe = pd.concat([final_dataframes[k] for k in final_dataframes.keys() if c_algo in k])
    writable_dataframe.to_csv(f"{era}/{taggerName[c_algo]}_wc_v1.csv", index=False)
print(writable_dataframe)
