import os
import argparse
import time

parser = argparse.ArgumentParser(description="hist plotter for commissioning")
parser.add_argument("--dataMC", default=False, action="store_true", help="Produce the data-MC plots")
parser.add_argument("--root", default=False, action="store_true", help="Produce the root histograms")
parser.add_argument("--sf", default=False, action="store_true", help="Produce the SF")
args = parser.parse_args()

splits = ["flavor","sample", "sample_flav"]
splits = ["flavor", "sample"]
variables = ["pt", "eta", "phi", "mass"]

path = "/eos/user/a/adeiorio/btv_ctag_SF/"
v = "v2eEE"
lumi = "27000" # "8175" #
era = "22EE"
lep = "e"

if args.dataMC:
    for split in splits:
        for variable in variables:
            os.popen("python scripts/plotdataMC.py -i \"" + path + v + "/*/hists_*/*.coffea\" -p myctag_Wc_sf --lumi " + lumi + "  -v \*" + variable + "\* --split " + split + " &")
            #os.popen("python scripts/plotdataMC.py -i \"" + path + v + "/hist_*/hists_*/*.coffea\" -p myctag_Wc_sf --lumi " + lumi + "  -v \*" + variable + "\* --split " + split + " --ext SS --splitOSSS -1 &")
            #os.popen("python scripts/plotdataMC.py -i \"" + path + v + "/hist_*/hists_*/*.coffea\" -p myctag_Wc_sf --lumi " + lumi + "  -v \*" + variable + "\* --split " + split + " --ext OS --splitOSSS 1 &")


bvar = "mujet_pt"
allvar = [bvar]
c_algos = ["DeepFlav", "RobustParTAK4", "PNet"]
c_WPs = ["L", "M", "T"]
for c_algo in c_algos:
    for c_WP in c_WPs:
        allvar.append(bvar+"_"+c_algo+c_WP)
print(allvar)

if args.root:
    for var in allvar:
        #os.popen("python scripts/make_template.py -i \"" + path + v + "/data*/hists_*/*.coffea\" --lumi " + lumi + "  -o " + lep + "_" + era + "_histdata.root -v " + var + " -a \'{\"syst\":\"nominal\",\"flav\":\"sum\",\"osss\":\"sum\"}\' --mergemap mergemapdata" + era + lep + ".json  --autorebin \'24,30,42,60,84,144,204\'")
        #os.popen("python scripts/make_template.py -i \"" + path + v + "/MC*/hists_*/*.coffea\" --lumi " + lumi + "  -o " + lep + "_" + era + "_c_histMC.root -v " + var + " -a \'{\"syst\":\"nominal\",\"flav\":2,\"osss\":\"sum\"}\' --mergemap mergemapMC" + lep + ".json  --autorebin \'24,30,42,60,84,144,204\'")
        os.popen("python scripts/make_template.py -i \"" + path + v + "/MC*/hists_*/*.coffea\" --lumi " + lumi + "  -o " + lep + "_" + era + "_histMC.root -v " + var + " -a \'{\"syst\":\"nominal\",\"flav\":\"sum\",\"osss\":\"sum\"}\' --mergemap mergemapMC" + lep + ".json  --autorebin \'24,30,42,60,84,144,204\'")
        #os.popen("python scripts/make_template.py -i \"" + path + v + "/data*/hists_*/*.coffea\" --lumi " + lumi + "  -o " + lep + "_" + era + "_histdata.root -v " + var + " -a \'{\"syst\":\"nominal\",\"flav\":\"sum\",\"osss\":\"sum\"}\' --mergemap mergemapdata" + era + lep + ".json  --autorebin \'25,30,40,60,80,140,200\'")
        #print("python scripts/make_template.py -i \"" + path + v + "/data*/hists_*/*.coffea\" --lumi " + lumi + "  -o " + lep + "_" + era + "_histdata.root -v " + var + " -a \'{\"syst\":\"nominal\",\"flav\":\"sum\",\"osss\":\"sum\"}\' --mergemap mergemapdata" + era + lep + ".json  --autorebin \'25,30,40,60,80,140,200\'")
        #os.popen("python scripts/make_template.py -i \"" + path + v + "/MC*/hists_*/*.coffea\" --lumi " + lumi + "  -o " + lep + "_" + era + "_c_histMC.root -v " + var + " -a \'{\"syst\":\"nominal\",\"flav\":2,\"osss\":\"sum\"}\' --mergemap mergemapMC" + lep + ".json  --autorebin \'25,30,40,60,80,140,200\'")
        #os.popen("python scripts/make_template.py -i \"" + path + v + "/MC*/hists_*/*.coffea\" --lumi " + lumi + "  -o " + lep + "_" + era + "_histMC.root -v " + var + " -a \'{\"syst\":\"nominal\",\"flav\":\"sum\",\"osss\":\"sum\"}\' --mergemap mergemapMC" + lep + ".json  --autorebin \'25,30,40,60,80,140,200\'")
        #print("python scripts/make_template.py -i \"" + path + v + "/MC*/hists_*/*.coffea\" --lumi " + lumi + "  -o " + lep + "_" + era + "_c_histMC.root -v " + var + " -a \'{\"syst\":\"nominal\",\"flav\":2,\"osss\":\"sum\"}\' --mergemap mergemapMC" + lep + ".json  --autorebin \'25,30,40,60,80,140,200\'")
#print("python scripts/make_template.py -i \"" + path + v + "/MC*/hists_*/*.coffea\" --lumi " + lumi + "  -o histMC.root -v " + var + " -a \'{\"syst\":\"nominal\",\"flav\":2,\"osss\":\"sum\"}\' --mergemap mergemapMC.json  --autorebin \'0,24,30,42,60,84,144,204\'")
#
#print("python scripts/make_template.py -i \"" + path + v + "/data/hists_*/*.coffea\" --lumi " + lumi + "  -o histdata.root -v mujet_pt -a \'{\"syst\":\"sum\", :, :}\' ")

'''
histn = ["WJets",
         "ZJets",
         "VV",
         "TT",
         "ST"]
fout = rt.TFile.Open("SF22.root", "RECREATE")
allvar.pop(bvar)
inf_c = rt.TFile.Open(f"{bvar}_c_histMC.root")
inf_tot = rt.TFile.Open(f"{bvar}_histMC.root")
inf_data = rt.TFile.Open(f"{bvar}_histdata.root")
tmp = inf_c.Get(histn[0])
tmp.Reset("ICES")
tmp.Add([inf_c.Get(histn[h]) for h in histn])
print(tmp.Integral())
for var in all_var:
    inf_c = rt.TFile.Open(f"{var}_c_histMC.root")
    inf_tot = rt.TFile.Open(f"{var}_histMC.root")
    inf_data = rt.TFile.Open(f"{var}_histdata.root")

    full_MC_c = rt.TH1F()
'''
