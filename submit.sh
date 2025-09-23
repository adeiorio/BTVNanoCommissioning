ver="v0"
syst="--isSyst all" # "" #
extra="" #"--condorFileSize 2"
year="2024"
campaign="Summer24"
# ************* ${campaign} *************
# ************* muon *************
python condor/submitter.py --workflow ctag_Wc_WP_sf --json metadata/${campaign}/MC_${campaign}.json --campaign ${campaign} --year ${year} --jobName MC_${campaign}_$ver --outputDir root://eosuser.cern.ch///eos/user/a/adeiorio/btv_ctag_SF/${campaign}/$ver/MC/ $syst --overwrite
#dataMu_${campaign}.json
#python condor/submitter.py --workflow ctag_Wc_WP_sf --json metadata/${campaign}/dataMu_${campaign}.json  --campaign ${campaign} --year ${year} --jobName data_${campaign}_$ver --outputDir root://eosuser.cern.ch///eos/user/a/adeiorio/btv_ctag_SF/${campaign}/$ver/data --overwrite $extra
# ************* electron *************
python condor/submitter.py --workflow ectag_Wc_WP_sf --json metadata/${campaign}/MC_${campaign}.json --campaign ${campaign} --year ${year} --jobName MC_${campaign}_${ver}e --outputDir root://eosuser.cern.ch///eos/user/a/adeiorio/btv_ctag_SF/${campaign}/${ver}e/MC/ $syst --overwrite
#dataEle_${campaign}.json
#python condor/submitter.py --workflow ectag_Wc_WP_sf --json metadata/${campaign}/dataEle_${campaign}.json --campaign ${campaign} --year ${year} --jobName data_${campaign}_${ver}e --outputDir root://eosuser.cern.ch///eos/user/a/adeiorio/btv_ctag_SF/${campaign}/${ver}e/data  --overwrite $extra
