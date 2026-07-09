import os
import argparse

parser = argparse.ArgumentParser(description="hist plotter for commissioning")
parser.add_argument("--dataMC", default=False, action="store_true", help="Produce the data-MC plots")
parser.add_argument("--root", default=False, action="store_true", help="Produce the root histograms")
parser.add_argument("--sf", default=False, action="store_true", help="Produce the SF")
args = parser.parse_args()

splits = ["flavor","sample", "sample_flav"]
splits = [ "sample"]
variables = ["pt", "eta", "phi", "mass"]

version = "v4"
path = "/eos/user/a/adeiorio/btv_ctag_SF/"
input_folder = {'mu22':f'{path}{version}/',
                'e22':f'{path}{version}e/',
                'mu22EE':f'{path}{version}EE/',
                'e22EE':f'{path}{version}eEE/',
                'mu23':f'{path}Summer23/{version}/',
                'e23':f'{path}Summer23/{version}e/',

                'mu23BP':f'{path}Summer23BPix/{version}/',
                'e23BP':f'{path}Summer23BPix/{version}e/',
                'mu24':f'{path}Summer24/{version}/',
                'e24':f'{path}Summer24/{version}e/'
                }
lumi = {"22": "8175",
        "22EE":"27000",
        '23':'17650',
        '23BP':'9450',
        '24': '109080' 
        }
era = "24"
lep = "mu"
phase = 'ctag_Wc_WP_sf'

if args.dataMC:
    for split in splits:
        for variable in variables:
            #print("python scripts/plotdataMC.py -i \"" + input_folder[lep+era] + "*/hists_*/*.coffea\" -p  " + phase + " --lumi " + lumi[era] + "  -v \*" + variable + "\* --split " + split)
            os.system("python scripts/plotdataMC.py -i \"" + input_folder[lep+era] + "*/hists_*/*.coffea\" -p  " + phase + " --lumi " + lumi[era] + "  -v \*" + variable + "\* --split " + split + " --ext " + lep + era + "_" + version.replace("*", "")) #+ " " + " --xrange 0,300"
            #os.popen("python scripts/plotdataMC.py -i \"" + input_folder[lep+era] + "/hist_*/hists_*/*.coffea\" -p  " + phase + " --lumi " + lumi[era] + "  -v \*" + variable + "\* --split " + split + " --ext SS --splitOSSS -1 &")
            #os.popen("python scripts/plotdataMC.py -i \"" + input_folder[lep+era] + "/hist_*/hists_*/*.coffea\" -p  " + phase + " --lumi " + lumi[era] + "  -v \*" + variable + "\* --split " + split + " --ext OS --splitOSSS 1 &")


bvar = "mujet_pt"
allvar = [bvar]
c_algos = ["DeepFlav", "RobustParTAK4", "PNet"]
c_algos = ["UParTAK4"]
c_WPs = ["L", "M", "T", "XT"]
for c_algo in c_algos:
    for c_WP in c_WPs:
        allvar.append(bvar+"_"+c_algo+c_WP)
print(allvar)
systs = {"mu22":['nominal', 'puweightUp', 'puweightDown', 'mu_IDUp', 'mu_IDDown', 'mu_IsoUp', 'mu_IsoDown', 'JESUp', 'JESDown', 'UESUp', 'UESDown', 'JERUp', 'JERDown'],
         "mu22EE":['nominal', 'puweightUp', 'puweightDown', 'mu_IDUp', 'mu_IDDown', 'mu_IsoUp', 'mu_IsoDown', 'JESUp', 'JESDown', 'UESUp', 'UESDown', 'JERUp', 'JERDown'],
         "e22":['nominal', 'puweightUp', 'puweightDown', 'JESUp', 'JESDown', 'UESUp', 'UESDown', 'JERUp', 'JERDown'],
         "e22EE":['nominal', 'puweightUp', 'puweightDown', 'ele_IDUp', 'ele_IDDown', 'ele_Reco_medDown', 'ele_Reco_medUp', 'JESUp', 'JESDown', 'UESUp', 'UESDown', 'JERUp', 'JERDown'],
         "mu23":['nominal', 'UEPS_ISRUp', 'puweightDown', 'PDF_weightUp', 'puweightUp', 'aS_weightUp', 'scalevar_muR_muFDown', 'UEPS_FSRDown', 'UEPS_ISRDown', 'scalevar_muR_muFUp', 'PDF_weightDown', 'mu_IDDown', 'mu_IsoUp', 'UEPS_FSRUp', 'scalevar_muFDown', 'ttbar_weightDown', 'mu_IsoDown', 'aS_weightDown', 'PDFaS_weightUp', 'scalevar_muRDown', 'mu_IDUp', 'scalevar_muFUp', 'ttbar_weightUp', 'PDFaS_weightDown', 'scalevar_muRUp', 'JESUp', 'JESDown', 'UESUp', 'UESDown', 'JERUp', 'JERDown'],
         "e23":['nominal', 'puweightUp', 'ele_RecoDown', 'scalevar_muFUp', 'ttbar_weightUp', 'scalevar_muRUp', 'UEPS_FSRUp', 'ele_IDUp', 'scalevar_muFDown', 'scalevar_muR_muFUp', 'UEPS_ISRDown', 'ttbar_weightDown', 'PDFaS_weightUp', 'ele_IDDown', 'PDF_weightUp', 'scalevar_muRDown', 'aS_weightUp', 'ele_RecoUp', 'puweightDown', 'PDF_weightDown', 'UEPS_FSRDown', 'PDFaS_weightDown', 'UEPS_ISRUp', 'scalevar_muR_muFDown', 'aS_weightDown', 'JESUp', 'JESDown', 'UESUp', 'UESDown', 'JERUp', 'JERDown'],
         "mu23BP":['nominal', 'UEPS_FSRUp', 'puweightDown', 'PDF_weightDown', 'ttbar_weightDown', 'puweightUp', 'mu_IDUp', 'scalevar_muFDown', 'PDFaS_weightDown', 'mu_IDDown', 'scalevar_muR_muFDown', 'PDFaS_weightUp', 'UEPS_ISRUp', 'ttbar_weightUp', 'mu_IsoUp', 'UEPS_ISRDown', 'aS_weightUp', 'mu_IsoDown', 'scalevar_muRDown', 'aS_weightDown', 'scalevar_muFUp', 'UEPS_FSRDown', 'scalevar_muR_muFUp', 'scalevar_muRUp', 'PDF_weightUp', 'JESUp', 'JESDown', 'JERUp', 'JERDown'],
         "e23BP":['nominal', 'UEPS_ISRDown', 'ele_RecoDown', 'scalevar_muRDown', 'aS_weightDown', 'ttbar_weightDown', 'PDF_weightUp', 'puweightDown', 'UEPS_FSRDown', 'PDFaS_weightUp', 'PDFaS_weightDown', 'scalevar_muFUp', 'ele_IDUp', 'scalevar_muR_muFUp', 'ele_IDDown', 'ttbar_weightUp', 'PDF_weightDown', 'ele_RecoUp', 'scalevar_muR_muFDown', 'scalevar_muFDown', 'aS_weightUp', 'puweightUp', 'scalevar_muRUp', 'UEPS_ISRUp', 'UEPS_FSRUp', 'JESUp', 'JESDown', 'JERUp', 'JERDown'],
         "mu24":['nominal', 'aS_weightDown', 'ttbar_weightUp', 'scalevar_muR_muFDown', 'PDF_weightDown', 'UEPS_ISRUp', 'scalevar_muRDown', 'UEPS_FSRDown', 'aS_weightUp', 'UEPS_ISRDown', 'scalevar_muRUp', 'ttbar_weightDown', 'mu_IDDown', 'puweightDown', 'UEPS_FSRUp', 'mu_IsoDown', 'mu_IsoUp', 'scalevar_muR_muFUp', 'PDF_weightUp', 'PDFaS_weightDown', 'scalevar_muFUp', 'PDFaS_weightUp', 'puweightUp', 'mu_IDUp', 'scalevar_muFDown', 'JESUp', 'JESDown', 'JERUp', 'JERDown'],
         "e24":['nominal', 'puweightDown', 'scalevar_muFDown', 'UEPS_FSRUp', 'aS_weightUp', 'scalevar_muR_muFDown', 'UEPS_ISRUp', 'PDF_weightDown', 'puweightUp', 'scalevar_muRDown', 'PDFaS_weightDown', 'scalevar_muR_muFUp', 'UEPS_ISRDown', 'scalevar_muFUp', 'aS_weightDown', 'PDF_weightUp', 'ttbar_weightDown', 'UEPS_FSRDown', 'ttbar_weightUp', 'PDFaS_weightUp', 'scalevar_muRUp', 'JESUp', 'JESDown', 'JERUp', 'JERDown']
     }

if args.root:
    for var in allvar:
        print(f"Making template for variable {var} data {era} {lep}")
        os.system("python scripts/make_template.py -i \"" + input_folder[lep+era] + "/data*/hists_*/*.coffea\" --lumi " + lumi[era] + "  -o " + lep + "_" + era + "_histdata.root -v " + var + " -a \'{\"syst\":\"nominal\",\"flav\":\"sum\",\"osss\":\"sum\"}\' --mergemap mergemapdata" + era + lep + ".json  --autorebin \'25,30,40,60,80,140,200\'")
        for syst in systs[lep+era]:
            print(f"Making template for variable {var}, syst {syst} MC c")
            os.system("python scripts/make_template.py -i \"" + input_folder[lep+era] + "/MC*/hists_*/*.coffea\" --lumi " + lumi[era] + "  -o " + lep + "_" + era + "_c_histMC_" + syst + ".root -v " + var + " -a \'{\"syst\":\"" + syst + "\",\"flav\":2,\"osss\":\"sum\"}\' --mergemap mergemapMC" + era + ".json  --autorebin \'25,30,40,60,80,140,200\'")
            print(f"Making template for variable {var}, syst {syst} MC")
            os.system("python scripts/make_template.py -i \"" + input_folder[lep+era] + "/MC*/hists_*/*.coffea\" --lumi " + lumi[era] + "  -o " + lep + "_" + era + "_histMC_" + syst + ".root -v " + var + " -a \'{\"syst\":\"" + syst + "\",\"flav\":\"sum\",\"osss\":\"sum\"}\' --mergemap mergemapMC" + era + ".json  --autorebin \'25,30,40,60,80,140,200\'")
    os.system(f"mv mujet_pt_*{lep}_{era}_*.root {input_folder[lep+era]}/hist/")
