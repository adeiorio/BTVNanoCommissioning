from coffea import util
from coffea.processor.accumulator import accumulate
import os

era = "Summer23BPix"
pathin = f"/eos/user/a/adeiorio/btv_ctag_SF/{era}/"
pathout = {"mu": f"/eos/user/a/adeiorio/btv_ctag_SF/{era}/v8/data/hists_1/",
            "e": f"/eos/user/a/adeiorio/btv_ctag_SF/{era}/v8e/data/hists_1/"}
subpathin = {"mu": ["v7", "vbis7",  "vquar7"], #"vtris7",
             "e": ["v7e", "vbis7e", "vquar7e"]}



#search in each subdirectory
for key in subpathin:
    #check if the output directory exists
    if not os.path.exists(pathout[key]):
        os.makedirs(pathout[key])
    files = []
    for subpath in subpathin[key]:
        for root, dirs, filenames in os.walk(pathin + subpath + "/data/"):
            files += [os.path.join(root, f) for f in filenames if f.endswith(".coffea")]
    print(files)
    histograms = [util.load(f) for f in files]
    merged = accumulate(histograms)
    util.save(merged, pathout[key] + "hists_1.coffea")
    #merged = accumulate(histograms)
    #util.save(merged, pathout + key + "_" + subpath + ".coffea")
