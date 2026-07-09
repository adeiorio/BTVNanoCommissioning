#import ROOT
import os


eras = ['22', '22EE']
eras = ['23', '23BP']
eras = ['24']

input_folder = {'mu22':'/eos/user/a/adeiorio/btv_ctag_SF/v4/hist/',
                'e22':'/eos/user/a/adeiorio/btv_ctag_SF/v2e/hist/',
                'mu22EE':'/eos/user/a/adeiorio/btv_ctag_SF/v3EE/hist/',
                'e22EE':'/eos/user/a/adeiorio/btv_ctag_SF/v2eEE/hist/',
                'mu23':'/eos/user/a/adeiorio/btv_ctag_SF/Summer23/v8/hist/',
                'e23':'/eos/user/a/adeiorio/btv_ctag_SF/Summer23/v8e/hist/',
                'mu23BP':'/eos/user/a/adeiorio/btv_ctag_SF/Summer23BPix/v8/hist/',
                'e23BP':'/eos/user/a/adeiorio/btv_ctag_SF/Summer23BPix/v8e/hist/',
                'e24':'/eos/user/a/adeiorio/btv_ctag_SF/Summer24/v2e/hist/',
                'mu24':'/eos/user/a/adeiorio/btv_ctag_SF/Summer24/v2/hist/',
                }
taggers = ['DeepFlav', 'RobustParTAK4', 'PNet']
taggers = ['UParTAK4']
WPs = ['L', 'M', 'T', 'XT']

variations = ['Down', 'Up']
corr_systs = {'22':['puweight', 'UES', 'JER', 'JES'],
              '23':['puweight', 'UES', 'JER', 'JES', 'UEPS_ISR', 'UEPS_FSR', 'PDF_weight', 'aS_weight', 'scalevar_muR_muF', 'PDFaS_weight', 'scalevar_muR', 'scalevar_muF'],
              '24':['puweight', 'ttbar_weight', 'JER', 'JES', 'UEPS_ISR', 'UEPS_FSR', 'PDF_weight', 'aS_weight', 'scalevar_muR_muF', 'PDFaS_weight', 'scalevar_muR', 'scalevar_muF'],
              }
uncorr_systs_mu = ['mu_ID', 'mu_Iso']
uncorr_systs_ele = {'22': ['ele_ID', 'ele_Reco_med'],
                    '23': ['ele_ID', 'ele_Reco'],
                    '24': []
                    }

hist_types = ['c_histMC', 'histMC']

def hadd_files(target, sources):
    cmd = f"hadd -f {target} " + " ".join(sources)
    print(cmd)
    os.system(cmd)

def main():
    for era in eras:
        target_folder = f'/eos/user/a/adeiorio/btv_ctag_SF/{era}/sum_v1/'
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        
        hadd_files(f"{target_folder}mujet_pt_{era}_histdata.root", [
            f"{input_folder['mu'+era]}mujet_pt_mu_{era}_histdata.root",
            f"{input_folder['e'+era]}mujet_pt_e_{era}_histdata.root"
        ])
        
        for hist_type in hist_types:
            hadd_files(f"{target_folder}mujet_pt_{era}_{hist_type}_nominal.root", [
                f"{input_folder['mu'+era]}mujet_pt_mu_{era}_{hist_type}_nominal.root",
                f"{input_folder['e'+era]}mujet_pt_e_{era}_{hist_type}_nominal.root"
            ])
            
            for var in variations:
                for corr_syst in corr_systs[era[:2]]:
                    hadd_files(f"{target_folder}mujet_pt_{era}_{hist_type}_{corr_syst}{var}.root", [
                        f"{input_folder['mu'+era]}mujet_pt_mu_{era}_{hist_type}_{corr_syst}{var}.root",
                        f"{input_folder['e'+era]}mujet_pt_e_{era}_{hist_type}_{corr_syst}{var}.root"
                    ])
                for uncorr_syst in uncorr_systs_mu:
                    hadd_files(f"{target_folder}mujet_pt_{era}_{hist_type}_{uncorr_syst}{var}.root", [
                        f"{input_folder['mu'+era]}mujet_pt_mu_{era}_{hist_type}_{uncorr_syst}{var}.root",
                        f"{input_folder['e'+era]}mujet_pt_e_{era}_{hist_type}_nominal.root"
                    ])
                for uncorr_syst in uncorr_systs_ele[era[:2]]:
                    if era == '22': continue
                    hadd_files(f"{target_folder}mujet_pt_{era}_{hist_type}_{uncorr_syst}{var}.root", [
                        f"{input_folder['mu'+era]}mujet_pt_mu_{era}_{hist_type}_nominal.root",
                        f"{input_folder['e'+era]}mujet_pt_e_{era}_{hist_type}_{uncorr_syst}{var}.root"
                    ])

        for tagger in taggers:
            for WP in WPs:
                hadd_files(f"{target_folder}mujet_pt_{tagger}{WP}_{era}_histdata.root", [
                    f"{input_folder['mu'+era]}mujet_pt_{tagger}{WP}_mu_{era}_histdata.root",
                    f"{input_folder['e'+era]}mujet_pt_{tagger}{WP}_e_{era}_histdata.root"
                ])
                
                for hist_type in hist_types:
                    hadd_files(f"{target_folder}mujet_pt_{tagger}{WP}_{era}_{hist_type}_nominal.root", [
                        f"{input_folder['mu'+era]}mujet_pt_{tagger}{WP}_mu_{era}_{hist_type}_nominal.root",
                        f"{input_folder['e'+era]}mujet_pt_{tagger}{WP}_e_{era}_{hist_type}_nominal.root"
                    ])
                    
                    for var in variations:
                        for corr_syst in corr_systs[era[:2]]:
                            hadd_files(f"{target_folder}mujet_pt_{tagger}{WP}_{era}_{hist_type}_{corr_syst}{var}.root", [
                                f"{input_folder['mu'+era]}mujet_pt_{tagger}{WP}_mu_{era}_{hist_type}_{corr_syst}{var}.root",
                                f"{input_folder['e'+era]}mujet_pt_{tagger}{WP}_e_{era}_{hist_type}_{corr_syst}{var}.root"
                            ])
                        
                        for uncorr_syst in uncorr_systs_mu:
                            hadd_files(f"{target_folder}mujet_pt_{tagger}{WP}_{era}_{hist_type}_{uncorr_syst}{var}.root", [
                                f"{input_folder['mu'+era]}mujet_pt_{tagger}{WP}_mu_{era}_{hist_type}_{uncorr_syst}{var}.root",
                                f"{input_folder['e'+era]}mujet_pt_{tagger}{WP}_e_{era}_{hist_type}_nominal.root"
                            ])
                        for uncorr_syst in uncorr_systs_ele[era[:2]]:
                            if era == '22': continue
                            hadd_files(f"{target_folder}mujet_pt_{tagger}{WP}_{era}_{hist_type}_{uncorr_syst}{var}.root", [
                                f"{input_folder['mu'+era]}mujet_pt_{tagger}{WP}_mu_{era}_{hist_type}_nominal.root",
                                f"{input_folder['e'+era]}mujet_pt_{tagger}{WP}_e_{era}_{hist_type}_{uncorr_syst}{var}.root"
                            ])

if __name__ == '__main__':
    main()