from classes import *
from headers import *

def CalculateTotalError(hist):
    esq = 0
    for i in range(0, (hist.GetNbinsX()+2)):
        esq += pow(hist.GetBinError(i), 2)

    return sqrt(esq)


def histToCSV(hist):
    with open(f"{hist.GetName()}.csv","w", newline='') as csvfile:
        filednames = ['bin',
                      'binContent',
                      'binerror'
                    ]

        writer = csv.DictWriter(csvfile, fieldnames=filednames)
        writer.writeheader()
        writer.writerow({
            'bin'        : "under",
            'binContent' : hist.GetBinContent(0),
            'binerror'   : hist.GetBinError(0)

        })

        for i in range(1, (hist.GetNbinsX() + 1)):
            writer.writerow({
                'bin'        : i,
                'binContent' : hist.GetBinContent(i),
                'binerror'   : hist.GetBinError(i)
            })

        writer.writerow({
            'bin'        : "over",
            'binContent' : hist.GetBinContent((hist.GetNbinsX() + 1)),
            'binerror'   : hist.GetBinError((hist.GetNbinsX() + 1))
        })

def GetAllEventsWithErrors(hist):
    total = 0
    errorsq = 0
    for i in range(1, (hist.GetNbinsX()+1)):
        total += hist.GetBinContent(i)
        errorsq += pow(hist.GetBinError(i), 2)

    total += hist.GetBinContent((hist.GetNbinsX() + 1))
    total += hist.GetBinContent(0)

    errorsq += pow(hist.GetBinError((hist.GetNbinsX() + 1)), 2)
    errorsq += pow(hist.GetBinError(0), 2)

    return [total, sqrt(errorsq)]

def GetHist(rootFile, histName):
    """Get TH1 saved in a TFile 

    Args:
        rootFile (string): Input file name
        histName (string): Name of histogram

    Returns:
        TH1: histogram
    """
    keys = rootFile.GetListOfKeys()
    for key in keys:
        if ((key.GetClassName() == "TH1D")):
            hist = rootFile.Get(key.GetName())
            hist.SetDirectory(0)
            newHist = hist.Clone(histName)
            newHist.SetDirectory(0)
            finalHist = CalculateStatisticalErrorBinByBin(newHist)
            return finalHist


def GetAllEvents(hist):
    """Calculate Total Number of Events of a histogram including under+upper bins.

    Args:
        hist (TH1): ROOT.TH1

    Returns:
        double: total Number of events
    """
    return ((hist.GetBinContent(0)) + (hist.Integral()) + (hist.GetBinContent((hist.GetNbinsX()+1))))

def do_something(seconds):
    print(f'Sleeping {seconds}s')
    time.sleep(seconds)
    print (f'Done Sleeping {seconds}s')

def ProcessFile(inputList):
    print(f"Program: {inputList[0]} with the file: {inputList[1]}")
    result = subprocess.run(inputList, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(result.stdout)
    print(f"File: {inputList[1]} process completed successfully.!")

def CreateCumulativePlot(inHist):
    hist = ROOT.TH1D(f"{inHist.GetName()}_cum","", inHist.GetNbinsX(), inHist.GetXaxis().GetXmin(), inHist.GetXaxis().GetXmax() )
    hist.SetDirectory(0)
    total = 0
    for i in range(1, inHist.GetNbinsX() + 1):
        total = inHist.Integral(i, inHist.GetNbinsX())
        hist.SetBinContent(i, total)

    return hist

def CreatePurityHist(sig, back):
    hist = ROOT.TH1F("purity", "", sig.GetNbinsX(), sig.GetXaxis().GetXmin(), sig.GetXaxis().GetXmax())
    hist.SetDirectory(0)
    for i in range(1, sig.GetNbinsX() + 1):
        sigEvents = sig.GetBinContent(i)
        backEvents = back.GetBinContent(i)
        if ((sigEvents + backEvents) == 0):
            purity = 0
        else:
            purity = sigEvents/(sigEvents + backEvents)
        hist.SetBinContent(i, purity)

    return hist

def CreateSensitivityHist(sig, back):
    hist = ROOT.TH1F("purity", "", sig.GetNbinsX(), sig.GetXaxis().GetXmin(), sig.GetXaxis().GetXmax())
    hist.SetDirectory(0)
    for i in range(1, sig.GetNbinsX() + 1):
        sigEvents = sig.GetBinContent(i)
        backEvents = back.GetBinContent(i)
        if ((sigEvents + backEvents) == 0):
            purity = 0
        else:
            purity = sigEvents/sqrt(sigEvents + backEvents)
        hist.SetBinContent(i, purity)

    return hist

def SelectProngMuonCandidate(prongs):
    """This function is the old way of choosing the muon candidate based on single particle prong CVN and prong length.

    Args:
        prongs (List of Prong Objects): Prong Object with all attributes

    Returns:
        prong: Muon Candidate Prong
    """
    muonID   = -1.0
    prongLen = -1.0
    for prong in prongs:
        #print(f"Prong MuonID: {prong.GetMuonID()} Prong Length: {prong.GetLength()} Prong PID: {prong.GetPID()}")
        if (prong.GetMuonID() > muonID):
            muonID = prong.GetMuonID()
            muonCand = prong
        elif ((prong.GetLength() >= 500) and (prong.GetLength() > prongLen)):
        #elif (prong.GetLength() >= 500):
            muonID = prong.GetMuonID()
            prongLen = prong.GetLength()
            prongLen = prong.GetLength()
            muonCand = prong
    return muonCand


def AverageBeamDirection():
    dir = ROOT.TVector3(0.0011401229, -0.061901052, 0.99807253)
    return dir.Unit()

def MuonEnergyEstimator(muonLen):
    return (0.00206646*muonLen + 0.0201737)

def PionEEst(calE):
    #p0 =    0.220848   
    #p1 =    -1.62171    
    #p2 =      1.7838    
    #p3 =      83.802    
    #p4 =    -455.285    
    #p5 =     1046.78    
    #p6 =    -1162.29    
    #p7 =     501.243    
    #p8 =     79.3445    
    #p9 =    -93.2052


    p0 =     0.348592    
    p1 =     -5.98497    
    p2 =       54.545    
    p3 =     -207.531    
    p4 =      361.683    
    p5 =     -41.3106    
    p6 =     -941.125    
    p7 =      1647.79    
    p8 =     -1210.14    
    p9 =      343.351    
    
    return (p0              +
            p1*calE         +
            p2*pow(calE, 2) +
            p3*pow(calE, 3) +
            p4*pow(calE, 4) +
            p5*pow(calE, 5) +
            p6*pow(calE, 6) +
            p7*pow(calE, 7) +
            p8*pow(calE, 8) +
            p9*pow(calE, 9))

def CalculateRecoT(muonInfo, pionInfo):
    if(pionInfo[0] >= 0 and muonInfo[0] >= 0):
        beamDir = AverageBeamDirection()
        Ppion = sqrt(pionInfo[0]*(pionInfo[0] + (2*0.13957)))
        pionDir = ROOT.TVector3(pionInfo[1],pionInfo[2],pionInfo[3])
        unitPionDir = pionDir.Unit()
        vecPion = unitPionDir*Ppion
        Epion = pionInfo[0] + 0.13957


        muonKE = MuonEnergyEstimator(muonInfo[0])
        Pmuon = sqrt(muonKE*(muonKE + (2*0.105658)))
        muonDir = ROOT.TVector3(muonInfo[1],muonInfo[2],muonInfo[3])
        unitMuonDir = muonDir.Unit()
        vecMuon = unitMuonDir*Pmuon
        Emuon = muonKE + 0.105658

        muonPl = vecMuon.Dot(beamDir)
        pionPl = vecPion.Dot(beamDir) 

        vecTotalP = vecMuon + vecPion
        
        return (pow((Emuon - muonPl + Epion - pionPl), 2) + (vecTotalP.Mag2() - pow((vecTotalP.Dot(beamDir)), 2)))

    else:
        return (-10.0)

def CalculatePionPt(pionInfo):
    if(pionInfo[0] >= 0):
        Ppion = sqrt(pionInfo[0]*(pionInfo[0] + (2*0.13957)))
        pionDir = ROOT.TVector3(pionInfo[1],pionInfo[2],pionInfo[3])
        unitPionDir = pionDir.Unit()
        vecPion = unitPionDir*Ppion
        beamDir = AverageBeamDirection()
        pionPlDir = (vecPion.Dot(beamDir))*beamDir
        pionPtDir    = vecPion - pionPlDir
        return pionPtDir.Mag()
    else:
        return -10.0

def CalculateMuonPt(muonInfo):
    if(muonInfo[0] >= 0):
        muonKE = MuonEnergyEstimator(muonInfo[0])
        Pmuon = sqrt(muonKE*(muonKE + (2*0.105658)))
        muonDir = ROOT.TVector3(muonInfo[1],muonInfo[2],muonInfo[3])
        unitMuonDir = muonDir.Unit()
        vecMuon = unitMuonDir*Pmuon
        beamDir = AverageBeamDirection()
        muonPlDir = (vecMuon.Dot(beamDir))*beamDir
        muonPtDir    = vecMuon - muonPlDir
        return muonPtDir.Mag()
    else:
        return -10.0

def CalculateMuonPtUsingKalman(muonInfo):
    if(muonInfo[0] >= 0):
        muonKE = MuonEnergyEstimator(muonInfo[0])
        Pmuon = sqrt(muonKE*(muonKE + (2*0.105658)))
        muonDir = ROOT.TVector3(muonInfo[1],muonInfo[2],muonInfo[3])
        unitMuonDir = muonDir.Unit()
        vecMuon = unitMuonDir*Pmuon
        beamDir = AverageBeamDirection()
        muonPlDir = (vecMuon.Dot(beamDir))*beamDir
        muonPtDir    = vecMuon - muonPlDir
        return muonPtDir.Mag()
    else:
        return -10.0




def CalculateMissingPt(muonInfo, pionInfo):
    if(pionInfo[0] >= 0 and muonInfo[0] >= 0):
        Ppion = sqrt(pionInfo[0]*(pionInfo[0] + (2*0.13957)))
        pionDir = ROOT.TVector3(pionInfo[1],pionInfo[2],pionInfo[3])
        unitPionDir = pionDir.Unit()
        vecPion = unitPionDir*Ppion

        muonKE = MuonEnergyEstimator(muonInfo[0])
        Pmuon = sqrt(muonKE*(muonKE + (2*0.105658)))
        muonDir = ROOT.TVector3(muonInfo[1],muonInfo[2],muonInfo[3])
        unitMuonDir = muonDir.Unit()
        vecMuon = unitMuonDir*Pmuon

        vecTotalP = vecMuon + vecPion
        beamDir = AverageBeamDirection()

        return (sqrt(vecTotalP.Mag2() - pow(vecTotalP.Dot(beamDir), 2)))
    else:
        return -10.0

def CalculateOpeningAngle(muonInfo, pionInfo):
    if(pionInfo[0] >= 0 and muonInfo[0] >= 0):
        #Ppion = sqrt(pionInfo[0]*(pionInfo[0] + (2*0.13957)))
        pionDir = ROOT.TVector3(pionInfo[1],pionInfo[2],pionInfo[3])
        unitPionDir = pionDir.Unit()
        #vecPion = unitPionDir*Ppion

        #muonKE = MuonEnergyEstimator(muonInfo[0])
        #Pmuon = sqrt(muonKE*(muonKE + (2*0.105658)))
        muonDir = ROOT.TVector3(muonInfo[1],muonInfo[2],muonInfo[3])
        unitMuonDir = muonDir.Unit()
        #vecMuon = unitMuonDir*Pmuon

        theta = acos(unitMuonDir.Dot(unitPionDir))

        return theta

    else:
        return -10.0

def CalculateVisibleAngle(muonInfo, pionInfo):
    if(pionInfo[0] >= 0 and muonInfo[0] >= 0):
        Ppion = sqrt(pionInfo[0]*(pionInfo[0] + (2*0.13957)))
        pionDir = ROOT.TVector3(pionInfo[1],pionInfo[2],pionInfo[3])
        unitPionDir = pionDir.Unit()
        vecPion = unitPionDir*Ppion

        muonKE = MuonEnergyEstimator(muonInfo[0])
        Pmuon = sqrt(muonKE*(muonKE + (2*0.105658)))
        muonDir = ROOT.TVector3(muonInfo[1],muonInfo[2],muonInfo[3])
        unitMuonDir = muonDir.Unit()
        vecMuon = unitMuonDir*Pmuon

        vecTotalP = vecMuon + vecPion
        unitVecTotalP = vecTotalP.Unit()
        beamDir = AverageBeamDirection()
        return (acos(unitVecTotalP.Dot(beamDir)))

    else:
        return -10.0

def TrkLenAct(MuonInfo):
    if(MuonInfo.GetNTracks() < 1):
      return -1000.0

    # If leninact is positive and lenincat is negative, 
    # the transition plane is to the right of the track.

    if( (MuonInfo.GetLenInAct() > 0) and
        (MuonInfo.GetLenInCat() < 0) ):
        return ((MuonInfo.GetLenInAct() / 100.0) + (MuonInfo.GetLenInCat() / 100.0))

    # If leninact is positive and lenincat is positive,
    # the transition plane is in the middle of the track.

    if( (MuonInfo.GetLenInAct() > 0) and
        (MuonInfo.GetLenInCat() > 0) ):
        return (MuonInfo.GetLenInAct() / 100.0)

    # If leninact is negative and lenincat is positive,
    # the transition plane is to the left of the track.

    if( (MuonInfo.GetLenInAct() < 0 ) and
        (MuonInfo.GetLenInCat() > 0 ) ):
        return 0.0
    return -1000.0

def TrkLenCat(MuonInfo):
    if (MuonInfo.GetNTracks() < 1):
        return -1000.0

    # If leninact is positive and lenincat is negative,
    # the transition plane is to the right of the track.

    if  ( (MuonInfo.GetLenInAct() > 0) and
          (MuonInfo.GetLenInCat() < 0) ):
        return 0.0

    # If leninact is positive and lenincat is positive,
    # the transition plane is in the middle of the track.

    if ( (MuonInfo.GetLenInAct() > 0) and
         (MuonInfo.GetLenInCat() > 0) ):
        return (MuonInfo.GetLenInCat() / 100.)

    # If leninact is negative and lenincat is positive,
    # the transition plane is to the left of the track.

    if ( (MuonInfo.GetLenInAct() < 0) and
         (MuonInfo.GetLenInCat() > 0) ):
        return ( (MuonInfo.GetLenInAct() / 100.) + (MuonInfo.GetLenInCat() / 100.))

    return -1000.0

def MuonEAct(TrackLenAct):
    p0    =  1.67012e-01
    p1    =  1.79305e-01
    p2    =  3.74708e-03
    p3    = -1.54232e-04
    MuonE =  0.0

    if (TrackLenAct <= 0.0): 
        return 0.0
    MuonE = p0 + p1 * TrackLenAct + p2 * pow(TrackLenAct, 2) + p3 * pow(TrackLenAct, 3)
    return MuonE

def MuonECat(trklencat):
    offset  =  1.31325e-01
    slope   =  5.35146e-01
    MuonE   =  0.0

    if (trklencat <= 0.0): 
        return 0.0

    MuonE = slope*trklencat + offset
    return MuonE

def MuonEActandCat(trklenactandcat):
    p0   =  1.21130e-02
    p1   =  1.97903e-01
    p2   =  7.82459e-04
    MuonE = 0.0

    if (trklenactandcat <= 0.0):
        return 0.0

    MuonE = p0 + p1 * trklenactandcat + p2 * pow(trklenactandcat, 2)
    return MuonE

def CalculateMuonEUsingKalmanTracks(muonInfo):
    muonE          = 0.0
    muonEact       = 0.0
    muonEcat       = 0.0
    muonEactandcat = 0.0
    trkLenAct      = 0.0
    trkLenCat      = 0.0
    trkLenAct = TrkLenAct(muonInfo)
    trkLenCat = TrkLenCat(muonInfo)

    if ( muonInfo.GetNTracks() < 1 ):
        return -1000.0

    if ( (muonInfo.GetLenInAct() > 0) and
         (muonInfo.GetLenInCat() < 0) ):
        muonEact = MuonEAct(trkLenAct)

    elif ( (muonInfo.GetLenInAct() > 0) and
           (muonInfo.GetLenInCat() > 0)):
        muonEcat       = MuonECat(trkLenCat)
        muonEactandcat = MuonEActandCat(trkLenAct)
        muonE          = muonEactandcat + muonEcat

    return ( muonE + muonEact )/(1 - 7.65237e-4 )

def VisibleHadE(vishadE):
    p0    =   5.85254e-02
    p1    =   1.27796e+00
    p2    =   3.75457e-01
    p3    =  -5.45618e-01
    p4    =   1.65975e-01
    HadE  =   0.0

    HadE = p0 + (p1 * vishadE) + p2 * pow(vishadE, 2) + p3 * pow(vishadE, 3) + p4 * pow(vishadE, 4)
    return HadE



def CalculatePionEUsingKalmanTracks(pionInfo):
    # if (pionInfo.GetNTracks() == 2):
    #     # Extra energy (hadronic contamination) associated with muon track
    #     ExtraHadE = pionInfo.GetMuonOverlapE()

    #     # calorimetric slice  energy - Calorimetric Energy of Muon Track
    #     CalhadE   = pionInfo.GetSlcCalE() - pionInfo.GetMuonCalE()

    #     # Add calorimetric hadE and Overlap energy in the muon track
    #     vishadE   = CalhadE + ExtraHadE
    #     hadE      = VisibleHadE(vishadE)
    #     return hadE/((1 + 8.24107e-2)*(1 - 5.77832e-4))
    # else:
    hadE      = pionInfo.GetPionPngKE() + 0.13957
    return hadE/(1 + 3.82389e-2)

def CalculateMuonPtUsingKalmanTracks(muonInfo):
    muonE       = CalculateMuonEUsingKalmanTracks(muonInfo)
    if( (muonInfo.GetNTracks() > 0) and (muonE > 0)): 
        Pmuon       = sqrt( pow(muonE, 2) - pow(0.105658, 2) )
        muonDir     = ROOT.TVector3(muonInfo.GetDirX(), muonInfo.GetDirY(), muonInfo.GetDirZ())
        unitMuonDir = muonDir.Unit()
        vecMuon     = unitMuonDir*Pmuon
        beamDir     = AverageBeamDirection()
        muonPlDir   = (vecMuon.Dot(beamDir))*beamDir
        muonPtDir   = vecMuon - muonPlDir
        return muonPtDir.Mag()
    else:
        return -10000.0

def CalculatePionPtUsingKalmanTracks(pionInfo):
    #muonE       = CalculateMuonEUsingKalmanTracks(muonInfo)
    pionE       = CalculatePionEUsingKalmanTracks(pionInfo)
    if(pionInfo.GetNTracks() == 2 and pionE > 0.13957 ):
        pionE       = CalculatePionEUsingKalmanTracks(pionInfo)
        #print(pionE)
        Ppion       = sqrt( (pionE * pionE) - pow(0.13957, 2) )
        pionDir     = ROOT.TVector3(pionInfo.GetTrackDirX(), pionInfo.GetTrackDirY(), pionInfo.GetTrackDirZ())
        unitPionDir = pionDir.Unit()
        vecPion     = unitPionDir*Ppion
        beamDir     = AverageBeamDirection()
        pionPlDir   = (vecPion.Dot(beamDir))*beamDir
        pionPtDir   = vecPion - pionPlDir
        return pionPtDir.Mag()
    elif(pionInfo.GetPionPngKE() > 0):
        pionE       = pionInfo.GetPionPngKE() + 0.13957
        #print(pionInfo.GetPionPngKE())
        Ppion       = sqrt( (pionE * pionE) - pow(0.13957, 2) )
        pionDir     = ROOT.TVector3(pionInfo.GetProngDirX(), pionInfo.GetProngDirY(), pionInfo.GetProngDirZ())
        unitPionDir = pionDir.Unit()
        vecPion     = unitPionDir*Ppion
        beamDir     = AverageBeamDirection()
        pionPlDir   = (vecPion.Dot(beamDir))*beamDir
        pionPtDir   = vecPion - pionPlDir
        return pionPtDir.Mag()

    else:
        return -10000.0


def CalculateMissingPtUsingKalmanTracks(muonKalmanInfo, pionKalmanInfo):
    muonE       = CalculateMuonEUsingKalmanTracks(muonKalmanInfo)
    pionE       = CalculatePionEUsingKalmanTracks(pionKalmanInfo)
    if(muonKalmanInfo.GetNTracks() == 2 and (muonE > 0) and (pionE > 0.13957)):
        pionE       = CalculatePionEUsingKalmanTracks(pionKalmanInfo)
        Ppion       = sqrt( (pionE * pionE) - pow(0.13957, 2) )
        pionDir     = ROOT.TVector3(pionKalmanInfo.GetTrackDirX(), pionKalmanInfo.GetTrackDirY(), pionKalmanInfo.GetTrackDirZ())
        unitPionDir = pionDir.Unit()
        vecPion     = unitPionDir*Ppion

        muonE       = CalculateMuonEUsingKalmanTracks(muonKalmanInfo)
        Pmuon       = sqrt( pow(muonE, 2) - pow(0.105658, 2) )
        muonDir     = ROOT.TVector3(muonKalmanInfo.GetDirX(), muonKalmanInfo.GetDirY(), muonKalmanInfo.GetDirZ())
        unitMuonDir = muonDir.Unit()
        vecMuon     = unitMuonDir*Pmuon

        vecTotalP = vecMuon + vecPion
        beamDir = AverageBeamDirection()

        return (sqrt(vecTotalP.Mag2() - pow(vecTotalP.Dot(beamDir), 2)))
    elif ((muonE > 0) and pionKalmanInfo.GetPionPngKE() > 0):
        pionE       = pionKalmanInfo.GetPionPngKE() + 0.13957
        Ppion       = sqrt( (pionE * pionE) - pow(0.13957, 2) )
        pionDir     = ROOT.TVector3(pionKalmanInfo.GetProngDirX(), pionKalmanInfo.GetProngDirY(), pionKalmanInfo.GetProngDirZ())
        unitPionDir = pionDir.Unit()
        vecPion     = unitPionDir*Ppion

        muonE       = CalculateMuonEUsingKalmanTracks(muonKalmanInfo)
        Pmuon       = sqrt( pow(muonE, 2) - pow(0.105658, 2) )
        muonDir     = ROOT.TVector3(muonKalmanInfo.GetDirX(), muonKalmanInfo.GetDirY(), muonKalmanInfo.GetDirZ())
        unitMuonDir = muonDir.Unit()
        vecMuon     = unitMuonDir*Pmuon

        vecTotalP = vecMuon + vecPion
        beamDir = AverageBeamDirection()

        return (sqrt(vecTotalP.Mag2() - pow(vecTotalP.Dot(beamDir), 2)))

    else:
        return -10000.0

def CalculateOpeningAngleUsingKalmanTracks(muonKalmanInfo, pionKalmanInfo):
    muonE       = CalculateMuonEUsingKalmanTracks(muonKalmanInfo)
    if(muonKalmanInfo.GetNTracks() == 2 and (muonE > 0)):
        
        pionDir     = ROOT.TVector3(pionKalmanInfo.GetTrackDirX(), pionKalmanInfo.GetTrackDirY(), pionKalmanInfo.GetTrackDirZ())
        unitPionDir = pionDir.Unit()
        
        muonDir     = ROOT.TVector3(muonKalmanInfo.GetDirX(), muonKalmanInfo.GetDirY(), muonKalmanInfo.GetDirZ())
        unitMuonDir = muonDir.Unit()
        
        theta = acos(unitMuonDir.Dot(unitPionDir))
        return theta
    else:
        pionDir     = ROOT.TVector3(pionKalmanInfo.GetProngDirX(), pionKalmanInfo.GetProngDirY(), pionKalmanInfo.GetProngDirZ())
        unitPionDir = pionDir.Unit()
        
        muonDir     = ROOT.TVector3(muonKalmanInfo.GetDirX(), muonKalmanInfo.GetDirY(), muonKalmanInfo.GetDirZ())
        unitMuonDir = muonDir.Unit()
        
        theta = acos(unitMuonDir.Dot(unitPionDir))
        return theta

def CalculateVisibleAngleUsingKalmanTracks(muonKalmanInfo, pionKalmanInfo):
    muonE       = CalculateMuonEUsingKalmanTracks(muonKalmanInfo)
    pionE       = CalculatePionEUsingKalmanTracks(pionKalmanInfo)
    if(muonKalmanInfo.GetNTracks() == 2 and (muonE > 0) and (pionE > 0.13957)):
        pionE       = CalculatePionEUsingKalmanTracks(pionKalmanInfo)
        Ppion       = sqrt( (pionE * pionE) - pow(0.13957, 2) )
        pionDir     = ROOT.TVector3(pionKalmanInfo.GetTrackDirX(), pionKalmanInfo.GetTrackDirY(), pionKalmanInfo.GetTrackDirZ())
        unitPionDir = pionDir.Unit()
        vecPion     = unitPionDir*Ppion

        muonE       = CalculateMuonEUsingKalmanTracks(muonKalmanInfo)
        Pmuon       = sqrt( pow(muonE, 2) - pow(0.105658, 2) )
        muonDir     = ROOT.TVector3(muonKalmanInfo.GetDirX(), muonKalmanInfo.GetDirY(), muonKalmanInfo.GetDirZ())
        unitMuonDir = muonDir.Unit()
        vecMuon     = unitMuonDir*Pmuon

        vecTotalP = vecMuon + vecPion
        unitVecTotalP = vecTotalP.Unit()
        beamDir = AverageBeamDirection()
        return (acos(unitVecTotalP.Dot(beamDir)))
    
    elif(muonE > 0 and pionKalmanInfo.GetPionPngKE() > 0):
        pionE       = pionKalmanInfo.GetPionPngKE() + 0.13957
        Ppion       = sqrt( (pionE * pionE) - pow(0.13957, 2) )
        pionDir     = ROOT.TVector3(pionKalmanInfo.GetProngDirX(), pionKalmanInfo.GetProngDirY(), pionKalmanInfo.GetProngDirZ())
        unitPionDir = pionDir.Unit()
        vecPion     = unitPionDir*Ppion

        muonE       = CalculateMuonEUsingKalmanTracks(muonKalmanInfo)
        Pmuon       = sqrt( pow(muonE, 2) - pow(0.105658, 2) )
        muonDir     = ROOT.TVector3(muonKalmanInfo.GetDirX(), muonKalmanInfo.GetDirY(), muonKalmanInfo.GetDirZ())
        unitMuonDir = muonDir.Unit()
        vecMuon     = unitMuonDir*Pmuon

        vecTotalP = vecMuon + vecPion
        unitVecTotalP = vecTotalP.Unit()
        beamDir = AverageBeamDirection()
        return (acos(unitVecTotalP.Dot(beamDir)))
    
    else:
        return -10000.0

def CalculateRecoTUsingKalmanTracks(muonKalmanInfo, pionKalmanInfo):
    muonE       = CalculateMuonEUsingKalmanTracks(muonKalmanInfo)
    pionE       = CalculatePionEUsingKalmanTracks(pionKalmanInfo)
    if(muonKalmanInfo.GetNTracks() == 2 and (muonE > 0) and (pionE > 0.13957)):
        pionE       = CalculatePionEUsingKalmanTracks(pionKalmanInfo)
        Ppion       = sqrt( (pionE * pionE) - pow(0.13957, 2) )
        pionDir     = ROOT.TVector3(pionKalmanInfo.GetTrackDirX(), pionKalmanInfo.GetTrackDirY(), pionKalmanInfo.GetTrackDirZ())
        unitPionDir = pionDir.Unit()
        vecPion     = unitPionDir*Ppion

        muonE       = CalculateMuonEUsingKalmanTracks(muonKalmanInfo)
        Pmuon       = sqrt( pow(muonE, 2) - pow(0.105658, 2) )
        muonDir     = ROOT.TVector3(muonKalmanInfo.GetDirX(), muonKalmanInfo.GetDirY(), muonKalmanInfo.GetDirZ())
        unitMuonDir = muonDir.Unit()
        vecMuon     = unitMuonDir*Pmuon

        beamDir = AverageBeamDirection()

        muonPl = vecMuon.Dot(beamDir)
        pionPl = vecPion.Dot(beamDir) 

        vecTotalP = vecMuon + vecPion
        
        return (pow((muonE - muonPl + pionE - pionPl), 2) + (vecTotalP.Mag2() - pow((vecTotalP.Dot(beamDir)), 2)))

    elif(muonE > 0 and pionKalmanInfo.GetPionPngKE() > 0):
        pionE       = pionKalmanInfo.GetPionPngKE() + 0.13957
        Ppion       = sqrt( (pionE * pionE) - pow(0.13957, 2) )
        pionDir     = ROOT.TVector3(pionKalmanInfo.GetProngDirX(), pionKalmanInfo.GetProngDirY(), pionKalmanInfo.GetProngDirZ())
        unitPionDir = pionDir.Unit()
        vecPion     = unitPionDir*Ppion

        muonE       = CalculateMuonEUsingKalmanTracks(muonKalmanInfo)
        Pmuon       = sqrt( pow(muonE, 2) - pow(0.105658, 2) )
        muonDir     = ROOT.TVector3(muonKalmanInfo.GetDirX(), muonKalmanInfo.GetDirY(), muonKalmanInfo.GetDirZ())
        unitMuonDir = muonDir.Unit()
        vecMuon     = unitMuonDir*Pmuon

        beamDir = AverageBeamDirection()

        muonPl = vecMuon.Dot(beamDir)
        pionPl = vecPion.Dot(beamDir) 

        vecTotalP = vecMuon + vecPion
        
        return (pow((muonE - muonPl + pionE - pionPl), 2) + (vecTotalP.Mag2() - pow((vecTotalP.Dot(beamDir)), 2)))
    
    else:
        return -10000.0

def CalculateErrorOfTheBin(BinContent):
    return sqrt(BinContent)

def CalculateErrorOfRatioHist(numHist, denomHist):
    """
    This function creates the ratio histogram of the two histograms provided.
    
    Args:
        numHist   ([TH1]): [Histogram that goes to numerator]
        denomHist ([TH1]): [Histogram that goes to denominator]
    """
    hist = numHist.Clone("hist")
    hist.SetDirectory(0)
    hist.Divide(denomHist)

    for i in (range(0, hist.GetNbinsX()+2)):
        numBinContent   = numHist.  GetBinContent(i)
        denomBinContent = denomHist.GetBinContent(i)

        # numBinError   = sqrt(numBinContent)
        # denomBinError = sqrt(denomBinContent)

        if (denomBinContent != 0 and numBinContent != 0):
            ratioBinContent = numBinContent/denomBinContent
            ratioBinError   = sqrt(((1/numBinContent) + (1/denomBinContent)))*ratioBinContent

            hist.SetBinContent(i, ratioBinContent)
            hist.SetBinError(i, ratioBinError)

        elif (numBinContent != 0 and denomBinContent == 0):
            # ratioBinContent = hist.GetBinContent(i)
            # ratioBinError   = sqrt( pow(((numBinError)/numBinContent)    , 2) +
            #                         0
            #                     )*ratioBinContent

            hist.SetBinError(i, 0)

        elif (numBinContent == 0 and denomBinContent != 0):
            # ratioBinContent = hist.GetBinContent(i)
            # ratioBinError   = sqrt( 0 +
            #                         pow(((denomBinError)/denomBinContent), 2)
            #                     )*ratioBinContent

            hist.SetBinError(i, 0)

        elif (numBinContent == 0 and denomBinContent == 0):
            hist.SetBinError(i, 0)


    return hist

def CalculateStatisticalErrorBinByBin(hist):
    for i in (range(1, hist.GetNbinsX() + 1)):
        binVal = hist.GetBinContent(i)
        binError = sqrt(binVal)
        hist.SetBinError(i, binError)
    return hist

def CalculateStatErrorBinByBin(hist):
    for i in (range(1, hist.GetNbinsX() + 1)):
        binVal = hist.GetBinContent(i)
        binError = sqrt(binVal)
        hist.SetBinError(i, binError)

def CalculateStatisticalErrorOfSumOfHist(hist1, hist2):
    """Generate sum of Two Hists with errors.

    Args:
        hist1 (TH1D): Hist1 with errors
        hist2 (TH1D): Hist2 with errors

    Returns:
        TH1D: Total Hist = Hist1 + Hist2
    """
    nBins1 = hist1.GetNbinsX()
    nBins2 = hist2.GetNbinsX()

    if (nBins1 != nBins2):
        print(f"Unable to sum bins Hist1 nBins: {nBins1} Hist2 nBins: {nBins2}")
    else:
        total = hist1.Clone("total")
        total.SetDirectory(0)
        for i in range(1, (nBins1 + 1)):
            bin1 = hist1.GetBinContent(i)
            bin2 = hist2.GetBinContent(i)
            error1 = hist1.GetBinError(i)
            error2 = hist2.GetBinError(i)
            total.SetBinContent(i, (bin1 + bin2))
            total.SetBinError(i, sqrt(pow(error1, 2) + pow(error2, 2)))

        return total





def CalculateErrorOfRatioHistFullyCorelated(numHist, denomHist):
    """
    This function creates the ratio histogram of the two histograms provided.
    
    Args:
        numHist   ([TH1]): [Histogram that goes to numerator]
        denomHist ([TH1]): [Histogram that goes to denominator]
    """
    hist = numHist.Clone("hist")
    hist.SetDirectory(0)
    #hist.Divide(denomHist)

    for i in (range(1, hist.GetNbinsX()+1)):
        numBinContent   = numHist.  GetBinContent(i)
        denomBinContent = denomHist.GetBinContent(i)

        numBinError   = 0
        denomBinError = denomHist.GetBinError(i)
        

        if (denomBinContent != 0 and numBinContent != 0):
            #ratioBinContent = hist.GetBinContent(i)
            ratioBinContent = numBinContent/denomBinContent
            ratioBinError   = sqrt( pow(((numBinError)/numBinContent)    , 2) +
                                    pow(((denomBinError)/denomBinContent), 2)
                                )*ratioBinContent

            hist.SetBinContent(i, ratioBinContent)
            hist.SetBinError(i, ratioBinError)

        elif (numBinContent != 0 and denomBinContent == 0):
            ratioBinContent = hist.GetBinContent(i)
            ratioBinError   = sqrt( pow(((numBinError)/numBinContent)    , 2) +
                                    0
                                )*ratioBinContent

            hist.SetBinContent(i, 0)
            hist.SetBinError(i, ratioBinError)

        elif (numBinContent == 0 and denomBinContent != 0):
            ratioBinContent = hist.GetBinContent(i)
            ratioBinError   = sqrt( 0 +
                                    pow(((denomBinError)/denomBinContent), 2)
                                )*ratioBinContent

            hist.SetBinContent(i, ratioBinContent)
            hist.SetBinError(i, ratioBinError)

        elif (numBinContent == 0 and denomBinContent == 0):
            hist.SetBinContent(i, 0)
            hist.SetBinError(i, 0)


    return hist


# # # #def FillHistograms(tree, variable, histogram):
#Function made to Fill Histograms
def FillHistograms(inputs):
    for event in inputs[0]:
        inputs[2].Fill(getattr(event, inputs[1]))
    return inputs[2]

def SysEff(trueNum, eff):
    return round(sqrt(((eff*(1 - eff))/pow(trueNum, 2)))*100,3)




def GetCumulativeHistWithErrors(inHist):
    """Calculate Cumulative TH1D with Errors

    Args:
        inHist (TH1D): Input Histogram with errors

    Returns:
        TH1D: Cumulative Histogram
    """

    hist = ROOT.TH1D(f"{inHist.GetName()}_cum","", inHist.GetNbinsX(), inHist.GetXaxis().GetXmin(), inHist.GetXaxis().GetXmax() )
    hist.SetDirectory(0)
    total = 0
    for i in range(1, inHist.GetNbinsX() + 1):
        total = inHist.Integral(i, inHist.GetNbinsX())
        hist.SetBinContent(i, total)
        hist.SetBinError(i, sqrt(total))

    return hist




    
        


    


