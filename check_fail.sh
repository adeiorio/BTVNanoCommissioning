 
 ver="v0e"
 channel="Ele"
 #channel="Mu"
 type="data" # MC
 campaign="Summer24"
 #campaign="Summer23"
 
 
 python scripts/dump_processed.py -t failed -c "/eos/user/a/adeiorio/btv_ctag_SF/${campaign}/${ver}/${type}/hists_*/hists_*.coffea" --json metadata/${campaign}/${type}${channel}_${campaign}.json -n ${campaign}_${type}${channel}_${ver}